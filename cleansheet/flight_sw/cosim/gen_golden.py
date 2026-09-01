"""Golden-vector generator — extracts reference values from the seeded Rev E
sim code (scripts/sim_gnc_check.py) for the FSW unit tests.

Run:  python3 cosim/gen_golden.py       (from cleansheet/flight_sw/)

Writes tests/golden/*.json. Values come from the sim's OWN classes and
inline blocks (NavEKF_E, RollEstimatorE, the anchor solve and servo mirror
math of sim_gnc_revE, propagate, laws, duty_pattern) fed by a seeded stream
(seed 20260901). The tests then demand the FSW port reproduce them.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FLIGHT_SW = os.path.dirname(HERE)
CLEANSHEET = os.path.dirname(FLIGHT_SW)
sys.path.insert(0, FLIGHT_SW)
sys.path.insert(0, os.path.join(CLEANSHEET, "scripts"))

import sim_gnc_check as sim  # noqa: E402

GOLDEN_DIR = os.path.join(FLIGHT_SW, "tests", "golden")
SEED = 20260901


def dump(name, obj):
    os.makedirs(GOLDEN_DIR, exist_ok=True)
    path = os.path.join(GOLDEN_DIR, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
    print(f"wrote {path} ({os.path.getsize(path)} bytes)")


def recorded_states(cd_cal, epochs=(45.0, 60.0, 75.0, 89.0)):
    """Truth trajectory states at the requested epochs (nominal shot)."""
    s = sim.initial_state(sim.V0_NOM, sim.ELEV0, 0.0)
    t = 0.0
    out = {}
    next_epoch = 0
    while t < sim.TMAX and next_epoch < len(epochs):
        s_prev = s
        s = sim.rk4_step(s, sim.DT_TRUTH, cd_cal, (0.0, 0.0))
        t += sim.DT_TRUTH
        if s[2] <= 0 < s_prev[2]:
            break
        if next_epoch < len(epochs) and t >= epochs[next_epoch] - 1e-9:
            out[epochs[next_epoch]] = tuple(float(v) for v in s)
            next_epoch += 1
    return out


def gen_navekf(cd_cal, states):
    """NavEKF_E stream: init + alternating predict bursts and updates with
    varied r_floor / pos_only, all inputs drawn from the seeded stream."""
    rng = np.random.default_rng(SEED)
    ekf = sim.NavEKF_E(cd_cal)
    epochs = sorted(states)
    s0 = states[epochs[0]]
    pos_m = np.array([s0[0] + rng.normal(0, sim.GPS_POS_SIG),
                      s0[1] + rng.normal(0, sim.GPS_POS_SIG),
                      s0[2] + rng.normal(0, sim.GPS_POS_SIG * 1.6)])
    vel_m = np.array([s0[3] + rng.normal(0, sim.GPS_VEL_SIG),
                      s0[4] + rng.normal(0, sim.GPS_VEL_SIG),
                      s0[5] + rng.normal(0, sim.GPS_VEL_SIG)])
    pos_p = pos_m + vel_m * sim.GNSS_LAT
    ekf.init_from_fix(pos_p, vel_m, 45.0)
    ops = [{"op": "init", "pos_p": pos_p.tolist(), "vel": vel_m.tolist(),
            "x": ekf.x.tolist(), "P": ekf.P.tolist(), "t": 45.0}]
    ff_mag = 0.3
    for i in range(1, 24):
        for _ in range(40):
            az = 2.0 * math.pi * (i % 7) / 7.0
            ekf.predict(sim.DT_TRUTH, (ff_mag * math.cos(az), ff_mag * math.sin(az)))
        st_true = states[epochs[min(i, len(epochs) - 1)]]
        pos_m = np.array([st_true[0] + rng.normal(0, sim.GPS_POS_SIG),
                          st_true[1] + rng.normal(0, sim.GPS_POS_SIG),
                          st_true[2] + rng.normal(0, sim.GPS_POS_SIG * 1.6)])
        vel_m = np.array([st_true[3] + rng.normal(0, sim.GPS_VEL_SIG),
                          st_true[4] + rng.normal(0, sim.GPS_VEL_SIG),
                          st_true[5] + rng.normal(0, sim.GPS_VEL_SIG)])
        pos_p = pos_m + vel_m * sim.GNSS_LAT
        r_floor = [1.0, 2.0, 4.0, 16.0][i % 4]
        pos_only = (i % 7 == 0)
        ok, maha = ekf.update_gnss(pos_p, vel_m, r_floor=r_floor, pos_only=pos_only)
        ops.append({"op": "update", "az": az, "pos_p": pos_p.tolist(),
                    "vel": vel_m.tolist(),
                    "r_floor": r_floor, "pos_only": pos_only, "accepted": bool(ok),
                    "maha": maha, "nis": ekf.nis, "r_scale": ekf.r_scale,
                    "x": ekf.x.tolist(), "P": ekf.P.tolist(),
                    "sigma_pos": ekf.sigma_pos()})
    dump("navekf.json", {"seed": SEED, "cd_cal": cd_cal, "ops": ops})


def gen_rollekf():
    rng = np.random.default_rng(SEED + 1)
    est = sim.RollEstimatorE()
    ops = []
    psi_true = 0.0
    for i in range(90):
        rate = 0.5 * math.sin(0.3 * i) + rng.normal(0, math.radians(0.2))
        sat = (i % 23 == 0)
        if not sat:
            psi_true += rate * sim.DT_TRUTH
        est.predict(rate, sim.DT_TRUTH, sat)
        ops.append({"op": "predict", "gyro": rate, "sat": sat,
                    "psi": est.psi, "b": est.b, "m": est.m,
                    "P": est.P.tolist()})
        if i % 3 == 0:
            psi_meas = psi_true + rng.normal(0, math.radians(1.5))
            R = (math.radians(rng.uniform(0.8, 3.0))) ** 2
            ok, nis = est.update(psi_meas, R)
            ops.append({"op": "update", "psi_meas": psi_meas, "R": R,
                        "accepted": bool(ok), "nis": nis,
                        "psi": est.psi, "b": est.b, "m": est.m,
                        "P": est.P.tolist()})
    # init-rejection case: fresh estimator, garbage window
    est2 = sim.RollEstimatorE()
    ok, nis = est2.update(1.234, (math.radians(15.0)) ** 2)
    ops.append({"op": "update", "fresh": True, "psi_meas": 1.234,
                "R": (math.radians(15.0)) ** 2, "accepted": bool(ok), "nis": nis,
                "psi": est2.psi, "P": est2.P.tolist()})
    dump("rollekf.json", {"seed": SEED + 1, "ops": ops})


def gen_anchor():
    """Reference anchor solves — the inline sim_gnc_revE math on seeded
    window averages (includes both magnitude-gate failure shapes)."""
    rng = np.random.default_rng(SEED + 2)
    cases = []
    for k in range(36):
        scale = [1.0, 0.02, 1.0, 1.0][k % 4] if k % 2 == 0 else 1.0
        c_bar = (rng.normal(0, 1.2) * scale, rng.normal(0, 1.2) * scale)
        m_bar = (rng.normal(0, 0.9) * (0.01 if k % 5 == 0 else 1.0),
                 rng.normal(0, 0.9) * (0.01 if k % 5 == 0 else 1.0))
        u_bar = (rng.normal(0, 0.7), rng.normal(0, 0.7))
        expected = None
        if math.hypot(*m_bar) > 0.3 and math.hypot(*c_bar) > 0.1:
            delta = (math.atan2(c_bar[1], c_bar[0])
                     - math.atan2(m_bar[1], m_bar[0]))
            psi_meas = (math.atan2(u_bar[1], u_bar[0]) - delta)
            res = (c_bar[0] - (math.cos(delta) * m_bar[0] - math.sin(delta) * m_bar[1]),
                   c_bar[1] - (math.sin(delta) * m_bar[0] + math.cos(delta) * m_bar[1]))
            cmag = math.hypot(*c_bar)
            res_perp = abs(-c_bar[1] * res[0] + c_bar[0] * res[1]) / max(cmag, 1e-9)
            sig_psi = math.radians(0.8) + res_perp / max(cmag, 0.3)
            expected = [psi_meas, sig_psi * sig_psi]
        cases.append({"c_bar": list(c_bar), "m_bar": list(m_bar),
                      "u_bar": list(u_bar), "expected": expected})
    dump("anchor.json", {"seed": SEED + 2, "cases": cases})


def gen_ipp(cd_cal, states):
    rng = np.random.default_rng(SEED + 3)
    cases = []
    for t_e, st in sorted(states.items()):
        cd = cd_cal * float(1.0 + rng.normal(0, 0.008))
        wind = (float(rng.normal(0, 3.0)), float(rng.normal(0, 3.0)))
        xi, yi, t_imp, apo = sim.propagate(st, cd, wind, sim.DT_IPP)
        cases.append({"t": t_e, "st": list(st), "cd": cd, "wind": list(wind),
                      "xi": xi, "yi": yi, "t_imp": t_imp, "apo": apo})
    # degenerate: already at ground
    st0 = sim.initial_state(sim.V0_NOM, sim.ELEV0, 0.0)
    xi, yi, t_imp, apo = sim.propagate(st0, cd_cal, (0.0, 0.0), sim.DT_IPP)
    cases.append({"t": 0.0, "st": list(st0), "cd": cd_cal, "wind": [0.0, 0.0],
                  "xi": xi, "yi": yi, "t_imp": t_imp, "apo": apo})
    dump("ipp.json", {"seed": SEED + 3, "cd_cal": cd_cal, "cases": cases})


def gen_pattern():
    cases = []
    for base in (0.3, -1.2, 2.7):
        for d in (0.0, 0.01, 0.3, 0.6, 0.97, 1.0):
            for i in range(0, 121):
                t = i * 0.1
                cases.append([t, base, d, sim.duty_pattern(t, base, d)])
    dump("pattern.json", {"cases": cases})


def gen_laws():
    rng = np.random.default_rng(SEED + 4)
    l0, zem, apn = [], [], []
    for _ in range(40):
        mx, my = float(rng.uniform(-400, 400)), float(rng.uniform(-400, 400))
        t_go = float(rng.uniform(2.5, 45.0))
        l0.append([mx, my, t_go] + list(sim.law_l0(mx, my, t_go)))
        zem.append([mx, my, t_go] + list(sim.law_zem(mx, my, t_go)))
        pos = (float(rng.uniform(0, 30000)), float(rng.uniform(-2000, 2000)))
        vel = (float(rng.uniform(-400, 0)), float(rng.uniform(-80, 80)))
        apn.append([list(pos), list(vel)] + list(sim.law_apn_clean(pos, vel, (30000.0, 0.0))))
    dump("laws.json", {"l0": l0, "zem": zem, "apn": apn})


def gen_servo():
    cases = []
    dt = sim.DT_TRUTH
    for i in range(-60, 61):
        err = i * 0.02
        om_mag = min(6.28, math.sqrt(2.0 * 55.0 * abs(err)), abs(err) / (2.0 * dt))
        om_des = 0.0 if abs(err) < math.radians(0.1) else math.copysign(om_mag, err)
        cases.append([err, dt, om_des])
    dump("servo.json", {"cases": cases})


def gen_pretables(cd_cal):
    dump("pretables.json", {"cd_cal": cd_cal,
                            "q_profile": sim.q_profile(cd_cal),
                            "q70": sim.q70_ref(cd_cal)})


def main():
    cd_cal, x_nom, tof, apo = sim.calibrate_cd()
    print(f"cd_cal={cd_cal:.12f} x_nom={x_nom:.1f} tof={tof:.1f} apo={apo/1000:.2f}km")
    states = recorded_states(cd_cal)
    gen_navekf(cd_cal, states)
    gen_rollekf()
    gen_anchor()
    gen_ipp(cd_cal, states)
    gen_pattern()
    gen_laws()
    gen_servo()
    gen_pretables(cd_cal)


if __name__ == "__main__":
    main()
