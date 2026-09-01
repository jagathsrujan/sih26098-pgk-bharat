"""Mode state machine — the E2 fail-safe ladder.

    pre --fix--> acq (R x2, commands neutral until absolute roll exists)
          --engage--> guide <-----------------+
          sigma>12.5 m --> degraded (R x4, guidance CONTINUES open-loop) --sigma<=12.5--> guide
          sigma>25 m ----> denied (neutral coast, position-only R x16 re-acq) --sigma<8--> guide
          never locked / t>50 s --> ballistic (neutral park, timed fuze)

Transition order inside a guidance tick matches sim_gnc_revE exactly
(sigma thresholds evaluated against the CURRENT sigma after the acq->guide
engagement check; denied->guide resume happens before the command branch, so
a resumed tick steers immediately).
"""
from . import config as C

MODES = ("pre", "acq", "guide", "degraded", "denied", "ballistic")


class ModeLadder:
    def __init__(self):
        self.mode = "pre"
        self.t_first_fix = None
        self.next_guid = None       # guidance cadence, anchored to first-fix epoch
        self.hard_rej = 0

    # ---------------------------------------------------------------- fix events
    def on_first_fix(self, t_e):
        """Hard init: mode -> acq, guidance cadence anchored to the fix epoch.
        NOTE: next_guid uses T_GUID_ENGAGE (2.0 s) — the Rev E reference quirk
        (the acq->guide threshold itself is T_GUID_ENGAGE_E = 1.0 s, so the
        first guidance tick at +2.0 s engages immediately). Ported as-is."""
        self.mode = "acq"
        self.t_first_fix = t_e
        self.next_guid = t_e + C.T_GUID_ENGAGE

    def on_fix_result(self, accepted):
        if accepted:
            self.hard_rej = 0
            return
        self.hard_rej += 1
        if self.hard_rej >= 3 and self.mode == "guide":
            self.mode = "degraded"

    # ---------------------------------------------------------------- ticks
    def deadline_tick(self, t):
        """Lock deadline fail-safe, evaluated every task tick."""
        if self.mode == "pre" and t >= C.T_LOCK_DEADLINE_E:
            self.mode = "ballistic"

    def guidance_tick(self, t, sig_p, roll_ref_available, blind):
        """Ladder evaluation at a guidance tick. Returns True when the
        command branch runs this tick (guide / degraded)."""
        if (self.mode == "acq" and t >= self.t_first_fix + C.T_GUID_ENGAGE_E
                and (roll_ref_available or blind)):
            self.mode = "guide"
        if self.mode in ("guide", "degraded"):
            if sig_p > C.SIG_POS_DENIED:
                self.mode = "denied"
            elif sig_p > C.SIG_POS_DEGRADED:
                self.mode = "degraded"
            else:
                self.mode = "guide"
        if self.mode == "denied" and sig_p < C.SIG_POS_RESUME:
            self.mode = "guide"
        return self.mode in ("guide", "degraded")

    # ---------------------------------------------------------------- reporting
    def r_floor(self):
        return {"acq": C.R_FLOOR_ACQ, "degraded": C.R_FLOOR_DEGRADED,
                "denied": C.R_FLOOR_DENIED}.get(self.mode, 1.0)
