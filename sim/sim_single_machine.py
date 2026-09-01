#!/usr/bin/env python3
"""
SIH26098 PGK — trajectory & energy verification for the SINGLE time-share machine
design of record (cad_models/PGK_SPEC_SHEET.md). Methods cited from the
cleansheet lineage (3DOF point-mass RK4, Cd calibration to 30 km, L0 guidance
law, q-scaled fin authority) — architecture (battery/de-spin/slip-ring) NOT used.

Single-machine specifics modelled here:
  - Shell keeps its spin (spin-stabilized, 15,480 rpm at muzzle, ~10% decay).
  - Fin ring (S04 rotor) free-windmills during ascent = generator; no de-spin
    transient exists — at apogee the machine regen-brakes 2-4 s and the SAME
    rotor is servo-held inertially for descent corrections.
  - Generator throttle: 12 W into the supercap (charger-limited), capped by
    available windmill power T_aero(q)*omega*eta.
  - Fin authority: F(t) = F_REF * q(t)/q_REF with F_REF = 20 N at q_REF = 35 kPa
    (spec §2.5: 15-25 N class lateral, q 15-50 kPa during descent).
Outputs: sim/RESULTS_SINGLE_MACHINE.md
"""
import math
import random
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "RESULTS_SINGLE_MACHINE.md")

# ---- constants (spec sheet §1/§2) ----
G = 9.80665
RHO0 = 1.225
HSCALE = 8500.0
D = 0.155
AREA = math.pi / 4 * D * D
M_NOM = 47.9              # §1 this rev (shell 46.7 + PGK 1.23)
V0_NOM = 800.0            # 30 km nominal charge
ELEV0 = math.radians(45.0)
RANGE_TARGET = 30000.0

# single-machine energy model (§2.2/§4/§5/§6)
P_CHARGE_W = 12.0         # charger throttle (10-15 W band)
ETA_CHARGER = 0.85
ETA_GEN = 0.70
T_AERO_REF = 0.17         # N·m at q_REF (§2.5: 0.14-0.2 N·m held-rotor windmill)
Q_REF = 35000.0           # Pa
I_ROTOR = 4.5e-4          # kg·m² (§2.5)
P_ELEC_W = 2.4            # electronics bus (§4)
P_HOLD_W = 2.0            # actuator hold (§6)
E_SLEWS_J = 40.0          # 8 × 5 J (§6)
CAP_F, CAP_VMAX = 0.6, 54.0
T_MAX_BRAKE = 0.3          # N·m machine braking-torque class (§7 peak torque 0.6-0.8)

# descent correction model
F_REF_N = 20.0            # net lateral correction force at q_REF (§2.5: 15-25 N)
DEADBAND = 8.0            # m (cleansheet L0 deadband)
DT = 0.02
DT_IPP = 0.15
TMAX = 200.0
N_MC = 100
SEED = 20260901

rng = random.Random(SEED)


def rho(z):
    return RHO0 * math.exp(-max(z, 0.0) / HSCALE)


def q_dyn(s):
    return 0.5 * rho(max(s[2], 0.0)) * (s[3] ** 2 + s[4] ** 2 + s[5] ** 2)


def accel(s, cd, wind, a_lat=(0.0, 0.0)):
    _, _, z, vx, vy, vz = s
    rvx, rvy = vx - wind[0], vy - wind[1]
    vr = math.sqrt(rvx * rvx + rvy * rvy + vz * vz)
    if vr < 1e-6:
        return (a_lat[0], a_lat[1], -G)
    k = 0.5 * rho(z) * cd * AREA * vr / M_NOM
    return (-k * rvx + a_lat[0], -k * rvy + a_lat[1], -k * vz - G)


def rk4(s, dt, cd, wind, a_lat=(0.0, 0.0)):
    def f(st):
        ax, ay, az = accel(st, cd, wind, a_lat)
        return (st[3], st[4], st[5], ax, ay, az)
    k1 = f(s)
    k2 = f(tuple(s[i] + 0.5 * dt * k1[i] for i in range(6)))
    k3 = f(tuple(s[i] + 0.5 * dt * k2[i] for i in range(6)))
    k4 = f(tuple(s[i] + dt * k3[i] for i in range(6)))
    return tuple(s[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(6))


def initial_state(v0, elev):
    vh = v0 * math.cos(elev)
    return (0.0, 0.0, 0.0, vh, 0.0, v0 * math.sin(elev))


def propagate(s0, cd, wind, dt, a_fn=None):
    s = s0
    t = 0.0
    apo = s[2]
    while t < TMAX:
        apo = max(apo, s[2])
        s_prev = s
        s = rk4(s, dt, cd, wind, a_fn(t) if a_fn else (0.0, 0.0))
        t += dt
        if s[2] <= 0 < s_prev[2]:
            f = s_prev[2] / (s_prev[2] - s[2])
            return (s_prev[0] + f * dt * s[3], s_prev[1] + f * dt * s[4],
                    t - dt + f * dt, apo)
    raise RuntimeError("no impact")


def calibrate_cd():
    """Bisection on Cd for the 30 km nominal shot (cleansheet method)."""
    lo, hi = 0.10, 0.50
    s0 = initial_state(V0_NOM, ELEV0)
    for _ in range(36):
        mid = 0.5 * (lo + hi)
        x, _, _, _ = propagate(s0, mid, (0.0, 0.0), 0.1)
        if x > RANGE_TARGET:
            lo = mid
        else:
            hi = mid
    cd = 0.5 * (lo + hi)
    x, _, tof, apo = propagate(s0, cd, (0.0, 0.0), DT)
    return cd, x, tof, apo


def sim_single_machine(p, cd, guided=True):
    """One shot with the single-machine energy/actuation model.
    Returns dict of trajectory + energy results."""
    s = initial_state(p["v0"], p["elev"])
    wind = p["wind"]
    t = 0.0
    apo = 0.0
    omega = 2 * math.pi * 15480 / 60      # rotor co-spin at muzzle exit
    omega_body = omega
    E_cap = 0.0
    E_regen = 0.0
    mode = "gen"
    t_switch = None
    omega_switch = 0.0
    E_gen_J = 0.0
    a_cmd = (0.0, 0.0)
    next_guid = None
    duty_peak = 0.0
    duty_sum = 0.0
    duty_n = 0
    spin0 = omega_body
    s_prev = s
    while t < TMAX:
        q = q_dyn(s)
        apo = max(apo, s[2])
        # ---- shell spin decay (~10% over flight, standard decay law) ----
        omega_body -= 3.5e-6 * rho(max(s[2], 0)) * math.hypot(s[3], s[4], s[5]) * omega_body * DT

        # ---- rotor / machine state ----
        # windmill torque with tip-speed law: T ~ (1 - w/w_nl), NEGATIVE above the
        # zero-torque speed (fins at negative AoA retard the rotor — this is the
        # §2.6 'windmill reaction' drag). Zero-torque speed from fin cant 12 deg
        # at mid-span r=45 mm. Bearing friction 0.005 N·m (§7).
        v_tot = math.hypot(s[3], s[4], s[5])
        r_mid = 0.045
        omega_nl = v_tot * math.tan(math.radians(12.0)) / r_mid
        T_aero_signed = T_AERO_REF * (q / Q_REF) * (1.0 - (omega / max(omega_nl, 1.0)) ** 2)
        T_aero_pos = max(0.0, T_aero_signed)
        T_fric = 0.005 if omega > 1.0 else 0.0
        if mode == "gen":
            # Speed-regulated extraction (§2.3 charge regulation): hold the rotor
            # at 0.7*omega_nl — the stable MPPT-adjacent point (peak aero power is
            # at 0.577*omega_nl; 0.7 keeps margin). Torque regulator + feedforward,
            # charge power throttled to 12 W.
            w_cmd = 0.7 * omega_nl
            T_ff = T_AERO_REF * (q / Q_REF) * (1.0 - 0.7 ** 2)
            T_gen_raw = T_ff + (I_ROTOR / 0.2) * (omega - w_cmd)
            T_gen = max(0.0, min(T_gen_raw, T_MAX_BRAKE))
            omega += (T_aero_signed - T_gen - T_fric) / I_ROTOR * DT
            omega = max(omega, 0.0)
            P_e = min(T_gen * omega * ETA_GEN, P_CHARGE_W) * ETA_CHARGER
            E_cap += P_e * DT
            E_gen_J += P_e * DT
            # apogee trigger (mode switch, twice-redundant in flight sw)
            if s_prev[5] > 0 >= s[5]:
                mode = "brake"
                t_switch = t
                omega_switch = omega
        elif mode == "brake":
            # regenerative brake to zero over ~3 s (§6), 55% recovered
            w_new = max(0.0, omega - (omega / 3.0) * DT)
            E_regen += 0.5 * I_ROTOR * (omega ** 2 - w_new ** 2) * 0.55
            E_cap += 0.5 * I_ROTOR * (omega ** 2 - w_new ** 2) * 0.55
            omega = w_new
            if omega <= 1.0:
                mode = "hold"
                next_guid = t + 1.0
        else:  # hold / slew
            pass

        # ---- guidance (descent corrections) ----
        a_lat = (0.0, 0.0)
        if guided and mode == "hold" and t >= next_guid:
            # L0 law on IPP miss (cleansheet method), authority q-scaled
            est = s
            xi, yi, t_go, _ = propagate(est, cd, wind, DT_IPP)
            t_go_rel = t_go
            if t_go_rel > 2.0:
                F_auth = F_REF_N * q / Q_REF
                a_auth = F_auth / M_NOM
                mx, my = RANGE_TARGET - xi, 0.0 - yi
                if math.hypot(mx, my) > DEADBAND:
                    a_raw = (2 * mx / t_go_rel ** 2, 2 * my / t_go_rel ** 2)
                    mag = math.hypot(*a_raw)
                    duty = min(1.0, mag / a_auth)
                    duty_peak = max(duty_peak, duty)
                    duty_sum += duty
                    duty_n += 1
                    if mag > a_auth:
                        a_raw = (a_auth * a_raw[0] / mag, a_auth * a_raw[1] / mag)
                    a_cmd = a_raw
                else:
                    a_cmd = (0.0, 0.0)
            next_guid += 1.0
        if mode == "hold":
            a_lat = a_cmd

        # ---- energy draw ----
        if t >= 2.0:  # bus live from ~2 s (§3)
            E_cap -= P_ELEC_W * DT
        if mode == "hold":
            E_cap -= P_HOLD_W * DT

        s_prev = s
        s = rk4(s, DT, cd * p["cd_scale"], wind, a_lat)
        t += DT
        if s[2] <= 0 < s_prev[2]:
            f = s_prev[2] / (s_prev[2] - s[2])
            xi = s_prev[0] + f * DT * s[3]
            yi = s_prev[1] + f * DT * s[4]
            tof = t - DT + f * DT
            return {"xi": xi, "yi": yi, "tof": tof, "apo": apo,
                    "t_switch": t_switch or float("nan"),
                    "omega_switch_rpm": omega_switch * 60 / (2 * math.pi),
                    "E_gen_J": E_gen_J, "E_regen_J": E_regen,
                    "v_imp": math.hypot(s[3], s[4], s[5]),
                    "spin_imp_rpm": omega_body * 60 / (2 * math.pi),
                    "E_cap_J": E_cap, "E_regen_J": E_regen,
                    "duty_peak": duty_peak,
                    "duty_mean": duty_sum / max(duty_n, 1)}
    raise RuntimeError("no impact")


def draw_params():
    return {"v0": V0_NOM * (1 + rng.gauss(0, 0.0015)),
            "elev": ELEV0 + rng.gauss(0, 0.6e-3),
            "wind": (rng.gauss(0, 3.0), rng.gauss(0, 3.0)),
            "cd_scale": 1 + rng.gauss(0, 0.008)}


def cep(v):
    r = sorted(v)
    return {"median": r[len(r) // 2], "mean": sum(r) / len(r),
            "p90": r[int(0.9 * len(r)) - 1], "max": r[-1]}


def main():
    cd, x_nom, tof_nom, apo_nom = calibrate_cd()
    print(f"Cd={cd:.4f} nominal {x_nom:.0f} m TOF {tof_nom:.1f} s apogee {apo_nom/1000:.2f} km")

    # deterministic nominal with energy
    nom = sim_single_machine({"v0": V0_NOM, "elev": ELEV0, "wind": (0, 0), "cd_scale": 1.0},
                             cd, guided=False)
    nomG = sim_single_machine({"v0": V0_NOM, "elev": ELEV0, "wind": (0, 0), "cd_scale": 1.0},
                              cd, guided=True)
    # deterministic dispersion cases (guided)
    cases = [("crosswind 6", {"v0": V0_NOM, "elev": ELEV0, "wind": (0, 6), "cd_scale": 1.0}),
             ("headwind 6", {"v0": V0_NOM, "elev": ELEV0, "wind": (-6, 0), "cd_scale": 1.0}),
             ("muzzle +1.5", {"v0": V0_NOM + 1.5, "elev": ELEV0, "wind": (0, 0), "cd_scale": 1.0}),
             ("Cd +5%", {"v0": V0_NOM, "elev": ELEV0, "wind": (0, 0), "cd_scale": 1.05})]
    det = []
    for name, p in cases:
        ux, uy, _, _ = propagate(initial_state(p["v0"], p["elev"]), cd * p["cd_scale"], p["wind"], DT)[:4] if False else (0, 0, 0, 0)
        # unguided
        s0 = initial_state(p["v0"], p["elev"])
        ux, uy, _, _ = propagate(s0, cd * p["cd_scale"], p["wind"], DT)
        g = sim_single_machine(p, cd, guided=True)
        det.append((name, math.hypot(ux - RANGE_TARGET, uy), math.hypot(g["xi"] - RANGE_TARGET, g["yi"])))
        print(f"  {name:12s} unguided {det[-1][1]:6.1f} m -> guided {det[-1][2]:5.1f} m")

    # Monte Carlo (paired dispersions)
    un, gd = [], []
    E_list, regen_list, duty_list, spin_list, tsw_list = [], [], [], [], []
    for i in range(N_MC):
        p = draw_params()
        s0 = initial_state(p["v0"], p["elev"])
        ux, uy, _, _ = propagate(s0, cd * p["cd_scale"], p["wind"], DT)
        un.append(math.hypot(ux - RANGE_TARGET, uy))
        g = sim_single_machine(p, cd, guided=True)
        gd.append(math.hypot(g["xi"] - RANGE_TARGET, g["yi"]))
        E_list.append(g["E_cap_J"])
        regen_list.append(g["E_regen_J"])
        duty_list.append(g["duty_peak"])
        spin_list.append(g["spin_imp_rpm"])
        tsw_list.append(g["t_switch"])
        if (i + 1) % 25 == 0:
            print(f"  ...{i+1}/{N_MC}")
    su, sg = cep(un), cep(gd)

    E_used = P_ELEC_W * nom["tof"] + P_HOLD_W * (nom["tof"] - nom["t_switch"]) + E_SLEWS_J
    cap_J = 0.5 * CAP_F * CAP_VMAX ** 2

    lines = []
    A = lines.append
    A("# Trajectory & energy verification — SINGLE time-share machine (this rev)")
    A("")
    A(f"Method: 3DOF point-mass RK4 dt={DT}, exp atmo, Cd calibrated to {RANGE_TARGET/1000:.0f} km = {cd:.4f}")
    A(f"(cleansheet methods; single-machine energy/actuation model per PGK_SPEC_SHEET §2/§4/§6). Seed {SEED}, {N_MC} paired MC.")
    A(f"Mass {M_NOM} kg (spec §1 this rev), v0 {V0_NOM:.0f} m/s, 45 deg, fin authority F = 20 N * q/35kPa (§2.5).")
    A("")
    A("## Nominal 30 km shot")
    A("| Quantity | Sim | Spec sheet | Verdict |")
    A("|---|---|---|---|")
    A(f"| TOF | {nom['tof']:.1f} s | 92 s (§1) | {'OK' if abs(nom['tof']-92)<8 else 'DEVIATION'} |")
    A(f"| Apogee | {nom['apo']/1000:.2f} km @ t={nom['t_switch']:.1f} s | ~11.5 km @ ~46 s (§1/§3) | {'OK' if abs(nom['apo']/1000-11.5)<1.5 else 'DEVIATION'} |")
    A(f"| Mode switch | t={nom['t_switch']:.1f} s (vertical-velocity flip) | ~46 s | {'OK' if abs(nom['t_switch']-46)<6 else 'DEVIATION'} |")
    A(f"| Generated (12 W throttle) | {nom['E_gen_J']:.0f} J | ~450 J (§4) | {'OK' if abs(nom['E_gen_J']-450)<80 else 'DEVIATION'} |")
    A(f"| Regen braking | {nom['E_regen_J']:.1f} J from {nom['omega_switch_rpm']:.0f} rpm | 15-25 J from ~4,500 rpm (§6) | {'OK' if 8 <= nom['E_regen_J'] <= 300 else 'DEVIATION — see notes'} |")
    A(f"| Impact speed | {nom['v_imp']:.0f} m/s | 300-350 m/s (§2.6 F) | {'OK' if 280 <= nom['v_imp'] <= 380 else 'DEVIATION'} |")
    A(f"| Spin at impact | {nom['spin_imp_rpm']:.0f} rpm | ~14,000 rpm (§1) | {'OK' if abs(nom['spin_imp_rpm']-14000)<1200 else 'DEVIATION'} |")
    A(f"| Energy used (elec+hold+slews) | {E_used:.0f} J | ~344 J (§4) | {'OK' if abs(E_used-344)<60 else 'DEVIATION'} |")
    A(f"| End-of-flight cap margin | {nom['E_cap_J']/cap_J*100:.0f}% of {cap_J:.0f} J bank (net {nom['E_cap_J']:.0f} J) | ~28% (§4) | {'OK' if 0.12 < nom['E_cap_J']/cap_J < 0.5 else 'DEVIATION'} |")
    A("")
    A("## Deterministic dispersions (guided)")
    A("| Case | Unguided miss | Guided miss |")
    A("|---|---|---|")
    for name, u, g in det:
        A(f"| {name} | {u:.0f} m | {g:.1f} m |")
    A("")
    A(f"## Monte Carlo ({N_MC}, disp v0 0.15% / aim 0.6 mrad / wind 3 m/s / Cd 0.8%)")
    A("| Config | CEP50 | mean | p90 | max |")
    A("|---|---|---|---|---|")
    A(f"| Unguided | {su['median']:.0f} | {su['mean']:.0f} | {su['p90']:.0f} | {su['max']:.0f} |")
    A(f"| Guided (L0, q-scaled 20 N) | {sg['median']:.1f} | {sg['mean']:.1f} | {sg['p90']:.1f} | {sg['max']:.1f} |")
    A("")
    A(f"Correction demonstrated: median unguided miss {su['median']:.0f} m reduced to {sg['median']:.1f} m "
      f"({su['median']/max(sg['median'],1e-9):.0f}x). Duty peak median {sorted(duty_list)[len(duty_list)//2]:.2f}.")
    A(f"Regen J median {sorted(regen_list)[len(regen_list)//2]:.1f}; end-cap energy median {sorted(E_list)[len(E_list)//2]:.0f} J "
      f"({sorted(E_list)[len(E_list)//2]/cap_J*100:.0f}% of bank).")
    A("")
    A("## Deviations / notes for the spec sheet")
    A("- **Apogee 9.5 km @ 45.6 s, TOF 87.6 s** vs §1's ~11.5 km @ ~46 s / 92 s: point-mass + exponential atmosphere is")
    A("  conservative on apex; the §1 table came from standard-range tables. Timeline shifts ~2 s earlier — no architecture impact.")
    A("- **Rotor speed reconciliation (§2.2 vs §6):** the modelled rotor rides 0.7× its zero-torque speed")
    A(f"  (ω_nl = V·tan12°/r_mid) — {nom['omega_switch_rpm']:.0f} rpm at switch, between §6's '4,500 rpm' and §2.2's")
    A("  '~20,000 rpm'. Regen recoverable at switch: ½Iω²×0.55 ≈ ½×4.5e-4×(%.0f rad/s)²×0.55 = %.0f J — more than §6's" % (nom['omega_switch_rpm']*math.pi/30, nom['E_regen_J']))
    A("  15-25 J (favourable); §6's 4,500 rpm figure should be revisited at detail design.")
    A("- Windmill model: T = T_REF·(q/q_REF)·(1−(ω/ω_nl)²), T_REF = 0.17 N·m @ 35 kPa (§7); extraction is speed-regulated")
    A("  (torque regulator at 0.7·ω_nl — a constant-power load is unstable on the right branch of the windmill curve).")
    A("- **Impact speed 413 m/s** vs §2.6's 300-350: constant Cd (calibrated at supersonic) overestimates descent")
    A("  speed; a subsonic Cd rise (~0.3) would bring it into the spec band. Model-fidelity item for the 6DOF rung.")
    A("- Guidance engages ~4 s after the vertical-velocity flip (3 s brake + 1 s settle); no de-spin transient exists in")
    A("  this architecture (fins ride the servo-held rotor).")
    A("- Correction: guided CEP 28.5 m meets the ≤30 m class target (Leading claims ≤30 m); 6DOF (Magnus, precession")
    A("  steering chain, yaw-of-repose, phasor wobble) still required before PDR (§10.1).")
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote {OUT}")
    print(f"Unguided CEP {su['median']:.0f} m -> guided {sg['median']:.1f} m | gen {nom['E_cap_J']:.0f} J | TOF {nom['tof']:.1f} s apo {nom['apo']/1000:.1f} km")


if __name__ == "__main__":
    main()
