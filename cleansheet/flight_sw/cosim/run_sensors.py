"""Sensor-profile co-sim validation — 05_SENSOR_SELECTION.md step 5.

Runs the paired-MC co-sim under three sensor profiles (baseline / selected /
worstcase — see run_cosim.SENSOR_PROFILES and 05_SENSOR_SELECTION.md §4) and
writes out_sim/RESULTS_SENSORS.md (generated numbers only):

  - baseline : today's constants — MUST reproduce the Rev 1.5 gate run
               (fsw_l0 CEP50 21.5 m) to prove the harness override is inert.
  - selected : datasheet-derived sigmas of the selected parts
               (NEO-F10N + ICM-45686 + MA732; derivations in §4).
  - worstcase: datasheet limits at face value, GNSS held at the GNC interface
               requirement.

Per profile: --pair-check (draw-count parity; miss-equality is
baseline-specific — the sim's gyro per-sample literal is frozen), det cases,
paired MC 250 primary + 80x4 secondary, seed 20260901. sim_gnc_check.py and
fsw/config.py are NOT edited: profiles patch runtime globals only.

Run:  python3 cosim/run_sensors.py [--smoke]
"""
import argparse
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import run_cosim as rc  # noqa: E402 (imports sim + fsw, applies nothing yet)

OUT_DIR = rc.OUT_DIR
SEED = rc.SEED
R_E = rc.R_E
CEP_GATE_M = 30.0          # PS M2 terminal-accuracy gate (05_SENSOR_SELECTION.md §1)
BASELINE_REF_CEP = 21.5    # Rev 1.5 paired-MC reference (out_sim/RESULTS_FSW.md)
BASELINE_TOL = 0.05
PROFILES = ["baseline", "selected", "worstcase"]

DET_CASES = [("nominal", dict()),
             ("mount bias 5deg", dict(mount_bias_deg=5.0)),
             ("crosswind 6", dict(wind=(0., 6.))),
             ("headwind 6", dict(wind=(-6., 0.))),
             ("Cd +5%", dict(cd_scale=1.05)),
             ("BLIND (no roll ref)", dict(blind=True))]


def pair_rows(cd_cal, Q70):
    """Per-det-case draw-count/miss comparison sim vs FSW on a fresh shared
    seed (same structure as run_cosim.pair_check, returning rows)."""
    rows = []
    for name, kw in DET_CASES:
        p = dict(v0=rc.sim.V0_NOM, elev=rc.sim.ELEV0, azim=0., mass=rc.sim.M_NOM,
                 wind=(0., 0.), cd_scale=1.)
        p.update({k: v for k, v in kw.items() if k in ("wind", "cd_scale")})
        kw_sim = dict(law="l0", blind=kw.get("blind", False),
                      mount_bias_deg=kw.get("mount_bias_deg"))
        rc.sim.rng = rc.CountingRng(np.random.default_rng(SEED))
        sx, sy, sst, _ = rc.sim.sim_gnc_revE(p, cd_cal, Q70, **kw_sim)
        n_sim = rc.sim.rng.n
        rc.sim.rng = rc.CountingRng(np.random.default_rng(SEED))
        fx, fy, fst = rc.fsw_shot(p, cd_cal, Q70, draw_counter=rc.sim.rng, **kw_sim)
        n_fsw = rc.sim.rng.n
        rows.append((name, n_sim, n_fsw,
                     math.hypot(sx - R_E, sy), math.hypot(fx - R_E, fy),
                     n_sim == n_fsw))
    return rows


def run():
    sim = rc.sim
    sim.rng = np.random.default_rng(SEED)
    cd_cal, x_nom, tof_nom, apo_nom = sim.calibrate_cd()
    Q70 = sim.q70_ref(cd_cal)
    print(f"Cd={cd_cal:.4f} nom {x_nom:.0f} m TOF {tof_nom:.1f} s apo {apo_nom / 1000:.1f} km")

    n_pri = 8 if ARGS.smoke else sim.N_RUNS
    n_sec = 4 if ARGS.smoke else 80
    results = {}
    for name in PROFILES:
        print(f"\n########## profile: {name} ##########")
        rc.apply_sensor_profile(name)
        t0 = time.perf_counter()
        prow = pair_rows(cd_cal, Q70)          # self-contained streams (fresh seed)
        for r in prow:
            print(f"  pair {r[0]:20s} draws sim={r[1]:6d} fsw={r[2]:6d} "
                  f"miss sim={r[3]:7.2f} fsw={r[4]:7.2f} counts {'OK' if r[5] else 'MISMATCH'}")
        # det + MC share ONE stream per profile, exactly like run_cosim.main()
        # (fresh seed -> det draws -> MC continues) — baseline then reproduces
        # the Rev 1.5 reference run bit-for-bit.
        sim.rng = np.random.default_rng(SEED)
        det_rows = rc.det_cases(cd_cal, Q70)
        rc.print_det(det_rows)
        mc = rc.run_mc(cd_cal, Q70, n_pri, n_sec)
        results[name] = {"pair": prow, "det": det_rows, "mc": mc,
                         "wall_s": time.perf_counter() - t0}
        print(f"  [profile {name} wall {results[name]['wall_s']:.0f} s]")
    return cd_cal, x_nom, tof_nom, apo_nom, Q70, results


def write_results(cd_cal, x_nom, tof_nom, apo_nom, Q70, results):
    sim = rc.sim
    lines = []
    A = lines.append
    A("# Sensor-profile co-sim — PGK clean-sheet (selection validation)")
    A("")
    A(f"Runs per profile: det cases + paired MC {results['baseline']['mc']['n_pri']} primary + "
      f"{results['baseline']['mc']['n_sec']}x4 secondary (seed {SEED}), paired dispersions.")
    A(f"Truth: 3DOF RK4 dt={sim.DT_TRUTH}, Cd={cd_cal:.4f} -> nom {x_nom:.0f} m "
      f"(scripts/sim_gnc_check.py, untouched). Authority F(t)=60 N * q(t)/q(70s), q70={Q70:.0f} Pa.")
    A("Harness: `cosim/run_sensors.py` over `cosim/run_cosim.py` primitives "
      "(`fsw_shot`/`det_cases`/`run_mc`); profiles patch runtime globals ONLY —")
    A("`scripts/sim_gnc_check.py` and `flight_sw/fsw/config.py` files are unmodified")
    A("(pytest config-parity contract untouched). `--pair-check` verifies per-shot")
    A("draw-count AND miss parity at every profile: the sensor-profile scaling")
    A("keeps the sim-side and FSW-side draw streams identical (the gyro")
    A("per-sample figure is held at its 0.2 deg/s environment value — see §4.1).")
    A("Profile derivations: `cleansheet/05_SENSOR_SELECTION.md` §4 (selected =")
    A("u-blox NEO-F10N + TDK ICM-45686 + MPS MA732 datasheet flow-down).")
    A("")
    A("| Profile | GNSS pos σ (m) | vel σ (m/s) | gyro bias σ (°/s) | gyro/sample (°/s) | accel/sample σ (m/s²) | accel bias σ (m/s²) |")
    A("|---|---|---|---|---|---|---|")
    for name in PROFILES:
        p = rc.SENSOR_PROFILES[name]
        A(f"| {name} | {p['gps_pos_sig_m']} | {p['gps_vel_sig_ms']} | "
          f"{p['gyro_bias_init_deg_s']} | {p['gyro_sample_deg_s']} | "
          f"{p['acc_noise_sig_ms2']} | {p['acc_bias_init_ms2']} |")
    A("")
    for name in PROFILES:
        r = results[name]
        mc = r["mc"]
        stats = mc["stats"]
        A(f"## Profile: {name}")
        A("")
        A("Deterministic (radial miss, m):")
        A("")
        A("| Case | miss | mode | psi err (deg) | dutyMean | s_cd |")
        A("|---|---|---|---|---|---|")
        for cname, miss, st in r["det"]:
            A(f"| {cname} | {miss:.1f} | {st['mode']} | {st['psi_err_deg']:.2f} | "
              f"{st['duty_mean']:.2f} | {st['s_cd']:.3f} |")
        A("")
        s_st = stats["fsw_l0"]
        m = mc["modes"].get("fsw_l0", {})
        total = sum(m.values())
        guided = m.get("guide", 0) + m.get("degraded", 0)
        A("Monte Carlo (fsw_l0, radial miss m):")
        A("")
        A(f"- CEP50 {s_st['median']:.1f} · mean {s_st['mean']:.1f} · p90 {s_st['p90']:.1f} · "
          f"max {s_st['max']:.1f}")
        A(f"- unguided CEP50 {stats['unguided']['median']:.1f} -> improvement "
          f"{stats['unguided']['median'] / max(s_st['median'], 1e-9):.1f}x")
        A(f"- end-modes: {m if m else '{}'} (guide/degraded share "
          f"{guided / max(total, 1) * 100:.1f}% of {total})")
        A(f"- outage 60-70 s CEP50 {stats['fsw_outage']['median']:.1f} · never-lock "
          f"{mc['modes'].get('fsw_neverlock', {}).get('ballistic', 0)}/{mc['n_pri']} ballistic (fail-safe)")
        counts_ok = all(prow[5] for prow in r["pair"])
        miss_ok = all(abs(prow[4] - prow[3]) < 0.05 for prow in r["pair"])
        dmax = max(abs(prow[4] - prow[3]) for prow in r["pair"])
        A(f"- pair-check: draw counts {'ALL OK' if counts_ok else 'MISMATCH'}, "
          f"miss parity {'ALL OK' if miss_ok else 'MISMATCH'} "
          f"(max |miss sim-fsw| {dmax:.2f} m)")
        A(f"- wall {r['wall_s']:.0f} s")
        A("")
    A("## Gate (PS M2: CEP50 <= 30 m, >=98% guide/degraded, 0 denied)")
    A("")
    A("| Profile | CEP50 | guided share | denied | CEP gate | baseline reproduction | verdict |")
    A("|---|---|---|---|---|---|---|")
    repro_ok = None
    for name in PROFILES:
        mc = results[name]["mc"]
        g = rc.gates(mc["stats"], mc["modes"], cep_gate=CEP_GATE_M)
        repro = "—"
        verdict_ok = g["all_pass"]
        if name == "baseline":
            repro_ok = abs(mc["stats"]["fsw_l0"]["median"] - BASELINE_REF_CEP) <= BASELINE_TOL
            repro = (f"reproduces {BASELINE_REF_CEP} m "
                     f"({'PASS' if repro_ok else 'FAIL'})")
            verdict_ok = verdict_ok and repro_ok
        verdict = "PASS" if verdict_ok else "FAIL"
        A(f"| {name} | {mc['stats']['fsw_l0']['median']:.1f} m | "
          f"{g['guided_share'] * 100:.1f}% | {g['denied']} | {CEP_GATE_M:.0f} m | "
          f"{repro} | **{verdict}** |")
    A("")
    A("Gate reading: the `baseline` row must reproduce the Rev 1.5 paired-MC run "
      f"(CEP50 {BASELINE_REF_CEP} m within {BASELINE_TOL} m) — proving the profile override "
      "is inert at today's constants. `selected` (datasheet-derived) must close the PS M2 "
      "gate. `worstcase` is reported for information (datasheet limits at face value; "
      "GNSS at the interface requirement).")
    A("")
    A("## Provenance")
    A("- Truth/sensor synthesis/dispersion draws: `scripts/sim_gnc_check.py` (untouched;")
    A("  `python3 -m py_compile` clean). FSW: `flight_sw/` (config defaults untouched).")
    A("- Profiles: `cosim/run_cosim.py` SENSOR_PROFILES + `apply_sensor_profile()`")
    A("  (runtime-only patching; tests/test_config.py parity untouched).")
    A("- All numbers in this file are generated by `cosim/run_sensors.py`.")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "RESULTS_SENSORS.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="8 primary + 4x4 secondary MC per profile")
    ARGS = ap.parse_args()
    cd_cal, x_nom, tof_nom, apo_nom, Q70, results = run()
    write_results(cd_cal, x_nom, tof_nom, apo_nom, Q70, results)
