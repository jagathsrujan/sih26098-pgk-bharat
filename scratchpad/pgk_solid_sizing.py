import math
G=9.80665
m_shell=46.0
# ---- Solid gas generator sizing ----
# Grain density ~1.7 g/cm3, Isp 200-250 s (AP/HTPB-ish or gas-generant like a mini PRM)
rho_grain = 1700.0  # kg/m3
for Isp, name in [(200,'AP/HTPB'), (250,'high-energy'), (150,'gas-generant')]:
    # required prop mass for 15 m/s dv (same as cold-gas mission, at better Isp)
    # rocket eq: dv = Isp*g*ln(1+m_p/m_s)  (m_s=46kg, dv=15)
    m_p = m_shell*(math.exp(15.0/(Isp*G))-1)
    V = m_p/rho_grain
    # cylinder in 0.15L bore: length for Ø35
    L = V/(math.pi*0.0175**2)
    print(f"{name:12s} Isp={Isp:3d}s: m_p={m_p*1e3:6.1f} g  V={V*1e6:7.0f} cm3  in Ø35 bore: L={L*1e3:5.1f} mm")
print()
print("=== Single-face fire at 60N, one face at a time ===")
print("Total prop for 15 m/s @ single-face (4x worse than simultaneous-all):")
Isp=200
m_p_single = 4*m_shell*(math.exp(15.0/(Isp*G))-1)
print(f"  @ Isp 200s: {m_p_single*1e3:.0f} g = {m_p_single/1700*1e6:.0f} cm3")
print()
print("=== If we relax authority to what 0.15L bore can hold ===")
# 0.15L = 150 cm3, at 1.7g/cm3 = 255g grain, at Isp 200s -> dv
m_grain = 0.15*1e-3*1700
dv = Isp*G*math.log(1+m_grain/m_shell)
print(f"  0.15L @ 1.7g/cm3 = {m_grain*1e3:.0f} g grain -> dv = {dv:.1f} m/s (vs 15 m/s needed)")
# what authority does that dv give over 55s?
print(f"  -> avg accel over 55s window = {dv/55:.2f} m/s^2 = {dv/55/G:.2f} g")
