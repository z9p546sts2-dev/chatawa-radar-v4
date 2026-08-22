# Chatawa Radar V4

## Status: BUILD UNITS 1–6 COMPLETE WITHIN SCOPE

Radar V4 has a bounded evidence foundation: envelope, validation, intake/quarantine, JSON document intake, in-memory registry, and identity-collision gate.

Todd authorized continued building without per-unit stops. Phase 5 market data is still not authorized. This is not a market method, data feed, signal, or trading system.

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
BUILD UNIT 1 — COMPLETE WITHIN SCOPE / ACCEPTED-TC
BUILD UNIT 2 — COMPLETE WITHIN SCOPE / ACCEPTED-TC
BUILD UNIT 3 — JSON DOCUMENT INTAKE — COMPLETE WITHIN SCOPE
BUILD UNIT 4 — IN-MEMORY REGISTRY — COMPLETE WITHIN SCOPE
BUILD UNIT 5 — IDENTITY COLLISION GATE — COMPLETE WITHIN SCOPE
BUILD UNIT 6 — FIXTURE PACK LOADER — COMPLETE WITHIN SCOPE
BUILD UNIT 7 — NOT STARTED
LIVE / HISTORICAL MARKET DATA — NOT AUTHORIZED
LIVE / HISTORICAL MARKET DATA — NOT AUTHORIZED
BACKTESTING — NOT AUTHORIZED
SIGNALS / EDGE / TRADING — NOT AUTHORIZED
```

## Build Unit 1

The accepted first-code unit is:

> **Evidence Envelope and Provenance Gate**

It can represent, serialize, fingerprint, and validate evidence identity. Invalid or provenance-unknown records fail visibly and are not repaired.

See `README_BUILD_UNIT_1.md` and `RADAR_V4_BUILD_UNIT_1_ACCEPTANCE_TC.md`.

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

See `README_BUILD_UNIT_2.md` and `RADAR_V4_BUILD_UNIT_2_ACCEPTANCE_TC.md`.

Acceptance of this unit is not authorization of market data or Phase 5.

## Build Units 3–5

- **Unit 3** — JSON document intake (`README_BUILD_UNIT_3.md`)
- **Unit 4** — in-memory evidence registry (`README_BUILD_UNIT_4.md`)
- **Unit 5** — identity collision / contradiction gate (`README_BUILD_UNIT_5.md`)
- **Unit 6** — fixture pack loader (`README_BUILD_UNIT_6.md`)

These units still do not ingest vendor data or define a market method.

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

- no market-data ingestion;
- no market features;
- no ranking logic;
- no thresholds;
- no backtests;
- no signals or edge claims;
- no trading or execution;
- no automatic reuse of legacy components;
- no Build Unit 7;
- no Phase 5 dataset;
- no assumption that V1 or V2 behavior remains valid.

The repository now has a small evidence/provenance and intake/quarantine software foundation. It is not a trading-system authorization.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.
