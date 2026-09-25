# AUTHORIZE BUILD UNIT HA-1 — TC (R1.3)

**Status:** AUTHORIZED — IN FORCE  
**Date:** 2026-09-24  
**Authority:** Todd C. (`TC`)  
**Bound proposal:** `RADAR_V4_HA1_PROPOSAL_TC_R1.3.md` (SHA256 `a891148084b98158a29230ac7c4e58211c70a5fafa37b16543315d726aec1a48`)  
**Chat custody:** Authorized by Todd chat direction “Go ahead and do it-TC” on 2026-09-24, applying the fields below. This file banks that decision on the public repository so procedural binding has a durable record.

Does **not** by itself authorize LIVE, Q-011, Phase 6–9, VTI land, network clients in `radar_v4/`, market bytes in git, or commercial redistribution of Stooq data.

---

## AUTHORIZE block

```text
DECISION: AUTHORIZE BUILD UNIT HA-1 — TC (R1.3)

SYMBOL:          SPY
PROVIDER STRING: STOOQ
ENTITLEMENT NOTE:
  Private Phase 5 LEVEL 0 MEASURED run only (close-to-close difference).
  Source class: Stooq public daily download for SPY (CSV obtained privately;
  converted to workshop JSON outside radar_v4/; .csv never inside a pack).
  Relying on Stooq’s published terms for personal / non-redistributed use of
  downloaded daily series as of DATE 2026-09-24. No market bytes in git.
  No vendor HTTP client in radar_v4/. Does not authorize LIVE, Q-011,
  Phase 6–9, VTI, daily observe carve-out, redistribution of Stooq data,
  or commercial redistribution.

ITEM 0 / BACKLOG BANKED AT:
  docs/governance/2026-09-24-radar-v4-next-actions-TC.md
  (on main via PR 46 merge commit 0a0b4a0c882051f82750a730d92b69619b08d9b8)

DATE: 2026-09-24
TODD: TC
```

---

## Procedural binding (auditor)

Before the first real MEASURED run is **accepted**, the auditor checks that the pack declaration matches this memo **exactly**:

- `universe` = `SPY`
- `provider` = `STOOQ`

Not enforced in code (R1.3).

## First-run hygiene (auditor notes, not code gates)

1. Run `unexpected-files` on the pack before `session` (`.csv` does not stop `session` alone).  
2. Prefer `--report` to a path **outside** the repo.  
3. Accept the first real result only if quarantine count is zero, or every quarantined row is explained.

**Tools verify. Cursor codes. Claude audits. Todd authorizes.**
