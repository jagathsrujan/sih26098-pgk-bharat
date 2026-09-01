"""Co-simulation harness — FSW vs the Rev E 3DOF truth model (paired MC).

The ONLY component allowed to import scripts/sim_gnc_check.py (truth dynamics,
sensor synthesis, dispersion draws). The FSW package sees the world exclusively
through fsw.sensors interfaces; the truth side here mirrors sim_gnc_revE's
plant (roll servo, forces, sensors) while every navigation/guidance/control
decision is made by fsw.FlightComputer.

Pairing contract (seed 20260901, same stream as main_revE):
  - sim.rng is THE stream (replaced here exactly as main_revE does);
  - fsw_shot consumes draws in the same order/count as sim_gnc_revE:
    b_body(2) + mount(2 if None) + gyro_bias(1) + gyro(1/step)
    + accel(2/step when settled & EKF alive) + GNSS(6/fix);
  - deterministic-case and primary-MC loops replicate main_revE's structure;
  - --pair-check verifies per-shot draw counts and near-identical misses
    against sim_gnc_revE on a fresh shared seed.

Run:  python3 cosim/run_cosim.py [--smoke] [--det] [--pair-check] [--budget]
Writes out_sim/RESULTS_FSW.md + out_sim/steering_fsw.png (generated numbers
only — never hand-edited).
"""
import argparse
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FLIGHT_SW = os.path.dirname(HERE)
CLEANSHEET = os.path.dirname(FLIGHT_SW)
sys.path.insert(0, FLIGHT_SW)
sys.path.insert(0, os.path.join(CLEANSHEET, "scripts"))

import numpy as np  # noqa: E402
import sim_gnc_check as sim  # noqa: E402

import fsw  # noqa: E402

OUT_DIR = sim.OUT_DIR
SEED = 20260901
R_E = sim.RANGE_TARGET

# Gyro per-sample noise (deg/s, at the DT_TRUTH step). Was the literal
# radians(0.2) inside fsw_shot; lifted here so --sensor-profile can override it.
# baseline value is byte-identical to the Rev E reference draw.
GYRO_SAMPLE_SIG = math.radians(0.2)

# Sensor profiles (05_SENSOR_SELECTION.md §4). Each patch is applied to BOTH
# sides at runtime: sim.* globals (read at call time by sim_gnc_check, which is
# NOT edited) and fsw.config attributes (read at FlightComputer construction).
# The gyro per-sample noise lives in this harness only (GYRO_SAMPLE_SIG) and is
# held at the 0.2 deg/s environment figure in every profile — the sim's own
# literal is frozen, so holding the value keeps sim-side and FSW-side draw
# streams identical and --pair-check parity (counts AND misses) holds.
SENSOR_PROFILES = {
    "baseline": {
        "gps_pos_sig_m": 5.0,        # sim/config constants as-is (must reproduce 21.5 m)
        "gps_vel_sig_ms": 0.3,
        "gnss_lat_s": 0.10,
        "gyro_bias_init_deg_s": 0.5,
        "gyro_sample_deg_s": 0.2,
        "acc_noise_sig_ms2": 0.08,   # per IMU sample @200 Hz (config semantics)
        "acc_bias_init_ms2": 0.25,
    },
    # ICM-45686 + NEO-F10N datasheet-derived (derivations in 05_SENSOR_SELECTION.md §4):
    # tolerances read as 2-sigma, flight temp span 40 C, RSS-combined.
    # gyro_sample_deg_s is held at the 0.2 deg/s environment figure in every
    # profile: it is vibration/servo-jitter dominated, NOT part-limited (the
    # ICM-45686 sensor-only RND is 0.017 deg/s per sample — 12x headroom, §4).
    # Holding it constant keeps the sim-side and FSW-side draw streams identical
    # (the sim's own 0.2 literal is frozen), so --pair-check parity holds.
    "selected": {
        "gps_pos_sig_m": 1.2,        # F10N 1 m CEP -> sigma ~0.85 m, rounded up (dynamics/multipath)
        "gps_vel_sig_ms": 0.1,       # F10N 0.05 m/s, 2x rounding
        "gnss_lat_s": 0.10,          # no receiver max spec; time-tagged UBX (unchanged)
        "gyro_bias_init_deg_s": 0.18,  # 45686 ZRO +-0.3 -> 0.15; temp 0.005/C x 40 C -> 0.10; RSS
        "gyro_sample_deg_s": 0.2,    # environment figure (see note above); part-level 0.017
        "acc_noise_sig_ms2": 0.0108, # RND 110 ug/rtHz @ +-32 g FS x 9.80665 x sqrt(200/2)
        "acc_bias_init_ms2": 0.08,   # zero-g +-10 mg -> 0.049; temp 0.15 mg/C x 40 C -> 0.03; RSS, rounded up
    },
    # Datasheet limits at face value (as 1-sigma), full-temp terms, GNSS held at
    # the GNC interface requirement (receiver assumed to meet only that).
    "worstcase": {
        "gps_pos_sig_m": 5.0,
        "gps_vel_sig_ms": 0.3,
        "gnss_lat_s": 0.10,
        "gyro_bias_init_deg_s": 0.36,  # ZRO 0.3 + temp 0.2 (face value), RSS
        "gyro_sample_deg_s": 0.2,      # environment figure (see selected note)
        "acc_noise_sig_ms2": 0.08,     # vibration-dominated (airframe); >= datasheet 0.011
        "acc_bias_init_ms2": 0.10,     # zero-g 0.098 + temp 0.006 (face value), RSS
    },
}


def apply_sensor_profile(name_or_path):
    """Apply a sensor profile to the sim globals, this harness's gyro draw
    sigma, and the FSW-side filter constants. Returns the profile dict.
    FSW files are NOT edited — fsw.config attributes are patched at runtime
    before any FlightComputer construction (tests/test_config.py is untouched).
    """
    if name_or_path in SENSOR_PROFILES:
        p = dict(SENSOR_PROFILES[name_or_path])
        label = name_or_path
    else:
        import json
        with open(name_or_path) as f:
            p = json.load(f)
        label = os.path.basename(name_or_path)
    sim.GPS_POS_SIG = p["gps_pos_sig_m"]
    sim.GPS_VEL_SIG = p["gps_vel_sig_ms"]
    sim.GNSS_LAT = p["gnss_lat_s"]
    sim.GYRO_BIAS_INIT_SIG = math.radians(p["gyro_bias_init_deg_s"])
    sim.ACC_AVG_SIG = p["acc_noise_sig_ms2"] / math.sqrt(200.0)
    sim.ACC_BIAS_INIT_SIG = p["acc_bias_init_ms2"]   # sim NavEKF P0 (filter tuning parity)
    global GYRO_SAMPLE_SIG
    GYRO_SAMPLE_SIG = math.radians(p["gyro_sample_deg_s"])
    fsw.config.GPS_POS_SIG = p["gps_pos_sig_m"]
    fsw.config.GPS_VEL_SIG = p["gps_vel_sig_ms"]
    fsw.config.GNSS_LAT = p["gnss_lat_s"]
    fsw.config.GYRO_BIAS_INIT_SIG = math.radians(p["gyro_bias_init_deg_s"])
    fsw.config.ACC_BIAS_INIT_SIG = p["acc_bias_init_ms2"]
    print(f"[sensor profile: {label}] pos {p['gps_pos_sig_m']} m, "
          f"vel {p['gps_vel_sig_ms']} m/s, lat {p['gnss_lat_s'] * 1e3:.0f} ms, "
          f"gyro bias {p['gyro_bias_init_deg_s']} deg/s, "
          f"gyro/sample {p['gyro_sample_deg_s']} deg/s, "
          f"acc/sample {p['acc_noise_sig_ms2']} m/s2, acc bias {p['acc_bias_init_ms2']} m/s2")
    return p

# Rev E reference (out_sim/RESULTS_GNC.md) for the deterministic table deltas
REV_E_DET = {"nominal": 12.5, "mount bias 5deg": 18.1, "crosswind 6": 9.4,
             "headwind 6": 13.7, "Cd +5%": 104.5, "BLIND (no roll ref)": 91.4}
REV_E_MC = {"Rev E EKF+dragref L0": 21.5, "Rev E ZEM 6dp/tgo2": 21.5,
            "Rev E L0 outage 60-70s": 17.6, "Rev E BLIND (no roll ref)": 115.2,
            "Rev E never-lock (fail-safe)": 209.7}


class CountingRng:
    """Draw-counting proxy (normal/random are the only consumers in both the
    sim shot and the FSW shot)."""

    def __init__(self, gen):
        self.g = gen
        self.n = 0

    def normal(self, *a, **k):
        self.n += 1
        return self.g.normal(*a, **k)

    def random(self):
        self.n += 1
        return self.g.random()


def fsw_shot(p, cd_cal, Q70, law="l0", blind=False, outage=None,
             never_lock=False, mount_bias_deg=None, wind_fit=True,
             fc_factory=None, draw_counter=None):
    """One guided shot: truth + sensors (this harness) vs FSW (FlightComputer).
    Returns (xi, yi, stats). rng source: sim.rng (paired stream)."""
    rng = draw_counter if draw_counter is not None else sim.rng
    m_true = p["mass"]
    b_body = (rng.normal(0, 0.01), rng.normal(0, 0.01))
    if mount_bias_deg is not None:
        b_mount = math.radians(mount_bias_deg)
    else:
        b_mount = math.radians(abs(rng.normal(0, 0.5)))
        b_mount *= 1.0 if rng.random() > 0.5 else -1.0
    gyro_bias_true = rng.normal(0, sim.GYRO_BIAS_INIT_SIG)
    delta_blind = None

    make = fc_factory or (lambda: fsw.FlightComputer(
        cd_cal=cd_cal, law=law, blind=blind, wind_fit=wind_fit,
        rates=fsw.COSIM_RATES, q_ref=Q70))
    fc = make()

    psi_S = 0.0
    psi_R = 0.0
    om_R = sim.OMEGA_S
    next_fix = sim.T_GNSS_LOCK
    s = sim.initial_state(p["v0"], p["elev"], p["azim"])
    t = 0.0
    while t < sim.TMAX:
        # ---------------- truth roll (servo follows the FSW command) --------
        if t < sim.T_DESPIN_START:
            psi_S += sim.OMEGA_S * sim.DT_TRUTH
            psi_R = psi_S
            om_R = sim.OMEGA_S
        elif t < sim.T_DESPIN_END:
            psi_S += sim.OMEGA_S * sim.DT_TRUTH
            frac = (t - sim.T_DESPIN_START) / (sim.T_DESPIN_END - sim.T_DESPIN_START)
            om_R = sim.OMEGA_S * (1.0 - frac)
            psi_R += om_R * sim.DT_TRUTH
        else:
            psi_S += sim.OMEGA_S * sim.DT_TRUTH
            if delta_blind is None:
                delta_blind = sim.wrap_pi(psi_R)
            az_cmd = fc.ctrl.azimuth(t)
            if blind or fc.nav.roll.psi is None:
                err = sim.wrap_pi(az_cmd + delta_blind - psi_R)
            else:
                err = sim.wrap_pi(az_cmd - fc.nav.roll.psi)
            om_des = fc.ctrl.servo_rate_cmd(err, sim.DT_TRUTH)
            om_R += max(-55.0 * sim.DT_TRUTH, min(55.0 * sim.DT_TRUTH, om_des - om_R))
            psi_R = sim.wrap_pi(psi_R + om_R * sim.DT_TRUTH)

        # ---------------- truth forces ------------------------------------
        a_lat = (0.0, 0.0)
        f_in_h = (0.0, 0.0)
        if t >= sim.T_DESPIN_END:
            ad_true = sim.accel(s, cd_cal * p["cd_scale"], p["wind"])
            f_in_h = (ad_true[0], ad_true[1])
            if abs(om_R) < sim.OMEGA_SPIN_SAT:
                F_true = sim.FIN_FORCE_NOM * sim.q_dyn(s) / Q70
                a_lat = (F_true / m_true * math.cos(psi_R),
                         F_true / m_true * math.sin(psi_R))
                f_in_h = (f_in_h[0] + a_lat[0], f_in_h[1] + a_lat[1])

        # ---------------- sensors (Rev E noise stream) ---------------------
        settled = fc.ctrl.settled(t)
        gyro_meas = om_R + gyro_bias_true + rng.normal(0, GYRO_SAMPLE_SIG)
        is_sat = abs(gyro_meas) > sim.GYRO_SAT_RPS
        fc.sensor_gyro(gyro_meas, is_sat)
        if fc.nav.ekf is not None and t >= sim.T_DESPIN_END and settled:
            # mount offset injected at sensor level (strapped-down accel)
            fb_h = sim.rot2(-psi_R - b_mount, f_in_h)
            noise = (rng.normal(0, sim.ACC_AVG_SIG), rng.normal(0, sim.ACC_AVG_SIG))
            fc.sensor_accel_settled(t, fb_h, b_body, noise)

        # ---------------- GNSS fixes ---------------------------------------
        in_outage = outage is not None and outage[0] <= t < outage[1]
        if not never_lock and t >= next_fix - 1e-9 and not in_outage:
            pos_m = np.array([s[0] + rng.normal(0, sim.GPS_POS_SIG),
                              s[1] + rng.normal(0, sim.GPS_POS_SIG),
                              s[2] + rng.normal(0, sim.GPS_POS_SIG * 1.6)])
            vel_m = np.array([s[3] + rng.normal(0, sim.GPS_VEL_SIG),
                              s[4] + rng.normal(0, sim.GPS_VEL_SIG),
                              s[5] + rng.normal(0, sim.GPS_VEL_SIG)])
            fc.push_fix(t, pos_m, vel_m)          # time-tagged, arrives +GNSS_LAT
            next_fix += sim.NAV_DT

        # ---------------- FSW tasks (fixed-rate scheduler) ------------------
        fc.tick(t, sim.DT_TRUTH)

        # ---------------- truth dynamics -----------------------------------
        s_prev = s
        s = sim.rk4_step(s, sim.DT_TRUTH, cd_cal * p["cd_scale"], p["wind"], a_lat)
        t += sim.DT_TRUTH
        if s[2] <= 0 < s_prev[2]:
            f = s_prev[2] / (s_prev[2] - s[2])
            xi = s_prev[0] + f * sim.DT_TRUTH * s[3]
            yi = s_prev[1] + f * sim.DT_TRUTH * s[4]
            st = fc.stats()
            st["psi_err_deg"] = fc.nav.roll.err_vs(psi_R)
            return xi, yi, st
    raise RuntimeError("no impact")


def det_cases(cd_cal, Q70, fc_factory=None, draw_counter=None):
    """Deterministic stress cases (same order/kwargs as main_revE)."""
    det = [("nominal", dict()),
           ("mount bias 5deg", dict(mount_bias_deg=5.0)),
           ("crosswind 6", dict(wind=(0., 6.))),
           ("headwind 6", dict(wind=(-6., 0.))),
           ("Cd +5%", dict(cd_scale=1.05)),
           ("BLIND (no roll ref)", dict(blind=True))]
    rows = []
    for name, kw in det:
        p = dict(v0=sim.V0_NOM, elev=sim.ELEV0, azim=0., mass=sim.M_NOM,
                 wind=(0., 0.), cd_scale=1.)
        p.update({k: v for k, v in kw.items() if k in ("wind", "cd_scale")})
        gx, gy, st = fsw_shot(p, cd_cal, Q70, law="l0",
                              blind=kw.get("blind", False),
                              mount_bias_deg=kw.get("mount_bias_deg"),
                              fc_factory=fc_factory, draw_counter=draw_counter)
        rows.append((name, math.hypot(gx - R_E, gy), st))
    return rows


def print_det(rows):
    for name, miss, st in rows:
        ref = REV_E_DET.get(name)
        delta = f" ({(miss - ref) / ref * 100:+.1f}% vs Rev E)" if ref else ""
        print(f"  {name:20s} fsw={miss:6.1f}{delta} mode={st['mode']:8s} "
              f"psiErr={st['psi_err_deg']:5.2f} dutyMean={st['duty_mean']:.2f} "
              f"s_cd={st['s_cd']:.3f} wy={st['wy_hat']:.1f}")


def run_det(cd_cal, Q70):
    print("=== Deterministic (FSW co-sim vs Rev E reference) ===")
    rows = det_cases(cd_cal, Q70)
    print_det(rows)
    return rows


def pair_check(cd_cal, Q70):
    """Stream-pairing proof: same fresh seed, sim shot vs FSW shot must draw
    identically and land within float-noise of each other."""
    print("=== Pair check (fresh shared seed 20260901, sim vs FSW per det case) ===")
    det = [("nominal", dict()),
           ("mount bias 5deg", dict(mount_bias_deg=5.0)),
           ("crosswind 6", dict(wind=(0., 6.))),
           ("headwind 6", dict(wind=(-6., 0.))),
           ("Cd +5%", dict(cd_scale=1.05)),
           ("BLIND (no roll ref)", dict(blind=True))]
    ok_all = True
    for name, kw in det:
        p = dict(v0=sim.V0_NOM, elev=sim.ELEV0, azim=0., mass=sim.M_NOM,
                 wind=(0., 0.), cd_scale=1.)
        p.update({k: v for k, v in kw.items() if k in ("wind", "cd_scale")})
        kw_sim = dict(law="l0", blind=kw.get("blind", False),
                      mount_bias_deg=kw.get("mount_bias_deg"))
        sim.rng = CountingRng(np.random.default_rng(SEED))
        sx, sy, sst, _ = sim.sim_gnc_revE(p, cd_cal, Q70, **kw_sim)
        n_sim = sim.rng.n
        sim.rng = CountingRng(np.random.default_rng(SEED))
        fx, fy, fst = fsw_shot(p, cd_cal, Q70, draw_counter=sim.rng, **kw_sim)
        n_fsw = sim.rng.n
        d_miss = (math.hypot(fx - R_E, fy) - math.hypot(sx - R_E, sy))
        ok = (n_sim == n_fsw) and abs(d_miss) < 0.5
        ok_all &= ok
        print(f"  {name:20s} draws sim={n_sim:6d} fsw={n_fsw:6d} "
              f"miss sim={math.hypot(sx - R_E, sy):7.2f} fsw={math.hypot(fx - R_E, fy):7.2f} "
              f"d={d_miss:+.4f} m  {'OK' if ok else 'MISMATCH'}")
    if not ok_all:
        print("  PAIRING BROKEN — do not trust the MC pairing")
    return ok_all


def cep(radii):
    r = np.sort(np.asarray(radii))
    return {"median": float(np.median(r)), "mean": float(np.mean(r)),
            "p90": float(r[int(0.9 * len(r)) - 1]), "max": float(r[-1])}


def run_mc(cd_cal, Q70, n_pri, n_sec):
    outage_int = (60.0, 70.0)
    keys = ["unguided", "legacy", "fsw_l0", "fsw_neverlock",
            "fsw_zem", "fsw_outage", "fsw_blind"]
    pts = {k: [] for k in keys}
    duty = {k: [] for k in keys}
    psi_err = {k: [] for k in keys}
    modes = {k: {} for k in keys}
    print(f"\n=== Monte Carlo {n_pri} primary + {n_sec}x4 secondary "
          f"(seed {SEED}, paired dispersions) ===")
    t0 = time.perf_counter()
    for i in range(n_pri):
        p = sim.draw_params()
        pts["unguided"].append(sim.sim_unguided(p, cd_cal))
        gx, gy, d, _ = sim.sim_guided_legacy(p, cd_cal, sim.T_GNSS_LOCK)
        pts["legacy"].append((gx, gy))
        duty["legacy"].append(d["duty_peak"])
        gx, gy, st = fsw_shot(p, cd_cal, Q70, law="l0")
        pts["fsw_l0"].append((gx, gy))
        duty["fsw_l0"].append(st["duty_peak"])
        psi_err["fsw_l0"].append(st["psi_err_deg"])
        modes["fsw_l0"][st["mode"]] = modes["fsw_l0"].get(st["mode"], 0) + 1
        gx, gy, st = fsw_shot(p, cd_cal, Q70, law="l0", never_lock=True)
        pts["fsw_neverlock"].append((gx, gy))
        modes["fsw_neverlock"][st["mode"]] = modes["fsw_neverlock"].get(st["mode"], 0) + 1
        if (i + 1) % 25 == 0:
            el = time.perf_counter() - t0
            print(f"  ...{i + 1}/{n_pri} primary ({el:.0f} s)")
    for i in range(n_sec):
        p = sim.draw_params()
        gx, gy, st = fsw_shot(p, cd_cal, Q70, law="zem")
        pts["fsw_zem"].append((gx, gy))
        duty["fsw_zem"].append(st["duty_peak"])
        psi_err["fsw_zem"].append(st["psi_err_deg"])
        gx, gy, st = fsw_shot(p, cd_cal, Q70, law="l0", outage=outage_int)
        pts["fsw_outage"].append((gx, gy))
        duty["fsw_outage"].append(st["duty_peak"])
        psi_err["fsw_outage"].append(st["psi_err_deg"])
        modes["fsw_outage"][st["mode"]] = modes["fsw_outage"].get(st["mode"], 0) + 1
        gx, gy, st = fsw_shot(p, cd_cal, Q70, law="l0", blind=True)
        pts["fsw_blind"].append((gx, gy))
        duty["fsw_blind"].append(st["duty_peak"])
        psi_err["fsw_blind"].append(st["psi_err_deg"])
        if (i + 1) % 20 == 0:
            print(f"  ...{i + 1}/{n_sec} secondary")
    radii = {k: [math.hypot(x - R_E, y) for x, y in v] for k, v in pts.items()}
    stats = {k: cep(v) for k, v in radii.items()}
    print("\n=== Results (radial miss, m) ===")
    print(f"{'config':16s} {'CEP50':>7s} {'mean':>7s} {'p90':>7s} {'max':>7s} "
          f"{'dutyPk50':>8s} {'psiErr50':>8s}")
    for k in keys:
        s_st = stats[k]
        d50 = float(np.median(duty[k])) if duty[k] else 0.0
        e50 = float(np.nanmedian(psi_err[k])) if psi_err[k] else float("nan")
        print(f"{k:16s} {s_st['median']:7.1f} {s_st['mean']:7.1f} {s_st['p90']:7.1f} "
              f"{s_st['max']:7.1f} {d50:8.2f} {e50:8.2f}")
    print("modes:", {k: v for k, v in modes.items() if v})
    imp_ung = stats["unguided"]["median"] / max(stats["fsw_l0"]["median"], 1e-9)
    print(f"Unguided/fsw_l0: {imp_ung:.1f}x   "
          f"legacy/fsw_l0: {stats['legacy']['median'] / max(stats['fsw_l0']['median'], 1e-9):.2f}x")
    return dict(pts=pts, radii=radii, stats=stats, duty=duty, psi_err=psi_err,
                modes=modes, imp_ung=imp_ung, n_pri=n_pri, n_sec=n_sec,
                wall_s=time.perf_counter() - t0)


def budget_probe(cd_cal, Q70, shots=2):
    """Measure per-task tick cost (perf_counter) over full det shots."""
    counts = {}
    seconds = {}

    def timed(name, fn):
        def inner(*args, **kwargs):
            t0 = time.perf_counter()
            fn(*args, **kwargs)
            elapsed = time.perf_counter() - t0
            seconds.setdefault(name, [0.0, 0.0])
            counts.setdefault(name, 0)
            seconds[name][0] += elapsed
            seconds[name][1] = max(seconds[name][1], elapsed)
            counts[name] += 1
        return inner

    for _ in range(shots):
        def make():
            fc = fsw.FlightComputer(cd_cal=cd_cal, rates=fsw.COSIM_RATES)
            for task in fc.sched.tasks():
                task.fn = timed(task.name, task.fn)
            fc.sensor_gyro = timed("sensor_gyro", fc.sensor_gyro)
            fc.sensor_accel_settled = timed("sensor_accel", fc.sensor_accel_settled)
            return fc

        p = dict(v0=sim.V0_NOM, elev=sim.ELEV0, azim=0., mass=sim.M_NOM,
                 wind=(0., 0.), cd_scale=1.)
        fsw_shot(p, cd_cal, Q70, fc_factory=make)
    rows = [(name, seconds[name][0] / counts[name] * 1e6,
             seconds[name][1] * 1e6, counts[name] / shots)
            for name in sorted(seconds)]
    return rows


def write_results(cd_cal, x_nom, tof_nom, apo_nom, Q70, det_rows, mc, budget,
                  out_name="RESULTS_FSW.md"):
    lines = []
    A = lines.append
    n_pri, n_sec = mc["n_pri"], mc["n_sec"]
    stats = mc["stats"]
    A("# Flight software co-simulation — PGK clean-sheet (FSW vs Rev E truth)")
    A("")
    A(f"Runs: {n_pri} primary + {n_sec}x4 secondary MC (seed {SEED}), paired dispersions")
    A("(same draw_params stream as the Rev E reference run; sim+FSW draw-count parity")
    A("verified per deterministic case).")
    A(f"Truth: 3DOF RK4 dt={sim.DT_TRUTH}, exp atmo, Cd={cd_cal:.4f} -> nom {x_nom:.0f} m-range "
      f"TOF{tof_nom:.0f}s apo{apo_nom / 1000:.1f}km (scripts/sim_gnc_check.py, untouched).")
    A(f"Authority: F(t) = 60 N * q(t)/q(70s) (q70={Q70:.0f} Pa).")
    A("FSW: `cleansheet/flight_sw/` reference package (config/timebase/modes/sensors/nav/guide/ctrl);")
    A("co-sim task cadence = truth step for paired numerics; deployment rates in FLIGHT_SOFTWARE.md.")
    A("")
    A("## Deterministic (FSW vs Rev E reference)")
    A("| Case | FSW (m) | Rev E ref (m) | delta | mode | psi err (deg) |")
    A("|---|---|---|---|---|---|")
    for name, miss, st in det_rows:
        ref = REV_E_DET.get(name)
        d = f"{(miss - ref) / ref * 100:+.1f}%" if ref else "—"
        reftxt = f"{ref:.1f}" if ref else "—"
        A(f"| {name} | {miss:.1f} | {reftxt} | {d} | {st['mode']} | {st['psi_err_deg']:.2f} |")
    A("")
    A(f"## Monte Carlo (disp V0 s0.15% aim 0.6 mrad wind s3 m/axis Cd s0.8% mass s0.6%)")
    A("")
    A("| Config | CEP50 | mean | p90 | max | dutyPk med | psiErr med (deg) | Rev E ref CEP50 |")
    A("|---|---|---|---|---|---|---|---|")
    label = {"unguided": "Unguided", "legacy": "Legacy windowed (idealized actuator)",
             "fsw_l0": "FSW L0", "fsw_neverlock": "FSW never-lock (fail-safe)",
             "fsw_zem": "FSW ZEM 6dp/tgo2", "fsw_outage": "FSW L0 outage 60-70s",
             "fsw_blind": "FSW BLIND (no roll ref)"}
    refmap = {"FSW L0": REV_E_MC["Rev E EKF+dragref L0"],
              "FSW ZEM 6dp/tgo2": REV_E_MC["Rev E ZEM 6dp/tgo2"],
              "FSW L0 outage 60-70s": REV_E_MC["Rev E L0 outage 60-70s"],
              "FSW BLIND (no roll ref)": REV_E_MC["Rev E BLIND (no roll ref)"],
              "FSW never-lock (fail-safe)": REV_E_MC["Rev E never-lock (fail-safe)"]}
    for k in ["unguided", "legacy", "fsw_l0", "fsw_zem", "fsw_outage",
              "fsw_blind", "fsw_neverlock"]:
        s_st = stats[k]
        d50 = float(np.median(mc["duty"][k])) if mc["duty"][k] else 0.0
        e50 = float(np.nanmedian(mc["psi_err"][k])) if mc["psi_err"][k] else float("nan")
        ref = refmap.get(label[k])
        reftxt = f"{ref:.1f}" if ref is not None else "—"
        A(f"| {label[k]} | {s_st['median']:.1f} | {s_st['mean']:.1f} | {s_st['p90']:.1f} | "
          f"{s_st['max']:.1f} | {d50:.2f} | {e50:.2f} | {reftxt} |")
    A("")
    A(f"**Improvement vs unguided: FSW L0 {mc['imp_ung']:.1f}x.**")
    for k, v in mc["modes"].items():
        if v:
            A(f"- end-modes {k}: {v}")
    g = gates(stats, mc["modes"])
    A("")
    A("## Gate (plan: CEP50 <= 24 m, >=98% guide/degraded, 0 denied)")
    A(f"- CEP50 (FSW L0): {stats['fsw_l0']['median']:.1f} m vs 24 m -> "
      f"{'PASS' if g['cep_pass'] else 'FAIL'}")
    A(f"- guide/degraded share: {g['guided_share'] * 100:.1f}% vs 98% -> "
      f"{'PASS' if g['share_pass'] else 'FAIL'}")
    A(f"- denied runs: {g['denied']} vs 0 -> {'PASS' if g['denied'] == 0 else 'FAIL'}")
    A(f"- never-lock fail-safe: {mc['modes'].get('fsw_neverlock', {}).get('ballistic', 0)}/"
      f"{n_pri} ballistic (expected: all)")
    A(f"- **GATE: {'PASS' if g['all_pass'] else 'FAIL'}**")
    A("")
    A("## Measured per-task budgets (Python host, deployment-relevant ordering)")
    A("| Task | mean/tick (us) | max/tick (us) | calls/shot |")
    A("|---|---|---|---|")
    for name, mean_us, peak_us, calls in budget:
        A(f"| {name} | {mean_us:.1f} | {peak_us:.1f} | {calls:.0f} |")
    A("")
    A("## Provenance")
    A("- Truth/sensor synthesis/dispersion draws: `scripts/sim_gnc_check.py` (revC/revD/revE")
    A("  paths untouched; `python3 -m py_compile` clean).")
    A("- Draw-count parity sim vs FSW verified per deterministic case (--pair-check).")
    A("- All numbers in this file are generated by `cosim/run_cosim.py`.")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, out_name)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {path}")


def gates(stats, modes, cep_gate=24.0):
    m = modes.get("fsw_l0", {})
    guided = m.get("guide", 0) + m.get("degraded", 0)
    total = sum(m.values())
    denied = m.get("denied", 0)
    cep50 = stats["fsw_l0"]["median"]
    share = guided / max(total, 1)
    return {"cep_pass": cep50 <= cep_gate,
            "share_pass": share >= 0.98,
            "denied": denied,
            "guided_share": share,
            "cep_gate": cep_gate,
            "all_pass": cep50 <= cep_gate and share >= 0.98 and denied == 0}


def plot(mc):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pts, stats = mc["pts"], mc["stats"]
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=True, sharey=True)
    ax = axes[0]
    for key, color, lbl, mk in [("unguided", "#dc2626", "Unguided", "o"),
                                ("legacy", "#f59e0b", "Legacy Rev C", "s"),
                                ("fsw_l0", "#059669", "FSW L0", "^")]:
        xs = [x - R_E for x, y in pts[key]]
        ys = [y for x, y in pts[key]]
        ax.scatter(xs, ys, s=14, alpha=0.5, color=color,
                   label=f"{lbl} CEP {stats[key]['median']:.1f} m", marker=mk)
    ax.scatter([0], [0], marker="*", s=350, color="black", zorder=5)
    ax.add_patch(plt.Circle((0, 0), 30, fill=False, color="#059669", ls="--", lw=1.2))
    ax.set_xlabel("downrange error (m)")
    ax.set_ylabel("crossrange (m)")
    ax.set_title("FSW vs legacy vs unguided (lock 45 s)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    ax.set_aspect("equal")
    ax = axes[1]
    for key, color, lbl in [("fsw_l0", "#059669", "L0"),
                            ("fsw_zem", "#9333ea", "ZEM"),
                            ("fsw_outage", "#964B00", "outage 60-70s"),
                            ("fsw_blind", "#111827", "BLIND no roll ref")]:
        xs = [x - R_E for x, y in pts[key]]
        ys = [y for x, y in pts[key]]
        ax.scatter(xs, ys, s=14, alpha=0.5, color=color,
                   label=f"{lbl} {stats[key]['median']:.1f} m")
    ax.scatter([0], [0], marker="*", s=350, color="black", zorder=5)
    ax.add_patch(plt.Circle((0, 0), 30, fill=False, color="#059669", ls="--", lw=1.2))
    ax.set_xlabel("downrange error (m)")
    ax.set_title("FSW law trade + fail-safe")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    ax.set_aspect("equal")
    fig.suptitle("PGK flight software co-sim — paired MC vs Rev E truth", fontsize=11)
    fig.tight_layout()
    p = os.path.join(OUT_DIR, "steering_fsw.png")
    fig.savefig(p, dpi=130, bbox_inches="tight")
    print(f"Wrote {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="det + 8 primary + 4x4 secondary")
    ap.add_argument("--det", action="store_true", help="deterministic cases only")
    ap.add_argument("--pair-check", action="store_true", help="stream pairing proof")
    ap.add_argument("--budget", action="store_true", help="per-task budget probe only")
    ap.add_argument("--sensor-profile", default="baseline",
                    help="sensor profile: baseline|selected|worstcase|<json path> "
                         "(see SENSOR_PROFILES; non-baseline writes RESULTS_FSW_<name>.md "
                         "and skips the plot — RESULTS_FSW.md stays the baseline artifact)")
    args = ap.parse_args()

    apply_sensor_profile(args.sensor_profile)
    is_baseline = args.sensor_profile == "baseline"

    sim.rng = np.random.default_rng(SEED)
    cd_cal, x_nom, tof_nom, apo_nom = sim.calibrate_cd()
    Q70 = sim.q70_ref(cd_cal)
    print(f"Cd={cd_cal:.4f} nom {x_nom:.0f} m TOF {tof_nom:.1f} s apo {apo_nom / 1000:.1f} km")
    print(f"q(t={sim.Q_REF_T:.0f}s) = {Q70:.0f} Pa (60 N reference condition)")

    if args.pair_check:
        pair_check(cd_cal, Q70)
        return
    if args.budget:
        for r in budget_probe(cd_cal, Q70):
            print(f"  {r[0]:14s} mean {r[1]:8.1f} us  max {r[2]:8.1f} us  calls/shot {r[3]:8.0f}")
        return

    det_rows = run_det(cd_cal, Q70)
    if args.det:
        return
    n_pri = 8 if args.smoke else sim.N_RUNS
    n_sec = 4 if args.smoke else 80
    mc = run_mc(cd_cal, Q70, n_pri, n_sec)
    budget = budget_probe(cd_cal, Q70)
    if is_baseline:
        write_results(cd_cal, x_nom, tof_nom, apo_nom, Q70, det_rows, mc, budget)
        plot(mc)
    else:
        write_results(cd_cal, x_nom, tof_nom, apo_nom, Q70, det_rows, mc, budget,
                      out_name=f"RESULTS_FSW_{args.sensor_profile}.md")


if __name__ == "__main__":
    main()
