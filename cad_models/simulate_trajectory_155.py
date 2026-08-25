# SIH26098 - Full-scale 155 mm trajectory study: ballistic vs PGK-guided
# ---------------------------------------------------------------------------
# 3-DOF point-mass, ISA atmosphere, M107-style Cd(Mach), full-size parameters
# (m=43.2 kg, d=155 mm, v0=684 m/s, m/s inputs). Guided case models M1156-style
# canard lift authority (q-dependent, fade at altitude) with ZEM steering.
# Outputs (out_sim/): two CSVs, Monte-Carlo CEP results, charts (SVG+PNG).
# Run: python3 simulate_trajectory_155.py
# ============================================================================

import os
import math
import json
import csv
import sys

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_sim")

# ---------------------------------------------------- full-scale parameters
MASS     = 43.2        # kg (M107 HE projectile)
DIAM     = 0.155       # m
S_REF    = math.pi * DIAM * DIAM / 4.0
G        = 9.80665
T0_P     = 101325.0    # Pa
LAPSE    = 0.0065      # K/m
RS_AIR   = 287.05
GAMMA    = 1.4

V0       = 684.0       # m/s (M3A1 charge)
QE       = 45.0        # deg quadrant elevation

CLS_CAN  = 0.005       # m^2 -> canard lift-area (CLmax * S_canards)
A_MAX_G  = 3.0         # hard limit, g's
TGUIDE   = 0.1         # s guidance update rate
DGUIDE   = 2.0         # m dead-zone for ZEM
TOF_MAX  = 90.0        # s

# M107-style drag coefficient vs Mach (smoothed public-domain model)
MACH_TAB = np.array([0.50, 0.80, 0.90, 0.95, 1.00, 1.05, 1.10, 1.20,
                     1.35, 1.50, 1.70, 2.00, 2.50, 3.00])
CD_TAB   = np.array([0.095, 0.111, 0.122, 0.160, 0.310, 0.360, 0.340, 0.235,
                     0.200, 0.173, 0.160, 0.148, 0.143, 0.137])


def density_alt(z):
    z = max(z, 0.0)
    if z < 11000.0:
        T = 288.15 - LAPSE * z
        p = T0_P * (T / 288.15) ** (G / (LAPSE * RS_AIR))
    else:
        T = 216.65
        p = 22632.06 * math.exp(-G * (z - 11000.0) / (RS_AIR * T))
    return p / (RS_AIR * T), T


def cd_mach(m):
    return float(np.interp(m, MACH_TAB, CD_TAB))


def aero_accel(v, w):
    rel = v - w
    sv = np.linalg.norm(rel)
    if sv < 1e-9:
        return np.zeros(3), 0.0
    rho, _ = density_alt(v[2])
    q = 0.5 * rho * sv * sv
    cd = cd_mach(sv / math.sqrt(GAMMA * RS_AIR * 288.15))
    return -0.5 * rho * sv * cd * S_REF * rel / MASS, q


def step_rk4(s, w, dt, accel_cmd=None):
    # s: [x, y, z, vx, vy, vz]
    def deriv(u):
        pos = np.array(u[:3]); vel = np.array(u[3:])
        a, _ = aero_accel(vel + np.array([0.0, 0.0, 0.0]) if False else vel, w)
        a[2] += -G
        ua = accel_cmd(u)
        if ua is not None:
            a += ua
        return np.concatenate([vel, a])

    k1 = deriv(s)
    k2 = deriv(s + dt / 2 * k1)
    k3 = deriv(s + dt / 2 * k2)
    k4 = deriv(s + dt * k3)
    return s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4), w


def fly(s0, w, guided, target_xy=None, collect=False, dt=0.005, gdt=0.02):
    s = np.array(s0, dtype=float)
    data = []
    t = 0.0
    next_guide = gdt

    def cmd_accel(u):
        if not guided:
            return None
        if u[2] <= 0.0:
            return None
        p2, _ = predict_impact(u, w)
        zx, zy = target_xy[0] - p2[0], target_xy[1] - p2[1]
        if math.hypot(zx, zy) < DGUIDE:
            return None
        rho, _ = density_alt(u[2])
        sv = np.linalg.norm(u[3:])
        a_max = min(q * CLS_CAN / MASS for q in [0.5 * rho * sv * sv]) if sv > 1 else 0.0
        a_max = min(max(a_max, 0.0), A_MAX_G * G)
        n = math.hypot(zx, zy)
        # null the horizontal miss residual perpendicular to velocity
        vel_h = np.array([u[3], u[4]])
        vn = math.hypot(vel_h[0], vel_h[1])
        if vn < 1e-6:
            return None
        # command horizontal, perpendicular-ish to velocity, toward miss
        cmd = np.zeros(3)
        fx = gd_dir(vel_h, np.array([zx, zy]))
        cmd[0] = a_max * fx[0]
        cmd[1] = a_max * fx[1]
        return cmd

    while t < TOF_MAX:
        s, _ = step_rk4(s, w, dt, cmd_accel)
        t += dt
        if collect and (t >= next_guide or s[2] <= 0.0):
            data.append((t, s.copy()))
            next_guide = t + 0.1
        if s[2] <= 0.0 and s[5] < 0.0:
            break
    return s, np.array(data)


def gd_dir(v, m):
    # direction of m projected perpendicular to v (unit)
    vm = v[0] * m[0] + v[1] * m[1]
    u = np.array([m[0] - vm / (np.dot(v, v) + 1e-12) * v[0],
                  m[1] - vm / (np.dot(v, v) + 1e-12) * v[1]])
    n = np.hypot(u[0], u[1])
    if n < 1e-9:
        return np.array([1.0, 0.0])
    return u / n


def predict_impact(u, w):
    v = np.array(u, dtype=float)
    cmds = lambda s: None
    while v[2] > 0.0:
        v, _ = step_rk4(v, w, 0.05, cmds)
        if v[2] > 8000.0 and v[5] > 0.0:
            break
    return v[:2], None


def make_scene(qe_deg, v0=V0, wind=(0.0, 0.0)):
    qe = math.radians(qe_deg)
    s0 = [0.0, 0.0, 0.0,
          v0 * math.cos(qe), 0.0, v0 * math.sin(qe)]
    return np.array(s0)


# =================================================================== flight
def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(42)

    wind = np.array([0.0, 7.0, 0.0])

    s0 = make_scene(QE)
    s_bal, _ = fly(s0, wind, False, collect=False)
    tgt = (s_bal[0] - 150.0, s_bal[1] + 85.0)

    s_g, data_g = fly(s0, wind, True, target_xy=tgt, collect=True)
    s_b, data_b = fly(s0, wind, False, collect=True)

    def wcsv(name, rows, header):
        with open(os.path.join(OUT, name), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    wcsv("traj_no_control.csv",
         [[round(r[0], 3), round(r[1][0], 1), round(r[1][1], 1),
           round(r[1][2], 1), round(np.linalg.norm(r[1][3:]), 1)]
          for r in data_b],
         ["t_s", "x_m", "y_m", "z_m", "v_mps"])

    wcsv("traj_with_control.csv",
         [[round(r[0], 3), round(r[1][0], 1), round(r[1][1], 1),
           round(r[1][2], 1), round(np.linalg.norm(r[1][3:]), 1)]
          for r in data_g],
         ["t_s", "x_m", "y_m", "z_m", "v_mps"])

    # ------------------------------------------------------------ Monte Carlo
    N = 300
    def one_shot(guided):
        qe_err = rng.normal(0.0, 0.10)
        v_err = rng.normal(0.0, 0.0035)
        w = np.array([rng.normal(0.0, 4.0), rng.normal(0.0, 4.0), 0.0])
        s0i = make_scene(QE + qe_err, v0=V0 * (1 + v_err))
        s_i, _ = fly(s0i, w, guided, target_xy=tgt if guided else None)
        return s_i[0], s_i[1]

    bal = np.array([one_shot(False) for _ in range(N)])
    gud = np.array([one_shot(True) for _ in range(N)])

    def cep(hits, tgt_xy):
        d = np.hypot(hits[:, 0] - tgt_xy[0], hits[:, 1] - tgt_xy[1])
        return float(np.median(d)), float(np.percentile(d, 50)), float(np.mean(d))

    bcep = cep(bal, tgt)
    gcep = cep(gud, tgt)
    print("MONTE CARLO (N=%d, target=(%.0f, %.0f) m)" % (N, tgt[0], tgt[1]))
    print("  ballistic ballistic-mean CEP : %.1f m   (mean radial %.1f m)"
          % (bcep[0], bcep[2]))
    print("  guided    ballistic-mean CEP : %.1f m   (mean radial %.1f m)"
          % (gcep[0], gcep[2]))
    print("  CEP improvement = %.1f x" % (bcep[0] / gcep[0]))

    res = {
        "units": "SI", "scale": "1:1 full-size",
        "projectile_mass_kg": MASS, "caliber_mm": DIAM * 1000,
        "muzzle_velocity_mps": V0, "quadrant_elevation_deg": QE,
        "wind_mps": wind.tolist(),
        "target_xy_m": list(tgt),
        "impact_ballistic": [round(s_bal[0], 1), round(s_bal[1], 1)],
        "impact_guided": [round(s_g[0], 1), round(s_g[1], 1)],
        "m_carlo_N": N,
        "cep_ballistic_m": round(bcep[2], 1),
        "cep_guided_m": round(gcep[2], 1),
        "cep_ratio_x": round(bcep[2] / gcep[2], 1),
        "canard_lift_area_m2": CLS_CAN,
        "max_canard_accel_g": A_MAX_G,
    }
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=2)

    # ------------------------------------------------------------------ charts
    def svg_chart():
        W, H = 1280, 760
        pl = 70; pr = 30; pt = 40; pb = 60
        def sv(x, x0, x1, px0, px1):
            return px0 + (x - x0) / (x1 - x0) * (px1 - px0)
        def svy(y, y0, y1, py0, py1):
            return py1 - (y - y0) / (y1 - y0) * (py1 - py0)

        els = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d">' % (W, H)]
        els.append('<rect width="100%" height="100%" fill="#fdfdfd"/>')

        panels = [
            ("altitude vs range", "RANGE (m)", "ALTITUDE (m)",
             (data_b, data_g), tgt),
            ("cross-range vs range", "RANGE (m)", "CROSS-RANGE (m)",
             (data_b, data_g), tgt),
        ]

        def draw_panel(px0, py0, px1, py1, title, xlab, ylab, sr, plot_tgt):
            x0 = min(min(s[1][0] for s in d) for d in sr)
            x0 = min(x0, plot_tgt[0] - 220)
            x1 = max(max(s[1][0] for s in d) for d in sr)
            y0 = 0.0
            y1 = max(max(s[1][2] for s in d) for d in sr)
            els.append('<rect x="%d" y="%d" width="%d" height="%d" fill="white" stroke="#999"/>'
                       % (px0, py0, px1 - px0, py1 - py0))
            nx, ny = 8, 4
            for i in range(nx + 1):
                xx = px0 + i * (px1 - px0) / nx
                xv = x0 + i * (x1 - x0) / nx
                els.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#eee"/>' % (xx, py0, xx, py1))
                els.append('<text x="%.1f" y="%d" font-size="11" text-anchor="middle" fill="#555">%d</text>' % (xx, py1 + 16, xv))
            for i in range(ny + 1):
                yy = py0 + i * (py1 - py0) / ny
                yv = y0 + i * (y1 - y0) / ny
                els.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#eee"/>' % (px0, yy, px1, yy))
                els.append('<text x="%d" y="%.1f" font-size="11" text-anchor="end" fill="#555" dominant-baseline="middle">%d</text>' % (px0 - 6, yy, yv))
            els.append('<text x="%d" y="%d" font-size="13" font-weight="bold" fill="#222">%s</text>' % (px0, py0 - 8, title))
            els.append('<text x="%.1f" y="%d" font-size="12" fill="#555" text-anchor="middle">%s</text>' % ((px0 + px1) / 2, py1 + 40, xlab))
            els.append('<text x="14" y="%.1f" font-size="12" fill="#555" text-anchor="middle" transform="rotate(-90 14 %f)" dominant-baseline="middle">%s</text>' % ((py0 + py1) / 2, (py0 + py1) / 2, ylab))

            if plot_tgt is not None:
                tx = sv(plot_tgt[0], x0, x1, px0, px1)
                els.append('<circle cx="%.1f" cy="%.1f" r="7" fill="none" stroke="#000" stroke-width="2"/>' % (tx, py1))
                els.append('<text x="%.1f" y="%d" font-size="11" fill="#000" text-anchor="middle">TARGET</text>' % (tx, py1 + 30))

            for srset, col, lab in ((sr[0] if isinstance(sr, tuple) else None, None, None),) if False else (
                    (sr[0], "#c0392b", "NO CONTROL"),
                    (sr[1], "#2980b9", "WITH CONTROL")):
                pts = " ".join("%.1f,%.1f" % (sv(s[1][0], x0, x1, px0, px1), svy(s[1][2], y0, y1, py0, py1)) for s in col_set(srset))
                els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, col))
                els.append('<text x="%d" y="%d" font-size="12" fill="%s">%s</text>' % (px1 - 190, py0 + 15 + (30 if lab == "WITH CONTROL" else 0), col, lab))
            return x0, x1, y0, y1

        def col_set(srset):
            return srset

        # altitude panel
        px0, py0, px1, py1 = pl, pt + 20, W - pr - 460, pt + 340
        x0, x1, y0, y1 = draw_panel(px0, py0, px1, py1, "A. Flight profile (range vs altitude)",
                                    "RANGE (m)", "ALTITUDE (m)", (data_b, data_g), tgt)
        # cross range panel (draw again with y = cross)
        px0b, py0b, px1b, py1b = pl, py1 + 40, W - pr - 460, py1 + 360
        xb0 = min(min(r[1][0] for r in d) for d in (data_b, data_g))
        xb1 = max(max(r[1][0] for r in d) for d in (data_b, data_g))
        yb0, yb1 = -40, 40
        els.append('<rect x="%d" y="%d" width="%d" height="%d" fill="white" stroke="#999"/>' % (px0b, py0b, px1b - px0b, py1b - py0b))
        for srset, col in ((data_b, "#c0392b"), (data_g, "#2980b9")):
            pts = " ".join("%.1f,%.1f" % (
                sv(r[1][0], xb0, xb1, px0b, px1b), svy(r[1][1], yb0, yb1, py0b, py1b))
                for r in srset)
            els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, col))
        els.append('<text x="%d" y="%d" font-size="13" font-weight="bold" fill="#222">B. Cross-range drift correction</text>' % (px0b, py0b - 8))
        for i in range(9):
            yy = py0b + i * (py1b - py0b) / 8
            yv = yb0 + i * (yb1 - yb0) / 8
            els.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#eee"/>' % (px0b, yy, px1b, yy))
            els.append('<text x="%d" y="%.1f" font-size="11" text-anchor="end" fill="#555" dominant-baseline="middle">%d</text>' % (px0b - 6, yy, yv))
        for i in range(8):
            xx = px0b + i * (px1b - px0b) / 8
            xv = xb0 + i * (xb1 - xb0) / 8
            els.append('<text x="%.1f" y="%d" font-size="11" text-anchor="middle" fill="#555">%d</text>' % (xx, py1b + 16, xv))
        els.append('<text x="%.1f" y="%d" font-size="12" fill="#555" text-anchor="middle">RANGE (m)</text>' % ((px0b + px1b) / 2, py1b + 36))
        els.append('<text x="14" y="%.1f" font-size="12" fill="#555" transform="rotate(-90 14 0)" text-anchor="middle" dominant-baseline="middle">X DRIFT (m)</text>' % ((py0b + py1b) / 2,))
        els.append('<text x="%d" y="%d" font-size="11" fill="#c0392b">NO CONTROL</text>' % (px1b - 190, py0b + 15))
        if True:
            els.append('<text x="%d" y="%d" font-size="11" fill="#2980b9">WITH CONTROL</text>' % (px1b - 190, py0b + 32))

        # CEP scatter
        px0c, py0c, px1c, py1c = W - pr - 440, pt + 60, W - pr - 10, pt + 330
        ex0, ex1 = -30, 30
        ey0, ey1 = -30, 30
        els.append('<rect x="%d" y="%d" width="%d" height="%d" fill="white" stroke="#999"/>' % (px0c, py0c, px1c - px0c, py1c - py0c))
        els.append('<text x="%d" y="%d" font-size="13" font-weight="bold" fill="#222">C. Impact scatter (300 shots, +-30 m window)</text>' % (px0c, py0c - 8))
        for i in range(7):
            yy = py0c + i * (py1c - py0c) / 6
            xx = px0c + i * (px1c - px0c) / 6
            els.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#eee"/>' % (px0c, yy, px1c, yy))
            els.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#eee"/>' % (xx, py0c, xx, py1c))
        for i, (hits, col) in enumerate(((bal, "#c0392b"), (gud, "#2980b9"))):
            for hx, hy in hits[::3]:
                if abs(hx - tgt[0]) < 30 and abs(hy - tgt[1]) < 30:
                    els.append('<circle cx="%.1f" cy="%.1f" r="1.6" fill="%s" opacity="0.55"/>' % (
                        sv(hx, ex0, ex1, px0c, px1c), svy(hy, ey0, ey1, py0c, py1c), col))
        tx = sv(tgt[0], ex0, ex1, px0c, px1c)
        ty = svy(tgt[1], ey0, ey1, py0c, py1c)
        els.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#333" stroke-width="2"/>' % (tx - 6, ty, tx + 6, ty))
        els.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#333" stroke-width="2"/>' % (tx, ty - 6, tx, ty + 6))

        els.append('<text x="%d" y="%d" font-size="13" fill="#333">Target: range %.0f m  cross %.0f m</text>' % (px0c, py1c + 40, tgt[0], tgt[1]))
        els.append('<text x="%d" y="%d" font-size="13" fill="#c0392b">ballistic CEP ~ %.0f m</text>' % (px0c, py1c + 58, bcep[2]))
        els.append('<text x="%d" y="%d" font-size="13" fill="#2980b9">guided CEP ~ %.0f m</text>' % (px0c, py1c + 76, gcep[2]))
        els.append('</svg>')
        with open(os.path.join(OUT, "trajectory_comparison.svg"), "w") as f:
            f.write("\n".join(els))

    svg_chart()
    print("written:", OUT)

    # try PNG via FreeCAD's matplotlib
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(14, 6))
        for rr, lab, col in ((data_b, "NO CONTROL", "#c0392b"), (data_g, "WITH CONTROL", "#2980b9")):
            ax[0].plot([r[1][0] for r in rr], [r[1][2] for r in rr], lw=2, color=col, label=lab)
        ax[0].plot(tgt[0], 0, "k+", ms=14)
        ax[0].annotate("TARGET", (tgt[0], 0), textcoords="offset points", xytext=(-15, -25))
        ax[0].set_xlabel("Range (m)"); ax[0].set_ylabel("Altitude (m)")
        ax[0].set_title("A. Ballistic vs guided (1:1, v0=684 m/s)")
        ax[0].legend(); ax[0].grid(alpha=0.3)
        for rr, lab, col in ((data_b, "NO CONTROL", "#c0392b"), (data_g, "WITH CONTROL", "#2980b9")):
            ax[1].plot([r[1][0] for r in rr], [r[1][1] for r in rr], lw=2, color=col, label=lab)
        ax[1].set_xlabel("Range (m)"); ax[1].set_ylabel("Cross drift (m)")
        ax[1].set_title("B. Cross-range correction")
        ax[1].legend(); ax[1].grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(OUT, "trajectory_comparison.png"), dpi=130)
        plt.close(fig)
        print("PNG written (via FreeCAD matplotlib)")
    except Exception as e:
        print("PNG skipped:", e)


if __name__ == "__main__":
    main()
