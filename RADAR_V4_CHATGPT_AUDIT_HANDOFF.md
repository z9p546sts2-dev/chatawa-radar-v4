# ChatGPT Audit Handoff — Radar V4 through Unit 100

```text
DATE — 2026-08-22
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4
BRANCH — cursor/phase-5-dataset-session-9fd5
PR — https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/8
HEAD — 053fc2808d6fe3b53de984b20f2e9ef6a1a3c15a
BASE / main — 1ff2333 (Phase 5 units 7–11 only)
AUTHORITY — Todd C. (toddmcraft@gmail.com) only
IMPLEMENTER — Cursor (bounded engineer)
INTENDED AUDITOR — ChatGPT (independent)
```

This record is for independent audit. It is not a method claim, not a performance report, and not authorization of the next class of work.

**Tools verify. Todd authorizes.**

---

## Auditor assignment

Review this repository as an independent auditor. Do not implement. Do not enlarge scope. Do not treat software tests as market evidence.

Answer:

1. Did the implementer stay inside Todd-authorized Phase 5 evidence-ops?
2. Are the earned-claim statements honest?
3. Did later units (especially 43–100) add integrity, or only decorative surface area?
4. Is V1/V2 correctly excluded from inheritance?
5. What, if anything, is overclaimed in README / ROADMAP / GOVERNANCE / this handoff?
6. What is the smallest next authorization that would change the claim class?

Do not recommend buying a vendor API, opening paper trading, or starting Phase 6 unless Todd has already named that authorization.

---

## Roles and control

| Role | Bound |
|---|---|
| Todd C. | Sole authority. Accepts, authorizes, stops. |
| Cursor | Bounded implementer. May write only inside authorized units. |
| ChatGPT | Independent auditor. Verifies claims. Does not authorize. |
| Tests / CLI | Verify software behavior. Do not authorize. |

Exact authorizations used on this path include:

- `AUTHORIZE BUILD UNIT 1 — TC`
- `Accepted-TC` (Units 1 and 2)
- `AUTHORIZE PHASE 5 — TC`
- continued-build phrases (`Lets keep building`, `You can continue to build and not stop after building the units -TC`)
- `Go ahead and do up too 100 units-TC`

Ready / complete-within-scope of a unit is **not** authorization of the next *class* of work (vendor API, Phase 6 method, paper trading, Product B).

---

## What Radar V4 is

A **human-controlled local evidence workshop** for one locked Phase 5 question.

It can:

- represent evidence identity and provenance;
- refuse invalid, contradictory, or wrong-provenance records without repair;
- admit a declared local dataset;
- describe ordinary close-to-close **difference** (not percent) for one symbol, interval `1d`;
- persist snapshots, rulers, checksums, manifests, journals, registries, and reports;
- inspect and compare those artifacts locally.

It is **not**:

- a trader, broker, or execution engine;
- a signal factory;
- a revival of Radar V1 or V2;
- Product B (a separately named autonomous trading program);
- a claim of edge.

Intended product order still locked by Todd:

1. **Product A** — evidence system first (later packagable as records/refusals, not trades).
2. **Product B** — only if a method is later earned. Year 5 does not create it. “Best trades” is a prohibited claim.

---

## Governing claim classes

These remain separate. Passing one does not earn the next.

| Class | Status now |
|---|---|
| Software correctness | Earned on the local FIXTURE/SYNTHETIC path. 166 tests passed at HEAD. |
| Data correctness | **Not earned.** No real HISTORICAL records are in the workshop. |
| Method validity | **Not defined.** No Phase 6 authorization. |
| Usefulness / edge | **Not asked. Not shown.** |

Allowed Phase 5 result language: `MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`.

Claim level available now: `LEVEL 0 — MEASURED` only.

`NO EDGE SHOWN` is not applicable because no edge was asked.

---

## Locked Phase 5 question

Source: `RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`

> In one declared daily dataset for one symbol, what are the ordinary close-to-close differences when every observation uses the same interval, timezone, and transformation version?

Primary metric: `close[t] - close[t-1]` as a decimal string. Not percent. Not a score.

Provenance classes: `LIVE`, `HISTORICAL`, `BACKFILL`, `SYNTHETIC`, `FIXTURE`, `REPLAY`, `MANUALLY_EDITED`.

Pack loaders (`load_fixture_pack`, `load_dataset_pack`, pack export) allow **only FIXTURE/SYNTHETIC**. HISTORICAL/LIVE labels are quarantined as `PACK_PROVENANCE_NOT_ALLOWED`. In-memory `admit_to_dataset` may admit HISTORICAL if the declaration says so. Nothing in this repo downloads HISTORICAL or LIVE data.

The in-repo pack `fixtures/synthetic_one_symbol_1d/` is labeled **SYNTHETIC**. On that pack the session reports:

- 3 admitted daily bars;
- baseline status `MEASURED`;
- claim level `LEVEL 0 — MEASURED`;
- changes `0.50`, `-0.50`;
- ruler checksum `403b2863229368350ac8f20a07a800a6927dc017f0efa6ec0b15305234fc9cee`.

Those numbers are software-test material. They are **not** market evidence.

---

## Legacy V1 / V2 (closed)

Banked in `postmortem/RADAR_V1_V2_FINAL_FINDINGS.md`.

- V1: REJECT AND PRESERVE.
- V2: stronger software (89/89 tests historically) but no method validity; daily features on an intraday clock; 30+ unevidenced thresholds; `outcome_history.csv` is not trustworthy as performance evidence.

V4 does **not** inherit V1/V2 code or trading methodology. No legacy file may be copied merely because it exists.

---

## What was built (units)

### Build units 1–6 (foundation)

Evidence envelope, intake/quarantine, JSON document intake, in-memory registry, identity collision gate, fixture pack loader.

Units 1 and 2 were separately accepted by Todd. Units 3–6 were built under continued-build authorization without per-unit stop.

### Phase 5 units 7–22 (measurement path)

Dataset declaration and admission, observation payload, ordinary close-to-close description, series integrity (no calendar fill), snapshot, session composition, observation/declaration JSON, local pack, local session, session report, snapshot compare, pack identity collision, CLI, SYNTHETIC fixture pack.

This is the only slice that can produce `MEASURED` on a valid series.

### Phase 5 units 23–42 (record identity)

Change records, snapshot checksum, pack session report, CLI replay, reason-code catalog, snapshot verify, pack export, registry files, change continuity, measurement ruler (`dataset_id` is a name, not the ruler), quarantine journal, checksum sidecar, replay ruler lock, pack artifact skip list, pack manifest verify, ruler sidecar, session-report `document_kind`.

### Phase 5 units 43–57 (integrity workshop)

Atomic write (temp sibling, then replace), manifest gate on load, `session --require-manifest` / `--expect-ruler`, pack-compare, `MANIFEST_REQUIRED`, overwrite refusal (`FILE_EXISTS` unless `--replace`), pack inventory, bundle write/verify, journal/registry document kinds, inventory digests.

### Phase 5 units 58–100 (inspect / compare / status)

Document-kind detect, show declaration/snapshot/observation, provenance mix, admission without measurement, compare rulers/reports/inventories, journal summary, report-to-snapshot bind, determinism (run twice, compare snapshot checksums), snapshot inventory, pack layout, canonical JSON check, pack identities/describe/readiness, reason-code lookup, workshop `status`.

`python -m radar_v4 status` at HEAD:

```text
highest_unit: 100
method_defined: false
vendor_authorized: false
historical_evidence: false
fixture_is_market_evidence: false
paper_trading_authorized: false
claim_level: LEVEL 0 — MEASURED
```

Honest auditor note: units 58–100 do not change the claim class. They make the workshop inspectable. Completing unit 100 is not a research result.

---

## Software facts at HEAD

```text
LANGUAGE — Python 3.12, stdlib only
TEST COMMAND — PYTHONPATH=. python3 -m unittest discover -s tests -v
TESTS AT HEAD — 166 passed
REASON CODES — catalog present (python -m radar_v4 codes)
CLI — python -m radar_v4
NETWORK — none in this package
VENDOR CLIENT — none
BROKER / PAPER — none
```

CLI command groups:

- run: `session`, `replay`, `admission`, `determinism`
- persist: `export-pack`, `write-bundle`, `pack-manifest`, `quarantine`, `registry-write`
- verify: `verify`, `pack-verify`, `bundle-verify`, `canonical-check`, `report-bind`, `inventory-manifest`
- compare: `compare`, `pack-compare`, `compare-rulers`, `compare-reports`, `compare-inventories`
- inspect: `pack-inventory`, `pack-layout`, `pack-identities`, `pack-describe`, `provenance-mix`, `readiness`, `snapshot-inventory`, `detect-kind`, `show-*`, `journal-summary`, `code`, `codes`, `status`

Serialization rules still bind:

- sorted-key compact JSON;
- timestamps ISO-8601 with microseconds and offset;
- missing timezone is **not** defaulted to UTC;
- provenance stored as `ProvenanceClass.value`.

The workshop will not invent market calendars, exchange hours, or missing bars.

---

## Still unauthorized

These remain unauthorized even though units 7–100 exist:

- purchased historical-stock API or any named vendor;
- live capture;
- labeling SYNTHETIC/FIXTURE prices as HISTORICAL;
- Phase 6 method research;
- indicators, scores, thresholds, ranking;
- backtesting as method validation;
- paper trading / simulated orders (Horizon 4A, only after a locked historical pilot);
- Product B;
- copying V1/V2 implementation.

Paper trading is not a start method.

Do not buy a historical-stock API until a question is locked **and** Todd names the vendor/API. Phase 5 software may *admit* `HISTORICAL` records in memory; it must not download them.

---

## Controlling-record honesty

`main` has **not** been fast-forwarded to this branch. `main` HEAD remains the series/snapshot slice (units 7–11). The unit 12–100 work lives on PR #8.

If a controlling record on `main` disagrees with this branch, the auditor should report the conflict rather than choose an interpretation.

---

## How to verify independently

From the PR branch:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m radar_v4 status
PYTHONPATH=. python3 -m radar_v4 pack-describe --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 session --pack fixtures/synthetic_one_symbol_1d --require-manifest
PYTHONPATH=. python3 -m radar_v4 determinism --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 pack-verify --pack fixtures/synthetic_one_symbol_1d
```

Expected:

- 166 tests pass;
- `status` denies method, vendor, historical evidence, and paper trading;
- `session` on the fixture pack is `MEASURED` with SYNTHETIC changes `0.50`, `-0.50`;
- `determinism` is equal;
- `pack-verify` matches the stored manifest.

If any command invents a session for a missing pack, downloads data, or prints an edge claim, that is a fail.

---

## Risks the auditor should press

1. **Claim-class drift.** Unit-count completion can be misread as research progress. Units 43–100 are workshop integrity/inspectability. They do not earn data correctness.
2. **SYNTHETIC familiarity.** Repeated `MEASURED` output on the fixture pack can start to feel like a result. It is not.
3. **Decorative surface.** Many CLI commands now exist. Ask whether each one refuses something a human could otherwise misread.
4. **Authorization breadth.** Continued-build phrases plus “up to 100 units” are wide. Confirm the implementer did not use that width to add indicators, vendors, or methods.
5. **Unmerged `main`.** Status docs on the branch say units 7–100. `main` still says 7–11. That is a record split, not a production promotion.

---

## Honest current claim

The local evidence workshop on PR #8 can load, refuse, measure LEVEL 0 close-to-close on a SYNTHETIC one-symbol daily pack, lock a ruler, journal refusals, snapshot, verify, export, tamper-check, inspect, and compare local artifacts.

**No edge. No HISTORICAL measurement. No vendor. No method. No paper trading.**

Completion of units 7–100 does not authorize a data purchase or Phase 6.

---

## Smallest next authorizations that would change the claim class

Only Todd can issue these. The auditor should not treat them as implied.

| If Todd names… | Then the class that can change is… |
|---|---|
| A vendor/API **by name**, after the locked question remains locked | Data access (still not method validity) |
| `AUTHORIZE PHASE 6 — TC` plus one predeclared comparison | Method research (still not usefulness) |
| A locked historical pilot, then Horizon 4A paper | Observation of a later operational layer (not a start method) |

Until one of those is named, further software on SYNTHETIC packs cannot honestly change the claim class.

---

## Disposition for ChatGPT

```text
RECORD TYPE — IMPLEMENTATION AUDIT HANDOFF
SCOPE — UNITS 1–6 + PHASE 5 UNITS 7–100
SOFTWARE CORRECTNESS — 166 TESTS PASSED AT HEAD (VERIFY)
DATA CORRECTNESS — NOT EARNED
METHOD VALIDITY — NOT DEFINED
USEFULNESS / EDGE — NOT SHOWN
VENDOR / LIVE / PAPER — NOT AUTHORIZED
V1/V2 INHERITANCE — FORBIDDEN
NEXT CLASS OF WORK — NOT AUTHORIZED BY UNIT 100
AUDITOR ACTION — VERIFY CLAIMS; REPORT OVERCLAIM; DO NOT IMPLEMENT
```

Learning and Earning It.  
Stay on course.  
No drift.
