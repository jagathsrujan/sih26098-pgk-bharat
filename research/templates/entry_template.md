# Research Entry Template — SIH26098

**Copy this to `research/<category>/entry_YYYYMMDD_<topic>.md` for every finding.**

```markdown
---
id: B3-20260825-piezo
category: B_aero
author: @your-github
date: 2026-08-25
source_type: patent | paper | datasheet | web | test
trl: 5
---

## Idea Title
Hollow Piezoelectric Motor Retractile Fins

## Summary (2-3 lines)
What it is, how it works, why it matters for PGK.

## Source (MANDATORY - no URL = reject)
- URL: https://doi.org/...
- Patent: US10295320
- Accessed: 2026-08-25
- Quote: "0.30 N·m wind load, 25rpm @450V 40.2kHz"

## Evidence
- Screenshot / PDF page / test data link
- Key figure/table number

## Indian Path
YIL Ambajhari forging + BEL ECIL + ISRO NavIC + ARDE

## Pros / Cons
- Pros: Self-locking, no EMI, survives 20kG
- Cons: 450V driver complexity

## Cost Estimate (lakhs)
₹7-9L per kit (motor ₹0.5L + driver ₹0.2L)

## Recommendation
Use / Park / Reject — and why

## Links to Code/CAD
- cad_models/...
- research/B_aero/...
```

**Rules:**
1.  Every claim needs URL + accessed date
2.  TRL 1-9 must be justified
3.  Update `SIH26098_Ideas_Database.json` via `research/merge.py` (don't edit manually)
