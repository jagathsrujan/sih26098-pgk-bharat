"""FSW configuration — ALL constants, ported 1:1 from the Rev E constants
blocks of scripts/sim_gnc_check.py (shared block + Rev D/E additions).

These are the on-board values. The co-sim harness asserts this module against
the sim's constants (tests/test_config.py) — never edit one side alone.

Units are stated on every constant. No dynamic allocation: every container
below is fixed-size by construction.
"""
import math

# ---------------------------------------------------------------- mission / flight regime
G = 9.80665                    # m/s2
RHO0 = 1.225                   # kg/m3, sea-level density
HSCALE = 8500.0                # m, exponential atmosphere scale height
M_NOM = 46.0                   # kg, nominal shell mass
D = 0.155                      # m, reference diameter
AREA = math.pi / 4 * D * D     # m2, frontal area (derived)
V0_NOM = 827.0                 # m/s, muzzle velocity
ELEV0 = math.radians(46.0)     # rad, quadrant elevation
RANGE_TARGET = 30000.0         # m, aim point (downrange)

# ---------------------------------------------------------------- phasing / rates
T_LOCK_NOM = 45.0              # s, scheduled GNSS lock (post-despin)
T_DESPIN_START = 25.0          # s
T_DESPIN_END = 40.0            # s, 15 s de-spin transient
T_GNSS_LOCK = 45.0             # s, first fix epoch
NAV_DT = 1.0                   # s, GNSS / guidance cycle
EKF_DT = 0.01                  # s, 100 Hz EKF prediction (deployment rate)
IMU_DT = 0.005                 # s, 200 Hz raw IMU (decimated to EKF)
GPS_POS_SIG = 5.0              # m, GNSS position sigma
GPS_VEL_SIG = 0.3              # m/s, GNSS velocity sigma
DEADBAND = 8.0                 # m, guidance deadband
FIN_FORCE_NOM = 60.0           # N, fixed-magnitude trim force
FIN_FORCE_MAX = 60.0           # N
DT_TRUTH = 0.025               # s, truth step (co-sim; = 40 Hz)
DT_IPP = 0.15                  # s, IPP integration step
TMAX = 200.0                   # s, integration guard
N_RUNS = 250                   # primary MC runs (verification harness)

# ---------------------------------------------------------------- sensors
GYRO_SAT_RPS = math.radians(4000.0)          # rad/s, ICM-42688 saturation
ANGLE_BITS = 12                              # bit, collar-bell angle sensor
ANGLE_Q = 2 * math.pi / (1 << ANGLE_BITS)    # rad, quantization step
ANGLE_SIG = ANGLE_Q / math.sqrt(12)          # rad, quantization noise sigma
GYRO_NOISE_DENS = math.radians(0.015)        # rad/s/rtHz (per-sample placeholder)
GYRO_BIAS_INIT_SIG = math.radians(0.5)       # rad/s, gyro bias 1-sigma
ACC_NOISE_SIG = 0.08                         # m/s2 per IMU sample (incl. vib)
ACC_BIAS_INIT_SIG = 0.25                     # m/s2, accel bias 1-sigma
BARO_SIG = 2.0                               # m, baro altitude sigma (unused)

# ---------------------------------------------------------------- GNC chain (carried from Rev D)
T_LOCK_DEADLINE = 50.0         # s, no fix by then -> ballistic
CHI2_GATE = 22.46              # 6-dof ~3-sigma (hard-reject threshold = GATE_HARD_X * this)
GNSS_LAT = 0.10                # s, fix latency (time-tagged)
T_GUID_ENGAGE = 2.0            # s, first guidance tick after first fix (NOTE: Rev E
                               #     keeps this 2.0 s value for next_guid even though
                               #     the acq->guide threshold below is 1.0 s — ported
                               #     as-is, it defines the reference run)
T_MOD = 3.0                    # s, phasor-duty modulation period
OMEGA_S = 2 * math.pi * 250.0  # rad/s, shell spin rate (const, aero decay ignored)
OMEGA_SPIN_SAT = 50.0          # rad/s, |omega_R| above this -> trim force averages out
ACC_AVG_SIG = ACC_NOISE_SIG / math.sqrt(200.0)  # m/s2, 1-s averaged accel noise
Q_REF_T = 70.0                 # s, 60 N reference condition epoch

# ---------------------------------------------------------------- Rev E additions
T_LOCK_DEADLINE_E = 50.0       # s, never-lock deadline (fail-safe)
SIG_POS_DEGRADED = 12.5        # m, sigma_pos -> degraded (guidance continues open-loop)
SIG_POS_DENIED = 25.0          # m, sigma_pos -> denied (neutral coast)
SIG_POS_RESUME = 8.0           # m, sigma_pos -> back to guide from denied
R_FLOOR_ACQ = 2.0              # x, R inflation while acquiring
R_FLOOR_DEGRADED = 4.0         # x, R inflation in degraded
R_FLOOR_DENIED = 16.0          # x, R inflation in denied (position-only)
GATE_HARD_X = 10.0             # x CHI2_GATE -> outright reject
R_INFLATE_MAX = 8.0            # x, adaptive-R clamp
FIT_BASELINE = 15.0            # s, slow (cd, wy) fit baseline
LP_A = 0.55                    # -, command vector low-pass blend per 1-Hz tick
T_GUID_ENGAGE_E = 1.0          # s, acq->guide threshold (see T_GUID_ENGAGE note)
SETTLE_T = 0.55                # s, servo settle time (180-deg slew ~0.48 s + margin)
ANCHOR_N = 32                  # samples, settled samples per anchor window

# ---------------------------------------------------------------- servo / motor caps (controller-side mirror)
SERVO_RATE_MAX = 6.28                 # rad/s, servo rate cap (Rev E literal; 360 deg/s = 6.2832
                                      #     but the reference run uses 6.28 — kept for pairing)
SERVO_ALPHA_MAX = 55.0                # rad/s2, servo acceleration cap
SERVO_DEADBAND = math.radians(0.1)    # rad, near-target command deadband
PATTERN_FLIP_EPS = math.radians(1.0)  # rad, commanded-azimuth jump that counts as a flip

# ---------------------------------------------------------------- guidance
GUIDE_FREEZE_TGO = 2.0                # s, freeze commands when t_go below this
APN_RANGE_MIN = 50.0                  # m, APN zero-output range

# ---------------------------------------------------------------- slow-fit guards
FIT_VH_MIN = 30.0              # m/s, horizontal speed gate for the slow fit
FIT_CD_STEP = 0.05             # -, max per-baseline cd_scale correction
FIT_CD_MIN = 0.90              # -, cd_scale floor
FIT_CD_MAX = 1.15              # -, cd_scale ceiling
FIT_WY_CLAMP = 12.0            # m/s, wy fit clamp
FIT_KV_MIN = 0.05              # -, minimum fit denominator for wy
FIT_ROLL_P_MAX = math.radians(2.0) ** 2  # rad2, roll-variance health gate for wy
FIT_NIS_MAX = 2.5              # -, anchor NIS health gate for wy

# ---------------------------------------------------------------- pre-flight calibrated values
# The ground process calibrates Cd against the nominal 30.0 km range (bisect,
# sim calibrate_cd()); the value ships with the kit. The co-sim harness passes
# the sim-computed value in, which matches this to <1e-11.
CD_CAL = 0.2115                # -, calibrated drag coefficient (nominal 30.0 km)

# ---------------------------------------------------------------- deployment task rates (STM32G474 mirror)
# The co-sim overrides these to the truth-step cadence for paired numerics —
# see FLIGHT_SOFTWARE.md ("Task rates").
SERVO_HZ = 400.0               # Hz, pattern/servo task
SENSOR_HZ = 40.0               # Hz, gyro/accel sample + roll EKF predict
NAV_PREDICT_HZ = 100.0         # Hz, translational EKF predict (deployment)
GNSS_HZ = 1.0                  # Hz, GNSS delivery
GUIDE_HZ = 1.0                 # Hz, guidance tick
