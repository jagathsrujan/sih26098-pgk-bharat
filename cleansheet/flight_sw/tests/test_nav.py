import json
import math
import os

import numpy as np
import pytest

import fsw
from fsw.nav import DragAnchor, NavEKF, RollEKF

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def load(name):
    with open(os.path.join(GOLDEN, name)) as f:
        return json.load(f)


def assert_close(a, b, rel=1e-9, abs_tol=1e-12, path=""):
    if isinstance(a, list) and isinstance(b, list):
        assert len(a) == len(b), f"{path}: length {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            assert_close(x, y, rel, abs_tol, f"{path}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return
        assert a == pytest.approx(b, rel=rel, abs=abs_tol), f"{path}: {a} vs {b}"
    else:
        assert a == b, f"{path}: {a} vs {b}"


def test_navekf_matches_sim_on_recorded_stream():
    g = load("navekf.json")
    ekf = NavEKF(g["cd_cal"])
    for k, op in enumerate(g["ops"]):
        if op["op"] == "init":
            ekf.init_from_fix(np.array(op["pos_p"]), np.array(op["vel"]), op["t"])
        else:
            for _ in range(40):
                ekf.predict(fsw.C.DT_TRUTH, (0.3 * math.cos(op["az"]),
                                             0.3 * math.sin(op["az"])))
            ok, maha = ekf.update_gnss(np.array(op["pos_p"]), np.array(op["vel"]),
                                       r_floor=op["r_floor"], pos_only=op["pos_only"])
            assert ok == op["accepted"]
            assert_close(float(maha), op["maha"], path=f"op{k}.maha")
            assert_close(float(ekf.nis), op["nis"], path=f"op{k}.nis")
            assert_close(float(ekf.r_scale), op["r_scale"], path=f"op{k}.r_scale")
        assert_close(ekf.x.tolist(), op["x"], path=f"op{k}.x")
        assert_close(ekf.P.tolist(), op["P"], path=f"op{k}.P")
        if "sigma_pos" in op:
            assert_close(ekf.sigma_pos(), op["sigma_pos"], path=f"op{k}.sigma")


def test_rollekf_matches_sim_on_recorded_stream():
    g = load("rollekf.json")
    est = RollEKF()
    for k, rec in enumerate(g["ops"]):
        if rec.get("fresh"):
            fresh = RollEKF()
            ok, nis = fresh.update(rec["psi_meas"], rec["R"])
            assert ok == rec["accepted"]
            assert_close(fresh.psi, rec["psi"], path=f"op{k}.psi")
            continue
        if rec["op"] == "predict":
            est.predict(rec["gyro"], fsw.C.DT_TRUTH, rec["sat"])
        else:
            ok, nis = est.update(rec["psi_meas"], rec["R"])
            assert ok == rec["accepted"]
            assert_close(float(nis), rec["nis"], path=f"op{k}.nis")
        assert_close(est.psi, rec["psi"], path=f"op{k}.psi")
        assert_close(est.b, rec["b"], path=f"op{k}.b")
        assert_close(est.m, rec["m"], path=f"op{k}.m")
        assert_close(est.P.tolist(), rec["P"], path=f"op{k}.P")


def test_anchor_solve_matches_sim_math():
    g = load("anchor.json")
    n_solved = 0
    for i, case in enumerate(g["cases"]):
        out = DragAnchor.solve(tuple(case["c_bar"]), tuple(case["m_bar"]),
                               tuple(case["u_bar"]))
        if case["expected"] is None:
            assert out is None, f"case {i}: expected gate failure"
        else:
            n_solved += 1
            assert_close(out[0], case["expected"][0], path=f"case{i}.psi_meas")
            assert_close(out[1], case["expected"][1], path=f"case{i}.R_psi")
    assert n_solved > 10


def test_roll_ekf_gates_and_health_fields():
    est = RollEKF()
    assert est.psi is None
    # never initialize from a garbage window
    ok, nis = est.update(1.0, (math.radians(15.0)) ** 2)
    assert not ok and est.psi is None
    # innovation gate: huge residual rejected, P inflated
    ok, _ = est.update(0.5, (math.radians(0.8)) ** 2)
    assert ok
    p00 = est.P[0, 0]
    ok, _ = est.update(0.5 + 1.0, (math.radians(0.8)) ** 2)
    assert not ok and est.P[0, 0] > p00
    # err_vs is nan while uninitialized, degrees otherwise
    est2 = RollEKF()
    assert math.isnan(est2.err_vs(0.3))
