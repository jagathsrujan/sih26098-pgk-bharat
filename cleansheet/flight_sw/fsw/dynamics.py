"""FSW plant model — the on-board copy of the 3DOF dynamics and small math
primitives. This is knowledge the flight software legitimately owns: the IPP
must propagate "the same dynamics as truth" (04_GNC_METHODOLOGY.md §3.3), and
the ctrl task needs the dynamic-pressure model for authority scaling.

Ported verbatim (numerics identical) from scripts/sim_gnc_check.py:
rho / accel / rk4_step / rk2_step / propagate / initial_state / q_dyn /
rot2 / wrap_pi. The co-sim harness imports the sim's own copies for the truth
side; tests assert equality of both implementations on golden vectors.

FSW code never imports the sim — this file is the FSW's single source.
"""
import math

from . import config as C


def wrap_pi(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def rot2(psi, v):
    c, s = math.cos(psi), math.sin(psi)
    return (c * v[0] - s * v[1], s * v[0] + c * v[1])


def rho(z):
    return C.RHO0 * math.exp(-max(z, 0.0) / C.HSCALE)


def q_dyn(s):
    z = max(s[2], 0.0)
    return 0.5 * rho(z) * (s[3] * s[3] + s[4] * s[4] + s[5] * s[5])


def accel(state, cd, wind):
    _, _, z, vx, vy, vz = state
    rvx = vx - wind[0]
    rvy = vy - wind[1]
    vr = math.sqrt(rvx * rvx + rvy * rvy + vz * vz)
    if vr < 1e-6:
        return (0.0, 0.0, -C.G)
    k = 0.5 * rho(z) * cd * C.AREA * vr / C.M_NOM
    return (-k * rvx, -k * rvy, -k * vz - C.G)


def rk4_step(state, dt, cd, wind, a_lat=(0.0, 0.0)):
    def f(s):
        ax, ay, az = accel(s, cd, wind)
        return (s[3], s[4], s[5], ax + a_lat[0], ay + a_lat[1], az)
    k1 = f(state)
    k2 = f(tuple(state[i] + 0.5 * dt * k1[i] for i in range(6)))
    k3 = f(tuple(state[i] + 0.5 * dt * k2[i] for i in range(6)))
    k4 = f(tuple(state[i] + dt * k3[i] for i in range(6)))
    return tuple(state[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(6))


def rk2_step(state, dt, cd, wind):
    def f(s):
        ax, ay, az = accel(s, cd, wind)
        return (s[3], s[4], s[5], ax, ay, az)
    k1 = f(state)
    k2 = f(tuple(state[i] + dt * k1[i] for i in range(6)))
    return tuple(state[i] + 0.5 * dt * (k1[i] + k2[i]) for i in range(6))


def initial_state(v0, elev, azim):
    vh = v0 * math.cos(elev)
    return (0.0, 0.0, 0.0, vh * math.cos(azim), vh * math.sin(azim), v0 * math.sin(elev))


def propagate_to_ground(state0, cd, wind, dt):
    """RK4 propagation to ground impact. Used by the IPP (dt = DT_IPP) and by
    the pre-flight q-profile generation (dt = DT_TRUTH). Verbatim port of the
    sim's propagate()."""
    s = state0
    if s[2] <= 0 and s[5] <= 0:
        return s[0], s[1], 0.0, 0.0
    t = 0.0
    apo = s[2]
    while t < C.TMAX:
        apo = max(apo, s[2])
        s_prev = s
        s = rk4_step(s, dt, cd, wind)
        t += dt
        if s[2] <= 0 < s_prev[2]:
            f = s_prev[2] / (s_prev[2] - s[2])
            x_imp = s_prev[0] + f * dt * s[3]
            y_imp = s_prev[1] + f * dt * s[4]
            return x_imp, y_imp, (t - dt) + f * dt, apo
    raise RuntimeError("no impact")


def q_profile(cd_cal, dt=C.DT_TRUTH):
    """Nominal dynamic-pressure profile q(t) (pre-flight loaded reference)."""
    s = initial_state(C.V0_NOM, C.ELEV0, 0.0)
    t = 0.0
    out = []
    while t < C.TMAX:
        out.append(q_dyn(s))
        s_prev = s
        s = rk4_step(s, dt, cd_cal, (0.0, 0.0))
        t += dt
        if s[2] <= 0 < s_prev[2]:
            out.append(0.0)
            break
    return out


def q_at(qprof, t):
    i = int(t / C.DT_TRUTH)
    return qprof[i] if 0 <= i < len(qprof) else 0.0


def q70_ref(cd_cal):
    """Nominal q at the 60 N reference epoch (pre-flight)."""
    s = initial_state(C.V0_NOM, C.ELEV0, 0.0)
    t = 0.0
    while t < C.TMAX:
        t_next = t + C.DT_TRUTH
        if t_next >= C.Q_REF_T:
            f = (C.Q_REF_T - t) / C.DT_TRUTH
            z = s[2] + f * C.DT_TRUTH * s[5]
            v = math.sqrt(s[3] ** 2 + s[4] ** 2 + s[5] ** 2)
            return 0.5 * rho(max(z, 0.0)) * v * v
        s = rk4_step(s, C.DT_TRUTH, cd_cal, (0.0, 0.0))
        t = t_next
    raise RuntimeError("q70 fail")
