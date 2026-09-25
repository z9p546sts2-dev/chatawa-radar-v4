# Radar V4 — What we need to do (TC)

**Recorded:** 2026-09-24  
**Authority:** Todd C. (`-TC`)  
**Operating split (declared TC):**

| Role | Who |
|---|---|
| Write what we need to do (plans, proposals, memos, revise paper) | **Grok Bot** |
| Implement authorized code in the repo | **Cursor** (cloud agent / IDE) |
| Independent audit of paper and code | **Claude** |
| Authorize, accept, reject, stop | **Todd** |

This record is the working backlog. It does **not** by itself authorize code, vendors, HISTORICAL bytes, HA-1 execution, Phase 6–9, or Q-011 data. VTI date-observe authority is the separate memo named in Item 1, not this file.

---

## Standing rules

1. Charter before code. Named AUTHORIZE before Cursor codes that slice.
2. Claude audits before Todd treats a slice as accepted (unless Todd waives in writing for that slice).
3. No tool writes “Todd authorized …” into controlling docs without a memo that already exists.
4. Public `radar_v4/` stays free of vendor HTTP clients unless a future unit explicitly says otherwise.
5. Sebastian Protocol is not displaced; whether work proceeds while that gate is unrecorded is Todd’s precondition call (Item 0).

---

## Item 0 — Sebastian precondition (Todd only)

**Decide:** May Radar V4 move on Items 1+ while Sebastian’s gate is unrecorded, or hold all movement until that gate is recorded?

- [x] Proceed with Items 1+ under this split  
- [ ] Hold all V4 movement until Sebastian gate is recorded  

**Decision (TC), 2026-09-24:** Proceed with Items 1+ under the Grok/Cursor/Claude/Todd split while the Sebastian gate remains unrecorded. Sebastian Protocol is still not displaced; this is a move-ahead precondition choice, not a claim that the gate is closed or satisfied.

Cursor work on HA-1 still requires the AUTHORIZE line in Item 4. VTI after-the-fact AUTHORIZE is the separate memo named in Item 1 (signed; Claude audit still open). Item 0 alone is not code authority.

---

## Item 1 — VTI custody (after-the-fact AUTHORIZE)

**Status:** AFTER-THE-FACT AUTHORIZE signed TC 2026-09-24. Memo banked at `docs/governance/2026-09-24-vti-private-date-observe-authorize-TC.md`. PR 45 already on `main` (`d47ad23d8ec680eaa1a9cf46e7f110aef765864a`).

**Owner:** Todd signed Accept as written; Claude still audits memo ↔ landed code. Scope description is no longer the blocker.

1. Todd described the authorized scope and signed Accept as written — TC (2026-09-24): symbol, cadence, source, claim ceiling, outputs/store, stop/review, explicit non-allows, patch author, relation to the withdrawn SPY carve-out / Phase 9, side path vs HA-1, and `marketPrice` / retain entitlement.  
2. The **VTI authorization memo** is banked at the path above (vacatur of the mistaken REJECT is in that memo).  
3. Claude audits memo ↔ landed `vti_date_observe`. Open defects (receipt date check, global statuses) remain open until that audit.  
4. Todd’s decision on this slice is the after-the-fact Accept as written, not a pre-land gate.  
5. The observation path is already on `main` via PR 45. This backlog line does not reopen land.

**Not blocked on scope.** Claude audit remains pending; known open defects stay open until that audit.

---

## Item 2 — Bank Q-011 metric contradiction finding

**Owner:** Grok Bot already drafted; Claude quick confirm; Todd bank.

- File: `docs/research/2026-09-24-q-011-phase5-metric-contradiction-finding.md`  
- Bank as custody only. Does not authorize Q-011 data or Phase 6.

---

## Item 3 — Revise HA-1 frozen draft (four fixes)

**Owner:** Grok Bot revises paper; Claude audits; Todd AUTHORIZE execution later.

Before any Cursor HA-1 coding, revise the proposal to:

1. **Separate constant** — dataset/export/snapshot paths get their own allowlist including HISTORICAL; leave `PACK_ALLOWED_PROVENANCE` in `fixture_pack.py` as FIXTURE/SYNTHETIC only (do not widen the shared import).  
2. **Binding** — state clearly: procedural-only **or** minimal declaration check that pack symbol/source match AUTHORIZE names.  
3. **Test-only marker** — required marker in test HISTORICAL declarations; real MEASURED path refuses that marker (no fragile path sniffing).  
4. **Sebastian** — move from mid-build stop to **precondition for AUTHORIZE** (ties to Item 0).

Then: Claude audit → Todd `AUTHORIZE BUILD UNIT HA-1 — TC` (must name symbol + source class) → Cursor implements → Claude audits diff/tests → Todd accept/STOP.

---

## Item 4 — HA-1 execution (Cursor)

Only after Items 0 and 3 and a filled AUTHORIZE line.

- Implement question-bound HISTORICAL admission; LIVE stays quarantined; tests under `tests/`; no real market bytes in git; no vendor client in `radar_v4/`.  
- Private CSV→JSON remains outside package if source is CSV.

---

## Item 5 — First real Phase 5 MEASURED run (after HA-1)

- Private pack for Todd-named symbol + source.  
- Workshop session / baseline close-to-close **difference** only.  
- Claude audits claim language and provenance.  
- Not Q-011. VTI date-only observe stays the separate authorized side path in Item 1; it is not this HA-1 MEASURED run.

---

## Explicitly not on this backlog yet

- Q-011 metric change / group means (Phase 6-adjacent)  
- Re-opening the withdrawn SPY observe carve-out as drafted  
- Phase 6–8 method / pilot / UI  
- Phase 9 earned status  
- More Phase 5 inspectability units for their own sake  

---

## Immediate next actions (in order)

| # | Action | Who |
|---|---|---|
| 0 | Sebastian proceed vs hold | **Todd — DONE 2026-09-24: proceed** |
| 1a | Describe VTI authorization scope | **Todd — DONE 2026-09-24: Accept as written** |
| 1b | Draft / bank VTI AUTHORIZE memo | **DONE 2026-09-24** — `docs/governance/2026-09-24-vti-private-date-observe-authorize-TC.md` |
| 1c | Audit memo ↔ landed `vti_date_observe` | **Claude — PENDING** (receipt date check, global statuses remain open) |
| 2 | Bank Q-011 contradiction finding | Todd (+ Claude skim) |
| 3 | Revise HA-1 on four points | **Grok Bot — R1 DRAFTED 2026-09-24** → Claude audit → Todd |
| 4 | AUTHORIZE HA-1 + Cursor implement | Todd → Cursor → Claude → Todd |

---

## Disposition

```text
OPERATING SPLIT — GROK PLANS / CURSOR CODES / CLAUDE AUDITS / TODD AUTHORIZES-TC
BACKLOG — RECORDED 2026-09-24
CODE AUTHORITY — NONE FROM THIS DOCUMENT ALONE
NEXT HUMAN INPUT — Q-011 FINDING BANK (ITEM 2); HA-1 AUTHORIZE NOT ON MAIN (ITEM 0 DONE: PROCEED)
```

**Tools verify. Todd authorizes.**
