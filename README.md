# Chatawa Radar V4

## Status: PHASE 5 AUTHORIZED — UNITS 7–1200 COMPLETE WITHIN LOCAL-SOFTWARE SCOPE

Radar V4 has a bounded evidence foundation plus a local Phase 5 path: admit a declared dataset, describe ordinary close-to-close differences, persist/verify/export snapshots, journal refusals, bind a measurement ruler, and verify pack-file integrity.

Vendor download, live capture, and method research are not authorized. This is not a trading system.

## Intended future role

Radar V4 may eventually become a human-controlled intelligence and opportunity-ranking system that preserves evidence, provenance, uncertainty, and human authority.

It is not an execution engine and does not authorize trading.

## Current earned state

```text
LEGACY V1/V2 FORENSIC REVIEW — COMPLETE
V4 CONTROL REQUIREMENTS — DOCUMENTED
V4 ENGINEERING REQUIREMENTS — DOCUMENTED
V4 RESEARCH METHODOLOGY — DEFINED / AUDITED
SPECIFIC MARKET METHOD — NOT DEFINED
BUILD UNITS 1–6 — COMPLETE WITHIN SCOPE
PHASE 5 — AUTHORIZED-TC / UNITS 7–1200 COMPLETE WITHIN LOCAL-SOFTWARE SCOPE
VENDOR API / LIVE DOWNLOAD — NOT AUTHORIZED
PHASE 6 METHOD RESEARCH — NOT AUTHORIZED
BACKTESTING — NOT AUTHORIZED
SIGNALS / EDGE / TRADING — NOT AUTHORIZED
```

The full unit ledger is `docs/UNITS.md`. Completing units 7–1200 is inspectability, not a research result.

Map of the rest of the documents: `docs/README.md`.

## Build Unit 1

The accepted first-code unit is:

> **Evidence Envelope and Provenance Gate**

It can represent, serialize, fingerprint, and validate evidence identity. Invalid or provenance-unknown records fail visibly and are not repaired.

See `docs/units/README_BUILD_UNIT_1.md` and `docs/units/RADAR_V4_BUILD_UNIT_1_ACCEPTANCE_TC.md`.

It does not authorize or define:

- live or historical market-data access;
- features or indicators;
- ranking logic;
- scores or thresholds;
- signals;
- backtesting;
- machine learning;
- brokerage;
- trading;
- autonomous operation;
- legacy-code reuse;
- Build Unit 2.

Acceptance of this unit is not authorization of the next unit.

## Build Unit 2

The accepted second-code unit is:

> **Evidence Intake and Quarantine Gate**

It validates a batch of envelopes and partitions them into accepted and quarantined records without repair.

See `docs/units/README_BUILD_UNIT_2.md` and `docs/units/RADAR_V4_BUILD_UNIT_2_ACCEPTANCE_TC.md`.

Acceptance of this unit is not authorization of market data or Phase 5.

## Build Units 3–5

- **Unit 3** — JSON document intake (`docs/units/README_BUILD_UNIT_3.md`)
- **Unit 4** — in-memory evidence registry (`docs/units/README_BUILD_UNIT_4.md`)
- **Unit 5** — identity collision / contradiction gate (`docs/units/README_BUILD_UNIT_5.md`)
- **Unit 6** — fixture pack loader (`docs/units/README_BUILD_UNIT_6.md`)

These units still do not ingest vendor data or define a market method.

## Historical planning records

These remain evidence, not present authorization:

- `docs/roadmap/RADAR_V4_HORIZON_ROADMAP.md` — long-horizon Product A before Product B. Years do not authorize stages.
- `docs/legacy/RADAR_V4_REACTIVATION_REVIEW_TC.md` — pre-Build-Unit-1 check. Later superseded as current status by completed Units 1–6 and Phase 5 units 7–950.

## Legacy relationship

The historical repositories remain:

- `legacy-radar-v1`
- `legacy-radar-v2`

Their bounded forensic review is complete. Their value is evidence, comparison, failure analysis, and engineering lessons—not automatic code reuse.

Any future legacy component decision must be classified as:

- reuse;
- rebuild;
- reject and preserve.

No component may enter Radar V4 without exact source identification, evidence, tests, dependency review, rollback planning, and Todd authorization.

No legacy source file may be copied merely because it already exists.

## Current boundary

Until Todd explicitly authorizes a later bounded unit:

- no vendor API or live download;
- no market features, indicators, scores, or thresholds;
- no ranking logic;
- no backtests;
- no signals or edge claims;
- no trading or execution;
- no automatic reuse of legacy components;
- no Phase 6 method research;
- no assumption that V1 or V2 behavior remains valid;
- no treating SYNTHETIC or FIXTURE numbers as HISTORICAL evidence.

`main` has Phase 5 local-software inspectability through unit 1000. It is not a trading-system authorization. The in-repo fixture pack is SYNTHETIC and is not market evidence. Units 101–1000 do not change the claim class.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.
