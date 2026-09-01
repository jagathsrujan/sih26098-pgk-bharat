"""Sensor interfaces — the ONLY way the flight software sees the world.

The co-sim harness synthesizes measurements (truth + sensor error model, same
noise stream as the Rev E reference run) and pushes them through these narrow
interfaces. FSW code contains no sensor synthesis and no truth access.

- GnssFixQueue: time-tagged 1 Hz fixes delivered after GNSS_LAT. FSW-side
  policy: the FIX is forward-propagated to arrival, not the filter.
- AccelAnchorWindow: settled-sample accumulation buffers for the drag-vector
  roll anchor (c = measured, m = modeled, u = reference unit-vector sums).
  Windows close on a fixed count (ANCHOR_N) and are flushed at pattern changes.
"""
import math

import numpy as np

from . import config as C


class GnssFixQueue:
    """Holds at most one pending fix (1 Hz arrival vs 100 ms latency)."""

    def __init__(self):
        self._pending = None      # (t_e, pos_m(3,), vel_m(3,))
        self.delivered = 0

    def push(self, t_meas, pos_m, vel_m):
        self._pending = (t_meas, np.asarray(pos_m, dtype=float),
                         np.asarray(vel_m, dtype=float))

    def pop_due(self, t_now):
        """Deliver the pending fix if t_now >= t_meas + GNSS_LAT.
        Returns (t_e, pos_propagated, vel) or None. pos is propagated to
        arrival by the FIX, not the filter (F6)."""
        if self._pending is None:
            return None
        t_e, pos_m, vel_m = self._pending
        if t_now >= t_e + C.GNSS_LAT - 1e-9:
            self._pending = None
            self.delivered += 1
            pos_p = pos_m + vel_m * C.GNSS_LAT
            return t_e, pos_p, vel_m
        return None

    @property
    def pending(self):
        return self._pending is not None


class AccelAnchorWindow:
    """Fixed-size settled-sample accumulation for the drag-vector anchor.

    add() accumulates, in the un-rotated (commanded-pattern) frame:
      cbuf += rot2(psi_ref, f_body) + bias_err + noise_err   (measured)
      mbuf += (-k_m*rvx_m + a_pat_x, -k_m*rvy_m + a_pat_y)   (modeled)
      usum += (cos psi_ref, sin psi_ref)                     (reference)
    The accumulation arithmetic matches the Rev E reference op-for-op.
    """

    __slots__ = ("cbuf", "mbuf", "usum", "n")

    def __init__(self):
        self.flush()

    def add(self, f_body, psi_ref, modeled, bias_err, noise_err):
        c, s = math.cos(psi_ref), math.sin(psi_ref)
        ctmp0 = c * f_body[0] - s * f_body[1]
        ctmp1 = s * f_body[0] + c * f_body[1]
        self.cbuf[0] += ctmp0 + bias_err[0] + noise_err[0]
        self.cbuf[1] += ctmp1 + bias_err[1] + noise_err[1]
        self.mbuf[0] += modeled[0]
        self.mbuf[1] += modeled[1]
        self.usum[0] += c
        self.usum[1] += s
        self.n += 1

    def ready(self):
        return self.n >= C.ANCHOR_N

    def averages(self):
        """(c_bar, m_bar, u_bar, n) or None if empty."""
        if self.n == 0:
            return None
        n = float(self.n)
        return ((self.cbuf[0] / n, self.cbuf[1] / n),
                (self.mbuf[0] / n, self.mbuf[1] / n),
                (self.usum[0] / n, self.usum[1] / n),
                self.n)

    def flush(self):
        self.cbuf = [0.0, 0.0]
        self.mbuf = [0.0, 0.0]
        self.usum = [0.0, 0.0]
        self.n = 0
