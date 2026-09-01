import json
import math
import os

import pytest

import fsw
from fsw.ctrl import CtrlTask, duty_pattern
from fsw.guide import Guidance
from fsw.nav import NavigationStack

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def load(name):
    with open(os.path.join(GOLDEN, name)) as f:
        return json.load(f)


def test_duty_pattern_matches_sim_grid():
    for t, base, d, expected in load("pattern.json")["cases"]:
        assert duty_pattern(t, base, d) == expected, (t, base, d)


def test_duty_pattern_segments():
    """dwell/±90 split and park alternation, analytically."""
    T = fsw.C.T_MOD
    # d = 0.6: [0, 1.8) at base, [1.8, 2.4) at +90, [2.4, 3.0) at -90
    base = 0.3
    assert duty_pattern(0.0, base, 0.6) == pytest.approx(base)
    assert duty_pattern(1.7999, base, 0.6) == pytest.approx(base)
    assert duty_pattern(1.8001, base, 0.6) == pytest.approx(base + math.pi / 2)
    assert duty_pattern(2.3999, base, 0.6) == pytest.approx(base + math.pi / 2)
    assert duty_pattern(2.4001, base, 0.6) == pytest.approx(base - math.pi / 2)
    assert duty_pattern(2.9999, base, 0.6) == pytest.approx(base - math.pi / 2)
    # d >= 0.98: pure dwell at base
    assert duty_pattern(2.5, base, 0.98) == pytest.approx(base)
    assert duty_pattern(2.5, base, 1.0) == pytest.approx(base)
    # d < 0.02: park alternates +90/-90 per full cycle
    assert duty_pattern(0.5, base, 0.0) == pytest.approx(base + math.pi / 2)
    assert duty_pattern(3.5, base, 0.0) == pytest.approx(base - math.pi / 2)
    assert duty_pattern(6.5, base, 0.0) == pytest.approx(base + math.pi / 2)


def test_servo_mirror_matches_sim():
    for err, dt, expected in load("servo.json")["cases"]:
        assert CtrlTask.servo_rate_cmd(err, dt) == expected, err


def test_ctrl_flip_events_and_settle():
    """A commanded flip publishes pattern_change (nav flushes) and resets the
    settle timer; a quiescent pattern accumulates SETTLE_T then reports settled."""
    bus = fsw.EventBus()
    guide = Guidance(0.2115, fsw.dynamics.q70_ref(0.2115))
    nav = NavigationStack(0.2115)
    ctrl = CtrlTask(bus, guide, nav, 0.2115, fsw.dynamics.q70_ref(0.2115))
    flips = []
    bus.subscribe("pattern_change", lambda ev: flips.append(ev["t"]))
    nav_flushes = []
    orig_handler = nav.on_pattern_change
    nav.on_pattern_change = lambda ev: (orig_handler(ev), nav_flushes.append(1))
    bus.subscribe("pattern_change", nav.on_pattern_change)

    # guide commands a 90-deg azimuth + duty: expect one flip per segment change
    guide.theta_cmd = 0.0
    guide.d_cmd = 0.6
    t = fsw.C.T_DESPIN_END + 0.025
    while t < fsw.C.T_DESPIN_END + 3.1:
        ctrl.tick(t, fsw.C.DT_TRUTH)
        t += fsw.C.DT_TRUTH
    assert flips, "expected at least one pattern-change event in the first cycle"
    assert len(nav_flushes) == len(flips), "nav must flush on every published flip"
    # settle timing: right after a flip -> not settled; SETTLE_T later -> settled
    t_flip = flips[-1]
    assert not ctrl.settled(t_flip + 0.3)
    assert ctrl.settled(t_flip + fsw.C.SETTLE_T + 1e-9)
    assert ctrl.t_change == t_flip


def test_ctrl_wobble_known_schedule():
    """The wobble integrator resets each T_MOD cycle and integrates the
    (a_pat - a_mean) residual."""
    bus = fsw.EventBus()
    ctrl = CtrlTask(bus, Guidance(0.2115, fsw.dynamics.q70_ref(0.2115)), NavigationStack(0.2115), 0.2115, fsw.dynamics.q70_ref(0.2115))
    ctrl.guide.theta_cmd = 0.0
    ctrl.guide.d_cmd = 0.0
    t = fsw.C.T_DESPIN_END
    for _ in range(200):  # 5 s -> crosses one T_MOD boundary
        ctrl.tick(t, fsw.C.DT_TRUTH)
        t += fsw.C.DT_TRUTH
    # d_cmd = 0 -> mean force 0, pattern parks +/-90: |wob_v| equals |a_pat| integral
    assert abs(ctrl.a_mean[0]) < 1e-12 and abs(ctrl.a_mean[1]) < 1e-12
    assert math.hypot(*ctrl.wob_v) > 0.0
    assert ctrl.cyc_last == int((t - fsw.C.DT_TRUTH) / fsw.C.T_MOD)
