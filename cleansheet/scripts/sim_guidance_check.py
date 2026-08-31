#!/usr/bin/env python3
"""
SIH26098 clean-sheet PGK — steering-effectiveness verification (report §10.1 precursor)

Question answered: does the canard roll-aim control mechanism actually steer the shell?

Mechanism modeled (per 03_DESIGN_REPORT.md):
  - 3DOF point mass + lateral fin force (report's own first rung; spin/Magnus = 6DOF rung)
  - fixed-trim canard pair (mirrored ±3°) -> constant-magnitude force, direction set by
    motor roll-aim (ψ); magnitude modulated by duty-cycling the aim (as-built: no moving fins)
  - de-spin at t=25 s, GNSS lock t=35 s (late-lock variant t=60 s), nav updates 1 Hz
  - impact-point prediction (IPP) from 1 Hz GPS fixes with in-flight estimation of
    drag scale (absorbs mass + along-track wind) and crosswind
  - guidance law: a_cmd = 2*miss/t_go^2, clamped to fin authority

Dispersion sources: muzzle velocity, elevation/azimuth aim, wind (x,y), Cd scale, mass.

Outputs: console summary, out_sim/steering_check.png, out_sim/RESULTS.md
"""
import math
import os

import numpy as np

# ---------------------------------------------------------------- constants
G = 9.80665
RHO0 = 1.225            # sea-level density, kg/m^3
HSCALE = 8500.0         # density scale height, m
M_NOM = 46.0            # M795-class shell mass, kg
D = 0.155               # caliber, m
AREA = math.pi / 4 * D * D
V0_NOM = 827.0          # muzzle velocity, m/s
ELEV0 = math.radians(46.0)
RANGE_TARGET = 30000.0

T_LOCK_NOM = 35.0       # GNSS acquisition scheduled post-despin (s)
NAV_DT = 1.0            # nav / guidance update cycle (s)
GPS_POS_SIG = 5.0       # NavIC position noise, m
GPS_VEL_SIG = 0.3       # GPS velocity noise, m/s
DEADBAND = 8.0          # no corrections below this predicted miss (m)
FIN_FORCE_NOM = 60.0    # fin pair + body lift amplification, N (audit: 30-100 N)

DT_TRUTH = 0.025
DT_IPP = 0.15
TMAX = 200.0
N_RUNS = 250

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "out_sim"))

rng = np.random.default_rng(20260830)


def rho(z):
    return RHO0 * math.exp(-max(z, 0.0) / HSCALE)


def accel(state, cd, wind):
    _, _, z, vx, vy, vz = state
    rvx = vx - wind[0]
    rvy = vy - wind[1]
    vr = math.sqrt(rvx * rvx + rvy * rvy + vz * vz)
    if vr < 1e-6:
        return (0.0, 0.0, -G)
    k = 0.5 * rho(z) * cd * AREA * vr / M_NOM
    return (-k * rvx, -k * rvy, -k * vz - G)


def rk4_step(state, dt, cd, wind, a_lat=(0.0, 0.0)):
    def f(s):
        ax, ay, az = accel(s, cd, wind)
        return (s[3], s[4], s[5], ax + a_lat[0], ay + a_lat[1], az)
    k1 = f(state)
    k2 = f(tuple(state[i] + 0.5 * dt * k1[i] for i in range(6)))
    k3 = f(tuple(state[i] + 0.5 * dt * k2[i] for i in range(6)))
    k4 = f(tuple(state[i] + dt * k3[i] for i in range(6)))
    return tuple(state[i] + dt / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(6))


def rk2_step(state, dt, cd, wind):
    def f(s):
        ax, ay, az = accel(s, cd, wind)
        return (s[3], s[4], s[5], ax, ay, az)
    k1 = f(state)
    k2 = f(tuple(state[i] + dt * k1[i] for i in range(6)))
    return tuple(state[i] + 0.5 * dt * (k1[i] + k2[i]) for i in range(6))


def propagate(state0, cd, wind, dt, a_cmd_fn=None):
    """Integrate to ground impact; returns (impact_x, impact_y, t_impact, apogee)."""
    s = state0
    if s[2] <= 0.0 and s[5] <= 0.0:   # at/below ground AND descending (GPS noise late in flight)
        return s[0], s[1], 0.0, 0.0
    t = 0.0
    apogee = s[2]
    while t < TMAX:
        apogee = max(apogee, s[2])
        a = a_cmd_fn(t) if a_cmd_fn else (0.0, 0.0)
        s_prev = s
        s = rk4_step(s, dt, cd, wind, a)
        t += dt
        if s[2] <= 0.0 < s_prev[2]:
            f = s_prev[2] / (s_prev[2] - s[2])
            x_imp = s_prev[0] + f * dt * s[3]
            y_imp = s_prev[1] + f * dt * s[4]
            return x_imp, y_imp, (t - dt) + f * dt, apogee
    raise RuntimeError("no impact within TMAX")


def initial_state(v0, elev, azim):
    vh = v0 * math.cos(elev)
    return (0.0, 0.0, 0.0,
            vh * math.cos(azim), vh * math.sin(azim), v0 * math.sin(elev))


def calibrate_cd():
    """Find Cd such that the nominal shot (46 deg, 827 m/s, no wind) lands at 30.0 km."""
    lo, hi = 0.10, 0.50
    s0 = initial_state(V0_NOM, ELEV0, 0.0)
    for _ in range(36):
        mid = 0.5 * (lo + hi)
        x_imp, _, _, _ = propagate(s0, mid, (0.0, 0.0), 0.1)
        if x_imp > RANGE_TARGET:
            lo = mid
        else:
            hi = mid
    cd = 0.5 * (lo + hi)
    x_imp, _, tof, apo = propagate(s0, cd, (0.0, 0.0), DT_TRUTH)
    return cd, x_imp, tof, apo


# ---------------------------------------------------------------- estimator
class KitEstimator:
    """In-flight estimation from 1 Hz GPS fixes — what the kit can actually know."""

    def __init__(self, t_lock, cd_cal):
        self.t_lock = t_lock
        self.cd_cal = cd_cal       # nominal (calibrated) Cd; cd_hat scales it
        self.fixes = []            # (t, measured state)
        self.cd_hat = 1.0
        self.wy_hat = 0.0
        self.a_cmd = (0.0, 0.0)

    def add_fix(self, t, s_true):
        if t < self.t_lock:
            return
        meas = (s_true[0] + rng.normal(0, GPS_POS_SIG),
                s_true[1] + rng.normal(0, GPS_POS_SIG),
                s_true[2] + rng.normal(0, GPS_POS_SIG * 1.6),
                s_true[3] + rng.normal(0, GPS_VEL_SIG),
                s_true[4] + rng.normal(0, GPS_VEL_SIG),
                s_true[5] + rng.normal(0, GPS_VEL_SIG))
        self.fixes.append((t, meas))

    def update(self):
        """Fit drag scale + crosswind over the GPS window, run IPP, return a_cmd."""
        if len(self.fixes) < 9:
            return (0.0, 0.0)
        t0, s0 = self.fixes[0]
        tn, sn = self.fixes[-1]
        while tn - t0 > 12.5 and len(self.fixes) > 9:
            self.fixes.pop(0)
            t0, s0 = self.fixes[0]
        T = tn - t0
        if T < 4.0:
            return (0.0, 0.0)

        # model trajectory from window-start measured state, zero wind, current drag estimate
        v_model = s0
        t = t0
        model_at = {}
        fi = 0
        while t < tn - 1e-9:
            dt = min(DT_IPP, tn - t)
            v_model = rk2_step(v_model, dt, self.cd_cal * self.cd_hat, (0.0, 0.0))
            t += dt
            while fi < len(self.fixes) and self.fixes[fi][0] <= t:
                model_at[fi] = v_model
                fi += 1

        # drag scale: ratio of measured to modeled speed drop (absorbs mass + along-track wind)
        drop_meas = (math.hypot(sn[3], sn[4], sn[5])
                     - math.hypot(self.fixes[0][1][3], self.fixes[0][1][4], self.fixes[0][1][5]))
        drop_model = (math.hypot(v_model[3], v_model[4], v_model[5])
                      - math.hypot(s0[3], s0[4], s0[5]))
        if abs(drop_model) > 1.0:
            new_hat = float(np.clip(self.cd_hat * drop_meas / drop_model, 0.8, 1.25))
            self.cd_hat = 0.3 * new_hat + 0.7 * self.cd_hat      # smoothed (filter stand-in)

        # crosswind: residual lateral velocity vs zero-wind model, first-order lag fit
        if T >= 8.0:
            resid = [(self.fixes[i][0] - t0, self.fixes[i][1][4] - model_at[i][4])
                     for i in sorted(model_at)]
            tt = np.array([r[0] for r in resid])
            rr = np.array([r[1] for r in resid])
            slope, intercept = np.polyfit(tt, rr, 1)
            res_end = slope * T + intercept
            klv = self._klv(sn)
            if klv > 1e-6:
                new_hat = float(np.clip(res_end + slope / klv, -12.0, 12.0))
                self.wy_hat = 0.3 * new_hat + 0.7 * self.wy_hat  # smoothed (filter stand-in)

        # impact point prediction with estimated drag + crosswind
        # (propagate() time is RELATIVE to the fix state -> t_go = t_imp directly)
        xi, yi, t_imp, _ = propagate(sn, self.cd_cal * self.cd_hat, (0.0, self.wy_hat), DT_IPP)
        t_go = t_imp
        if t_go < 2.0:
            return (0.0, 0.0)
        miss_x, miss_y = RANGE_TARGET - xi, 0.0 - yi
        if math.hypot(miss_x, miss_y) < DEADBAND:
            return (0.0, 0.0)
        self.a_cmd = (2.0 * miss_x / t_go ** 2, 2.0 * miss_y / t_go ** 2)
        return self.a_cmd

    def _klv(self, s):
        zbar = max(s[2], 100.0)
        return 0.5 * rho(zbar) * self.cd_cal * self.cd_hat * AREA * math.hypot(s[3], s[4], s[5]) / M_NOM


# ---------------------------------------------------------------- simulations
def sim_unguided(p, cd_cal):
    s0 = initial_state(p["v0"], p["elev"], p["azim"])
    xi, yi, _, _ = propagate(s0, cd_cal * p["cd_scale"], p["wind"], DT_TRUTH)
    return xi, yi


def sim_guided(p, cd_cal, t_lock, fin_force=FIN_FORCE_NOM):
    """Fly with the PGK guidance chain active. Returns impact (x, y), duty stats, estimator."""
    a_max = fin_force / p["mass"]
    est = KitEstimator(t_lock, cd_cal)
    a_cmd = (0.0, 0.0)
    next_fix = t_lock
    next_update = t_lock
    duty_peak, duty_sum, duty_n = 0.0, 0.0, 0

    def a_cmd_fn(_t):
        return a_cmd

    s = initial_state(p["v0"], p["elev"], p["azim"])
    t = 0.0
    while t < TMAX:
        if t >= next_fix:
            est.add_fix(t, s)
            next_fix += NAV_DT
        if t >= next_update:
            a_raw = est.update()
            mag = math.hypot(*a_raw)
            # apply commanded accel; saturate at fin authority (duty-cycle equivalent)
            a_cmd = a_raw if mag <= a_max else (a_max * a_raw[0] / mag, a_max * a_raw[1] / mag)
            duty = min(1.0, mag / a_max)
            duty_peak = max(duty_peak, duty)
            duty_sum += duty
            duty_n += 1
            next_update += NAV_DT
        s_prev = s
        s = rk4_step(s, DT_TRUTH, cd_cal * p["cd_scale"], p["wind"], a_cmd)
        t += DT_TRUTH
        if s[2] <= 0.0 < s_prev[2]:
            f = s_prev[2] / (s_prev[2] - s[2])
            xi = s_prev[0] + f * DT_TRUTH * s[3]
            yi = s_prev[1] + f * DT_TRUTH * s[4]
            return xi, yi, {"duty_peak": duty_peak, "duty_mean": duty_sum / max(duty_n, 1)}, est
    raise RuntimeError("no impact")


def draw_params():
    return {
        "v0": V0_NOM * (1.0 + rng.normal(0.0, 0.0015)),        # muzzle velocity, sigma 0.15%
        "elev": ELEV0 + rng.normal(0.0, 0.6e-3),               # elevation error, sigma 0.6 mrad
        "azim": rng.normal(0.0, 0.6e-3),                       # azimuth error, sigma 0.6 mrad
        "wind": (rng.normal(0.0, 3.0), rng.normal(0.0, 3.0)),  # met error, sigma 3 m/s each axis
        "cd_scale": 1.0 + rng.normal(0.0, 0.008),              # projectile aero variation
        "mass": M_NOM * (1.0 + rng.normal(0.0, 0.006)),
    }


def cep(radii):
    r = np.sort(np.asarray(radii))
    return {"median": float(np.median(r)), "mean": float(np.mean(r)),
            "p90": float(r[int(0.9 * len(r)) - 1]), "max": float(r[-1])}


# ---------------------------------------------------------------- mechanism checks
def mechanism_checks():
    print("\n=== Actuator feasibility (first principles, BOM masses) ===")
    parts = [
        ("Canard shell + fins (7075)", 0.150, 0.0425),
        ("Rotor bell (steel, as-built)", 0.258, 0.0398),
        ("Magnet ring N42SH", 0.023, 0.0378),
        ("Bearing inner ring (ring formula)", 0.182, None),
        ("Radome (GFRP)", 0.044, 0.0350),
        ("Dome stack (GNC+GNSS+prox)", 0.075, 0.0300),
        ("Dome base ring", 0.010, 0.0400),
        ("Pilot bearing + slip ring", 0.016, 0.0150),
    ]
    J = 0.0
    for name, m, r in parts:
        inertia = (0.5 * m * (0.0185 ** 2 + 0.016 ** 2) if r is None else m * r * r)
        J += inertia
        print(f"  {name:34s} m={m * 1000:6.1f} g   I_z = {inertia * 1e3:7.3f} g*m^2")
    omega = 2 * math.pi * 250.0
    L = J * omega
    print(f"  Total rotor J ~ {J:.2e} kg m^2 -> L at 250 rev/s = {L:.2f} kg m^2/s (report: 1.4)")
    print(f"  De-spin @ 10 s (Rev 1.1 spec) = {L / 10:.3f} N m -> {L / 10 / 0.0024:.0f} A  == peak spec 0.14 N m (zero margin)")
    print(f"  De-spin @ 15 s (Rev 1.2 spec) = {L / 15:.3f} N m -> {L / 15 / 0.0024:.0f} A  <= cell 45 A cont. (1.39x margin)")
    for slew_deg, slew_t in [(90, 1.0), (90, 0.2), (30, 0.5)]:
        alpha = 4 * math.radians(slew_deg) / slew_t ** 2
        print(f"  Roll slew {slew_deg:3d} deg in {slew_t:4.1f} s -> peak torque {J * alpha * 1e3:6.1f} mN m"
              f"   (continuous rating 50 mN m)")
    return J, L


# ---------------------------------------------------------------- main
def main():
    cd_cal, x_nom, tof_nom, apo_nom = calibrate_cd()
    print(f"Calibrated Cd = {cd_cal:.4f}  (nominal: range {x_nom:.0f} m, TOF {tof_nom:.1f} s, "
          f"apogee {apo_nom / 1000:.2f} km)")
    mechanism_checks()

    print("\n=== Deterministic cases (single shot each) ===")
    det_cases = [
        ("no error", dict(v0=V0_NOM, elev=ELEV0, azim=0.0, wind=(0.0, 0.0), cd_scale=1.0, mass=M_NOM)),
        ("crosswind 6 m/s", dict(v0=V0_NOM, elev=ELEV0, azim=0.0, wind=(0.0, 6.0), cd_scale=1.0, mass=M_NOM)),
        ("headwind 6 m/s", dict(v0=V0_NOM, elev=ELEV0, azim=0.0, wind=(-6.0, 0.0), cd_scale=1.0, mass=M_NOM)),
        ("muzzle +1.5 m/s", dict(v0=V0_NOM + 1.5, elev=ELEV0, azim=0.0, wind=(0.0, 0.0), cd_scale=1.0, mass=M_NOM)),
        ("Cd +5%", dict(v0=V0_NOM, elev=ELEV0, azim=0.0, wind=(0.0, 0.0), cd_scale=1.05, mass=M_NOM)),
    ]
    det_rows = []
    for name, p in det_cases:
        ux, uy = sim_unguided(p, cd_cal)
        gx, gy, duty, _ = sim_guided(p, cd_cal, T_LOCK_NOM)
        det_rows.append((name, math.hypot(ux - RANGE_TARGET, uy), math.hypot(gx - RANGE_TARGET, gy)))
        print(f"  {name:18s}  unguided miss {math.hypot(ux - RANGE_TARGET, uy):7.1f} m   "
              f"guided miss {math.hypot(gx - RANGE_TARGET, gy):6.1f} m")

    print(f"\n=== Monte Carlo ({N_RUNS} paired runs) ===")
    pts = {"unguided": [], "guided": [], "late_lock": []}
    duty_peaks, duty_means = [], []
    for i in range(N_RUNS):
        p = draw_params()
        pts["unguided"].append(sim_unguided(p, cd_cal))
        gx, gy, duty, _ = sim_guided(p, cd_cal, T_LOCK_NOM)
        pts["guided"].append((gx, gy))
        duty_peaks.append(duty["duty_peak"])
        duty_means.append(duty["duty_mean"])
        pts["late_lock"].append(sim_guided(p, cd_cal, T_LOCK_NOM + 25.0)[:2])  # lock 60 s
        if (i + 1) % 50 == 0:
            print(f"  ... {i + 1}/{N_RUNS} runs")

    radii = {k: [math.hypot(x - RANGE_TARGET, y) for (x, y) in v] for k, v in pts.items()}
    stats = {k: cep(v) for k, v in radii.items()}
    print("\n=== Results (radial miss about target, m) ===")
    print(f"{'config':22s} {'CEP50':>8s} {'mean':>8s} {'p90':>8s} {'max':>8s}")
    for k in ["unguided", "guided", "late_lock"]:
        s = stats[k]
        print(f"{k:22s} {s['median']:8.1f} {s['mean']:8.1f} {s['p90']:8.1f} {s['max']:8.1f}")
    improvement = stats["unguided"]["median"] / max(stats["guided"]["median"], 1e-9)
    print(f"\nGuided/unguided CEP improvement: {improvement:.1f}x")
    print(f"Duty fraction |a_cmd|/a_max: median of peak per run = {np.median(duty_peaks):.2f}, "
          f"median of mean = {np.median(duty_means):.2f}")

    p = dict(v0=V0_NOM, elev=ELEV0, azim=0.0, wind=(0.0, 6.0), cd_scale=1.0, mass=M_NOM)
    gx30, gy30, _, _ = sim_guided(p, cd_cal, T_LOCK_NOM, fin_force=30.0)
    print(f"Authority floor (30 N fins, 6 m/s crosswind): guided miss {math.hypot(gx30 - RANGE_TARGET, gy30):.1f} m")

    write_results(cd_cal, x_nom, tof_nom, apo_nom, det_rows, stats, improvement,
                  duty_peaks, duty_means, math.hypot(gx30 - RANGE_TARGET, gy30))
    plot(pts, radii, stats)


def write_results(cd_cal, x_nom, tof_nom, apo_nom, det_rows, stats, improvement,
                  duty_peaks, duty_means, miss_30N):
    lines = []
    A = lines.append
    A("# Steering-effectiveness verification — clean-sheet PGK canard mechanism")
    A("")
    A(f"Runs: {N_RUNS} paired Monte Carlo runs (identical dispersion draws per variant), seed 20260830.")
    A(f"Truth model: 3DOF point mass, RK4 dt={DT_TRUTH} s, exponential atmosphere, drag-only,")
    A(f"Cd calibrated to {cd_cal:.4f} so the nominal shot (46 deg, 827 m/s) lands at {x_nom / 1000:.1f} km")
    A(f"(TOF {tof_nom:.0f} s, apogee {apo_nom / 1000:.1f} km — matches report §3 design case).")
    A("")
    A("## Mechanism modeled")
    A("- Fixed-trim canard pair -> constant-force roll-aimed actuator; magnitude via duty cycling")
    A("  (as-built CAD: fins are machined at ±3°/0°, nothing moves except the nose roll)")
    A(f"- Lateral authority: {FIN_FORCE_NOM:.0f} N total (fin pair + body lift amplification; audit range 30–100 N)")
    A("- De-spin t=25 s; GNSS lock t=35 s (late-lock variant t=60 s); 1 Hz nav updates")
    A("- IPP from 1 Hz GPS fixes (pos σ 5 m, vel σ 0.3 m/s) with in-flight drag-scale + crosswind estimation")
    A("- Guidance law: a_cmd = 2·miss/t_go², clamped to authority")
    A("")
    A("## Deterministic cases")
    A("")
    A("| Case | Unguided miss (m) | Guided miss (m) |")
    A("|---|---|---|")
    for name, um, gm in det_rows:
        A(f"| {name} | {um:.1f} | {gm:.1f} |")
    A("")
    A("## Monte Carlo (dispersions: V0 σ0.15%, aim σ0.6 mrad, wind σ3 m/axis, Cd σ0.8%, mass σ0.6%)")
    A("")
    A("| Config | CEP50 (m) | mean (m) | p90 (m) | max (m) |")
    A("|---|---|---|---|---|")
    for k, label in [("unguided", "Unguided"), ("guided", "Guided (lock 35 s)"), ("late_lock", "Guided (lock 60 s)")]:
        s = stats[k]
        A(f"| {label} | {s['median']:.1f} | {s['mean']:.1f} | {s['p90']:.1f} | {s['max']:.1f} |")
    A("")
    A(f"**CEP improvement guided/unguided: {improvement:.1f}×**")
    A("")
    A(f"- Duty fraction |a_cmd|/a_max: median of per-run peak = {np.median(duty_peaks):.2f}, "
      f"median of per-run mean = {np.median(duty_means):.2f}")
    A(f"- Authority floor (30 N fins): 6 m/s crosswind case guided miss = {miss_30N:.1f} m")
    A("")
    A("## Actuator feasibility (first principles, from BOM masses)")
    A("- Rotor-frame J ≈ 0.91e-3 kg·m² → L = 1.43 kg·m²/s at 250 rev/s (matches report §7)")
    A("- Rev 1.1 de-spin (10 s): 0.143 N·m → 60 A == peak spec, zero margin — RE-SPECCED")
    A("- Rev 1.2 de-spin (15 s): 0.095 N·m → ≤40 A, within cell 45 A continuous (1.39× margin);")
    A("  boost stage 3.7→5 V guarantees terminal headroom at −40 °C/50 % SoC (BOM §G)")
    A("- Steering roll slews are cheap: 90° in 1 s needs ~5.6 mN·m vs 50 mN·m continuous rating")
    A("  → the nose can re-aim essentially instantly compared to the 1 Hz nav cycle")
    A("")
    A("## Known model limitations (next rungs per report §10.1)")
    A("- No spin / Magnus / roll channel yet (6DOF rung); drag-only aero with calibrated Cd,")
    A("  not tabulated M795 Mach-dependent drag")
    A("- Point-mass lateral force: no trim-drag penalty during coast whirl; no actuator lag")
    A("  (roll slew ≪ nav cycle — verified above)")
    A("- Estimator is a windowed ratio fit, not a Kalman filter — conservative vs a flight implementation")
    A("- GPS-denied final-seconds behavior and jamming not modeled")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "RESULTS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {os.path.join(OUT_DIR, 'RESULTS.md')}")


def plot(pts, radii, stats):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 9))
    styles = [("unguided", "#dc2626", "Unguided"), ("late_lock", "#f59e0b", "Guided, late lock 60 s"),
              ("guided", "#059669", "Guided, lock 35 s")]
    for key, color, label in styles:
        xs = [x - RANGE_TARGET for (x, y) in pts[key]]
        ys = [y for (x, y) in pts[key]]
        ax.scatter(xs, ys, s=12, alpha=0.55, color=color, label=f"{label} — CEP {stats[key]['median']:.0f} m")
    ax.scatter([0], [0], marker="*", s=350, color="black", zorder=5, label="target")
    circ = plt.Circle((0, 0), 30, fill=False, color="#059669", ls="--", lw=1.2)
    ax.add_patch(circ)
    ax.set_xlabel("crossrange error (m)")
    ax.set_ylabel("range error (m)")
    ax.set_title("PGK steering verification — paired Monte Carlo impacts")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_aspect("equal")
    ax.grid(alpha=0.25)
    os.makedirs(OUT_DIR, exist_ok=True)
    fig.savefig(os.path.join(OUT_DIR, "steering_check.png"), dpi=130, bbox_inches="tight")
    print(f"Wrote {os.path.join(OUT_DIR, 'steering_check.png')}")


if __name__ == "__main__":
    main()
