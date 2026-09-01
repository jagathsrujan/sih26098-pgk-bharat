"""Guidance — IPP, laws, command shaping (Rev E, E3).

- IPP: numerical propagation to ground (RK4 at DT_IPP, identical dynamics to
  truth) from the wobble-corrected mean-trajectory state.
- Laws: L0 (2*miss/t_go^2, fielded baseline), ZEM (6*miss/t_go^2), APN (N=3,
  clean) — clamped to q-scaled authority, deadband, t_go freeze.
- Shaping: vector low-pass (LP_A per 1-Hz tick) on the commanded correction;
  theta/d refresh every tick (E3) via the ctrl task reading theta_cmd/d_cmd.

Ported verbatim from the guidance block of sim_gnc_revE + Rev D law functions.
"""
import math

import numpy as np

from . import config as C
from .dynamics import propagate_to_ground, q_dyn


def law_l0(mx, my, t_go):
    return (2.0 * mx / t_go ** 2, 2.0 * my / t_go ** 2)


def law_zem(mx, my, t_go):
    """Min-energy, free final velocity, re-solved each cycle: a = 6*dp/t_go^2."""
    return (6.0 * mx / t_go ** 2, 6.0 * my / t_go ** 2)


def law_apn_clean(pos_h, vel_h, target):
    """Pure APN, N=3, horizontal plane. No blend, no Vc floor (honest trade point)."""
    lx, ly = target[0] - pos_h[0], target[1] - pos_h[1]
    R = math.hypot(lx, ly)
    if R < C.APN_RANGE_MIN:
        return (0.0, 0.0)
    Vc = -(lx * vel_h[0] + ly * vel_h[1]) / R
    lam_dot = (lx * vel_h[1] - ly * vel_h[0]) / (R * R)
    a = 3.0 * Vc * lam_dot
    lam = math.atan2(ly, lx)
    return (-math.sin(lam) * a, math.cos(lam) * a)


LAWS = {"l0": law_l0, "zem": law_zem, "apn": law_apn_clean}


class Guidance:
    """Command state (theta_cmd, d_cmd) + 1 Hz IPP/law/shaping tick."""

    def __init__(self, cd_cal, q_ref):
        self.cd_cal = cd_cal
        self.q_ref = q_ref        # Pa, q at the 60 N reference epoch (pre-flight)
        self.theta_cmd = 0.0      # inertial azimuth of MEAN force
        self.d_cmd = 0.0          # phasor duty (0 = neutral aim until guidance)
        self.a_cmd_s = (0.0, 0.0) # low-passed commanded correction (m/s2)
        self.ipp_miss = float("nan")
        self.t_go = float("nan")
        # run statistics (duty / mean authority)
        self.duty_peak = 0.0
        self.duty_sum = 0.0
        self.duty_n = 0
        self.acc_avg = 0.0
        self.acc_n = 0

    def neutral(self):
        """acq / denied / ballistic: neutral aim (duty 0, azimuth held)."""
        self.d_cmd = 0.0

    def tick(self, st, cd_scale, w_hat, law="l0"):
        """One guidance tick. st = wobble-corrected EKF state (6-tuple),
        cd_scale = ekf.x[9], w_hat = (ekf.x[10], ekf.x[11]).
        Returns the authority accel a_auth used for duty scaling."""
        cd_hat = float(np.clip(cd_scale, 0.6, 1.4)) * self.cd_cal
        a_auth = C.FIN_FORCE_NOM * q_dyn(st) / self.q_ref / C.M_NOM
        xi_i, yi_i, t_imp, _ = propagate_to_ground(st, cd_hat, w_hat, C.DT_IPP)
        t_go = t_imp
        mx, my = C.RANGE_TARGET - xi_i, 0.0 - yi_i
        self.ipp_miss = math.hypot(mx, my)
        self.t_go = t_go
        if t_go < C.GUIDE_FREEZE_TGO or self.ipp_miss < C.DEADBAND:
            a_raw = (0.0, 0.0)
        else:
            if law == "apn":
                a_raw = law_apn_clean((st[0], st[1]), (st[3], st[4]),
                                      (C.RANGE_TARGET, 0.0))
            else:
                a_raw = LAWS[law](mx, my, t_go)
            mag = math.hypot(*a_raw)
            if mag > a_auth:
                a_raw = (a_auth * a_raw[0] / mag, a_auth * a_raw[1] / mag)
        # vector low-pass on the command: the closed loop re-measures the miss
        # every cycle, so do NOT chase per-cycle estimator ringing
        self.a_cmd_s = (self.a_cmd_s[0] + C.LP_A * (a_raw[0] - self.a_cmd_s[0]),
                        self.a_cmd_s[1] + C.LP_A * (a_raw[1] - self.a_cmd_s[1]))
        mag_s = math.hypot(*self.a_cmd_s)
        self.d_cmd = min(1.0, mag_s / a_auth) if a_auth > 1e-9 else 0.0
        if mag_s > 1e-6:
            self.theta_cmd = math.atan2(self.a_cmd_s[1], self.a_cmd_s[0])
        duty = self.d_cmd
        self.duty_peak = max(self.duty_peak, duty)
        self.duty_sum += duty
        self.duty_n += 1
        self.acc_avg += a_auth * duty
        self.acc_n += 1
        return a_auth
