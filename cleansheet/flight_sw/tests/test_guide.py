import json
import math
import os

import pytest

import fsw
from fsw.dynamics import q70_ref, q_profile
from fsw.guide import Guidance, law_apn_clean, law_l0, law_zem

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def load(name):
    with open(os.path.join(GOLDEN, name)) as f:
        return json.load(f)


def test_ipp_matches_sim_propagate_on_recorded_states():
    g = load("ipp.json")
    for case in g["cases"]:
        xi, yi, t_imp, apo = fsw.dynamics.propagate_to_ground(
            tuple(case["st"]), case["cd"], tuple(case["wind"]), fsw.C.DT_IPP)
        assert xi == pytest.approx(case["xi"], rel=1e-9, abs=1e-9), case["t"]
        assert yi == pytest.approx(case["yi"], rel=1e-9, abs=1e-9)
        assert t_imp == pytest.approx(case["t_imp"], rel=1e-9, abs=1e-9)
        assert apo == pytest.approx(case["apo"], rel=1e-9, abs=1e-9)


def test_laws_match_sim():
    g = load("laws.json")
    for mx, my, t_go, ex, ey in g["l0"]:
        assert (law_l0(mx, my, t_go) == (ex, ey))
    for mx, my, t_go, ex, ey in g["zem"]:
        assert (law_zem(mx, my, t_go) == (ex, ey))
    for pos, vel, ex, ey in g["apn"]:
        assert (law_apn_clean(tuple(pos), tuple(vel), (30000.0, 0.0)) == (ex, ey))


def test_pre_flight_tables_match_sim():
    g = load("pretables.json")
    # The table is generated with the same equations, but libm/Python builds
    # can differ by a few ulps at isolated integration steps.
    assert q_profile(g["cd_cal"]) == pytest.approx(g["q_profile"], rel=1e-12, abs=1e-9)
    assert q70_ref(g["cd_cal"]) == pytest.approx(g["q70"], rel=1e-12)


def test_guidance_tick_command_chain():
    """Freeze, deadband, authority clamp, low-pass, duty mapping."""
    g = Guidance(cd_cal=0.2115, q_ref=fsw.dynamics.q70_ref(0.2115))
    # far state, large miss: commands should saturate authority at long t_go
    st = (0.0, 0.0, 9000.0, -180.0, 12.0, -160.0)
    a_auth = g.tick(st, 1.0, (0.0, 0.0), law="l0")
    assert a_auth > 0.0
    assert 0.0 < g.d_cmd <= 1.0
    first = g.a_cmd_s
    # low-pass converges toward the raw law over ticks
    for _ in range(50):
        g.tick(st, 1.0, (0.0, 0.0), law="l0")
    assert g.a_cmd_s != first
    # terminal state from the recorded run: t_go < 2 s freezes and the
    # sub-deadband miss keeps the command neutral
    g2 = Guidance(cd_cal=0.2115, q_ref=fsw.dynamics.q70_ref(0.2115))
    term = next(c for c in load("ipp.json")["cases"] if c["t"] == 89.0)
    g2.tick(tuple(term["st"]), 1.0, (0.0, 0.0), law="l0")
    assert g2.t_go < fsw.C.GUIDE_FREEZE_TGO
    assert g2.ipp_miss < fsw.C.DEADBAND
    assert g2.d_cmd == 0.0
    # neutral(): duty zero, azimuth held
    g2.theta_cmd = 1.234
    g2.neutral()
    assert g2.d_cmd == 0.0 and g2.theta_cmd == 1.234
