# SIH26098 — Physics Evaluation: Cold-Gas / Hypergolic RCS PGK Concept

> **Date:** 2026-09-01 | **Refines:** `SIH26098_COLDGAS_PGK.md`
> **Verdict: ❌ The RCS concept does not close for the full 155 mm mission.**
> It is physically feasible as a *concept* but fails the SWaP budget at your own
> sim's authority requirement. This doc shows exactly why, with numbers, and what
> alternatives DO fit.

---

## 1. What the concept claims (from `SIH26098_COLDGAS_PGK.md`)

| Claim | Value |
|---|---|
| Steering | 24 nozzles, 8 internal channels, 4 metal-3D-printed canards |
| Actuator | One rotating metering disk selects which nozzle face fires |
| Propellant | Cold gas (N₂) or hypergolic biprop |
| Authority | Matches the existing 60 N fin-force baseline |
| Envelope | Fuze bore Ø35 × ~100 mm (0.15 L) |

---

## 2. The authority requirement (from YOUR OWN sim)

`cleansheet/scripts/sim_guidance_check.py` (RUN, verified):

| Quantity | Value | Source |
|---|---|---|
| Shell mass | 46 kg | sim |
| Fin force (authority) | 60 N (audit 30–100 N) | `FIN_FORCE_NOM` |
| Lateral accel | 1.30 m/s² = 0.13 g | 60/46 |
| Guidance window | ~55 s (lock 35 s → impact 90 s) | sim |
| Mean duty cycle | 0.21 | sim output |
| **Required lateral Δv** | **~15 m/s** (1.3 m/s² × 0.21 × 55 s) | computed |
| ZEM law | a_cmd = 2·miss/t_go² | sim |

The sim's *hard* accel cap is `A_MAX_G = 3.0 g` (`simulate_trajectory_155.py`),
but the *achievable* authority (60 N fin force) is 0.13 g. **This is the number
your RCS must match.**

---

## 3. The physics: cold gas can't deliver the impulse

### 3.1 Specific impulse
- Cold gas (N₂/CO₂/He): **Isp ≈ 50–70 s** (exhaust ~500–700 m/s).
- Hypergolic biprop (NTO/hydrazine): Isp ≈ 250–300 s.
- To produce **F = 60 N** with cold gas: **ṁ = F/(Isp·g) = 60/(60×9.81) ≈ 0.10 kg/s**.

### 3.2 Tank mass for the mission
Needed gas = ṁ × duty × window = 0.10 × 0.21 × 55 ≈ **1.18 kg N₂**.

Ideal-gas volume at tank pressure (blowdown to 3 bar):

| P0 (bar) | Tank volume | vs 0.15 L bore |
|---|---|---|
| 100 | 10.2 L | **68× too big** |
| 200 | 5.0 L | **33× too big** |
| 300 | 3.3 L | **22× too big** |

**Even at 300 bar, the tank is 22× larger than the entire fuze bore.** There is no
cold-gas path that fits. The mass budget is equally dead: 1.2 kg of gas alone
exceeds the whole 770 g kit target.

### 3.3 Hypergolic doesn't rescue it
- At Isp 300 s: m_prop ≈ 1.18 × (60/300) ≈ **0.24 kg** — plus tank, two feed
  paths, valve stack. Still doesn't fit 0.15 L with all the electronics, and
  hypergolics are **energetics — outside the inert demo boundary** and a
  safety/S&A nightmare.

### 3.4 The metering-disk double-fire flaw (the fatal one)
Your design fires **opposite faces of the same canard simultaneously**
(e.g., top-L + bottom-L). Two jets on opposite faces produce:
- **Zero net lateral force** (equal and opposite pushes cancel).
- **A pure torque couple** → pitch/roll moment → the shell **tumbles**, doesn't
  steer.

The only fix — fire **one face at a time** — strictly *worsens* the tank problem
(now only ~1/4 of the nozzles fire at once, so the same Δv needs 4× the gas).

---

## 4. What DOES fit and close — the decision (per team direction)

Team decisions (2026-09-01):
- **Direction:** Solid gas-generator ring (the viable form of the concept).
- **Metering:** Single-face firing (one face's 3 nozzles open at a time — pure
  lateral push, no tumble).
- **Deliverable:** Ruled-out trade study (a "what we rejected and why" physics
  section in the submission).

### 4.1 Solid gas-generator sizing (the realistic reframe)

Solid grain (density 1.7 g/cm³) replacing the tank — the actual M1156 PGK-style
de-spin/gas-generator architecture:

| Grain | Isp (s) | Mass for 15 m/s Δv | Volume | In Ø35 bore length |
|---|---|---|---|---|
| AP/HTPB | 200 | 353 g | 208 cm³ | 216 mm |
| High-energy | 250 | 282 g | 166 cm³ | 173 mm |
| Gas-generant | 150 | 472 g | 277 cm³ | 288 mm |

**The 0.15 L bore holds ~150 cm³ / 255 g → Δv ≈ 10.8 m/s ≈ 72% of the 15 m/s
mission.** The full 60 N mission needs 208 cm³ — **still 40% over the bore.**

### 4.2 Single-face firing is the correct fix, but costs 4× impulse

| Firing mode | Δv in 0.15 L bore | Meets 15 m/s? |
|---|---|---|
| Opposite-pair (your original) | pure torque — **zero Δv, tumbles** | ❌ |
| Single-face (chosen) | 10.8 m/s @ Isp 200 | ⚠️ 72% |
| All-faces-simultaneous (ideal) | 10.8 m/s | ⚠️ 72% |

The single-face fix is *required* for not tumbling, but it doesn't make the
impulse budget any better — it only prevents catastrophic failure.

### 4.3 Final physics verdict across ALL propellant options

| Concept | Δv possible in 0.15 L bore | Meets 15 m/s? | Verdict |
|---|---|---|---|
| Cold gas N₂ 300 bar | ~1.4 m/s | ❌ 10% | **Dead** |
| Hypergolic (Isp 300) | ~4 m/s | ❌ 27% | Dead (energetics too) |
| Solid grain (Isp 200) | ~10.8 m/s | ⚠️ 72% | **Terminal-assist only** |
| Solid grain + full bore | ~15 m/s (needs 208 cm³) | ⚠️ 100% | Needs bigger bore |

**Bottom line:** no RCS/gas-generator variant fits the full 60 N authority in the
Ø35 fuze bore. The **solid-grain version is a credible terminal-phase trim
assist** on top of the ring-motor baseline, and is the honest "what we ruled out
and why" trade study.

---

## 5. Recommended architecture (terminal-assist trim, if pursued)

- **Primary steering:** existing ring-motor de-spin carrier (`PGK_155mm.FCStd`).
- **Secondary (optional):** solid gas-generator lateral thruster ring on the
  canard ring — fires **one face at a time**, only in the last ~5–10 s, for the
  residual miss the ring motor can't close.
- **Why it's worth one slide:** it shows the team considered the RCS alternative,
  ran the impulse math, rejected cold gas on SWaP, and kept the printed-nozzle
  idea as a *supplement*, not a replacement.

---

## 6. Numbers to reuse in the submission

- 60 N authority = 0.13 g on 46 kg shell → CEP 6.9 m (sim, verified).
- Cold gas: Isp 60 s → 0.10 kg/s at 60 N.
- Mission gas: 1.18 kg N₂ → 3.3 L @ 300 bar (22× the bore).
- Single-face fire needed (not opposite-pair) → prevents tumble, but doesn't
  change the impulse budget.
- Nozzle throat: 0.96 mm/nozzle @ 200 bar (feasible in LPBF).
- Solid grain: 353 g / 208 cm³ @ Isp 200 for full mission; bore holds 255 g →
  10.8 m/s → 72%.
- Hypergolic: 0.24 kg prop, still doesn't fit, and is out of inert scope.
