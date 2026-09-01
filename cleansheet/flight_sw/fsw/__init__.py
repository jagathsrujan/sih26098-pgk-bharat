"""PGK SIH26098 reference flight software (Python, deterministic).

Module boundaries, task rates and interfaces mirror the STM32G474 on-board
deployment (see FLIGHT_SOFTWARE.md). The co-sim harness (cosim/run_cosim.py)
is the ONLY consumer that touches truth/sim internals; FSW sees the world
through fsw.sensors.

Per-tick task order mirrors sim_gnc_revE exactly (required for paired
numerics): sensors -> GNSS delivery -> ctrl (pattern refresh, events) ->
anchor -> slow fit -> EKF predict -> lock deadline -> guidance.
"""
from . import config as C
from .ctrl import CtrlTask, EventBus
from .dynamics import q70_ref
from .guide import Guidance
from .modes import ModeLadder
from .nav import NavigationStack
from .timebase import Scheduler

__all__ = ["FlightComputer", "config", "DEPLOYMENT_RATES", "COSIM_RATES"]


def _rates(**overrides):
    base = {"servo": 1.0 / C.SERVO_HZ,
            "sensor": 1.0 / C.SENSOR_HZ,
            "predict": 1.0 / C.NAV_PREDICT_HZ,
            "gnss": 1.0 / C.GNSS_HZ,
            "guide": 1.0 / C.GUIDE_HZ}
    base.update(overrides)
    return base


DEPLOYMENT_RATES = _rates()
# Co-sim pairing rates: every FSW task offered once per truth step, EKF
# predict at the truth cadence (sim_gnc_revE's own documented simplification).
COSIM_RATES = _rates(servo=C.DT_TRUTH, sensor=C.DT_TRUTH,
                     predict=C.DT_TRUTH, gnss=C.DT_TRUTH, guide=C.DT_TRUTH)


class FlightComputer:
    """Wires ctrl -> events -> nav, guidance, modes on the fixed-rate
    scheduler. The co-sim harness feeds sensors and steps truth around it."""

    def __init__(self, cd_cal=C.CD_CAL, law="l0", blind=False, wind_fit=True,
                 rates=None, qprof=None, q_ref=None):
        self.cd_cal = cd_cal
        self.law = law
        self.blind = blind
        self.wind_fit = wind_fit
        # q at the 60 N reference epoch (Pa) — pre-flight table; the co-sim
        # passes the sim-computed value (identical computation) for provenance
        self.q_ref = q_ref if q_ref is not None else q70_ref(cd_cal)
        self.bus = EventBus()
        self.nav = NavigationStack(cd_cal)
        self.guide = Guidance(cd_cal, self.q_ref)
        self.ctrl = CtrlTask(self.bus, self.guide, self.nav, cd_cal,
                             self.q_ref, qprof=qprof)
        self.modes = ModeLadder()
        self.bus.subscribe("pattern_change", self.nav.on_pattern_change)

        self.sched = Scheduler()
        r = rates if rates is not None else DEPLOYMENT_RATES
        self.sched.add("gnss", r["gnss"], self.tick_gnss, priority=0)
        self.sched.add("ctrl", r["servo"], self.tick_ctrl, priority=1)
        self.sched.add("anchor", r["sensor"], self.tick_anchor, priority=2)
        self.sched.add("fit", r["sensor"], self.tick_fit, priority=3)
        self.sched.add("predict", r["predict"], self.tick_predict, priority=4)
        self.sched.add("deadline", r["sensor"], self.tick_deadline, priority=5)
        self.sched.add("guide", r["guide"], self.tick_guide, priority=6)

    # ------------------------------------------------------------------ sensor ISR (fed by the harness)
    def sensor_gyro(self, gyro, saturated):
        self.nav.roll_predict(gyro, C.DT_TRUTH, saturated)

    def sensor_accel_settled(self, t, f_body, bias_err, noise_err):
        """One settled strapped-down sample; the FSW decides consumption
        (pattern settled + EKF alive + post-despin). Call ONLY when those
        conditions hold so the sensor error stream stays paired."""
        self.nav.add_settled_sample(f_body, self.ctrl.azimuth(t), self.ctrl.a_pat,
                                    bias_err, noise_err)

    def push_fix(self, t_meas, pos_m, vel_m):
        self.nav.gnss.push(t_meas, pos_m, vel_m)

    # ------------------------------------------------------------------ scheduled tasks
    def tick_gnss(self, t, dt):
        outcome, maha, t_e = self.nav.deliver_fix(
            t, r_floor=self.modes.r_floor(),
            pos_only=(self.modes.mode == "denied"))
        if outcome == "init":
            self.modes.on_first_fix(t_e)
        elif outcome in ("accept", "reject"):
            self.modes.on_fix_result(outcome == "accept")

    def tick_ctrl(self, t, dt):
        self.ctrl.tick(t, dt)

    def tick_anchor(self, t, dt):
        self.nav.anchor_tick(t, self.blind)

    def tick_fit(self, t, dt):
        self.nav.fit_tick(t, self.ctrl.a_pat, self.ctrl.a_mean, self.wind_fit)

    def tick_predict(self, t, dt):
        self.nav.predict_tick(C.DT_TRUTH, self.ctrl.a_pat)

    def tick_deadline(self, t, dt):
        self.modes.deadline_tick(t)

    def tick_guide(self, t, dt):
        if self.nav.ekf is None:
            return
        if self.modes.next_guid is None or t < self.modes.next_guid - 1e-9:
            return
        if self.modes.mode not in ("acq", "guide", "degraded", "denied"):
            return
        sig_p = self.nav.ekf.sigma_pos()
        steer = self.modes.guidance_tick(
            t, sig_p, roll_ref_available=self.nav.roll.psi is not None,
            blind=self.blind)
        if steer:
            st = self.nav.ekf.state_tuple()
            # guidance controls the MEAN trajectory: subtract the known wobble
            st = (st[0] - self.ctrl.wob_p[0], st[1] - self.ctrl.wob_p[1], st[2],
                  st[3] - self.ctrl.wob_v[0], st[4] - self.ctrl.wob_v[1], st[5])
            self.guide.tick(st, self.nav.ekf.x[9],
                            (float(self.nav.ekf.x[10]), float(self.nav.ekf.x[11])),
                            law=self.law)
        else:
            self.guide.neutral()
        self.modes.next_guid += C.NAV_DT

    # ------------------------------------------------------------------ driver
    def tick(self, t, dt=C.DT_TRUTH):
        """Dispatch all FSW tasks due at t (fixed order, fixed rates)."""
        return self.sched.run(t, dt)

    # ------------------------------------------------------------------ telemetry
    def stats(self):
        g = self.guide
        return {"duty_peak": g.duty_peak,
                "duty_mean": g.duty_sum / max(g.duty_n, 1),
                "a_mean": g.acc_avg / max(g.acc_n, 1),
                "mode": self.modes.mode,
                "hard_rej": self.modes.hard_rej,
                "ba_cond": self.nav.ekf.ba_cond() if self.nav.ekf is not None else float("nan"),
                "s_cd": self.nav.fit.s_cd,
                "wy_hat": self.nav.fit.wy_hat,
                "anchors": self.nav.anchors}
