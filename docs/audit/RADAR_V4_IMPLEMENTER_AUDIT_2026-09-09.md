# Radar V4 — Implementer Program Audit

**Audit date:** 2026-09-09  
**Role:** Cursor (bounded implementer), executing a program-level audit at Todd’s request  
**Authority created by this record:** NONE  
**Software / docs HEAD at start of audit:** `5bbb726` (`main`; night-close audit already banked)  
**Packet PR:** https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/35  
**Workshop code lineage:** units 7–1300 on `main` (workshop lock `PHASE5_HIGHEST_UNIT = 1300`)  
**Independent auditor this packet is for:** ChatGPT  
**Not:** a method claim, performance report, vendor recommendation, or authorization of Horizon 2

**Tools verify. Todd authorizes.**

This is Cursor auditing Cursor, then executing the local test suite and bounded probes. It is **not** ChatGPT’s independent audit. Counts below are **implementer-executed on 2026-09-09** unless labeled otherwise.

---

## 0. Question asked

> Perform a very detailed audit of this program to make sure everything is right, and provide a summary for the auditor.

“Right” is scored against the program’s own rules, not against a desire to keep building:

1. Did the implementer stay inside Todd-authorized Phase 5 local FIXTURE/SYNTHETIC evidence-ops?
2. Are earned / not-earned claim classes honest?
3. Do governing documents match `main` HEAD, or do they overclaim / underclaim?
4. Do the tests, catalogs, and refusal machinery still hold?
5. What is the smallest next authorization that would change the claim class?

---

## 1. Disposition

```text
IMPLEMENTER AUDIT DISPOSITION — 2026-09-09

AUTHORIZED LOCAL WORKSHOP                 PASS
CLAIM-CLASS HONESTY                       PASS
HISTORICAL / LIVE PACK LOAD               STILL REFUSED
NO-VENDOR IMPORT SCAN                     PASS
STATUS SEMANTICS                          PASS (measured=false; no claim_level)
BASELINE REFUSAL CLAIM SEMANTICS          PASS (refusals use claim_level NONE)
CANONICAL-JSON CHECKER                    PASS (full text vs compact JSON + newline)
CADENCE / FRESHNESS / LOOKAHEAD           PASS AS DISTINCT CHECKS
UNIT LEDGER 7–1300                        PASS (no missing unit numbers)
317 / 279 / 351                           IMPLEMENTER-EXECUTED THIS SESSION
CONTROLLING-DOC HIGH-WATER MARKS          FAIL, THEN REPAIRED (docs only)
FIXTURE JSON CANONICAL BYTES              NOTED (pretty-printed; loader accepts)
IN-MEMORY HISTORICAL ADMIT                NOTED (pack loader still refuses)
GITHUB ACTIONS / CI                       ABSENT
INDEPENDENT CHATGPT RE-RUN                NOT THIS RECORD
DATA CORRECTNESS                          NOT EARNED
METHOD VALIDITY                           NOT DEFINED
USEFULNESS / EDGE                         NOT SHOWN
NEXT CLASS OF WORK                        NOT AUTHORIZED
STOPPING POINT                            STILL CLEAN
```

Program judgment: **everything this class of work was allowed to earn is banked.** Remaining holes are either documentation drift (repaired in this packet) or the next *class* of work (historical admission), which Todd has not authorized.

---

## 2. What the program is

Radar V4 is **Product A**: a human-controlled local evidence workshop.

It is not:

- a trader or execution engine;
- a signal, score, or ranking factory;
- a revival of Radar V1/V2;
- Product B (autonomous trading).

Locked Phase 5 question (`docs/phase5/RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`):

> In one declared daily dataset for one symbol, what are the ordinary close-to-close differences when every observation uses the same interval, timezone, and transformation version?

Allowed result language: `MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`.  
Available claim: `LEVEL 0 — MEASURED` only. Difference, not percent.

---

## 3. Earned vs not earned

| Class | State | Evidence this session |
|---|---|---|
| Software correctness | Implementer-executed **317 passed**, 0 failed | `PYTHONPATH=. python3 -m unittest discover -s tests -v` — 20.229s, `OK` |
| Reason-code catalog | **279** codes; catalog audit `valid` | `len(REASON_CODES)==279`; `audit_reason_catalog()` missing=[] |
| Document-kind catalog | **351** kinds; kind audit `valid` | `len(KNOWN_DOCUMENT_KINDS)==351`; `audit_document_kinds()` unknown=[] |
| Data correctness | **Not earned** | Only loadable measurement pack is SYNTHETIC `fixtures/synthetic_one_symbol_1d/` |
| Method validity | **Not defined** | No feature, threshold, score, ranking, or inherited V1/V2 method |
| Usefulness / edge | **Not shown** | `NO EDGE SHOWN` was not asked by the locked question |
| Vendor / live / paper / Phase 6 / Product B | **Not authorized** | `workshop_bounds()` and `workshop_status()` both false |

Four classes stay separate. Unit 1300 is inspectability, not a research result.

---

## 4. Authorization map

Completed within authorized scope:

- Phase 0 purpose / authority
- Phase 1 legacy V1/V2 forensic review
- Phase 2 methodology defined / audited
- Phase 3–4 Build Unit 1 proposal / Accepted-TC
- Phase 4A–4B Build Units 2–6 Accepted-TC / complete within scope
- Phase 5 local workshop units **7–1300** Authorized-TC / complete within local-software scope

Not authorized:

- vendor API or live download
- HISTORICAL pack admission through the loader
- Phase 6 method research
- backtesting as method validation
- paper trading / simulated orders
- Product B
- V1/V2 method inheritance

Exact prior authorizations on this path include `AUTHORIZE BUILD UNIT 1 — TC`, `Accepted-TC` (Units 1 and 2), `AUTHORIZE PHASE 5 — TC`, and continued-build phrases that authorized more **local inspectability units**, not a class change.

---

## 5. Software probes executed 2026-09-09

Commands were run from the repository root on this audit branch, against the banked `main` tree (plus later documentation repairs in this packet).

### 5.1 Status / bounds / freeze

`python -m radar_v4 status` / `workshop_status()`:

```text
highest_unit                 1300
units_complete               1-6 / 7-1300
measured                     false
historical_evidence          false
method_defined               false
vendor_authorized            false
paper_trading_authorized     false
fixture_is_market_evidence   false
available_claim_level        LEVEL 0 — MEASURED
claim_level field            ABSENT
```

`check_workshop_status_semantics()` → valid.  
`workshop_bounds()` → vendor/paper false; Phase 6 listed as not authorized.  
`scan_package_network_imports()` → `valid: true`, `found: []`.  
`readme_unit_lock()` → README contains `UNITS 7–1300`.  
`workshop_freeze()` → valid.

Forbidden-import scan covers the `radar_v4` package AST for: `requests`, `httpx`, `aiohttp`, `urllib.request`, `websocket`/`websockets`, `http.client`, `http.server`, `ftplib`.

Top-level non-`radar_v4` imports observed in the package are stdlib only (`argparse`, `ast`, `collections`, `dataclasses`, `datetime`, `decimal`, `hashlib`, `json`, `pathlib`, `re`, `sys`, `typing`, etc.). No `requirements.txt`. No third-party dependency file.

### 5.2 Synthetic pack session (not market evidence)

Pack: `fixtures/synthetic_one_symbol_1d/`

- `declaration.provenance_class = SYNTHETIC`
- universe `SYN:AAA`, interval `1d`, timezone `UTC`, `UNADJUSTED`
- `load_dataset_pack` usable; 3 accepted observations; 0 quarantined
- `run_session_from_pack` error_code `None`
- series valid and ordered
- baseline `status=MEASURED`, `claim_level=LEVEL 0 — MEASURED`
- close-to-close differences `('0.50', '-0.50')` from closes `10.00 → 10.50 → 10.00`
- notes include `descriptive close-to-close differences only` and `not a threshold, signal, or edge`

This is a **software-path** measurement on SYNTHETIC numbers. It does not earn data correctness.

`check_pack_determinism` on this pack: two sessions produce equal snapshot checksums. Equality is not a market result.

### 5.3 HISTORICAL / LIVE pack prohibition

Copied the synthetic declaration, set `provenance_class` to `HISTORICAL`, then `LIVE`:

```text
HISTORICAL load_dataset_pack.usable() = False
  PACK_PROVENANCE_NOT_ALLOWED
  "dataset pack may declare only FIXTURE or SYNTHETIC"

LIVE load_dataset_pack.usable() = False
  same code
```

Loader docstring and `PACK_ALLOWED_PROVENANCE = {FIXTURE, SYNTHETIC}` match that behavior.

**Noted distinction (not a pack-loader leak):** in-memory `admit_to_dataset()` will accept a `HISTORICAL` envelope when the **declaration also says HISTORICAL**. Nothing in this repository downloads those records. The pack loader is the local-file gate; it still refuses HISTORICAL/LIVE labels. Horizon 2 still requires a separate Todd authorization to admit HISTORICAL **through the pack loader**.

### 5.4 Claim-level semantics

`close_to_close_changes()`:

- fewer than two observations → `INSUFFICIENT_EVIDENCE` / `claim_level=NONE`
- LIVE provenance → `INVALID_COMPARISON` / `NONE`
- invalid observation or mixed ruler → `INVALID_COMPARISON` / `NONE`
- successful description → `MEASURED` / `LEVEL 0 — MEASURED`

`check_claim_level()` on session reports enforces that pairing. Workshop `status` must not carry `claim_level`. Confirmed.

### 5.5 Canonical JSON checker

`check_canonical_json()` compares the **entire file text** to `json.dumps(..., sort_keys=True, separators=(",", ":")) + "\n"`. It does not strip surrounding whitespace. That is the Unit-82 repair.

**Note, not a fail:** in-repo fixture `declaration.json` and `obs_*.json` are pretty-printed, so they are **not** canonical bytes. `manifest.json` is compact. The pack loader accepts pretty-printed observation files. Canonical enforcement is a checker, not a load requirement for this fixture. Do not treat pretty fixture JSON as a claim-class defect.

### 5.6 Three distinct temporality refusals

Probed with temporary documents against the synthetic pack (last bar `2026-08-09T14:00:00+00:00`):

| Check | Module | Refusal | Probe result |
|---|---|---|---|
| Evaluation cadence faster than bar interval | `cadence_lock.py` | `CADENCE_OVERRUN` | `1m` eval vs `1d` bar → refused; equal `1d`/`1d` → valid |
| Later stamp claiming stale bars are current | `current_claim.py` + `freshness_lock.py` | `FRESH_STAMP_STALE_BARS` | `as_of` next day + `claim_current: true` → refused; same stamp with `claim_current: false` → valid |
| Window after as-of | `horizon_lock.py` | `LOOKAHEAD_WINDOW` | `include_through` after `as_of` → refused |
| Pack bar after as-of | `horizon_bind.py` | `LOOKAHEAD_BAR` | `as_of` before last pack bar → refused |

These are four codes, three concerns: decision clock vs bars, later clock claiming currency, future information vs as-of. Freshness and lookahead are inverses, not one lock renamed.

All four codes exist in `REASON_CODES`.

### 5.7 Unit ledger

`docs/UNITS.md` lists units 7 through 1300 with **no missing numbers** (1294 entries). Footer still states vendor / Phase 6 / backtesting / signals are not authorized. `PHASE5_HIGHEST_UNIT = 1300` in `workshop_check.py`.

Package: 95 Python modules under `radar_v4/`. Tests: 62 files. Module count is not research progress.

---

## 6. Documentation findings

### 6.1 Material defect found and repaired (this packet)

Controlling files still **headlined** unit 1300, but **body current-status sentences** were frozen at earlier high-water marks. That can be misread as “`main` is only through 200” or “units 7–850 are the authorized scope.”

Repaired in this packet, documentation only, no software change:

| File | What was wrong | Repair |
|---|---|---|
| `ROADMAP.md` | “stacked draft”; “`main` currently carries units 7–200”; authorized work and next-action still said 7–850; status table said `STACKED DRAFT 7–850; MAIN THROUGH 200` | Current status, authorized work, next action, and phase table now say 7–1300 on `main` |
| `GOVERNANCE.md` | Authorized-scope item 5 and the class-change sentence still said 7–850 | 7–1300 |
| `README.md` | Historical-planning line said 7–950; current-boundary paragraph said unit 1000 | 7–1300 / unit 1300 |
| `V4_CONTROL_REQUIREMENTS.md` | “Later current status (2026-08-23)” said stacked draft 7–850 and `main` through 200 | 2026-09-09; 7–1300 on `main` |

These repairs do **not** authorize Horizon 2. They stop underclaiming `main`.

### 6.2 Historical records left as history

Dated audit snapshots, stacked-draft handoff paragraphs, and the horizon roadmap’s “later record (2026-08-22): units 7–150” remain evidence of earlier states. Do not rewrite them. Do not treat them as current HEAD.

`docs/audit/RADAR_V4_CHATGPT_AUDIT_HANDOFF.md` still contains older snapshot blocks that say `main` was through 200 / stacked drafts through 850. Those blocks are labeled history. The **current packet pointer** is updated to this 2026-09-09 summary.

### 6.3 Self-stale sentence already recorded

The 2026-08-23 ChatGPT status packet still says draft PR #33 is open. The session-close record already noted that sentence became self-stale after merge. Left unchanged as a historical packet.

---

## 7. Independent-audit gap (unchanged class)

Preserved ChatGPT independent audits:

| Audit | Scope | Disposition |
|---|---|---|
| PR #8 | units 7–100 | PASS WITH MATERIAL OPEN ITEMS |
| PR #22 at `2991557` | later inspectability slice | PASS WITH MATERIAL OPEN ITEMS |
| PR #33 posture packet | claim-class / docs at unit 1300 | PASS WITH TWO BOUNDED DOCUMENTATION REPAIRS |
| Night-close 2026-08-24 | `main` after 7–1300 | PASS WITH DECLARED VERIFICATION LIMITATION (suite not independently re-run) |

This 2026-09-09 record **does** re-run the 317 tests, but it is still implementer-executed. There is still **no GitHub Actions workflow** in the repository. ChatGPT should treat 317 / 279 / 351 as claims to confirm, not as CI-promoted facts.

Independent line-by-line software audit of units 101–1300 as a class remains incomplete. That gap does not reopen Horizon 2, and filling it with more unit-count is not required for a clean stop.

---

## 8. What would be wrong to do next

Do not, without a new named Todd authorization:

- add units 1301+ for momentum;
- buy or wire a market-data API;
- treat SYNTHETIC `0.50` / `-0.50` as historical performance;
- start Phase 6 features / thresholds;
- open paper trading;
- generate the 3,000-unit curriculum as a substitute for evidence;
- copy V1/V2 scoring paths.

---

## 9. Smallest next authorization that changes the claim class

Horizon 2, Product A only:

1. Todd names one historical source (vendor/API **or** a bounded static file). Naming is authorization-shaped; this audit does not name one.
2. Written reason a download is required instead of a smaller bounded file.
3. Declared adjustment policy and maximum staleness. No invented calendar. No filled bars.
4. Separate authorization to admit `HISTORICAL` through `load_dataset_pack`.
5. Run the **already locked** LEVEL 0 question. Allowed endings: `MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`.

Until then: **stop**, or optional documentation/custody polish that does not change the claim class.

---

## 10. Auditor packet

Give ChatGPT `docs/audit/RADAR_V4_CHATGPT_STATUS_2026-09-09.md` first.

Ask ChatGPT to confirm or refute:

1. the earned / not-earned table;
2. that HISTORICAL/LIVE still cannot load through the pack loader;
3. that cadence, freshness, and lookahead remain distinct;
4. that unit 1300 still does not change the claim class;
5. that the controlling-doc repairs in this packet are documentation-only and do not authorize Horizon 2.

**Learning and Earning It.**  
**Stay on course. No drift.**
