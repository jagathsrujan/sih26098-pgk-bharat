"""Step-2 assert-script: fsw.config must match the Rev E constants blocks of
scripts/sim_gnc_check.py EXACTLY (paired-numerics contract)."""
import math

import pytest

import fsw.config as C


def test_constants_match_sim():
    sim = pytest.importorskip("sim_gnc_check")
    pairs = [
        # shared block
        ("G", C.G), ("RHO0", C.RHO0), ("HSCALE", C.HSCALE), ("M_NOM", C.M_NOM),
        ("D", C.D), ("AREA", C.AREA), ("V0_NOM", C.V0_NOM), ("ELEV0", C.ELEV0),
        ("RANGE_TARGET", C.RANGE_TARGET),
        ("T_LOCK_NOM", C.T_LOCK_NOM), ("T_DESPIN_START", C.T_DESPIN_START),
        ("T_DESPIN_END", C.T_DESPIN_END), ("T_GNSS_LOCK", C.T_GNSS_LOCK),
        ("NAV_DT", C.NAV_DT), ("EKF_DT", C.EKF_DT), ("IMU_DT", C.IMU_DT),
        ("GPS_POS_SIG", C.GPS_POS_SIG), ("GPS_VEL_SIG", C.GPS_VEL_SIG),
        ("DEADBAND", C.DEADBAND), ("FIN_FORCE_NOM", C.FIN_FORCE_NOM),
        ("FIN_FORCE_MAX", C.FIN_FORCE_MAX), ("DT_TRUTH", C.DT_TRUTH),
        ("DT_IPP", C.DT_IPP), ("TMAX", C.TMAX), ("N_RUNS", C.N_RUNS),
        ("GYRO_SAT_RPS", C.GYRO_SAT_RPS), ("ANGLE_BITS", C.ANGLE_BITS),
        ("ANGLE_Q", C.ANGLE_Q), ("ANGLE_SIG", C.ANGLE_SIG),
        ("GYRO_NOISE_DENS", C.GYRO_NOISE_DENS),
        ("GYRO_BIAS_INIT_SIG", C.GYRO_BIAS_INIT_SIG),
        ("ACC_NOISE_SIG", C.ACC_NOISE_SIG),
        ("ACC_BIAS_INIT_SIG", C.ACC_BIAS_INIT_SIG), ("BARO_SIG", C.BARO_SIG),
        # GNC chain (carried from Rev D)
        ("T_LOCK_DEADLINE", C.T_LOCK_DEADLINE), ("CHI2_GATE", C.CHI2_GATE),
        ("GNSS_LAT", C.GNSS_LAT), ("T_GUID_ENGAGE", C.T_GUID_ENGAGE),
        ("T_MOD", C.T_MOD), ("OMEGA_S", C.OMEGA_S),
        ("OMEGA_SPIN_SAT", C.OMEGA_SPIN_SAT), ("ACC_AVG_SIG", C.ACC_AVG_SIG),
        ("Q_REF_T", C.Q_REF_T),
        # Rev E
        ("T_LOCK_DEADLINE_E", C.T_LOCK_DEADLINE_E),
        ("SIG_POS_DEGRADED", C.SIG_POS_DEGRADED),
        ("SIG_POS_DENIED", C.SIG_POS_DENIED),
        ("SIG_POS_RESUME", C.SIG_POS_RESUME),
        ("R_FLOOR_ACQ", C.R_FLOOR_ACQ),
        ("R_FLOOR_DEGRADED", C.R_FLOOR_DEGRADED),
        ("R_FLOOR_DENIED", C.R_FLOOR_DENIED),
        ("GATE_HARD_X", C.GATE_HARD_X), ("R_INFLATE_MAX", C.R_INFLATE_MAX),
        ("FIT_BASELINE", C.FIT_BASELINE), ("LP_A", C.LP_A),
        ("T_GUID_ENGAGE_E", C.T_GUID_ENGAGE_E), ("SETTLE_T", C.SETTLE_T),
        ("ANCHOR_N", C.ANCHOR_N),
    ]
    for name, mine in pairs:
        theirs = getattr(sim, name)
        assert mine == theirs, f"{name}: fsw={mine!r} sim={theirs!r}"


def test_derived_constants():
    assert C.AREA == pytest.approx(math.pi / 4 * 0.155 ** 2)
    assert C.ACC_AVG_SIG == pytest.approx(0.08 / math.sqrt(200.0))
    assert C.ANGLE_SIG == pytest.approx(2 * math.pi / 4096 / math.sqrt(12))
    # servo rate cap is the Rev E literal 6.28 (not exactly 2*pi) — pairing
    assert C.SERVO_RATE_MAX == 6.28
    assert C.SERVO_ALPHA_MAX == 55.0
