# SIH26098 — Cold-Gas / Hypergolic Reaction-Control PGK (Refined Concept)

> **Idea owner:** jagathsrujan | **Status:** Concept — v1 refinement
> **Date:** 2026-09-01
>
> A PGK that steers a 155 mm shell not by moving canards, but by firing
> **reaction-control thrusters** mounted on the canard surfaces. No alternator,
> no de-spin motor, no servo torque element — the steering authority comes from
> **cold gas** (or hypergolic bipropellant) metered through 3D-printed internal
> nozzle channels in a metal-printed canard ring.

---

## 1. The core idea in one paragraph

Remove the standard fuze, replace it with our PGK module. The module carries a
fixed ring of four metal-3D-printed canards. Each canard has, on its left and
right face, three small nozzle holes — shaped *inside the printed part* as
converging channels. All four canards → 8 faces × 3 holes = **24 nozzle exits**,
each fed by an internal channel. Per canard, the three holes on each face merge
into **one internal feed channel**, so the ring has **8 feed channels** total
(2 per canard).

A compressed-gas (or two-canister hypergolic) source in the fuze body feeds these
channels through a **metering valve stack**: a rotating disk with holes that
aligns with the channel openings. Rotating the disk opens only the channels for
one *pair* of canards on the *same* side (e.g., left faces of the top + bottom
canards). When those fire, the jet reaction pushes the shell toward the **right**
— pure lateral translation, no spin coupling.

The rotation of the metering disk is the **only actuation**: it selects *which*
lateral axis to push (up/down/left/right) and how hard (duty cycle / pulse
count). Steering authority is entirely cold-gas impulse, not aerodynamic control
surface deflection.

---

## 2. Why this is interesting (differentiation vs the status quo)

| | Northrop-style PGK (alternator + de-spun canards) | This concept |
|---|---|---|
| Steering actuator | Torque motor / servo rotating canards | **Fixed canards + RCS jets** |
| Power source | Shell-spin alternator (must harvest ~250 rev/s) | **Stored gas pressure** (no spin harvest needed) |
| Moving parts in flight | De-spin bearing, torque motor, servo | **One metering disk** |
| Roll coupling | Must de-spin a frame against body roll | Jets fire in a **fixed body frame**; no de-spin needed |
| Response | Millisecond-ish, continuous | **Discrete pulses**, duty-cycle controlled |
| Key engineering risk | Alternator survives 15,000 g; bearing survives spin | **Seals + valves survive 15,000 g**; gas volume budget |

**Headline advantage:** no spin-harvest, no de-spin torque element, no bearing
between two frames. The entire moving assembly is *one* rotating metering disk.

---

## 3. System architecture

```
        FUZE BODY (spins with shell @ ~250 rev/s)
        ┌──────────────────────────────────────────┐
        │  Propellant source                        │
        │   Option A: 1 × compressed-gas canister   │
        │   Option B: 2 × hypergolic canisters      │
        │        │                                  │
        │        ▼                                  │
        │  Pressure regulator / flow restrictor     │
        │        │                                  │
        │        ▼                                  │
        │  Metering disk stack (the ONLY actuator)  │
        │    [fixed disk: 8 feed holes]             │
        │    [rotating disk: valve openings]        │
        │        │ 8 channels                       │
        │        ▼                                  │
        └────────┼─────────────────────────────────┘
                 │ (internal feed tubes through hub)
                 ▼
        CANARD RING (fixed, 4 metal-printed canards)
        ┌──────────────────────────────────────────┐
        │  Top canard    : L3-nozzles + R3-nozzles  │
        │  Bottom canard : L3-nozzles + R3-nozzles  │
        │  Left canard   : L3-nozzles + R3-nozzles  │
        │  Right canard  : L3-nozzles + R3-nozzles  │
        └──────────────────────────────────────────┘
          8 faces × 3 nozzles = 24 exits, 8 feed channels
```

---

## 4. Propulsion options (trade)

### Option A — Compressed gas (cold gas RCS)
- **Propellant:** N₂, CO₂, or helium at ~100–300 bar in one canister.
- **Thrust:** cold-gas nozzles give modest Isp (~50–70 s), but the impulse per
  shot is *plenty* for terminal correction (we need only ~10–30 m/s Δv in the
  last seconds).
- **Pros:** simplest, safest, fully inert (fits the "no energetics" demo
  boundary), one metering disk.
- **Cons:** low density impulse → bigger/heavier tank; lower thrust authority if
  mis-sized.

### Option B — Hypergolic bipropellant (e.g., NTO + hydrazine / green monoprop)
- **Propellant:** two canisters, two feed paths, two channels per canard (one per
  side) — which actually **matches your existing "two channels per canard"
  plumbing perfectly**.
- **Pros:** high Isp (~200–300 s), small tanks, real thrust authority.
- **Cons:** hypergolics are toxic/corrosive, need handling, storage, and are
  **energetics** — outside the inert demo boundary; also needs two metering paths
  instead of one.

**Recommendation for SIH:** lead with **Option A (cold gas)** as the flight
concept, present Option B as the "productionized / higher-impulse variant".
The demo can be **fully inert**: use the same valve stack with **compressed air
or CO₂** blowing through the printed nozzles on a bench rig.

---

## 5. The metering disk (the heart of the invention)

- **Fixed disk:** 8 feed holes at 45° spacing, each connected to one canard-face
  channel.
- **Rotating disk:** a pattern of valve openings such that at any angular
  position, exactly **one opposite pair of faces** is open — e.g., top-left +
  bottom-left, OR top-right + bottom-right, OR top-top/bottom-bottom pairs.
- **Drive:** a small motor / stepper / solenoid ratchet steps the disk between
  the 4 valve positions. In a flight article this is the *only* powered moving
  part.
- **Effect:** firing one pair of faces gives a **pure lateral thrust** along one
  body axis. Since the shell body rolls at ~250 rev/s, firing for a short window
  pushes along a fixed body axis; the guidance law times the *start* of the pulse
  window to the roll angle to point the impulse where it's needed (or, if the
  shell is spin-stabilized and we want body-frame control, fire in the body
  frame — the jets rotate with the shell and we command by phase).

> **Design question to resolve (flag):** are the jets fired *in the spinning body
> frame* (phase-locked to roll angle, like a spin-stabilized thruster array) or
> do you keep the canard ring de-spun and fire in the inertial frame? The former
> needs only the metering disk; the latter needs the bearing again. **The elegant
> version is the former** — fire in the body frame, phase-lock to roll, no
> de-spin at all.

---

## 6. Guidance & control sketch

- **Sensors:** existing GNSS/IMU stack in the fuze (NEO-M9N + 6-axis IMU + roll
  rate).
- **Control law (candidate):** ZEM/PN with a **bang-bang RCS allocator** — when
  predicted miss > threshold, pick the body axis nearest the required lateral
  Δv, wait for the roll phase that aligns it, fire a pulse train at that phase.
- **Pulse modulation:** width/duty-cycle control of the metering disk (or a
  fast solenoid per channel) gives proportional-ish authority from discrete
  pulses.
- **Δv budget:** terminal correction for a 155 mm shell needs roughly **5–20 m/s**
  lateral Δv in the last 5–10 s of flight — that sets the tank size and nozzle
  throat sizing.

---

## 7. Manufacturing story (the 3D-printed canard ring)

- **Process:** metal LPBF (laser powder bed fusion), e.g., titanium or 17-4 PH
  stainless.
- **In-canard features:** the three nozzles per face are printed as converging
  channels *in situ* — no post-machining, no inserts. The internal feed channel
  per face runs from the hub to the three nozzle throats.
- **Why it's compelling for the demo:** the whole canard ring + channels is a
  single printed part; the bench demo can be printed in PA12/PLA with drilled
  nozzles for visuals, or metal-printed for a real cold-air firing.
- **Survivability question (flag):** can LPBF channel walls and nozzle throats
  survive 15,000 g setback and in-flight vibration? Needs structural FEA +
  HOP (high-overpressure) testing before claiming flight readiness. For the demo
  boundary this is simulation/reference only.

---

## 8. What we must build to prove it (demo roadmap)

1. **Bench cold-air firing rig** — metering disk + printed canard ring + CO₂/air
   tank; measure thrust per nozzle pair, prove the disk selects the axis.
2. **Spin-table integration** — mount the ring on a spinner, fire at ~roll rate,
   verify phase-locked impulse direction.
3. **GNC simulation** — extend `simulate_trajectory_155.py` with an RCS allocator
   + roll-phase scheduler; Monte Carlo CEP with jet noise.
4. **Structural FEA** — 15,000 g setback on the printed channels + valve stack;
   wall thickness, throat erosion, seal preload.
5. **Full inert demonstrator** — fuze-sized module with the metering disk turning,
   nozzle pairs visibly firing air, telemetry of which axis is commanded.

---

## 9. Open questions to resolve (for the team)

- [ ] **Spin-frame vs de-spun frame for the jets** — phase-locked body-frame
      firing (no bearing) vs inertial-frame (needs de-spin bearing again).
- [ ] **One metering disk vs four fast solenoids** — the disk is simpler, but a
      solenoid per channel gives faster response and proportional control.
- [ ] **Cold gas vs hypergolic** — demo-safe inert vs production-energetic.
- [ ] **Tank placement** — does the gas canister fit in the fuze bore (Ø35 mm
      constraint) for the required Δv? Sizing calc needed.
- [ ] **Nozzle orientation on the canards** — the jets fire perpendicular to the
      canard face; does that produce the intended *lateral* push, and does the
      canard itself add or cancel lift/force when the jets fire?
- [ ] **Backup actuator** — keep the alternator + de-spin carrier as a fallback
      track, or fully commit to RCS-only?

---

## 10. Summary statement (for the pitch)

> *"We replace the PGK's spinning alternator and servo-driven canards with a
> single printed canard ring that doubles as a reaction-control thruster array:
> 24 nozzles, 8 internal channels, one rotating metering disk. It steers the
> shell by firing cold gas (or hypergolic) pairs in the body frame — phase-locked
> to roll — cutting the moving parts from a bearing + torque motor + servos down
> to one disk. Simpler, cheaper, no spin-harvest dependency, and fully
> demonstrable on a bench with compressed air."*
