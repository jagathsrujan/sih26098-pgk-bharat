"""Control — phasor-duty pattern generator, settle tracking, pattern-change
events, commanded-force model with known wobble, and the servo rate command
(controller-side mirror of the motor caps).

The ctrl task PUBLISHES "pattern_change" events on the bus; the nav task
SUBSCRIBES (flushes anchor windows). This is the explicit control->nav
interface (the plan's hard rule): control and navigation are coupled through
the commanded pattern, and the coupling is a published event, not hidden state.

duty_pattern and the servo mirror are verbatim ports from sim_gnc_revE.
"""
import math

from . import config as C
from .dynamics import q_at, q_profile, q_dyn, wrap_pi


class EventBus:
    """Minimal deterministic pub/sub (fixed subscriber lists, no allocation
    at publish time)."""

    def __init__(self):
        self._subs = {}

    def subscribe(self, topic, fn):
        self._subs.setdefault(topic, []).append(fn)

    def publish(self, topic, payload):
        for fn in self._subs.get(topic, ()):
            fn(payload)


def duty_pattern(t, base, d):
    """Phasor-duty aim schedule (wall-clock anchored).
    d < 0.02: park alternating base+90 / base-90 per FULL cycle (long quiescent
    windows for roll anchoring; mean force ~0 over 2 cycles)."""
    if d >= 0.98:
        return base
    if d < 0.02:
        return base + math.pi / 2 if (int(t // C.T_MOD) % 2) == 0 else base - math.pi / 2
    tau = t % C.T_MOD
    if tau < d * C.T_MOD:
        return base
    half = (1.0 - d) * C.T_MOD * 0.5
    return base + math.pi / 2 if (tau - d * C.T_MOD) < half else base - math.pi / 2


class CtrlTask:
    """400 Hz (deployment) / truth-rate (co-sim) control task."""

    def __init__(self, bus, guide, nav, cd_cal, q_ref, qprof=None):
        self.bus = bus
        self.guide = guide
        self.nav = nav
        self.cd_cal = cd_cal
        self.q_ref = q_ref          # Pa, q at the 60 N reference epoch (pre-flight)
        self.qprof = qprof if qprof is not None else q_profile(cd_cal)
        self.theta_pat = 0.0      # inertial azimuth of the MEAN force (published pattern)
        self.d_pat = 0.0          # published duty
        self.az_prev = None
        self.t_change = C.T_DESPIN_END
        self.cyc_last = -1
        self.a_pat = (0.0, 0.0)   # instantaneous pattern force (m/s2)
        self.a_mean = (0.0, 0.0)  # commanded mean force (m/s2)
        self.a_auth_hat = 0.0
        self.wob_v = [0.0, 0.0]   # modeled within-cycle wobble velocity (known schedule)
        self.wob_p = [0.0, 0.0]

    def azimuth(self, t):
        return duty_pattern(t, self.theta_pat, self.d_pat)

    def settled(self, t):
        """True once the commanded pattern has been constant >= SETTLE_T."""
        return (t - self.t_change) >= C.SETTLE_T

    def tick(self, t, dt):
        if t < C.T_DESPIN_END:
            return
        cyc = int(t / C.T_MOD)
        if cyc != self.cyc_last:
            self.cyc_last = cyc
            self.wob_v = [0.0, 0.0]
            self.wob_p = [0.0, 0.0]     # wobble is cycle-periodic
        self.theta_pat, self.d_pat = self.guide.theta_cmd, self.guide.d_cmd  # E3: refresh every tick
        if self.nav.ekf is not None:
            self.a_auth_hat = C.FIN_FORCE_NOM * q_dyn(self.nav.ekf.state_tuple()) / self.q_ref / C.M_NOM
        else:
            self.a_auth_hat = C.FIN_FORCE_NOM * q_at(self.qprof, t) / self.q_ref / C.M_NOM
        az = self.azimuth(t)
        if self.az_prev is not None and abs(wrap_pi(az - self.az_prev)) > C.PATTERN_FLIP_EPS:
            self.t_change = t
            # E1: a window must live inside ONE pattern segment — mixing
            # samples across a flip makes u_bar bimodal and the solve
            # meaningless. Publish; nav flushes its partial window.
            self.bus.publish("pattern_change", {"t": t, "az": az})
        self.az_prev = az
        self.a_pat = (self.a_auth_hat * math.cos(az), self.a_auth_hat * math.sin(az))
        self.a_mean = (self.guide.d_cmd * self.a_auth_hat * math.cos(self.guide.theta_cmd),
                       self.guide.d_cmd * self.a_auth_hat * math.sin(self.guide.theta_cmd))
        # the within-cycle wobble is COMMANDED (known schedule): integrate it
        self.wob_v[0] += (self.a_pat[0] - self.a_mean[0]) * dt
        self.wob_v[1] += (self.a_pat[1] - self.a_mean[1]) * dt
        self.wob_p[0] += self.wob_v[0] * dt
        self.wob_p[1] += self.wob_v[1] * dt

    @staticmethod
    def servo_rate_cmd(err, dt):
        """Time-optimal, discretization-safe rate command (controller-side
        mirror): cap om so it cannot overshoot the target within one step
        (kills the near-target limit cycle that would otherwise erase all
        quiescent windows). The motor model integrates this with the alpha
        cap; truth-side in the co-sim."""
        om_mag = min(C.SERVO_RATE_MAX,
                     math.sqrt(2.0 * C.SERVO_ALPHA_MAX * abs(err)),
                     abs(err) / (2.0 * dt))
        if abs(err) < C.SERVO_DEADBAND:
            return 0.0
        return math.copysign(om_mag, err)
