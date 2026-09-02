#!/usr/bin/env python3
"""
SIH26098 PGK — PPT Visual Generator (production-grade, image-only)
Generates 8 high-res PNG + SVG for direct PPT insertion.
All values from cad_models/PGK_SPEC_SHEET.md + sim/sim_single_machine.py

Outputs ppt_resources/*.png|svg @ 1920×1080, white, no dependencies.
Run: python3 ppt_resources/generate_ppt_visuals.py
"""
import os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
DPI = 150
W, H = 1920, 1080  # 12.8x7.2 @150
FW, FH = W/DPI, H/DPI

# SIH palette
NAVY = "#0B1D3A"
TEAL = "#00C2A8"
AMBER = "#FFB000"
CORAL = "#E94560"
BLUE = "#1E88E5"
LIGHT = "#EEF2F7"
GREY = "#6B7A90"
GOLD = "#C9A227"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})

def add_header(ax, title, subtitle, number=""):
    # header bar
    bar = patches.FancyBboxPatch((0, 0.92), 1, 0.08, boxstyle="square,pad=0", transform=ax.transAxes, color=NAVY, zorder=1, clip_on=False)
    ax.add_patch(bar)
    ax.text(0.015, 0.965, number, transform=ax.transAxes, fontsize=9, color=GOLD, weight=900, va="center", ha="left", zorder=3, fontfamily="DejaVu Sans")
    ax.text(0.055, 0.97, title, transform=ax.transAxes, fontsize=13, color="white", weight=800, va="center", ha="left", zorder=3)
    ax.text(0.055, 0.937, subtitle, transform=ax.transAxes, fontsize=7.5, color="#B8C5D6", va="center", ha="left", zorder=3)
    ax.text(0.985, 0.965, "SINGLE TIME-SHARE PMSM  •  155mm PGK  •  cad_models/PGK_SPEC_SHEET.md", transform=ax.transAxes, fontsize=5.5, color="#7A8CA8", va="center", ha="right", zorder=3)
    ax.text(0.985, 0.935, "APPROVED FOR PPT — IMAGE ONLY  •  SIH26098", transform=ax.transAxes, fontsize=5, color="#5A6E8A", va="center", ha="right", zorder=3)

def finalize(fig, name):
    path_png = os.path.join(OUT, f"{name}.png")
    path_svg = os.path.join(OUT, f"{name}.svg")
    fig.savefig(path_png, dpi=DPI, facecolor="white")
    fig.savefig(path_svg, facecolor="white")
    plt.close(fig)
    print(f"✓ {name}.png  {W}x{H}")

# --------------------------------------------------------------------------
# 01 TRAJECTORY PROFILE
# --------------------------------------------------------------------------
def gen_01():
    fig = plt.figure(figsize=(FW, FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax, "BALLISTIC TRAJECTORY — 30 KM NOMINAL (45° QE, v₀ 800 m/s)", "Point-mass RK4  •  Apogee 9.46 km @ 40.6 s  •  TOF 87.6 s  •  M795 47.9 kg  [SPEC §1 + sim/RESULTS]", "01")

    # simulate quick RK4 similar to sim_single_machine with Cd calibrated
    G=9.80665; RHO0=1.225; HSCALE=8500; D=0.155; AREA=math.pi/4*D*D; M=47.9; Cd=0.203
    def rho(z): return RHO0*math.exp(-max(z,0)/HSCALE)
    def step(s, dt):
        # s [x,y,z,vx,vy,vz]
        def accel(st):
            x,y,z,vx,vy,vz = st
            v = math.hypot(vx, math.hypot(vy, vz))
            if v<1e-6: return (vx,vy,vz,0,0,-G)
            k=0.5*rho(z)*Cd*AREA*v/M
            return (vx,vy,vz, -k*vx, -k*vy, -k*vz -G)
        def add(a,b,s): return tuple(a[i]+s*b[i] for i in range(6))
        k1=accel(s); k2=accel(add(s,k1,dt/2)); k3=accel(add(s,k2,dt/2)); k4=accel(add(s,k3,dt))
        return tuple(s[i]+dt/6*(k1[i]+2*k2[i]+2*k3[i]+k4[i]) for i in range(6))
    s=(0,0,0, 800*math.cos(math.radians(45)),0, 800*math.sin(math.radians(45)))
    traj=[s]; t=0
    while s[2]>=0 or t<1:
        s=step(s,0.05); t+=0.05; traj.append(s)
        if s[2]<=0 and traj[-2][2]>0: break
    xs=np.array([p[0] for p in traj]); zs=np.array([p[2] for p in traj]); vs=np.array([math.hypot(p[3],p[5]) for p in traj])
    # main plot panel
    left, bot, wid, hei = 0.055, 0.18, 0.66, 0.64
    axp = fig.add_axes([left, bot, wid, hei])
    axp.set_facecolor("#F8FAFC")
    axp.grid(True, color="white", linewidth=1.2, linestyle="-")
    axp.grid(True, color="#E3EAF3", linewidth=0.6, linestyle="--", which="minor")
    axp.set_axisbelow(True)
    # altitude profile
    axp.plot(xs/1000, zs/1000, color=NAVY,lw=2.6, zorder=5)
    axp.fill_between(xs/1000, zs/1000, 0, color=BLUE, alpha=0.07)
    axp.set_xlim(0,32); axp.set_ylim(0,11)
    axp.set_xlabel("RANGE  (km)  →", fontsize=8, color=GREY, weight=600)
    axp.set_ylabel("ALTITUDE  (km)", fontsize=8, color=GREY, weight=600)
    # phases annotation
    # find apogee index
    i_apo = int(np.argmax(zs))
    x_apo, z_apo = xs[i_apo]/1000, zs[i_apo]/1000
    # phase markers - place ON trajectory by interpolation, not stray
    # only mark apogee and impact; phase labels via timeline bar below
    axp.scatter([x_apo],[z_apo], s=70, color=AMBER, edgecolor="white", linewidth=1.5, zorder=7)
    # impact is at 30km, 0
    axp.scatter([30],[0], s=45, color=NAVY, edgecolor="white", linewidth=1.2, zorder=7)
    phases = []
    # apogee vertical
    axp.axvline(x_apo, color=AMBER, ls=":", lw=1.2, alpha=0.8)
    axp.text(x_apo+0.3, z_apo-1.0, f"APOGEE\n{z_apo:.2f} km @ {i_apo*0.05:.1f}s", fontsize=5.5, color="#8A6D00",
             bbox=dict(boxstyle="round,pad=0.25", fc="#FFF8E1", ec="#FFE082", alpha=0.95))
    # velocity bottom overlay
    ax2 = axp.twinx()
    ax2.plot(xs/1000, vs, color=GREY, lw=1.0, ls="--", alpha=0.7)
    ax2.set_ylim(0,900); ax2.set_ylabel("VELOCITY m/s", fontsize=6, color=GREY)
    ax2.tick_params(colors=GREY)
    # impact marker
    axp.annotate("IMPACT\n30 km", xy=(30,0), xytext=(26,2.2), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2),
                 fontsize=6, weight=700, color=NAVY, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=NAVY))
    # inset table top right
    table_ax = fig.add_axes([0.745, 0.46, 0.22, 0.36])
    table_ax.axis("off")
    table_ax.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.02", facecolor="white", edgecolor="#DDE6F2", lw=1))
    table_ax.text(0.5,0.93,"FLIGHT TABLE  45° QE", ha="center", va="center", fontsize=7, weight=800, color=NAVY)
    rows = [
        ("RANGE", "v₀", "TOF", "APOGEE"),
        ("20 km", "650 m/s", "63 s", "31 s"),
        ("30 km *", "800 m/s", "88–92 s", "40–46 s"),
        ("40 km", "900 m/s", "118 s", "60 s"),
    ]
    for i,r in enumerate(rows):
        y=0.82 - i*0.14; weight=700 if i==0 else (800 if i==2 else 500); c=GREY if i==0 else NAVY
        if i==2:
            table_ax.add_patch(patches.FancyBboxPatch((0.02,y-0.055),0.96,0.11, boxstyle="round,pad=0.01", facecolor="#FFF3E0", edgecolor=AMBER, lw=0.8))
        for j,txt in enumerate(r):
            x = 0.08 + j*0.24
            table_ax.text(x, y, txt, fontsize=6, color=c, weight=weight, ha="left", va="center")
        if i>0:
            table_ax.plot([0.05,0.95],[y+0.08,y+0.08], color="#E8EEF6", lw=0.6)
    table_ax.text(0.5,0.12,"q descent 15–50 kPa  •  M ≈1.0–2.7  •  spin 15,480→14,000 rpm", ha="center", va="center", fontsize=5, style="italic", color=GREY)
    # bottom legend phase timeline bar
    bar_ax = fig.add_axes([0.055, 0.055, 0.94, 0.065])
    bar_ax.set_xlim(0,92); bar_ax.set_ylim(0,1); bar_ax.axis("off")
    segs = [(0,0.011,"A IN-BORE", NAVY, 0.011),(0.011,1,"B MUZZLE", "#8A97AE", 0.001),(1,46,"C ASCENT — GENERATOR", TEAL, 45),(46,50,"D BRAKE", AMBER,4),(50,92,"E DESCENT — ACTUATOR + VNS 84–92s", CORAL,42)]
    for x0,x1,lab,col,w in segs:
        bar_ax.add_patch(patches.FancyBboxPatch((x0,0.28), x1-x0, 0.45, boxstyle="round,pad=0.005", facecolor=col, edgecolor="white", lw=0.6))
        if x1-x0>6:
            bar_ax.text((x0+x1)/2,0.51, lab, fontsize=5, weight=700, color="white", ha="center", va="center")
        bar_ax.text((x0+x1)/2,0.12,f"{x0:.0f}–{x1:.0f}s" if x1-x0>2 else "", fontsize=4, color=GREY, ha="center")
    bar_ax.text(0.5,0.92,"MISSION TIME  t=0 LAUNCH  →  t=92s IMPACT    •    apogee = mode switch (IMU v_z flip OR time table, dual-redundant)", ha="center", fontsize=6, weight=700, color=NAVY)
    finalize(fig,"01_trajectory_profile")

# --------------------------------------------------------------------------
# 02 SYSTEM ARCHITECTURE — single time-share PMSM
# --------------------------------------------------------------------------
def gen_02():
    fig = plt.figure(figsize=(FW,FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax,"SYSTEM ARCHITECTURE — SINGLE TIME-SHARE 12s10p PMSM","One stator, one rotor, one inverter = generator ⇆ actuator (software role switch)", "02")

    # central motor schematic (cross-section)
    # Draw shaft, stator, rotor, fins, bearings
    cx, cy = 0.5, 0.48; scale=0.35
    # axes for schematic
    sch = fig.add_axes([0.28,0.12,0.44,0.58])
    sch.set_xlim(-68,68); sch.set_ylim(-68,68); sch.set_aspect("equal"); sch.axis("off")
    sch.set_facecolor("#F8FAFC")
    # shaft tube
    shaft = patches.Rectangle((-20,-26),40,52, facecolor="#CBD5E1", edgecolor=NAVY, lw=1.2)
    sch.add_patch(shaft)
    sch.add_patch(patches.Rectangle((-15,-26),30,52, facecolor="#E2E8F0", edgecolor="none"))
    # bore
    sch.add_patch(patches.Rectangle((-15,-15),30,30, facecolor=NAVY, alpha=0.85))
    sch.text(0,0,"Ø30\nBORE\n(EXPLOSIVE\nTRAIN)", ha="center", va="center", fontsize=5, color="white", weight=700)
    # stator core
    sch.add_patch(patches.Circle((0,0),29.25, facecolor="none", edgecolor=AMBER, lw=3))
    sch.add_patch(patches.Circle((0,0),20, facecolor="none", edgecolor=AMBER, lw=1.5, ls="--", alpha=0.6))
    sch.text(0,24,"STATOR\n12 slots", ha="center", fontsize=5, color="#8A6D00", weight=700)
    # rotor back iron
    sch.add_patch(patches.Circle((0,0),35, facecolor="none", edgecolor=CORAL, lw=3.5))
    # magnets
    for a in range(10):
        ang = a*36
        x = 31.5*math.cos(math.radians(ang)); y=31.5*math.sin(math.radians(ang))
        sch.add_patch(patches.Circle((x,y),4, facecolor=CORAL, edgecolor="white", lw=0.7))
    sch.text(0,-34,"ROTOR\n10 poles N42SH", ha="center", fontsize=5, color=CORAL, weight=700)
    # air gap label
    sch.annotate("AIR GAP\n0.75 mm", xy=(29,8), xytext=(45,18), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=5, color=GREY, ha="left")
    # fins (simple triangles outside)
    for ang in [0,90,180,270]:
        x0 = 35*math.cos(math.radians(ang)); y0=35*math.sin(math.radians(ang))
        x1 = 54*math.cos(math.radians(ang)); y1=54*math.sin(math.radians(ang))
        sch.add_patch(patches.Circle((x1,y1),6, facecolor=TEAL, edgecolor=NAVY, lw=1))
        sch.plot([x0,x1],[y0,y1], color=TEAL, lw=2.2)
        twist = "+12°" if ang!=180 else "-12°"
        # fin label
        lx = 42*math.cos(math.radians(ang+18)); ly=42*math.sin(math.radians(ang+18))
        sch.text(lx,ly, twist, fontsize=4, color=TEAL, weight=700, ha="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=TEAL, alpha=0.9))
    sch.text(0,48,"S11 CANARD SHELL Ø76 → FIN TIP Ø108", ha="center", fontsize=6, weight=800, color=NAVY, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=NAVY))
    # bearings
    for y in [-22,22]:
        sch.add_patch(patches.Rectangle((-26,y-3),52,4.5, facecolor="#94A3B8", edgecolor=NAVY, hatch="///", alpha=0.9))
    sch.text(-48,-22,"M09", fontsize=4, color=GREY); sch.text(-48,22,"M09", fontsize=4, color=GREY)
    # dimension
    sch.annotate("", xy=(-38,-38), xytext=(38,-38), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1))
    sch.text(0,-42,"Ø108.0 max envelope", ha="center", fontsize=5, weight=700, color=NAVY)

    # LEFT: GENERATOR MODE
    left = fig.add_axes([0.02,0.12,0.24,0.58]); left.axis("off")
    left.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.02", facecolor="#ECFDF5", edgecolor=TEAL, lw=1.2))
    left.text(0.5,0.94,"GENERATOR MODE", ha="center", fontsize=8, weight=900, color=TEAL)
    left.text(0.5,0.90,"ASCENT  0 → 46 s  •  windmill", ha="center", fontsize=6, color="#0F766E")
    # icon flow
    y=0.82
    for txt, sub in [("WINDMILL ROTOR\n0→20k rpm-free spin","aero 0.14–0.2 N·m"),("3-PHASE AC\n150–200 V @20k rpm","12s10p"),("SAME INVERTER\nActive Rectifier","3 half-bridges"),("BUCK CHARGER\n85% eff  12W avg","regulated"),("SUPERCAP 0.6F @54V\n875 J (535 usable)","z70–100 annulus"),("3.3/5 V RAILS\nGPS • IMU • MCU • FRAM","holdup caps")]:
        left.add_patch(patches.FancyBboxPatch((0.07,y-0.07),0.86,0.095, boxstyle="round,pad=0.015", facecolor="white", edgecolor="#A7F3D0", lw=0.8))
        left.text(0.5,y-0.02,txt,ha="center",va="center",fontsize=5.2, weight=700, color=NAVY, linespacing=1.2)
        left.text(0.5,y-0.055,sub,ha="center",fontsize=4, color=GREY, style="italic")
        if y>0.25: left.annotate("", xy=(0.5,y-0.075), xytext=(0.5,y-0.095), arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.4))
        y-=0.102
    left.text(0.5,0.055,"Cap charging IN FLIGHT\nself-discharge irrelevant", ha="center", fontsize=4.5, style="italic", color="#0F766E", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=TEAL, alpha=0.8))

    # RIGHT: ACTUATOR MODE
    right = fig.add_axes([0.74,0.12,0.24,0.58]); right.axis("off")
    right.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.02", facecolor="#FEF2F2", edgecolor=CORAL, lw=1.2))
    right.text(0.5,0.94,"ACTUATOR MODE", ha="center", fontsize=8, weight=900, color=CORAL)
    right.text(0.5,0.90,"DESCENT 46 → 92 s  •  servo-held", ha="center", fontsize=6, color="#991B1B")
    y=0.82
    for txt, sub in [("SUPERCAP SOLE SOURCE\n54→20 V window","sole after apogee"),("SAME INVERTER\nFOC Inverter", "≤16 A peak"),("PMSM TORQUE\nKt 0.095 N·m/A", "0.2 N·m hold, 1.5 peak"),("ROTOR SERVO-HOLD\n±12° hover", "0.5 kg·m inertia"),("MIRROR FIN FORCE\n15–25 N lateral", "precession Ω≈2.8°/s"),("200–300 m AUTHORITY\nCORRECTION", "½ a t²")]:
        right.add_patch(patches.FancyBboxPatch((0.07,y-0.07),0.86,0.095, boxstyle="round,pad=0.015", facecolor="white", edgecolor="#FECACA", lw=0.8))
        right.text(0.5,y-0.02,txt,ha="center",va="center",fontsize=5.2, weight=700, color=NAVY, linespacing=1.2)
        right.text(0.5,y-0.055,sub,ha="center",fontsize=4, color=GREY, style="italic")
        if y>0.25: right.annotate("", xy=(0.5,y-0.075), xytext=(0.5,y-0.095), arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.4))
        y-=0.102
    right.text(0.5,0.055,"Regen brake 155J recovers\nrotor inertia at switch", ha="center", fontsize=4.5, style="italic", color="#991B1B", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=CORAL, alpha=0.8))

    # bottom spec bar
    bottom = fig.add_axes([0.02,0.035,0.96,0.065]); bottom.axis("off")
    bottom.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    specs = ["12s10p OUTER-ROTOR", "Kt 0.095 N·m/A", "R 0.15 Ω", "CONT 0.5 N·m", "PEAK 1.5 N·m", "Ø108 × z0–220", "1.20 kg PGK", "THRU-BORE Ø30 KEEP-CLEAR"]
    for i,s in enumerate(specs):
        x=0.02 + i*0.122
        bottom.add_patch(patches.FancyBboxPatch((x,0.18),0.115,0.64, boxstyle="round,pad=0.005", facecolor="white", edgecolor=NAVY, alpha=0.12))
        bottom.text(x+0.0575,0.5,s, ha="center", va="center", fontsize=5, weight=700, color="white")
    bottom.text(0.5,0.92,"Motor module 723 g + caps 67 g  •  bore clear  •  Mode switch = software only, same half-bridges", ha="center", fontsize=5, color=GOLD)

    finalize(fig,"02_system_architecture")

# --------------------------------------------------------------------------
# 03 SENSOR & CPU LOGIC
# --------------------------------------------------------------------------
def gen_03():
    fig = plt.figure(figsize=(FW,FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax,"SENSORS  •  CPU LOGIC  •  EKF FUSION","Gun-hard for 15,480 rpm roll  •  Dual-core TI C2000  •  FOC 20 kHz  •  FRAM retention", "03")

    # LEFT sensor cards
    sensors = [
        ("IMU  SiIMU02", "Collins MEMS\ngun-hard 20,000 g\nroll ±25,000°/s\nbias 1–10°/h  ARW 0.1°/√h", "M01 z125-135\nr≤20  comp 5,700 g", TEAL, "BODY-FIXED"),
        ("GNSS  NavIC", "NavASIC V3  L5/L1 + GPS\n10 ch  25 dB-Hz\npreloaded eph <10s", "S08 z175-185\n+ patch S07 z199\nRF coax M01 slots", BLUE, "BODY-FIXED"),
        ("MAG  RM3100", "MR  ≥2 kHz (5 kHz raw)\n13 nT/√Hz  <0.5° roll\nEarth 25–65 µT", "M01 z115-120\n>25mm from rotor\nPhase 0 cal", AMBER, "ROLL REF"),
        ("ANGLE ARRAY", "sin/cos Hall/MR\n≤0.1° interp\nbias ring Ø41/51.6", "M01 z163-166\n0.5mm gap  + 3×Hall\nbkup 60°", CORAL, "ROTOR REL BODY"),
    ]
    for i,s in enumerate(sensors):
        x0 = 0.02 + i*0.185; w=0.175
        card = fig.add_axes([x0,0.52,w,0.30]); card.axis("off")
        card.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.015", facecolor="white", edgecolor=s[3], lw=1.3))
        card.add_patch(patches.FancyBboxPatch((0,0.78),1,0.22, boxstyle="round,pad=0.01", facecolor=s[3], edgecolor=s[3]))
        card.text(0.5,0.89,s[0], ha="center", fontsize=7, weight=900, color="white")
        card.text(0.5,0.80,s[4], ha="center", fontsize=5, weight=700, color="white", alpha=0.9)
        card.text(0.5,0.64,s[1], ha="center", va="center", fontsize=4.5, color=NAVY, linespacing=1.3)
        card.add_patch(patches.FancyBboxPatch((0.05,0.08),0.9,0.22, boxstyle="round,pad=0.01", facecolor="#F1F5F9", edgecolor="#E2E8F0"))
        card.text(0.5,0.19,s[2], ha="center", va="center", fontsize=4.2, color=GREY, style="italic", linespacing=1.2)

    # CENTER EKF fusion
    ekf = fig.add_axes([0.26,0.18,0.48,0.28]); ekf.axis("off")
    ekf.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.02", facecolor=NAVY, edgecolor=NAVY))
    ekf.text(0.5,0.90,"TI C2000 F2837xD  DUAL-CORE  •  FM25V05 FRAM 5 Mbit  •  M04 POWER STAGE 16–20 A", ha="center", fontsize=5.5, weight=700, color=GOLD)
    # three loops
    for i, (title, desc, col) in enumerate([("CORE 1  FOC\n20 kHz", "T=Kt·I  0.095 N·m/A\nhard 16A → 1.5N·m", TEAL),("CHARGE REG\nAPPLIED", "54→20 V window\nbuck 85%  12W thr", AMBER),("MODE STATE\nMACHINE", "Phase0→Gen→Brake→Hold\nIMU flip OR time", CORAL)]):
        x=0.04+i*0.32
        ekf.add_patch(patches.FancyBboxPatch((x,0.22),0.28,0.55, boxstyle="round,pad=0.01", facecolor="white", edgecolor=col, lw=1))
        ekf.add_patch(patches.Circle((x+0.14,0.62),0.05, color=col))
        ekf.text(x+0.14,0.62,str(i+1), ha="center", va="center", fontsize=8, weight=900, color="white")
        ekf.text(x+0.14,0.48,title, ha="center", fontsize=5.5, weight=800, color=NAVY, linespacing=1.1)
        ekf.text(x+0.14,0.32,desc, ha="center", fontsize=4, color=GREY, linespacing=1.2)
        if i<2:
            ekf.annotate("", xy=(x+0.32,0.5), xytext=(x+0.28,0.5), arrowprops=dict(arrowstyle="->", color="white", lw=1.2))
    ekf.text(0.5,0.12,"EKF FUSES  body roll (mag+gyro)  +  rotor angle (array)  →  INERTIAL CANARD = roll + rotor rel  ≤0.5°", ha="center", fontsize=5, weight=700, color="white", bbox=dict(boxstyle="round,pad=0.15", fc="#1E2F4D", ec=GOLD, alpha=0.9))
    ekf.text(0.5,0.045,"3.3/5V rails with local holdup caps — ms ride-through for 16A FOC bursts  •  Acquisition before actuation scheduling", ha="center", fontsize=4, color="#8AA0BE", style="italic")
    # right VNS
    vns = fig.add_axes([0.775,0.18,0.205,0.28]); vns.axis("off")
    vns.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.015", facecolor="#FEFCE8", edgecolor=GOLD, lw=1.2, ls="--"))
    vns.text(0.5,0.92,"VNS TERMINAL 2km", ha="center", fontsize=7, weight=900, color="#854D0E")
    vns.text(0.5,0.86,"GPS-DENIED FALLBACK", ha="center", fontsize=5, weight=600, color="#A16207")
    vns.add_patch(patches.FancyBboxPatch((0.06,0.62),0.88,0.18, boxstyle="round,pad=0.01", facecolor="white", edgecolor="#FDE68A"))
    vns.text(0.5,0.71,"Ø8 sapphire S07 flank\n1kfps global-shutter\n30–50µs gated @233 rev/s", ha="center", fontsize=4.2, color=NAVY, linespacing=1.2)
    vns.add_patch(patches.FancyBboxPatch((0.06,0.40),0.88,0.18, boxstyle="round,pad=0.01", facecolor="white", edgecolor="#FDE68A"))
    vns.text(0.5,0.49,"Scene-match 0.5s\n≤8MB ref Phase0 via setter\nσ ≤15m EKF update", ha="center", fontsize=4.2, color=NAVY, linespacing=1.2)
    vns.add_patch(patches.FancyBboxPatch((0.06,0.15),0.88,0.18, boxstyle="round,pad=0.01", facecolor="white", edgecolor=CORAL, lw=0.8))
    vns.text(0.5,0.24,"LIT pair trim\n~7–10m  •  1.2W×8s=10J", ha="center", fontsize=4.2, color=CORAL, weight=700, linespacing=1.2)
    vns.text(0.5,0.06,"concept — demo req before PDR", ha="center", fontsize=4, color=GREY, style="italic")
    # wiring map bottom
    wiring = fig.add_axes([0.02,0.045,0.96,0.095]); wiring.axis("off")
    wiring.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.01", facecolor="#F8FAFC", edgecolor="#DDE6F2"))
    wiring.text(0.01,0.78,"STACK WIRING  PHYSICAL MAP  (§9.6)", fontsize=5, weight=800, color=NAVY)
    wiring.text(0.01,0.50,"S07 radome GNSS antenna z199 ──RF coax (support-tube Ø18 → flange bore → M01 slots full-length to 175)──►  S08 shield can z175-184.8  GNSS+MCU+FRAM   │   M04 gate driver Z138  ◄── M01 slots 54V+S09 caps", fontsize=4.5, color="#334155", weight=500, family="monospace")
    wiring.text(0.01,0.22,"                                    inductive coupler z185.5-191.5 (Phase0 setter)                     │   SPI/UART   │  tube board z163-166 sin/cos → S04 bias ring  │  SiIMU02 z125 + RM3100 z115 (r≤20)", fontsize=4.2, color=GREY, family="monospace")
    # arrows top sensors to EKF
    fig.patches.extend([patches.FancyArrowPatch((0.11,0.52),(0.34,0.46), transform=fig.transFigure, arrowstyle="->", color=TEAL, lw=1.2, mutation_scale=10),
                        patches.FancyArrowPatch((0.295,0.52),(0.40,0.46), transform=fig.transFigure, arrowstyle="->", color=BLUE, lw=1.2, mutation_scale=10),
                        patches.FancyArrowPatch((0.48,0.52),(0.50,0.46), transform=fig.transFigure, arrowstyle="->", color=AMBER, lw=1.2, mutation_scale=10),
                        patches.FancyArrowPatch((0.665,0.52),(0.60,0.46), transform=fig.transFigure, arrowstyle="->", color=CORAL, lw=1.2, mutation_scale=10)])

    finalize(fig,"03_sensors_cpu_logic")

# --------------------------------------------------------------------------
# 04 CANARD PHYSICS
# --------------------------------------------------------------------------
def gen_04():
    fig = plt.figure(figsize=(FW,FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax,"CANARD ACTUATION — MIRROR-PITCH HOVER PHYSICS","Span-twist torque (windmill)  ⇆  Roll-phase lateral (correction)  •  S11 shell  •  4× 12°  Ø76→108", "04")

    # LEFT: top view schematic windmill
    left = fig.add_axes([0.02,0.38,0.31,0.46]); left.set_xlim(-68,68); left.set_ylim(-68,68); left.set_aspect("equal"); left.axis("off")
    left.set_facecolor("#F8FAFC")
    left.text(0.5,0.95,"FREE-SPINS  •  WINDMILL (= GENERATOR)", transform=left.transAxes, ha="center", fontsize=6.5, weight=900, color=TEAL)
    left.text(0.5,0.90,"torques ADD  •  lateral CANCELS  •  net 0", transform=left.transAxes, ha="center", fontsize=5, color=GREY, style="italic")
    # shell
    left.add_patch(patches.Circle((0,0),22, facecolor="#E2E8F0", edgecolor=NAVY, lw=1.2))
    left.add_patch(patches.Circle((0,0),16, facecolor=NAVY, alpha=0.9))
    left.text(0,0,"S11\nSHELL\n+ROTOR", ha="center", va="center", fontsize=5, color="white", weight=800)
    # fins - windmill mode show tangential forces all same rotational
    for ang, col, plus in [(0,TEAL,True),(90,TEAL,True),(180,CORAL,True),(270,TEAL,True)]:
        # fin rectangle outward
        x0 = 22*math.cos(math.radians(ang)); y0=22*math.sin(math.radians(ang))
        x1 = 48*math.cos(math.radians(ang)); y1=48*math.sin(math.radians(ang))
        left.plot([x0,x1],[y0,y1], color=TEAL, lw=6, solid_capstyle="round", alpha=0.9)
        # small foil twist indication
        left.add_patch(patches.Circle((x1,y1),7, facecolor="white", edgecolor=TEAL, lw=1.2))
        txt = "+12°" if ang!=180 else "-12° (mirror)"
        left.text(x1+9*math.cos(math.radians(ang)), y1+9*math.sin(math.radians(ang)), txt, fontsize=3.8, color=TEAL, weight=700, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=TEAL))
        # tangential arrow (all clockwise for example)
        # vector tangential = perpendicular to radial
        tx = -math.sin(math.radians(ang)); ty = math.cos(math.radians(ang))
        left.annotate("", xy=(x1+tx*14, y1+ty*14), xytext=(x1,y1), arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.6))
        left.text(x1+tx*19, y1+ty*19, "Ft", fontsize=4, color=AMBER, weight=800, ha="center")
    # center torque arrow
    left.annotate("", xy=(12,14), xytext=(-12,-14), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5, connectionstyle="arc3,rad=0.6"))
    left.text(0,-52,"T_wind 0.14–0.2 N·m  →  P = T·ω  →  10–15 W", ha="center", fontsize=5, color=NAVY, weight=700, bbox=dict(boxstyle="round,pad=0.2", fc="#ECFDF5", ec=TEAL))
    left.text(0.5,0.02,"FREE: I dω/dt = Taero −Tgen −Tbearing\nCPU sets Pe → equilibrium ω", transform=left.transAxes, ha="center", fontsize=4, color=GREY, style="italic")

    # CENTER: hover mode
    center = fig.add_axes([0.345,0.38,0.31,0.46]); center.set_xlim(-68,68); center.set_ylim(-68,68); center.set_aspect("equal"); center.axis("off")
    center.set_facecolor("#FEF2F2")
    center.text(0.5,0.95,"SERVO-HELD  •  HOVER (= CORRECTION)", transform=center.transAxes, ha="center", fontsize=6.5, weight=900, color=CORAL)
    center.text(0.5,0.90,"torques CANCEL  •  lateral ADDS  •  net 15–25 N", transform=center.transAxes, ha="center", fontsize=5, color=GREY, style="italic")
    center.add_patch(patches.Circle((0,0),22, facecolor="#FECACA", edgecolor=CORAL, lw=1.2))
    center.add_patch(patches.Circle((0,0),16, facecolor=CORAL, alpha=0.9))
    center.text(0,0,"HELD\n±12°\nHOVER", ha="center", va="center", fontsize=5, color="white", weight=800)
    # Hover: all lateral same direction (to the right for example)
    for ang in [0,90,180,270]:
        x0 = 22*math.cos(math.radians(ang)); y0=22*math.sin(math.radians(ang))
        x1 = 48*math.cos(math.radians(ang)); y1=48*math.sin(math.radians(ang))
        center.plot([x0,x1],[y0,y1], color=CORAL, lw=6, solid_capstyle="round", alpha=0.9)
        center.add_patch(patches.Circle((x1,y1),7, facecolor="white", edgecolor=CORAL, lw=1.2))
        # lateral force arrow all to the right (+X) — that's hover physics
        center.annotate("", xy=(x1+18, y1), xytext=(x1,y1), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8))
        # opposite pair annotation
        if ang==0: center.text(x1+23, y1+4,"Fn 4–6N", fontsize=3.8, color=NAVY, weight=700)
    # big net force
    center.annotate("", xy=(0,42), xytext=(0,-22), arrowprops=dict(arrowstyle="->", color=NAVY, lw=2.2, mutation_scale=16, linestyle="--"))
    center.text(18,8,"NET 20N", fontsize=6, weight=900, color=NAVY, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=NAVY))
    center.text(0,-52,"F = q·S·Cl  Cl≈0.38  S=3.2cm²  →  a=0.3–0.5 m/s²", ha="center", fontsize=5, color=NAVY, weight=700, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=CORAL))
    center.text(0.5,0.02,"HELD: 0 = Tmotor+Taero+Tfric → Tmotor≈0.2N·m\nLateral precesses shell Ω=M/Izωz 2.8°/s", transform=center.transAxes, ha="center", fontsize=4, color=GREY, style="italic")

    # RIGHT: numbers panel
    right = fig.add_axes([0.67,0.38,0.31,0.46]); right.axis("off")
    right.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.015", facecolor="white", edgecolor=NAVY, lw=1.2))
    right.text(0.5,0.96,"MAGNITUDES  q=35 kPa  M 1.0–1.3  (SPEC §2.5)", ha="center", fontsize=6, weight=900, color=NAVY)
    rows = [
        ("Normal / fin @12°", "4–6 N", "q·S·Cl 0.38"),
        ("Net lateral (4 fins)", "15–25 N", "mirror pairs sum"),
        ("Axial drag (4 fins)", "~8 N", "1–2% range penalty"),
        ("Centrifugal / fin", "~1.3 kN", "10g @45mm 15krpm"),
        ("Windmill torque", "0.14–0.2 N·m", "what servo fights"),
        ("Hold torque", "0.2–0.25 N·m", "spec 0.5 (2×)"),
        ("Peak slew 180°/0.15s", "0.6–0.8 N·m", "spec 1.5 (2×)"),
        ("Correction 35s", "200–300 m", "½ a t²"),
    ]
    for i,(a,b,c) in enumerate(rows):
        y=0.88 - i*0.095
        right.add_patch(patches.FancyBboxPatch((0.03,y-0.04),0.94,0.075, boxstyle="round,pad=0.01", facecolor="#F8FAFC" if i%2==0 else "white", edgecolor="#E2E8F0", lw=0.5))
        right.text(0.05,y, a, fontsize=4.8, color=NAVY, weight=600, va="center")
        right.text(0.62,y, b, fontsize=5, color=CORAL if i in [1,7] else NAVY, weight=900, va="center", ha="center")
        right.text(0.95,y, c, fontsize=3.8, color=GREY, va="center", ha="right", style="italic")
    right.text(0.5,0.055,"Fin root design load 100 N (2×)  •  ripple 1 kHz (4×258Hz) filtered by I=4.5e-4", ha="center", fontsize=4, color=GREY, style="italic")

    # BOTTOM: flow path + spin component
    bottom = fig.add_axes([0.02,0.06,0.96,0.26]); bottom.axis("off")
    bottom.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.015", facecolor="#F1F5F9", edgecolor="#CBD5E1", lw=0.7))
    # spin wind diagram
    spin_ax = fig.add_axes([0.035,0.08,0.26,0.20]); spin_ax.set_xlim(0,1); spin_ax.set_ylim(0,1); spin_ax.axis("off")
    spin_ax.text(0.5,0.88,"FLOW ENVIRONMENT  vt= ω·r ≈75 m/s", ha="center", fontsize=5, weight=800, color=NAVY)
    spin_ax.text(0.5,0.78,"axial V 300 m/s  +  tangential 75 m/s  →  effective AoA 14°  oscill. 1/rev", ha="center", fontsize=4, color=GREY, style="italic")
    spin_ax.add_patch(patches.FancyArrowPatch((0.15,0.45),(0.85,0.45), arrowstyle="->", color=BLUE, lw=2, mutation_scale=14))
    spin_ax.text(0.5,0.50,"V  axial", ha="center", fontsize=5, color=BLUE, weight=700)
    spin_ax.add_patch(patches.FancyArrowPatch((0.5,0.12),(0.5,0.68), arrowstyle="->", color=AMBER, lw=2, mutation_scale=14))
    spin_ax.text(0.68,0.40,"vt spin-induced", fontsize=4, color=AMBER, weight=700, rotation=90, va="center")
    spin_ax.add_patch(patches.FancyArrowPatch((0.5,0.45),(0.82,0.68), arrowstyle="->", color=CORAL, lw=1.6, ls="--", mutation_scale=12))
    spin_ax.text(0.82,0.72,"local wind  ~310 m/s\nAoA ~atan(vt/V)≈14°", fontsize=3.8, color=CORAL, weight=600, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#E2E8F0"))
    spin_ax.text(0.5,0.06,"every fin sees azimuth-dependent AoA  •  servo + windmill live with it (§2.5)", ha="center", fontsize=3.5, color=GREY, style="italic")
    # force flow path
    path_ax = fig.add_axes([0.33,0.08,0.37,0.20]); path_ax.set_xlim(0,1); path_ax.set_ylim(0,1); path_ax.axis("off")
    path_ax.text(0.5,0.88,"FORCE FLOW PATH  (closes through structure)", ha="center", fontsize=5, weight=800, color=NAVY)
    steps = ["FIN","8×M5\nS11 SHELL", "8×M4\nBACK-IRON","2×M09\nBEARINGS","M01 TUBE","FUZE THREADS","SHELL"]
    for i,s in enumerate(steps):
        x=0.03 + i*0.136
        path_ax.add_patch(patches.FancyBboxPatch((x,0.32),0.12,0.32, boxstyle="round,pad=0.01", facecolor="white" if i!=3 else "#DBEAFE", edgecolor=NAVY if i!=3 else BLUE, lw=0.8))
        path_ax.text(x+0.06,0.48,s, ha="center", va="center", fontsize=4, weight=700, color=NAVY, linespacing=1.1)
        if i<6:
            path_ax.annotate("", xy=(x+0.12,0.48), xytext=(x+0.136,0.48), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1))
    path_ax.text(0.5,0.18,"1.3 kN centrifugal / fin → sizes S11 drum, M5, bearing preload (not servo)", ha="center", fontsize=4, color=GREY, style="italic", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#E2E8F0"))
    path_ax.text(0.5,0.06,"SLS AlSi10Mg S11 sleeves back-iron — replaceable printed interface (§2.5)", ha="center", fontsize=3.5, color=TEAL)
    # LIT inset
    lit_ax = fig.add_axes([0.72,0.08,0.26,0.20]); lit_ax.set_xlim(0,1); lit_ax.set_ylim(0,1); lit_ax.axis("off")
    lit_ax.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.01", facecolor="#FEF2F2", edgecolor=CORAL, lw=0.7, ls="--"))
    lit_ax.text(0.5,0.88,"LIT MICRO-THRUSTERS  §2.7", ha="center", fontsize=5, weight=900, color=CORAL)
    lit_ax.text(0.5,0.78,"8 stations in S11 wall (2/fin)", ha="center", fontsize=4, color=GREY)
    lit_ax.add_patch(patches.FancyBboxPatch((0.06,0.52),0.88,0.20, boxstyle="round,pad=0.01", facecolor="white", edgecolor=CORAL))
    lit_ax.text(0.07,0.62,"• 0.9 g /station  1 N·s (pair 2.1 N·s)\n• 85 N/50ms  8.4 N·s → Δv 0.18 m/s", fontsize=3.8, color=NAVY, va="center", linespacing=1.2)
    lit_ax.add_patch(patches.FancyBboxPatch((0.06,0.28),0.88,0.20, boxstyle="round,pad=0.01", facecolor="white", edgecolor=AMBER))
    lit_ax.text(0.07,0.38,"→ 7–10 m terminal trim\n  NOT 200–300 m replacement", fontsize=3.8, color="#8A6D00", va="center", linespacing=1.2)
    lit_ax.text(0.5,0.12,"solid — OFB energetics  •  backup if windmill/servo fails", ha="center", fontsize=3.5, color=GREY, style="italic")

    finalize(fig,"04_canard_physics")

# --------------------------------------------------------------------------
# 05 ENERGY LEDGER
# --------------------------------------------------------------------------
def gen_05():
    fig = plt.figure(figsize=(FW,FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax,"ENERGY LEDGER — IN FLIGHT, NO BATTERY BASELINE","875 J supercap  •  ~450 J generated ascent  •  ~344 J used  •  28–35% margin (§4/§5)", "05")

    # LEFT sankey style
    left = fig.add_axes([0.02,0.14,0.48,0.54]); left.set_xlim(0,100); left.set_ylim(0,100); left.axis("off")
    left.set_facecolor("#F8FAFC")
    left.add_patch(patches.FancyBboxPatch((0,0),100,100, boxstyle="round,pad=0.01", facecolor="#F8FAFC", edgecolor="#DDE6F2", lw=0.8))
    left.text(50,94,"ENERGY FLOW  30 km nominal (§4)", ha="center", fontsize=7, weight=800, color=NAVY)
    # blocks
    left.add_patch(patches.FancyBboxPatch((5,64),28,22, boxstyle="round,pad=0.02", facecolor=TEAL, edgecolor=TEAL))
    left.text(19,79,"GENERATED", ha="center", fontsize=5.5, weight=900, color="white")
    left.text(19,74,"~465 J", ha="center", fontsize=9, weight=900, color="white")
    left.text(19,68,"12W×44s 85% +15J regen", ha="center", fontsize=4, color="white", alpha=0.9)
    # supercap center
    left.add_patch(patches.FancyBboxPatch((38,62),24,26, boxstyle="round,pad=0.02", facecolor=NAVY, edgecolor=NAVY))
    left.text(50,82,"SUPERCAP", ha="center", fontsize=5.5, weight=800, color=GOLD)
    left.text(50,77,"0.6F @54V", ha="center", fontsize=4.5, color="white")
    left.text(50,72,"875 J", ha="center", fontsize=9, weight=900, color="white")
    left.text(50,66,"535 usable\n54→20V", ha="center", fontsize=4, color="#B8C5D6", linespacing=1.1)
    # flows
    left.annotate("", xy=(38,75), xytext=(33,75), arrowprops=dict(arrowstyle="->", color=NAVY, lw=2.2, mutation_scale=12))
    # branches to consumers
    consumers = [
        (72,84,"ELECTRONICS\n220 J", "2.4W×92s\nGPS 1.2 IMU 0.4 MCU 0.3", AMBER),
        (72,64,"HOVER HOLD\n84 J", "2W×42s  2.1A\ncopper only", CORAL),
        (72,40,"SLEWS\n40 J", "8×5 J  90°/0.15s\n0.8J mech +I²R", "#9333EA"),
        (72,20,"VNS\n10 J", "1.2W×8s\nterminal 2km", GOLD),
    ]
    for (x,y,txt,sub,col) in consumers:
        left.add_patch(patches.FancyBboxPatch((x-15, y-8),30,16, boxstyle="round,pad=0.01", facecolor="white", edgecolor=col, lw=1))
        left.text(x, y+2, txt, ha="center", fontsize=4.5, weight=800, color=NAVY, linespacing=1.1)
        left.text(x, y-4, sub, ha="center", fontsize=3.3, color=GREY, linespacing=1.1)
        # line from cap to consumer
        left.plot([62,72-15],[75,y], color=NAVY, lw=1.0, alpha=0.6, ls="--")
    left.add_patch(patches.FancyBboxPatch((72-15,5),30,12, boxstyle="round,pad=0.01", facecolor="#ECFDF5", edgecolor=TEAL, lw=0.9))
    left.text(72,11,"MARGIN ~28%\ncap never empty", ha="center", fontsize=5, weight=800, color=TEAL)
    left.text(72,6,"end 310J /875  window 50→20V", ha="center", fontsize=3.5, color=GREY, style="italic")
    left.plot([62,72-15],[75,11], color=TEAL, lw=1.2)
    # sensitivity boxes at bottom of left panel
    left.text(50,2,"20km: gen360 vs 270J 25%  •  40km: 590 vs 470J 20%  → closes across board (§4)", ha="center", fontsize=3.8, color=GREY, style="italic")

    # RIGHT bar + cap gauge
    right = fig.add_axes([0.52,0.14,0.46,0.54]); right.axis("off")
    # stacked bar
    bar_ax = fig.add_axes([0.54,0.32,0.28,0.36]); bar_ax.set_facecolor("white")
    bar_ax.set_xlim(0,1.6); bar_ax.set_ylim(0,950)
    bar_ax.set_xticks([]); bar_ax.grid(True, axis="y", color="#EEF2F7", ls="-", lw=0.8)
    # cap total
    bar_ax.add_patch(patches.Rectangle((0.1,0),0.35,875, facecolor="#E8EEF6", edgecolor=NAVY, hatch="///", alpha=0.5))
    bar_ax.text(0.275,890,"BANK 875 J", ha="center", fontsize=6, weight=700, color=NAVY)
    # usable
    bar_ax.add_patch(patches.Rectangle((0.6,0),0.35,535, facecolor=TEAL, edgecolor=TEAL, alpha=0.85))
    bar_ax.text(0.775,550,"USABLE\n535 J", ha="center", fontsize=5, weight=800, color="white")
    bar_ax.text(0.775,505,"54→20V 85% conv", ha="center", fontsize=4, color="white", alpha=0.9, style="italic")
    # used
    # segment stacked inside usable
    segments = [(0,220,AMBER,"ELEC 220"),(220,84,CORAL,"HOLD 84"),(304,40,"#7C3AED","SLEW 40"),(344,10,GOLD,"VNS 10")]
    y0=0
    for (yo, h, col, lab) in segments:
        bar_ax.add_patch(patches.Rectangle((0.6,yo),0.35,h, facecolor=col, edgecolor="white", lw=0.8))
        bar_ax.text(1.15, yo+h/2, lab, fontsize=4.5, color=col, weight=700, ha="left", va="center")
        bar_ax.text(0.775, yo+h/2, f"{h}", fontsize=5, weight=900, color="white", ha="center", va="center")
    bar_ax.text(0.775,360,"USED 344 J", ha="center", fontsize=6, weight=900, color=NAVY, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=NAVY))
    bar_ax.annotate("", xy=(0.95,535), xytext=(1.05,875), arrowprops=dict(arrowstyle="<->", color=GREY))
    bar_ax.text(1.12,700,"RESERVE\n340J", ha="center", fontsize=4, color=GREY, style="italic", rotation=90, va="center")
    bar_ax.set_ylabel("ENERGY  J", fontsize=6, color=GREY, weight=600)
    # gauge
    gauge_ax = fig.add_axes([0.84,0.32,0.13,0.36]); gauge_ax.set_xlim(0,1); gauge_ax.set_ylim(0,1); gauge_ax.axis("off")
    gauge_ax.add_patch(patches.Circle((0.5,0.35),0.36, facecolor="none", edgecolor="#E2E8F0", lw=8))
    # progress arc 35% -> 126 deg from -90? simpler pie
    gauge_ax.add_patch(patches.Wedge((0.5,0.35),0.36, -90, -90+126, facecolor=TEAL, edgecolor="white", lw=1))
    gauge_ax.add_patch(patches.Wedge((0.5,0.35),0.36, -90+126, 270, facecolor="#E2E8F0", edgecolor="white", lw=0.5))
    gauge_ax.add_patch(patches.Circle((0.5,0.35),0.22, facecolor="white", edgecolor="#E2E8F0", lw=1))
    gauge_ax.text(0.5,0.42,"35%", ha="center", fontsize=14, weight=900, color=NAVY)
    gauge_ax.text(0.5,0.30,"MARGIN", ha="center", fontsize=5, weight=700, color=GREY)
    gauge_ax.text(0.5,0.88,"END-OF-FLIGHT", ha="center", fontsize=6, weight=800, color=NAVY)
    gauge_ax.text(0.5,0.80,"310 J / 875 J", ha="center", fontsize=5, color=GREY)
    gauge_ax.text(0.5,0.08,"sim median\nsim 28.5m CEP", ha="center", fontsize=4, color=GREY, style="italic")
    # bottom specs
    spec_ax = fig.add_axes([0.02,0.055,0.96,0.065]); spec_ax.axis("off")
    spec_ax.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    items = ["EDLC annular-wound  Ø49/31×30 + bus discs", "20×2.7V cells  0.6F", "No chemistry → g-hard 15k g", "Leak %/day irrelevant (charged in flight)", ">15 y shelf", "Battery-free — 40g Li-SOCl2 optional footprint §8"]
    for i,txt in enumerate(items):
        x=0.01 + i*0.166
        spec_ax.add_patch(patches.FancyBboxPatch((x,0.18),0.16,0.64, boxstyle="round,pad=0.005", facecolor="white", alpha=0.10, edgecolor="white"))
        spec_ax.text(x+0.08,0.5, txt, ha="center", va="center", fontsize=4, color="white", weight=500, linespacing=1.1)
    # top note
    fig.text(0.5,0.72, "Actuator (Ó regen 155 J @10,687 rpm) recovers ½ Iω²×0.55 vs spec 15–25J @4,500 rpm — favourable (§10.14)   •   Electronics live off rectifier ascent, cap sole descent", ha="center", fontsize=4.5, color=GREY, style="italic", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#DDE6F2"))

    finalize(fig,"05_energy_ledger")

# --------------------------------------------------------------------------
# 06 CAD STACK (vertical)
# --------------------------------------------------------------------------
def gen_06():
    fig = plt.figure(figsize=(FW,FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax,"CANONICAL CAD STACK — GLOBAL Z  (datum z=125 shell nose)","Ø30 bore keep-clear  •  Envelope Ø50.8 (z<125) / Ø110 (z125-220)  •  Verified 0 clashes, bore clear  [cad_models/README.md]", "06")

    # vertical stack diagram centered
    stack_ax = fig.add_axes([0.28,0.08,0.44,0.78]); stack_ax.set_xlim(-55,55); stack_ax.set_ylim(-12,228); stack_ax.axis("off")
    stack_ax.set_facecolor("#FBFCFE")
    # zones background
    stack_ax.add_patch(patches.Rectangle((-55,0),110,125, facecolor="#FFF7ED", alpha=0.6)) # fuze well
    stack_ax.add_patch(patches.Rectangle((-55,125),110,95, facecolor="#EFF6FF", alpha=0.6)) # PGK
    stack_ax.text(-52, 62, "FUZE WELL\nØ50.8\nz 0→125", fontsize=4.5, color="#9A3412", weight=700, va="center", bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#FDBA74", alpha=0.8))
    stack_ax.text(-52, 172, "PGK\nØ110\nz125→220", fontsize=4.5, color=BLUE, weight=700, va="center", bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="#93C5FD", alpha=0.8))
    # bore
    stack_ax.add_patch(patches.Rectangle((-15,0),30,173, facecolor=NAVY, alpha=0.08, edgecolor=NAVY, ls="--", lw=0.7))
    stack_ax.text(0, 5, "Ø30 THRU-BORE\nRESERVED", ha="center", fontsize=3.5, color=NAVY, weight=700, alpha=0.7)
    # datum line
    stack_ax.plot([-55,55],[125,125], color=GOLD, lw=1.2, ls="--")
    stack_ax.add_patch(patches.FancyBboxPatch((-18,125-4),36,8, boxstyle="round,pad=0.01", facecolor=GOLD, edgecolor=GOLD))
    stack_ax.text(0,125,"DATUM z=125", ha="center", va="center", fontsize=4, weight=900, color="white")
    # envelope
    stack_ax.plot([-55,55],[0,0], color=GREY, lw=0.8); stack_ax.plot([-55,55],[220,220], color=GREY, lw=0.8)
    stack_ax.text(52,2,"z0", ha="right", fontsize=4, color=GREY); stack_ax.text(52,218,"z220 tip", ha="right", fontsize=4, color=GREY)
    # parts blocks (x width ~35 for housing, centered)
    # S10 fuze stack zone
    def block(z0,z1, txt, sub, col, w=34, x0=-17):
        h=z1-z0
        stack_ax.add_patch(patches.FancyBboxPatch((x0,z0),w,h, boxstyle="round,pad=0.01", facecolor=col, edgecolor=NAVY, lw=0.8, alpha=0.95))
        stack_ax.text(x0+w/2, (z0+z1)/2+2, txt, ha="center", va="center", fontsize=4.5, weight=800, color="white", linespacing=1.1)
        stack_ax.text(x0+w/2, (z0+z1)/2-4, sub, ha="center", va="center", fontsize=3, color="white", alpha=0.9, style="italic")
        # z labels
        stack_ax.text(x0+w+2, z0, f"{z0}", fontsize=3.5, color=GREY, va="bottom")
        stack_ax.text(x0+w+2, z1, f"{z1}", fontsize=3.5, color=GREY, va="top")
    block(0,19,"THREAD RING","steel Ø37/50.8 142g", "#475569", w=32)
    block(19,68,"FUZE HOUSING","7075 Ø30/50.8 78g", "#64748B")
    # internals inside housing small
    stack_ax.add_patch(patches.Rectangle((-13,22),26,12, facecolor="#FEF3C7", edgecolor=AMBER, lw=0.6))
    stack_ax.text(0,28,"TRAIN Ø20/26 15g", ha="center", fontsize=3, color="#92400E")
    stack_ax.add_patch(patches.Rectangle((-14,34),28,6, facecolor="#FECACA", edgecolor=CORAL, hatch="///"))
    stack_ax.text(0,37,"S&A ROTOR Ø28 29g", ha="center", fontsize=3, color="#991B1B", weight=700)
    stack_ax.add_patch(patches.Rectangle((-23,46),46,1.6, facecolor="#A7F3D0", edgecolor=TEAL))
    stack_ax.text(0,48,"Firing PCB Ø46", ha="center", fontsize=2.8, color=TEAL)
    stack_ax.add_patch(patches.Rectangle((-17,64),34,2, facecolor="#BFDBFE", edgecolor=BLUE))
    stack_ax.text(0,65,"Connector 2.2g", ha="center", fontsize=2.8, color=BLUE)
    # S09 caps
    block(68.5,101.5,"S09 CAPS","ANNULAR 0.6F/54V 67g\nØ49/31×30", TEAL, w=30, x0=-15)
    stack_ax.add_patch(patches.Rectangle((-15,80),30,6, facecolor="white", alpha=0.25, edgecolor="white", ls=":"))
    # M01 tube endbell etc
    block(125,130,"M10 AFT ENDBELL","Ø52/70 22.9g  (fwd deleted→S11)", "#0F172A", w=24, x0=-12)
    stack_ax.add_patch(patches.Rectangle((-20,130),40,8, facecolor="#94A3B8", edgecolor=NAVY, hatch="///", alpha=0.9))
    stack_ax.text(22,134,"M09 z130", fontsize=3, color=GREY, va="center")
    # stator rotor zone
    block(136,172.5,"S11 SHELL","SLS AlSi10Mg Ø76 82.9g\nsleeves rotor, 4 fins +8 LIT", "#1E40AF", w=38, x0=-19)
    # stator inside S11
    stack_ax.add_patch(patches.Rectangle((-29,138),58,25, facecolor="#FEF3C7", edgecolor=AMBER, ls="--", alpha=0.9))
    stack_ax.add_patch(patches.Rectangle((-26,139.5),52,22, facecolor="#FDE68A", edgecolor=AMBER, alpha=0.7))
    stack_ax.text(0,150,"STATOR S01+S02", ha="center", fontsize=3, color="#92400E", weight=700)
    stack_ax.text(0,145,"12T  Ø40–58.5  243g", ha="center", fontsize=2.8, color=GREY)
    stack_ax.add_patch(patches.Rectangle((-35,138),70,25, facecolor="none", edgecolor=CORAL, lw=1.2, ls=":"))
    stack_ax.text(35,162,"ROTOR S04 199g\nØ60–70 + bias ring z163-166", ha="left", fontsize=3, color=CORAL, style="italic")
    # fins
    stack_ax.add_patch(patches.Rectangle((-54,138),8,25, facecolor=TEAL, edgecolor=NAVY))
    stack_ax.add_patch(patches.Rectangle((46,138),8,25, facecolor=TEAL, edgecolor=NAVY))
    stack_ax.text(-50,150,"FIN", fontsize=3, color="white", weight=800, rotation=90, ha="center", va="center")
    stack_ax.text(50,150,"FIN", fontsize=3, color="white", weight=800, rotation=90, ha="center", va="center")
    stack_ax.text(0,136,"138", fontsize=3, color=GREY); stack_ax.text(0,172,"172.5", fontsize=3, color=GREY)
    stack_ax.add_patch(patches.Rectangle((-20,166),40,4, facecolor="#94A3B8", edgecolor=NAVY, hatch="///"))
    stack_ax.text(22,168,"M09 z166", fontsize=3, color=GREY, va="center")
    # control ring + radome
    block(173,175,"FLANGE","Radome base Ø42–76", "#334155", w=38, x0=-19)
    block(175,176.6,"RING PCB","Ø69.8 12.2g FR4", "#475569", w=34, x0=-17)
    block(176.6,184.8,"SHIELD CAN","Al Ø59.6 5.0g + 6 int.", "#1E293B", w=30, x0=-15)
    # interior hint
    stack_ax.add_patch(patches.Rectangle((-14,178),28,4, facecolor="#E0E7FF", edgecolor=BLUE, lw=0.6))
    stack_ax.text(0,180,"Inner PCB Ø56 5.5g GNSS/MCU/FRAM", ha="center", fontsize=2.5, color=NAVY)
    stack_ax.add_patch(patches.Rectangle((-13,182),26,2, facecolor="#FEF3C7", edgecolor=AMBER, lw=0.6))
    stack_ax.text(0,183,"Upper PCB Ø54 PwrMux", ha="center", fontsize=2.5, color="#92400E")
    block(185.5,191.5,"COUPLER","Ferrite Ø42/57 34.5g", "#F59E0B", w=28, x0=-14)
    stack_ax.add_patch(patches.Rectangle((-21,173),42,47, facecolor="none", edgecolor="#94A3B8", ls="--", lw=0.8))
    stack_ax.text(0,216,"RADOME GFRP 53.6g\nogive ρ48.63 tip r2", ha="center", fontsize=3.5, color="#475569", style="italic")

    # RIGHT specs panel
    right = fig.add_axes([0.74,0.08,0.24,0.78]); right.axis("off")
    right.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.015", facecolor="white", edgecolor=NAVY, lw=1.2))
    right.text(0.5,0.97,"MASS ROLLUP  CAD VOLUMES", ha="center", fontsize=6, weight=900, color=NAVY)
    mass_rows=[
        ("Motor+shell §2.1", "723 g"),
        ("S09 caps", "67 g"),
        ("S07 radome", "99 g"),
        ("S08 control ring", "35.4 g"),
        ("S10 fuze stack", "269 g"),
        ("PGK total", "~1.20 kg"),
        ("Host H01 M795", "46.84 kg"),
        ("Mated round", "~48.0 kg  872mm"),
    ]
    for i,(a,b) in enumerate(mass_rows):
        y=0.92 - i*0.055
        is_total = i==5
        right.add_patch(patches.FancyBboxPatch((0.05,y-0.02),0.9,0.042, boxstyle="round,pad=0.01", facecolor="#ECFDF5" if is_total else ("#F8FAFC" if i%2==0 else "white"), edgecolor=TEAL if is_total else "#E2E8F0", lw=0.7))
        right.text(0.07,y,a, fontsize=4.5, color=NAVY, weight=800 if is_total else 600, va="center")
        right.text(0.93,y,b, fontsize=4.5, color=TEAL if is_total else NAVY, weight=800, ha="right", va="center")
    right.text(0.5,0.48,"DIMENSIONS", ha="center", fontsize=6, weight=800, color=NAVY)
    dim_rows=[
        ("Through bore", "Ø30  0→173"),
        ("Shaft tube M01", "Ø30/40 125→175"),
        ("Stator S01", "Ø40–58.5 138→163"),
        ("Rotor + bias ring", "Ø60–70 138→166"),
        ("Air gap", "0.75 mm"),
        ("Fins S05/S06", "Ø76→108  t2.5"),
        ("Envelope", "Ø108.0  z0–220"),
        ("Thread", '2"-12 UNEF-2A'), 
    ]
    for i,(a,b) in enumerate(dim_rows):
        y=0.44 - i*0.038
        right.add_patch(patches.FancyBboxPatch((0.05,y-0.015),0.9,0.03, boxstyle="round,pad=0.01", facecolor="#F8FAFC" if i%2==0 else "white", edgecolor="#E2E8F0", lw=0.5))
        right.text(0.07,y,a, fontsize=3.8, color=GREY, va="center")
        right.text(0.93,y,b, fontsize=3.8, color=NAVY, weight=700, ha="right", va="center")
    right.text(0.5,0.08,"All bodies global coords\n1 Body / file  •  App::Link identity\n0 clashes @0/90/180/270", ha="center", fontsize=3.8, color=GREY, style="italic", bbox=dict(boxstyle="round,pad=0.15", fc="#F1F5F9", ec="#CBD5E1"))

    # LEFT legend
    left_leg = fig.add_axes([0.02,0.08,0.24,0.78]); left_leg.axis("off")
    left_leg.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.015", facecolor="white", edgecolor="#CBD5E1", lw=0.7))
    left_leg.text(0.5,0.97,"ENVELOPE & RULES", ha="center", fontsize=6, weight=900, color=NAVY)
    left_leg.text(0.07,0.92,"Design of record  PGK_SPEC_SHEET + PGK_Motor_Assembly.FCStd", fontsize=3.8, color=NAVY, weight=700, va="top", wrap=True)
    left_leg.text(0.07,0.88,"Datum z=125 = shell nose surface (envelope zones)", fontsize=3.5, color=GREY, va="top")
    rules=[
        "Ø30 bore NEVER intrude — explosive train only",
        "One PartDesign Body per file in parts/",
        "LinkPlacement mirrors Placement — never both",
        "S-series current; M02/M03/M05–M08 DUAL ref only",
        "S11 replaces spars/carrier disc & fwd endbell",
        "Envelope zones + bore gate before release",
    ]
    for i,r in enumerate(rules):
        y=0.83 - i*0.055
        left_leg.add_patch(patches.FancyBboxPatch((0.06,y-0.02),0.04,0.04, boxstyle="round,pad=0.005", facecolor=TEAL if i<2 else (AMBER if i==5 else NAVY), edgecolor="white"))
        left_leg.text(0.12,y,r, fontsize=3.8, color=NAVY, va="center")
    left_leg.text(0.5,0.42,"INTERFACE CHECK", ha="center", fontsize=5, weight=800, color=NAVY)
    left_leg.add_patch(patches.FancyBboxPatch((0.05,0.22),0.9,0.18, boxstyle="round,pad=0.01", facecolor="#ECFDF5", edgecolor=TEAL, lw=0.8))
    left_leg.text(0.5,0.37,"✓  Assembly gate\n0 clashes (4 phases)\nexcl. winding wrap\n✓  Bore clear\n✓  Ø108 < Ø110  z0–220\n✓  Mated shell H01\ninterference NONE", ha="center", fontsize=4, color=NAVY, weight=600, linespacing=1.3)
    left_leg.text(0.5,0.14,"Open: bearing-B outer\ncapture fwd (§10.12)\n± LIT grain survival\n15.5k g + 258 rev/s", ha="center", fontsize=3.5, color=CORAL, style="italic", bbox=dict(boxstyle="round,pad=0.15", fc="#FEF2F2", ec="#FECACA"))

    finalize(fig,"06_cad_stack")

# --------------------------------------------------------------------------
# 07 CORRECTION CEP
# --------------------------------------------------------------------------
def gen_07():
    fig = plt.figure(figsize=(FW,FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax,"CORRECTION AUTHORITY — VERIFIED IN SIM (POINT-MASS 3DOF, 100 MC)","Guided CEP 28.5 m vs 196 m unguided  •  7× improvement  •  Meets ≤30 m class  [sim/RESULTS_SINGLE_MACHINE.md]", "07")

    # load or simulate MC? reuse deterministic numbers from RESULTS
    # Bar chart left
    bar_ax = fig.add_axes([0.04,0.18,0.42,0.54]); bar_ax.set_facecolor("white")
    cats = ["CEP50\nmedian","mean","p90","max"]
    ung = [196,223,409,636]
    guid = [28.5,85.7,244.1,473.6]
    x=np.arange(len(cats))
    bar_ax.bar(x-0.18, ung, 0.36, color="#E2E8F0", edgecolor=NAVY, hatch="///", label="UNGUIDED")
    bar_ax.bar(x+0.18, guid, 0.36, color=CORAL, edgecolor=CORAL, label="GUIDED 20N q-scaled L0")
    for i,(u,g) in enumerate(zip(ung,guid)):
        bar_ax.text(i-0.18, u+12, f"{u:.0f}m", ha="center", fontsize=5, weight=700, color=NAVY)
        bar_ax.text(i+0.18, g+12, f"{g:.1f}m" if i==0 else f"{g:.0f}m", ha="center", fontsize=5, weight=800, color=CORAL)
        bar_ax.text(i, max(u,g)+45, f"{u/max(g,1e-9):.1f}×" if g>0 else "", ha="center", fontsize=4, color=TEAL, weight=800, bbox=dict(boxstyle="round,pad=0.12", fc="#ECFDF5", ec=TEAL, alpha=0.9))
    bar_ax.set_xticks(x); bar_ax.set_xticklabels(cats, fontsize=7, color=NAVY)
    bar_ax.set_ylabel("MISS DISTANCE  m  (from target)", fontsize=7, weight=600, color=GREY)
    bar_ax.set_ylim(0,750); bar_ax.grid(True, axis="y", color="#EEF2F7")
    bar_ax.legend(frameon=False, fontsize=6, loc="upper right")
    bar_ax.set_title("MONTE CARLO  N=100  disp v0 0.15% / aim 0.6mrad / wind 3m/s / Cd 0.8%", fontsize=5.5, color=GREY, style="italic", pad=12)
    # dispersion table
    disp_ax = fig.add_axes([0.04,0.055,0.42,0.11]); disp_ax.axis("off")
    disp_ax.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.01", facecolor="#F8FAFC", edgecolor="#DDE6F2"))
    disp_ax.text(0.02,0.72,"Deterministic guided cases  (single dispersions)", fontsize=5, weight=800, color=NAVY)
    rows=[("crosswind 6 m/s","207 → 39.3 m"),("headwind 6 m/s","327 → 160.9 m"),("muzzle +1.5","80 → 6.1 m"),("Cd +5%","850 → 690 m (aero limit)")]
    for i,(a,b) in enumerate(rows):
        x0=0.02 + (i%2)*0.50; y=0.42 if i<2 else 0.18
        disp_ax.add_patch(patches.FancyBboxPatch((x0,y-0.10),0.46,0.18, boxstyle="round,pad=0.01", facecolor="white", edgecolor="#E2E8F0"))
        disp_ax.text(x0+0.02,y, a, fontsize=3.8, color=GREY, va="center")
        disp_ax.text(x0+0.44,y, b, fontsize=4, color=CORAL if "→" in b else NAVY, weight=700, ha="right", va="center")
    # scatter simulation (generate synthetic around medians for visual)
    sc_ax = fig.add_axes([0.50,0.18,0.46,0.54]); sc_ax.set_aspect("equal")
    sc_ax.set_facecolor("#F8FAFC")
    np.random.seed(42)
    # generate synthetic hits roughly matching CEPs
    def synth(n, cep): 
        r = np.random.rayleigh(cep/1.18, n)  # approx
        ang = np.random.uniform(0,2*math.pi,n)
        return r*np.cos(ang), r*np.sin(ang)
    ux, uy = synth(120,196)
    gx, gy = synth(120,28.5)
    sc_ax.scatter(ux,uy, s=14, color="#94A3B8", alpha=0.55, edgecolor="white", linewidth=0.4, label="unguided")
    sc_ax.scatter(gx,gy, s=26, color=CORAL, alpha=0.85, edgecolor="white", linewidth=0.6, label="guided")
    sc_ax.add_patch(patches.Circle((0,0),28.5, facecolor="none", edgecolor=CORAL, lw=1.2, ls="--"))
    sc_ax.add_patch(patches.Circle((0,0),196, facecolor="none", edgecolor=NAVY, lw=1.0, ls=":", alpha=0.6))
    sc_ax.plot([0],[0], marker="+", color="black", markersize=10, markeredgewidth=1.5)
    sc_ax.text(0, -245, "TARGET", ha="center", fontsize=5, weight=800, color="black", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black"))
    sc_ax.set_xlim(-280,280); sc_ax.set_ylim(-280,280)
    sc_ax.set_xlabel("CROSS-RANGE  m", fontsize=6, color=GREY); sc_ax.set_ylabel("DOWN-RANGE  m", fontsize=6, color=GREY)
    sc_ax.grid(True, color="white", lw=1); sc_ax.grid(True, color="#E2E8F0", ls="--", lw=0.6)
    sc_ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", fontsize=6, loc="upper right")
    sc_ax.set_title("IMPACT SCATTER  synthetic Rayleigh matched to CEP  (fort/camp class target area)", fontsize=5.5, color=GREY, style="italic", pad=10)
    # inset improvement badge
    badge = fig.add_axes([0.73,0.62,0.12,0.12]); badge.axis("off")
    badge.add_patch(patches.Circle((0.5,0.5),0.45, facecolor=TEAL, edgecolor="white", lw=2, transform=badge.transAxes))
    badge.text(0.5,0.62,"7×", transform=badge.transAxes, ha="center", fontsize=14, weight=900, color="white")
    badge.text(0.5,0.38,"BETTER", transform=badge.transAxes, ha="center", fontsize=5, weight=800, color="white")
    # bottom fidelity note
    note_ax = fig.add_axes([0.50,0.055,0.46,0.11]); note_ax.axis("off")
    note_ax.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.01", facecolor="#FFFBEB", edgecolor=AMBER, lw=0.7))
    note_ax.text(0.02,0.75,"MODEL FIDELITY  next rung → 6DOF before PDR", fontsize=5, weight=800, color="#92400E")
    note_ax.text(0.02,0.52,"Point-mass conservative: TOF 87.6 vs 92s spec, apogee 9.46 vs 11.5 km (exp atmo), impact 413 vs 300–350 (const Cd).", fontsize=3.8, color=GREY, va="top")
    note_ax.text(0.02,0.22,"Adds Magnus, carryover 1.2–1.4×, yaw-of-repose, precession chain, subsonic Cd rise — must stay ≤30m.", fontsize=3.8, color=GREY, va="top", style="italic")

    finalize(fig,"07_correction_CEP")

# --------------------------------------------------------------------------
# 08 TIMELINE
# --------------------------------------------------------------------------
def gen_08():
    fig = plt.figure(figsize=(FW,FH), dpi=DPI)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    add_header(ax,"MISSION TIMELINE — WHEN IT GENERATES, WHEN IT SWITCHES","Phase 0 inductive setter → in-bore dead → generator live 3s → apogee switch → correction → VNS terminal  [SPEC §3]", "08")

    # timeline canvas
    t_ax = fig.add_axes([0.04,0.22,0.92,0.54]); t_ax.set_xlim(-3.5,94); t_ax.set_ylim(0,6); t_ax.axis("off")
    t_ax.set_facecolor("#F8FAFC")
    # time axis
    t_ax.plot([-1,93],[0.8,0.8], color=NAVY, lw=1.8, solid_capstyle="round")
    for tt in [0,10,20,30,40,50,60,70,80,92]:
        t_ax.plot([tt,tt],[0.8,0.95], color=NAVY, lw=0.8)
        t_ax.text(tt,0.45,f"{tt}s", ha="center", fontsize=5, color=GREY, weight=600)
        t_ax.text(tt,0.15, str(tt), ha="center", fontsize=3.5, color=GREY)
    t_ax.text(93,0.8,"t", ha="left", va="center", fontsize=7, color=NAVY, weight=800)
    # Phase 0 block pre-launch
    t_ax.add_patch(patches.FancyBboxPatch((-3.2,1.6),2.8,2.2, boxstyle="round,pad=0.02", facecolor="#DBEAFE", edgecolor=BLUE, lw=1))
    t_ax.text(-1.8,3.4,"PHASE 0", ha="center", fontsize=5, weight=900, color=BLUE)
    t_ax.text(-1.8,2.85,"PRE-FIRE  60–90s\nSETTER ~1W 115k", ha="center", fontsize=3.2, color=NAVY, linespacing=1.1)
    t_ax.text(-1.8,2.15,"BIT • bias • tgt\n• eph → FRAM", ha="center", fontsize=2.8, color=GREY, style="italic", linespacing=1.1)
    t_ax.annotate("", xy=(0,2.5), xytext=(-0.4,2.5), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))
    t_ax.text(1.2,4.2,"POWER LATCHED OFF  → FRAM retains", ha="left", fontsize=3.8, color=BLUE, style="italic", bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=BLUE, alpha=0.9))
    # Phase A
    t_ax.add_patch(patches.FancyBboxPatch((0,1.6),0.6,2.2, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    t_ax.text(0.30,2.7,"A", ha="center", va="center", fontsize=5, weight=900, color="white", rotation=90)
    # Phase B muzzle
    t_ax.add_patch(patches.FancyBboxPatch((0.60,1.6),1.2,2.2, boxstyle="round,pad=0.01", facecolor="#334155", edgecolor=NAVY))
    t_ax.text(1.20,2.7,"B", ha="center", va="center", fontsize=4, color="white", weight=800)
    # Phase C ascent generator
    t_ax.add_patch(patches.FancyBboxPatch((1.80,2.2),44.0,2.2, boxstyle="round,pad=0.02", facecolor=TEAL, edgecolor=TEAL, alpha=0.95))
    t_ax.text(23.8,3.9,"C  ASCENT  —  GENERATOR  0→46 s", ha="center", fontsize=6, weight=900, color="white")
    t_ax.text(23.8,3.30,"windmill free-spins  •  3-phase 150–200V → active rectifier → 12W buck → supercap", ha="center", fontsize=3.4, color="white", alpha=0.95)
    t_ax.text(23.8,2.70,"q 392→13kPa  •  v 800→270  •  GPS 3–10s (eph preloaded)  •  trajectory solution", ha="center", fontsize=3.4, color="white")
    t_ax.add_patch(patches.FancyBboxPatch((4,1.6),8.5,0.55, boxstyle="round,pad=0.01", facecolor="#ECFDF5", edgecolor=TEAL, lw=0.7))
    t_ax.text(8.25,1.87,"REBOOT @2–3s\nbus, EKF from FRAM", ha="center", fontsize=2.8, color=TEAL, weight=700, linespacing=1.1)
    t_ax.add_patch(patches.FancyBboxPatch((13.2,1.6),30,0.55, boxstyle="round,pad=0.01", facecolor="#ECFDF5", edgecolor=TEAL, lw=0.7))
    t_ax.text(28.2,1.87,"CAP 10–15W  ≈412 J  •  FOC quiescent → GPS quiet", ha="center", fontsize=2.8, color=TEAL, weight=600)
    # Phase D brake
    t_ax.add_patch(patches.FancyBboxPatch((45.8,2.2),4.2,2.2, boxstyle="round,pad=0.02", facecolor=AMBER, edgecolor=AMBER))
    t_ax.text(47.9,3.9,"D", ha="center", fontsize=7, weight=900, color="white")
    t_ax.text(47.9,3.30,"APOGEE", ha="center", fontsize=4.5, weight=800, color="white")
    t_ax.text(47.9,2.70,"BRAKE\n2–4s 155J", ha="center", fontsize=3, color="white", weight=700, linespacing=1.1)
    t_ax.add_patch(patches.FancyBboxPatch((45.8,1.6),4.2,0.55, boxstyle="round,pad=0.01", facecolor="#FFFBEB", edgecolor=AMBER, lw=0.7))
    t_ax.text(47.9,1.87,"IMU v_z flip\nOR time", ha="center", fontsize=2.8, color="#92400E", weight=700, linespacing=1.1)
    # Phase E descent
    t_ax.add_patch(patches.FancyBboxPatch((50.0,2.2),42.0,2.2, boxstyle="round,pad=0.02", facecolor=CORAL, edgecolor=CORAL, alpha=0.95))
    t_ax.text(71,3.9,"E  DESCENT  —  ACTUATOR + CORRECTION  46→92 s", ha="center", fontsize=6, weight=900, color="white")
    t_ax.text(71,3.30,"servo-held hover 15–25N → precession 2.8°/s → 200–300m", ha="center", fontsize=3.4, color="white", alpha=0.95)
    t_ax.text(71,2.70,"q 13→50kPa  •  first slews 50–55s  •  cap sole 54→20V  •  IMU+mag+array→EKF", ha="center", fontsize=3, color="white")
    # VNS sub inside E
    t_ax.add_patch(patches.FancyBboxPatch((84,1.6),7.5,0.55, boxstyle="round,pad=0.01", facecolor="#FEFCE8", edgecolor=GOLD, lw=0.7, ls="--"))
    t_ax.text(87.75,1.87,"VNS 84–92s  2km\n1kfps gated 10J", ha="center", fontsize=2.6, color="#854D0E", weight=700, linespacing=1.1)
    t_ax.add_patch(patches.FancyBboxPatch((60,1.6),22,0.55, boxstyle="round,pad=0.01", facecolor="#FEF2F2", edgecolor=CORAL, lw=0.5))
    t_ax.text(71,1.87,"GPS tracking (acq before actuation)  •  FOC 16A isolated", ha="center", fontsize=2.8, color=CORAL, style="italic")
    # Phase F
    t_ax.add_patch(patches.FancyBboxPatch((92,1.6),1.4,2.2, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    t_ax.text(92.7,2.7,"F", ha="center", fontsize=5, weight=900, color="white")
    t_ax.text(93.8,4.6,"F IMPACT ~92s  300–350m/s\nfuze prox/impact\n+ self-destruct", ha="left", fontsize=3.2, color=NAVY, linespacing=1.1, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=NAVY))

    # middle band: power source + cpu
    mid = fig.add_axes([0.04,0.085,0.92,0.085]); mid.set_xlim(-2,94); mid.set_ylim(0,1); mid.axis("off")
    mid.add_patch(patches.FancyBboxPatch((-2,0),94,1, boxstyle="round,pad=0.01", facecolor="white", edgecolor="#DDE6F2", lw=0.7))
    mid.text(-1.5,0.82,"POWER SOURCE:", fontsize=4, weight=800, color=GREY, va="center")
    mid.add_patch(patches.FancyBboxPatch((3,0.55),42,0.32, boxstyle="round,pad=0.01", facecolor="#ECFDF5", edgecolor=TEAL, lw=0.6))
    mid.text(24,0.71,"RECTIFIED GENERATOR (ascent)  → cap charging in parallel  •  electronics live", ha="center", fontsize=3.8, color=TEAL, weight=600)
    mid.add_patch(patches.FancyBboxPatch((50,0.55),42,0.32, boxstyle="round,pad=0.01", facecolor="#FEF2F2", edgecolor=CORAL, lw=0.6))
    mid.text(71,0.71,"SUPERCAP SOLE (descent)  54→20V  •  actuator only after GPS solution stored", ha="center", fontsize=3.8, color=CORAL, weight=600)
    mid.text(-1.5,0.28,"CPU:", fontsize=4, weight=800, color=GREY, va="center")
    mid.add_patch(patches.FancyBboxPatch((3,0.08),20,0.28, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    mid.text(13,0.22,"FOC 20kHz current loops", ha="center", fontsize=3.5, color="white", weight=700)
    mid.add_patch(patches.FancyBboxPatch((25,0.08),20,0.28, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    mid.text(35,0.22,"Charge regulation 12W thr", ha="center", fontsize=3.5, color="white", weight=700)
    mid.add_patch(patches.FancyBboxPatch((47,0.08),20,0.28, boxstyle="round,pad=0.01", facecolor=NAVY, edgecolor=NAVY))
    mid.text(57,0.22,"Mode state machine", ha="center", fontsize=3.5, color="white", weight=700)
    mid.add_patch(patches.FancyBboxPatch((69,0.08),20,0.28, boxstyle="round,pad=0.01", facecolor="#1E2F4D", edgecolor=GOLD, lw=0.7))
    mid.text(79,0.22,"EKF + guidance L0", ha="center", fontsize=3.5, color=GOLD, weight=700)

    # top badge single-point failure
    fail_ax = fig.add_axes([0.71,0.79,0.25,0.11]); fail_ax.axis("off")
    fail_ax.add_patch(patches.FancyBboxPatch((0,0),1,1, boxstyle="round,pad=0.02", facecolor="#FEF2F2", edgecolor=CORAL, lw=0.9))
    fail_ax.text(0.5,0.75,"SINGLE-POINT ITEM  §10.3", ha="center", fontsize=5, weight=900, color=CORAL)
    fail_ax.text(0.5,0.48,"Windmill self-start = generation\nAND actuation — ≥0.999 needed", ha="center", fontsize=4, color=NAVY, linespacing=1.2)
    fail_ax.text(0.5,0.18,"if fails → no gen, no correction\n(fuze still via inertia)", ha="center", fontsize=3.5, color=GREY, style="italic", linespacing=1.1)

    finalize(fig,"08_mission_timeline")

# --------------------------------------------------------------------------
if __name__=="__main__":
    gen_01(); gen_02(); gen_03(); gen_04(); gen_05(); gen_06(); gen_07(); gen_08()
    print("\nAll 8 visuals done →", OUT)
