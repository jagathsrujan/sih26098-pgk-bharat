---
id: E06-20260831-tvs-esd-protection
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
ESD/TVS protection set: USBLC6-2SC6 (slip-ring UART) + SMAJ5.0A (5 V entry) + bridge bus clamp

## Summary (2-3 lines)
Two protection domains: (1) the slip-ring UART is a single-wire link crossing a rotating
contact — protected both ends with a bidirectional low-capacitance ESD array
(ST USBLC6-2SC6, SOT-23-6, 5 V-tolerant rails, rail-to-rail topology) plus 100 Ω series;
(2) the 5 V entry (both boards) gets a 400 W-class TVS (SMAJ5.0A) + bulk capacitance for
contact-bounce ride-through.

## Source (MANDATORY - no URL = reject)
- USBLC6-2: https://www.st.com/resource/en/datasheet/usblc6-2.pdf (DS, "Very low
  capacitance ESD protection", USBLC6-2SC6 SOT-23-6)
- SMAJ family: https://www.littelfuse.com/products/tvs-diodes/400w/smaj/smaj5.0a/
  (Littelfuse SMAJ5.0A 400 W TVS, VRWM 5.0 V)
- Accessed: 2026-08-31

## Evidence
- UART line: USBLC6-2 is 5 V-tolerant (the link is referenced to 3.3 V logic but the
  drive side sits on the 5 V rail domain — rail-to-rail clamping to VCC/GND both ends);
  3 pF-class capacitance is negligible at 115.2 kBd.
- 5 V entry: SMAJ5.0A VRWM 5.0 V, VC ≈ 9.2 V @ max surge — clamps slip-ring contact
  transients; bulk 470 µF (dome) / 220 µF (drive side is battery-direct, boost local)
  gives the documented ride-through (06 §2: ≥5 ms at the dome 0.5 W load).
- Bridge phase legs: bus-side SMAJ SMAJ5.0A + RC snubbers; the A7b dump path is the
  primary energy absorber (report §5 — Rev 1.2 decision).

## Indian Path
ST ESD arrays and Littelfuse/Bourns SMAJ TVS are Mouser/Digi-Key/India-distributor stock.

## Pros / Cons
- Pros: cheap, small, library-supported; rail-to-rail USBLC6 topology matches the
  3.3 V single-wire UART exactly; SMAJ is the standard 400 W clamp class.
- Cons: SMAJ5.0A clamping voltage (~9 V) needs downstream tolerance — the buck
  (3.8–30 V rated) and MCU pins are protected by the bulk + ferrite stages (documented
  chain in 06 §2).

## Cost Estimate (lakhs)
USBLC6-2SC6 ≈ ₹40 ×2; SMAJ5.0A ≈ ₹15 ×3. Board-line rounding — carried in §I.

## Recommendation
**Select USBLC6-2SC6 (×2, one per link end) + SMAJ5.0A (×3: dome 5 V, drive 5 V, bridge
bus).** No runner-up needed (commodity protection class).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §2 (sequencing/protection), §3, §4, §7 BOM
