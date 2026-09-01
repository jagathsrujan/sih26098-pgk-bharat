import math
G=9.80665; R=287.05
m_shell=46.0

def isentropic_throat(P0, T0, k, M, A_t):
    # choked: rho*a*A_t
    rho0 = P0/(R*T0)
    a0 = math.sqrt(k*R*T0)
    # rho* at throat
    rho_star = rho0*(2/(k+1))**(1/(k-1))
    a_star = a0*math.sqrt(2/(k+1))
    return rho_star*a_star*A_t

print("=== Single-face firing: all 3 nozzles of ONE canard face ===")
print("RCS force = mdot * Isp_eff * G (Isp_eff=60s cold gas), single jet on one side")
print()
for P0_bar in [100, 200, 300]:
    for dt in [0.5, 1.0]:
        # required mdot for 60N
        mdot = 60.0/(60*G)
        m_shot = mdot*dt
        print(f"  P0={P0_bar:3d}bar: 60N for {dt:.1f}s needs {m_shot*1e3:5.1f} g N2 per shot")

print()
print("=== Throat diameter for a single nozzle pair delivering 60N ===")
print("(3 nozzles per face share the load)")
for P0_bar in [100,200,300]:
    T0=293.15; k=1.4
    mdot=60.0/(60*G)   # kg/s
    A_t = mdot/( (P0_bar*1e5/(R*T0)) * (2/(k+1))**(1/(k-1)) * math.sqrt(k*R*T0)*math.sqrt(2/(k+1)) )
    d = math.sqrt(4*A_t/math.pi)*1000
    d_each = d/math.sqrt(3)
    print(f"  P0={P0_bar:3d}bar: total throat {d:6.2f} mm -> per-nozzle (3 nozzles) {d_each:6.2f} mm")

print()
print("=== Tank sizing for mission: 60N authority, 0.21 mean duty, 55s window ===")
print("= 15 m/s Δv budget = mdot_total = 60*0.21*55/(60*G) ...")
mdot_total = 60.0*0.21*55.0/(60*G)
m_gas_needed = mdot_total  # kg
print(f"  gas mass needed (all 8 faces, at mean duty): {m_gas_needed*1e3:.0f} g N2")
for P0_bar in [100,200,300]:
    # blowdown from P0 to 3bar, isothermal-ish in tank
    V = m_gas_needed*R*293.15/((P0_bar-3)*1e5)
    print(f"  @ {P0_bar:3d}bar: V = {V*1e3:6.1f} L  (fuze bore 0.15L is {('TIGHT' if V>0.15 else 'OK')})")
