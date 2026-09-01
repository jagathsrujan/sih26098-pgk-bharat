"""Navigation — verbatim-in-numerics port of the Rev E estimators.

- NavEKF: 12-state [pos3, vel3, ba3, cd_scale, wx, wy], model-based predict
  (drag(cd,wind) + g + commanded feedforward - ba), Joseph-form GNSS update
  with adaptive-R inflation and hard-reject fallback (E2).
- RollEKF: 3-state [psi, gyro_bias_z, mount_bias] with innovation-gated
  drag-vector-anchor updates (E1).
- DragAnchor: settled-window azimuth solve, azimuth-only R (unit-correct).
- SlowFit: two-time-scale (cd_scale, wy) fit over a 15 s model-propagation
  baseline, gated on roll health (E4).

Everything here is ported line-for-line from scripts/sim_gnc_check.py
(RollEstimatorE, NavEKF_D base + NavEKF_E override, and the inline anchor /
slow-fit blocks of sim_gnc_revE). Do not "improve" the numerics — the Rev E
evidence (out_sim/RESULTS_GNC.md) belongs to exactly these equations.
"""
import math

import numpy as np
import numpy.linalg as la

from . import config as C
from .dynamics import accel, rho, wrap_pi
from .sensors import AccelAnchorWindow, GnssFixQueue


class RollEKF:
    """3-state roll channel: psi (absolute nose roll), gyro_bias_z, mount_bias.
    Measurement: z = psi + mount_bias + noise (drag-vector anchor).
    Innovation-gated: |y| > 3*sqrt(S) -> inflate P, reject."""

    def __init__(self):
        self.psi = None
        self.b = 0.0
        self.m = 0.0
        self.P = np.diag([math.radians(5.0) ** 2, math.radians(0.5) ** 2,
                          math.radians(1.0) ** 2])
        self.q_ang = math.radians(0.2) ** 2
        self.q_bias = math.radians(0.05) ** 2
        self.q_mount = math.radians(0.02) ** 2
        self.nis = float("nan")

    def predict(self, gyro, dt, saturated):
        if saturated or self.psi is None:
            return
        F = np.array([[1.0, -dt, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        self.psi = wrap_pi(self.psi + (gyro - self.b) * dt)
        Q = np.diag([self.q_ang * dt, self.q_bias * dt, self.q_mount * dt])
        self.P = F @ self.P @ F.T + Q
        self.P = 0.5 * (self.P + self.P.T)

    def update(self, psi_meas, R_psi):
        if self.psi is None:
            if R_psi > math.radians(10.0) ** 2:
                return False, float("nan")   # never initialize from a garbage window
            self.psi = wrap_pi(psi_meas)
            self.P = np.diag([R_psi, math.radians(0.5) ** 2, math.radians(1.0) ** 2])
            return True, 0.0
        y = wrap_pi(psi_meas - self.psi - self.m)
        S = self.P[0, 0] + 2.0 * self.P[0, 2] + self.P[2, 2] + R_psi
        self.nis = abs(y) / math.sqrt(max(S, 1e-12))
        if abs(y) > 3.0 * math.sqrt(S):
            self.P[0, 0] *= 1.5
            self.P[2, 2] *= 1.2
            return False, self.nis
        H = np.array([1.0, 0.0, 1.0])
        Ph = self.P @ H
        K = Ph / S
        self.psi = wrap_pi(self.psi + K[0] * y)
        self.b += K[1] * y
        self.m += K[2] * y
        KH = np.outer(K, H)
        I = np.eye(3)
        self.P = (I - KH) @ self.P @ (I - KH).T + np.outer(K, K) * R_psi
        self.P = 0.5 * (self.P + self.P.T)
        return True, self.nis

    def err_vs(self, psi_true):
        return float("nan") if self.psi is None else math.degrees(abs(wrap_pi(self.psi - psi_true)))


class NavEKF:
    """12-state [pos3 vel3 ba3 cd wind2]; MODEL-based predict:
    a = -k*(v-w) + ff - ba + g,  k = 0.5*rho(z)*cd*A*|v-w|/m.
    GNSS pos+vel update, adaptive-R (E2), Joseph form.
    cd/wind are FROZEN at priors inside the KF (Q = 0): weakly observable per
    fix, and their estimate noise maps 1:1 into IPP error. The slow SlowFit
    owns the slow scale (two-time-scale design, D9 + E4)."""

    def __init__(self, cd_cal):
        self.cd_cal = cd_cal
        self.x = np.zeros(12)
        self.P = np.diag([10.0 ** 2, 10.0 ** 2, (16.0) ** 2, 5.0 ** 2, 5.0 ** 2, 5.0 ** 2,
                          C.ACC_BIAS_INIT_SIG ** 2, C.ACC_BIAS_INIT_SIG ** 2,
                          C.ACC_BIAS_INIT_SIG ** 2,
                          0.004 ** 2, 0.3 ** 2, 0.3 ** 2])
        self.Qc = np.diag([0, 0, 0, 0.05 ** 2, 0.05 ** 2, 0.05 ** 2,
                           1e-3 ** 2, 1e-3 ** 2, 1e-3 ** 2, 0.0, 0.0, 0.0])
        self.R_pos = C.GPS_POS_SIG ** 2
        self.R_vert = (C.GPS_POS_SIG * 1.6) ** 2
        self.R_vel = C.GPS_VEL_SIG ** 2
        self.chi2 = C.CHI2_GATE     # carried from Rev D; the E2 policy below gates on
                                    # GATE_HARD_X*CHI2_GATE (blind runs set this to 1e9
                                    # in the reference sim — no effect there either)
        self.t_last = None
        self.initialized = False
        self.nis = float("nan")
        self.r_scale = float("nan")

    def init_from_fix(self, pos, vel, t_now=0.0):
        self.x[0:3] = pos
        self.x[3:6] = vel
        self.x[9] = 1.0
        self.P[0:6, 0:6] = np.diag([self.R_pos, self.R_pos, self.R_vert,
                                    self.R_vel, self.R_vel, self.R_vel]) * 2.0
        self.t_last = t_now
        self.initialized = True

    def drag_parts(self, ff):
        x = self.x
        cd_abs = float(np.clip(x[9], 0.6, 1.4)) * self.cd_cal
        z = max(x[2], 0.0)
        rvx, rvy = x[3] - x[10], x[4] - x[11]
        rvz = x[5]
        vr = math.sqrt(rvx * rvx + rvy * rvy + rvz * rvz)
        k = 0.5 * rho(z) * cd_abs * C.AREA * vr / C.M_NOM if vr > 1e-6 else 0.0
        ad = (-k * rvx, -k * rvy, -k * rvz - C.G)
        return x, cd_abs, k, rvx, rvy, ad, ff

    def predict(self, dt, ff):
        """ff = commanded mean force accel (ax, ay) [m/s2]."""
        x, cd_abs, k, rvx, rvy, ad, ff = self.drag_parts(ff)
        nx = x.copy()
        nx[0:3] = x[0:3] + x[3:6] * dt
        nx[3] = x[3] + (ad[0] + ff[0] - x[6]) * dt
        nx[4] = x[4] + (ad[1] + ff[1] - x[7]) * dt
        nx[5] = x[5] + (ad[2] - x[8]) * dt
        self.x = nx
        self.t_last += dt
        F = np.eye(12)
        F[0, 3] = dt
        F[1, 4] = dt
        F[2, 5] = dt
        F[3, 6] = -dt
        F[4, 7] = -dt
        F[5, 8] = -dt
        if (rv2 := rvx * rvx + rvy * rvy) > 1e-6:
            v2full = rv2 + self.x[5] * self.x[5]
            if v2full > 1e-6:
                # d(a_h)/d(v_h) = -k*(I + rv_h rv_h^T / |rv_full|^2); d/dw = -d/dv
                Pvv = np.array([[rvx * rvx / v2full, rvx * rvy / v2full],
                                [rvx * rvy / v2full, rvy * rvy / v2full]])
                Jvv = -k * (np.eye(2) + Pvv)
                F[3:5, 3:5] += Jvv * dt
                F[3:5, 10:12] += -Jvv * dt          # d/dw = +k(I+..) = -Jvv
                F[3:5, 9] += (-(k / cd_abs) * np.array([rvx, rvy])) * dt
                F[3:5, 2] += (k / C.HSCALE) * np.array([rvx, rvy]) * dt
        Qd = self.Qc * dt
        self.P = F @ self.P @ F.T + Qd
        self.P = 0.5 * (self.P + self.P.T)

    def update_gnss(self, pos, vel, r_floor=1.0, pos_only=False):
        """Returns (accepted, maha). pos/vel already latency-propagated."""
        H6 = np.zeros((6, 12))
        H6[0, 0] = H6[1, 1] = H6[2, 2] = 1.0
        H6[3, 3] = H6[4, 4] = H6[5, 5] = 1.0
        z6 = np.hstack([pos, vel])
        h6 = np.hstack([self.x[0:3], self.x[3:6]])
        R6 = np.diag([self.R_pos, self.R_pos, self.R_vert,
                      self.R_vel, self.R_vel, self.R_vel])
        if pos_only:
            H, z, h, R = H6[0:3, :], z6[0:3], h6[0:3], R6[0:3, 0:3]
        else:
            H, z, h, R = H6, z6, h6, R6
        R = R * r_floor
        y = z - h
        S = H @ self.P @ H.T + R
        maha = float(y @ la.solve(S, y))
        self.nis = maha
        if maha > C.GATE_HARD_X * C.CHI2_GATE:
            self.P[0:3, 0:3] *= 1.3
            self.P[3:6, 3:6] *= 1.6
            self.r_scale = float("nan")
            return False, maha
        self.r_scale = min(max(maha / C.CHI2_GATE, 1.0), C.R_INFLATE_MAX)
        R = R * self.r_scale
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ la.inv(S)
        self.x = self.x + K @ y
        I = np.eye(12)
        self.P = (I - K @ H) @ self.P @ (I - K @ H).T + K @ R @ K.T
        self.P = 0.5 * (self.P + self.P.T)
        self.x[9] = float(np.clip(self.x[9], 0.6, 1.4))
        self.x[10] = float(np.clip(self.x[10], -15.0, 15.0))
        self.x[11] = float(np.clip(self.x[11], -15.0, 15.0))
        return True, maha

    def sigma_pos(self):
        return math.sqrt(np.trace(self.P[0:3, 0:3]) / 3.0)

    def state_tuple(self):
        return tuple(float(v) for v in self.x[0:6])

    def ba_cond(self):
        """E5: max off-diagonal correlation inside the live (ba) block."""
        P = self.P[6:9, 6:9]
        d = np.sqrt(np.diag(P))
        if np.all(d > 1e-12):
            Cmat = P / np.outer(d, d)
            return float(np.max(np.abs(Cmat - np.eye(3))))
        return float("nan")


class DragAnchor:
    """Drag-vector azimuth solve on a settled window (E1).

    psi_meas = az(u_bar) - delta, with delta = az(c_bar) - az(m_bar); the
    residual perpendicular component sets an AZIMUTH-only R — drag-magnitude
    error does not rotate the vector and must not inflate the azimuth
    variance (the Rev D rad/deg unit bug is the cautionary tale).
    """

    @staticmethod
    def solve(c_bar, m_bar, u_bar):
        if not (math.hypot(*m_bar) > 0.3 and math.hypot(*c_bar) > 0.1):
            return None
        delta = (math.atan2(c_bar[1], c_bar[0])
                 - math.atan2(m_bar[1], m_bar[0]))
        psi_meas = math.atan2(u_bar[1], u_bar[0]) - delta
        res = (c_bar[0] - (math.cos(delta) * m_bar[0] - math.sin(delta) * m_bar[1]),
               c_bar[1] - (math.sin(delta) * m_bar[0] + math.cos(delta) * m_bar[1]))
        cmag = math.hypot(*c_bar)
        res_perp = abs(-c_bar[1] * res[0] + c_bar[0] * res[1]) / max(cmag, 1e-9)
        sig_psi = math.radians(0.8) + res_perp / max(cmag, 0.3)
        return psi_meas, sig_psi * sig_psi


class SlowFit:
    """E4 slow (cd_scale, wy) fit over a FIT_BASELINE model-propagation twin.

    The twin integrates the LIVE a_mean command history (Euler, truth-step);
    cd_scale closes the along-track speed-drop residual, wy the cross-track
    residual. wy feeds the IPP, the EKF predict model AND the anchor
    drag-azimuth reference. The wy update is gated on roll-estimate health:
    a roll error eps rotates the feedforward and leaks |a_mean|*sin(eps) into
    the cross residual — a phantom-wind loop (E4 guard).
    """

    def __init__(self, cd_cal):
        self.cd_cal = cd_cal
        self.s_cd = 1.0
        self.wy_hat = 0.0
        self.fit_t0 = None
        self.fit_dvd_s = 0.0
        self.fit_kv = 0.0
        self.fit_wob_v = [0.0, 0.0]
        self.fit_sm = None

    def tick(self, t, ekf, roll_est, a_pat, a_mean):
        st_f = ekf.state_tuple()
        vh_f = math.hypot(st_f[3], st_f[4])
        if vh_f <= C.FIT_VH_MIN:
            return
        _, _, k_f, rvx_f, rvy_f, _, _ = ekf.drag_parts((0.0, 0.0))
        k_u = k_f / max(self.s_cd, 0.1)
        vhat_f = (st_f[3] / vh_f, st_f[4] / vh_f)
        if self.fit_t0 is None:
            self.fit_t0 = t
            self.fit_dvd_s = 0.0
            self.fit_kv = 0.0
            self.fit_wob_v = [0.0, 0.0]   # fit-window wobble (no cycle resets)
            # incremental model twin: integrates the LIVE a_mean history
            self.fit_sm = [st_f[0], st_f[1], st_f[2],
                           st_f[3], st_f[4], st_f[5]]
        axm, aym, azm = accel(self.fit_sm, self.cd_cal * self.s_cd, (0.0, 0.0))
        self.fit_sm[0] += self.fit_sm[3] * C.DT_TRUTH
        self.fit_sm[1] += self.fit_sm[4] * C.DT_TRUTH
        self.fit_sm[2] += self.fit_sm[5] * C.DT_TRUTH
        self.fit_sm[3] += (axm + a_mean[0]) * C.DT_TRUTH
        self.fit_sm[4] += (aym + a_mean[1]) * C.DT_TRUTH
        self.fit_sm[5] += azm * C.DT_TRUTH
        self.fit_dvd_s += (-k_u * (rvx_f * vhat_f[0] + rvy_f * vhat_f[1])) * C.DT_TRUTH
        self.fit_kv += k_u * C.DT_TRUTH
        self.fit_wob_v[0] += (a_pat[0] - a_mean[0]) * C.DT_TRUTH
        self.fit_wob_v[1] += (a_pat[1] - a_mean[1]) * C.DT_TRUTH
        if t - self.fit_t0 >= C.FIT_BASELINE:
            vh_m = math.hypot(self.fit_sm[3], self.fit_sm[4])
            resid_along = vh_f - vh_m
            if abs(self.fit_dvd_s) > 0.5:
                s_new = self.s_cd + float(np.clip(resid_along / self.fit_dvd_s,
                                                  -C.FIT_CD_STEP, C.FIT_CD_STEP))
                self.s_cd = float(np.clip(self.s_cd + 0.5 * (s_new - self.s_cd),
                                          C.FIT_CD_MIN, C.FIT_CD_MAX))
                ekf.x[9] = self.s_cd
            if self.fit_kv > C.FIT_KV_MIN:
                roll_ok = (roll_est.psi is not None
                           and roll_est.P[0, 0] < C.FIT_ROLL_P_MAX
                           and (not math.isfinite(roll_est.nis)
                                or roll_est.nis < C.FIT_NIS_MAX))
                if roll_ok:
                    resid_cross = ((st_f[4] - self.fit_sm[4]) - self.fit_wob_v[1])
                    wy_new = float(np.clip(resid_cross / self.fit_kv,
                                           -C.FIT_WY_CLAMP, C.FIT_WY_CLAMP))
                    self.wy_hat = 0.7 * self.wy_hat + 0.3 * wy_new
                    ekf.x[11] = self.wy_hat
            self.fit_t0 = None


class NavigationStack:
    """Owns the estimator chain and the sensor-side buffers.

    Interface contract with the ctrl task (the plan's hard rule): ctrl
    PUBLISHES pattern-change events; this stack SUBSCRIBES by flushing any
    partial anchor window (a window straddling a flip is slew-poisoned).
    """

    def __init__(self, cd_cal):
        self.cd_cal = cd_cal
        self.roll = RollEKF()
        self.ekf = None                      # created lazily at the first accepted fix
        self.window = AccelAnchorWindow()
        self.fit = SlowFit(cd_cal)
        self.gnss = GnssFixQueue()
        self.anchors = 0                     # diagnostics

    # ---------------------------------------------------------------- ctrl event
    def on_pattern_change(self, event):
        self.window.flush()

    # ---------------------------------------------------------------- sensor inputs
    def roll_predict(self, gyro, dt, saturated):
        self.roll.predict(gyro, dt, saturated)

    def add_settled_sample(self, f_body, psi_ref, a_pat, bias_err, noise_err):
        """One settled accel sample (body-frame horizontal specific force).
        bias_err/noise_err come from the sensor interface (co-sim error model);
        the modeled force uses the live EKF drag + the commanded pattern."""
        if self.ekf is None:
            return
        _, _, k_m, rvx_m, rvy_m, _, _ = self.ekf.drag_parts((0.0, 0.0))
        modeled = (-k_m * rvx_m + a_pat[0], -k_m * rvy_m + a_pat[1])
        self.window.add(f_body, psi_ref, modeled, bias_err, noise_err)

    # ---------------------------------------------------------------- tasks
    def anchor_tick(self, t, blind):
        """Close a settled window on the fixed count; solve; update the roll
        EKF. Continues through GNSS outages and rejected fixes (E1)."""
        if self.ekf is None or blind or t < C.T_DESPIN_END or not self.window.ready():
            return
        c_bar, m_bar, u_bar, n = self.window.averages()
        solved = DragAnchor.solve(c_bar, m_bar, u_bar)
        if solved is not None:
            psi_meas, R_psi = solved
            self.roll.update(psi_meas, R_psi)
            self.anchors += 1
        self.window.flush()

    def fit_tick(self, t, a_pat, a_mean, wind_fit=True):
        if self.ekf is None or not wind_fit or t < C.T_DESPIN_END:
            return
        self.fit.tick(t, self.ekf, self.roll, a_pat, a_mean)

    def predict_tick(self, dt, a_pat):
        if self.ekf is not None:
            self.ekf.predict(dt, a_pat)

    def deliver_fix(self, t_now, r_floor=1.0, pos_only=False):
        """Deliver a due GNSS fix through the EKF. Returns
        (outcome, maha, t_e) with outcome in {"none","init","accept","reject"};
        t_e is the measurement epoch (mode cadence anchors to it).
        r_floor/pos_only come from the mode ladder (E2)."""
        fix = self.gnss.pop_due(t_now)
        if fix is None:
            return "none", float("nan"), None
        t_e, pos_p, vel_m = fix
        if self.ekf is None:
            self.ekf = NavEKF(self.cd_cal)
            self.ekf.init_from_fix(pos_p, vel_m, t_now)
            return "init", 0.0, t_e
        ok, maha = self.ekf.update_gnss(pos_p, vel_m, r_floor=r_floor,
                                        pos_only=pos_only)
        return ("accept" if ok else "reject"), maha, t_e
