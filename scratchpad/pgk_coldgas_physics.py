import math

G = 9.80665
# ---- Guidance authority from YOUR sim ----
# sim_guidance_check.py: FIN_FORCE_NOM=60N on m=46kg shell, ZEM a=2*miss/t_go^2
m_shell = 46.0            # kg
a_guided = 60.0 / m_shell # m/s^2  (~1.3 m/s^2 = 0.13 g)
tof_guide = 55.0          # s, guidance-active window (lock 35s .. impact, sim: 90s TOF)
a_max = 3.0 * G           # simulate_trajectory_155.py A_MAX_G=3.0 -> hard cap 29.4 m/s^2

# Duty-cycle from the sim: median mean duty 0.21, peak 1.0
duty_mean = 0.21
# Available lateral Δv over guidance window (at mean duty)
dv_lat = a_guided * duty_mean * tof_guide
print(f"Guidance authority: {a_guided:.3f} m/s^2 = {a_guided/G:.2f} g  (60N/46kg)")
print(f"Lateral Δv available (mean duty, {tof_guide}s window): {dv_lat:.1f} m/s")
print(f"Peak authority (sim cap): {a_max:.1f} m/s^2 = {a_max/G:.1f} g")

# ---- Required Δv from ZEM: a = 2*miss/t_go^2, integrated over window ----
# For a miss M corrected over t_go, the impulse needed ≈ 2*M/t_go (rough)
for M, tg in [(200, 55), (100, 40), (50, 30), (20, 20)]:
    dv = 2*M/tg
    print(f"  miss {M:4d} m over t_go {tg:3d} s -> Δv ~ {dv:5.1f} m/s")

# ---- Cold-gas sizing (N2, blowdown) ----
# Tank internal volume available in fuze bore: reuse Ø35 bore x ~100 mm
for V_L, P0_bar in [(0.15, 300), (0.15, 200), (0.3, 300), (0.3, 200), (0.5, 300)]:
    V = V_L*1e-3  # m^3
    P0 = P0_bar*1e5
    m_gas = P0*V/(287.05*293.15)
    # isentropic blowdown to ~3 bar (usable expansion), T const approx -> mass usable
    # Isp ~ 60 s cold gas -> exhaust vel 60*G = 588 m/s
    Isp = 60.0
    # Delta-v of 46kg shell if ALL gas expelled at Isp:
    dv_max = Isp*G*math.log(1 + m_gas/m_shell)
    print(f"  tank {V_L:.2f}L @ {P0_bar} bar: gas {m_gas*1e3:6.1f} g -> Δv(all) {dv_max:5.1f} m/s")
