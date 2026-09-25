# AUTHORIZE — VTI private date-only observation (AFTER-THE-FACT — TC)

**Status:** AUTHORIZED — IN FORCE (AFTER-THE-FACT CUSTODY)  
**Custody / signature date:** 2026-09-24  
**Authority:** Todd C. (`TC`)  
**Chat custody:** Accepted as written — TC (2026-09-24). This file banks that after-the-fact authorization on the public repository so GOVERNANCE/PR 45 have a durable memo.  
**Purpose of this file:** Close the custody gap between (a) `GOVERNANCE.md` / README text and merged PR 45 claiming Todd authorized a narrow VTI private daily observation, and (b) backlog Item 1 previously waiting on a written memo. Scope matches what already appears on `main` / PR 45 plus Todd’s three gap answers (2026-09-24).

Does **not** by itself authorize HA-1 MEASURED packs, LIVE, Q-011, Phase 6–9, the withdrawn SPY observe carve-out, network clients in `radar_v4/`, market bytes in git, or commercial redistribution of Vanguard data.

---

## After-the-fact custody note

1. On 2026-09-24 Todd corrected an earlier chat answer: he **did** authorize a narrow VTI private daily observation. A prior REJECT draft of `vti-date-observe.patch` was **vacated** and must not be banked as a final reject.
2. Before a signed memo existed, PR **45** (`Add offline VTI date-only observation path`) merged to `main` as commit `d47ad23d8ec680eaa1a9cf46e7f110aef765864a` (head `5c585b6747ceb1fe84dd9d300d5e57b51ce44b4e`), adding `radar_v4/vti_date_observe.py`, CLI `observe-vti-date`, tests, and the GOVERNANCE/README paragraphs that cite Todd authorization.
3. Todd chose (2026-09-24) to resolve the contradiction by writing this authorization **after the fact**, not by reverting PR 45.
4. This memo is the missing paper trail. Todd filled STOP/REVIEW, PATCH AUTHOR, and retain entitlement on 2026-09-24, then accepted as written (`Accept as written — TC`). Item 1 closes when this file is banked on `main` and Claude has audited memo ↔ landed code (open defects remain until then).

---

## What already landed (PR 45) — factual bound

| Item | As implemented / documented on `main` |
|---|---|
| Instrument | **VTI** only |
| Command | `python -m radar_v4 observe-vti-date --capture <private-vti-session-directory>` |
| Cadence / granularity | Date-only session dates from Vanguard `effectiveDate`; **not** an exact market timestamp (`market_timestamp` must be null) |
| Source URL (code constant) | `https://investor.vanguard.com/irr/funds/profile/VTI-AdditionalFundData` |
| Capture layout | Private directory named `vti-<YYYY-MM-DD>` containing `receipt.json` + `vanguard-response.json` **outside** the repository |
| Price field used | Source `marketPrice` (and receipt `MarketPrice`); NAV / premium cross-check required |
| Output | Prints JSON: status `PRIVATE_DATE_OBSERVATION_ONLY`, close-to-close **difference** of the two newest dated market prices, no file writes, no network |
| Claim language in code | `LEVEL 0 descriptive price difference only; no signal or edge claim` |
| Pack admission | `radar_pack_admitted: false`; `session` still refuses HISTORICAL/LIVE for packs |
| Network | No network in this path |
| Raw vendor bytes / credentials | Remain outside the repository |

---

## AUTHORIZE block (sign when gaps filled)

```text
DECISION: AUTHORIZE VTI PRIVATE DATE-ONLY OBSERVATION — TC (AFTER-THE-FACT)

SYMBOL:            VTI
CADENCE:           Private, manual, date-granularity observation of one
                   manually captured Vanguard VTI session directory
                   (not a pack session; not HISTORICAL admission).
SOURCE:            Vanguard investor fund profile AdditionalFundData for VTI
                   (URL as coded in radar_v4/vti_date_observe.py SOURCE).
                   Capture obtained privately by Todd (or under Todd’s
                   direction); not fetched by radar_v4.
CLAIM CEILING:     LEVEL 0 — descriptive close-to-close marketPrice
                   difference only. No signal, edge, ranking, or method claim.
OUTPUTS / STORE:   Command prints JSON to stdout only. Capture directory,
                   receipt, and raw source response stay outside
                   chatawa-radar-v4. No persistence by the command.
STOP / REVIEW:     Human review after N = 10 completed observations,
                   or earlier on refuse storm, license doubt, or claim drift.
EXPLICIT NON-ALLOWS:
  - Network / HTTP client inside radar_v4/ for this path
  - Real-data pack admission via session (HISTORICAL or LIVE)
  - Representing effectiveDate / session_date as an exact market timestamp
  - Committing vendor bytes, credentials, or licensed series to git
  - Second symbol under this memo
  - Phase 6–8, Phase 9 complete, Q-011 data, HA-1 MEASURED entitlement
  - Withdrawn SPY one-ETF daily observe carve-out revival
  - Commercial redistribution of Vanguard data

PATCH AUTHOR:      Todd C. (TC)
RELATION TO WITHDRAWN SPY CARVE-OUT / PHASE 9:
  This is a separate, narrower offline date-observe side path. It is not
  the withdrawn SPY Phase-9-style daily observe carve-out, does not earn
  Phase 9, and does not revive that draft set.
SIDE PATH VS HA-1:
  Remains a side path. Does not route through HA-1 pack admission.
  HA-1 AUTHORIZE (SPY / STOOQ) is separate paper.
marketPrice / RETAIN ENTITLEMENT:
  Personal non-redistributed retain of private Vanguard VTI capture
  outside the repo, as of 2026-09-24.

CODE ALREADY ON MAIN:
  PR 45 merge commit d47ad23d8ec680eaa1a9cf46e7f110aef765864a
  GOVERNANCE.md VTI paragraph + README “Private VTI daily description”

VACATUR:
  Prior REJECT draft of vti-date-observe.patch is vacated (Todd correction
  2026-09-24). Do not bank that REJECT as final.

OPEN DEFECTS (known; signing does not close them):
  - Receipt / source date cross-check weaknesses called by independent audit
  - Global status vocabulary (PRIVATE_DATE_OBSERVATION_ONLY /
    SOURCE_CAPTURE_ONLY_NOT_RADAR_ADMITTED) still needs auditor comfort
  - Any remaining gate-bypass / Phase-9-shape concerns stay open until
    Claude audit of this memo ↔ landed code

DATE OF ORIGINAL AUTHORIZATION (Todd): 2026-09-24
DATE OF THIS AFTER-THE-FACT MEMO:       2026-09-24
TODD:                                  TC
```

---

## Acceptance

- [x] Gaps filled (STOP/REVIEW, PATCH AUTHOR, retain entitlement) — 2026-09-24  
- [x] Accepted as written — TC — 2026-09-24  
- [ ] Accepted with edits attached  
- [ ] Hold  
- [ ] Reject — revert PR 45 instead  

**Todd signature / date:** TC / 2026-09-24

---

## Banking (after signature)

1. Bank this file at `docs/governance/2026-09-24-vti-private-date-observe-authorize-TC.md` on `main`.  
2. Update backlog Item 1 in `docs/governance/2026-09-24-radar-v4-next-actions-TC.md` to record AUTHORIZE after-the-fact + PR 45 merge SHA (no longer “WAITING” on scope).  
3. Optionally add a one-line pointer in GOVERNANCE to this memo path so “Todd authorized…” cites durable paper.  
4. Claude audits memo ↔ landed `vti_date_observe` / CLI / tests before treating Item 1 as closed for audit purposes.

**Tools verify. Cursor codes. Claude audits. Todd authorizes.**

---

## ADDENDUM — HA-1 session gate (2026-09-24) — TC accepted

After this memo was signed, HA-1 #47 landed on `main` at a7451e4605ffb6914d4b1541add086c11fb1c2bb.
`session --allow-historical` may admit identity-valid HISTORICAL packs for the
SPY/STOOQ private MEASURED entitlement in docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md. LIVE remains refused.

This addendum corrects the factual statement that "`session` still refuses
HISTORICAL". It does **not** change VTI scope: VTI remains a side path;
`radar_pack_admitted: false`; VTI does not route through HA-1; Phase 5 metric
remains close-to-close **difference**.

TODD ACCEPT ADDENDUM: TC  DATE: 2026-09-24
