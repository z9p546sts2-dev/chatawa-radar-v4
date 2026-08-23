# Chatawa Radar V4 — Foundation Roadmap

## Status

**STACKED DRAFT BRANCH STATUS — PHASE 5 UNITS 7–900 COMPLETE WITHIN AUTHORIZED LOCAL-SOFTWARE SCOPE; MAIN CURRENTLY THROUGH UNIT 200.**

Radar V4 has a bounded evidence foundation plus Phase 5 dataset session software on this stacked draft branch. `main` currently carries units 7–200 only. Todd authorized continued building without per-unit stops. Vendor download and method research remain unauthorized.

Todd retains final authority over activation, scope, architecture, data use, testing, build authorization, deployment, and any future operational role.

The long-horizon companion is `RADAR_V4_HORIZON_ROADMAP.md`. Years do not authorize stages.

## Intended purpose

Radar V4 may eventually become a human-controlled intelligence and opportunity-ranking system that:

- organizes verified evidence;
- compares expectations with observed outcomes;
- ranks items for human review;
- preserves uncertainty and provenance;
- separates evidence from interpretation;
- remains advisory rather than autonomous.

Radar V4 is not:

- a trading engine;
- an execution system;
- an autonomous portfolio manager;
- a claim of edge;
- permission to revive legacy Radar code;
- an active implementation merely because planning is mature.

## Governing principles

1. Evidence before interface.
2. No label outruns operation.
3. No signal claim before a measurement rule exists.
4. No ranking rule before failure cases are defined.
5. No live data before a bounded test is approved.
6. No legacy reuse without file-level review and Todd authorization.
7. Human authority remains explicit.
8. Every output must preserve provenance and uncertainty.
9. A repository or readiness review is not implementation authorization.
10. Software correctness is not method validity.
11. Negative and unclear outcomes are valid.
12. No drift.

# Phase 0 — Purpose and authority

Objective:

Define purpose, authority, boundaries, and prohibited interpretations.

Deliverables include:

- `README.md`;
- `ROADMAP.md`;
- `GOVERNANCE.md`;
- prohibited-use boundaries;
- authority model.

**Status:** COMPLETE

# Phase 1 — Legacy V1 and V2 forensic evidence inventory

Objective:

Document `legacy-radar-v1` and `legacy-radar-v2` as historical evidence without automatically promoting or reusing components.

The bounded forensic review was completed and its findings were translated into V4 controls and engineering requirements.

Legacy repositories remain evidence sources. Legacy implementation is not inherited by V4.

**Status:** COMPLETE

# Phase 2 — Evidence-first research methodology

Objective:

Define the research process required before stronger market claims or methods can be considered.

The methodology now establishes:

- narrow question predeclaration;
- data identity and provenance;
- cadence and timing gates;
- ordinary baseline discipline;
- same-ruler comparisons;
- separation of direction, magnitude, usefulness, and validity;
- threshold-entitlement discipline;
- historical validation before promotion;
- replication and robustness before stronger claims;
- explicit human promotion decisions.

This phase defines a research process, not a trading method.

**Status:** COMPLETE / AUDITED

# Phase 3 — Build Unit 1 proposal: Evidence Envelope and Provenance Gate

Objective:

Define the smallest non-market software foundation that can represent, validate, serialize, and fingerprint evidence identity before market logic exists.

Build Unit 1 is limited to:

- evidence-envelope identity fields;
- provenance validation;
- deterministic serialization;
- checksum generation/verification;
- explicit fixture/synthetic examples;
- SOFTWARE CORRECTNESS tests;
- DATA CORRECTNESS tests;
- syntax/import integrity;
- one bounded unit README.

Explicitly excluded:

- live or historical market data;
- provider selection/fallback implementation;
- features;
- indicators;
- event logic;
- ranking;
- scores;
- confidence;
- thresholds;
- signals;
- backtesting;
- machine learning;
- dashboards;
- schedulers;
- brokerage;
- trading;
- autonomous operation;
- legacy code copy/import/adaptation.

The proposal and its audit are complete. The authorization-readiness review passed. Todd later authorized and accepted execution.

**Status:** COMPLETE

**Execution:** ACCEPTED-TC

# Phase 4 — Build Unit 1 execution

Objective:

If and only if Todd separately authorizes it, implement the bounded Evidence Envelope and Provenance Gate exactly within the approved scope.

Expected minimal file boundary:

```text
radar_v4/
  __init__.py
  evidence.py
  validation.py

tests/
  test_evidence_software.py
  test_evidence_data.py

README_BUILD_UNIT_1.md
```

Future execution constraints:

- no market-data network calls;
- no live data;
- no historical market data;
- no database access;
- no secrets;
- no legacy code reuse;
- no market method logic;
- no thresholds/signals/trading;
- unit tests plus syntax/import checks only.

Build Unit 1 earned only a small evidence/provenance software foundation. It does not authorize the next unit.

**Status:** COMPLETE WITHIN SCOPE / ACCEPTED-TC

# Phase 5 — Data / research foundation

Objective:

Local FIXTURE/SYNTHETIC dataset admission, ordinary close-to-close description, integrity, and inspectability. Real historical data access, vendor download, and method research remain a later class of work.

This phase must not begin automatically after Build Unit 1.

Before any real dataset is admitted, required controls include provenance, source identity, interval/cadence semantics, timestamps, timezone, transformation identity, integrity checks, and quarantine of contradictory or unknown-provenance data.

**Status:** AUTHORIZED-TC / STACKED DRAFT UNITS 7–900 COMPLETE WITHIN SCOPE FOR LOCAL SOFTWARE ONLY; MAIN CURRENTLY THROUGH UNIT 200

Vendor download, paper trading, and method research remain unauthorized. Completing units 7–900 does not authorize a data purchase.

# Phase 6 — Candidate feature / method research

Objective:

Only after evidence/data foundations are separately earned, evaluate one narrow predeclared market question under the controlling V4 methodology.

No feature, threshold, ranking, score, or method is inherited from legacy Radar.

A candidate method would require ordinary baseline evidence, predeclared comparisons, threshold entitlement where applicable, historical validation, and later robustness work.

**Status:** NOT AUTHORIZED

# Phase 7 — Bounded offline pilot

Objective:

Test one separately approved method using fixed historical material and preregistered rules.

Required controls include:

- one question;
- fixed dataset;
- fixed method/ranking rule;
- fixed review period;
- no live trading;
- no execution;
- no code changes mid-test without restart;
- explicit stop condition.

**Status:** NOT AUTHORIZED

# Phase 8 — Human review interface

Objective:

Only after a method is defined and tested, design a review surface showing underlying evidence, provenance, uncertainty, freshness, missing data, counterevidence, ranking reason, and human disposition.

No dashboard is required before method validation.

**Status:** NOT AUTHORIZED

# Phase 9 — Controlled live observation

Objective:

Observe live information without autonomous recommendations or execution.

Restrictions include:

- read-only;
- advisory only;
- no brokerage connection;
- no orders;
- no portfolio authority;
- explicit shutdown control;
- human review required.

**Status:** NOT AUTHORIZED

## Current authorized work

Authorized now:

- documentation/status maintenance;
- read-only repository inspection;
- completed forensic-evidence review and preservation;
- methodology review and maintenance;
- Build Units 1–6 evidence/provenance, intake, JSON, registry, collision, and fixture-pack software;
- Phase 5 units 7–850 dataset declaration through local pack session, integrity, inspect/compare/bind, claim/arithmetic/scope checks, pack safety, local audit copy, record/round-trip/catalog checks, hygiene/lineage/decimal/certify compose, byte-identity and freeze records, path/name/kind lock, workshop stamp, journal lock, report/ruler lock, snapshot/disposition lock, manifest/sidecar lock, bundle/export lock, audit/chain lock, inventory/layout lock, safety/leftover lock, and a workshop stop record.

Not authorized now:

- a purchased market-data API or live download;
- treating SYNTHETIC or FIXTURE numbers as HISTORICAL evidence;
- Phase 6 method research;
- backtesting;
- market features;
- ranking logic;
- scores or thresholds;
- signals or edge claims;
- legacy code migration;
- brokerage, paper trading, or simulated orders.

## Immediate next action

Vendor download, paper trading, and Phase 6 still require a separate named authorization. Do not buy an API or open a paper account because Units 7–850 exist. The in-repo fixture pack is SYNTHETIC and is not market evidence.

## Current roadmap status

```text
PHASE 0 — PURPOSE / AUTHORITY                         COMPLETE
PHASE 1 — LEGACY FORENSIC REVIEW                     COMPLETE
PHASE 2 — RESEARCH METHODOLOGY                       COMPLETE / AUDITED
PHASE 3 — BUILD UNIT 1 PROPOSAL / AUTH READINESS     COMPLETE / PASS
PHASE 4 — BUILD UNIT 1 EXECUTION                     COMPLETE WITHIN SCOPE / ACCEPTED-TC
PHASE 4A — BUILD UNIT 2 INTAKE / QUARANTINE          COMPLETE WITHIN SCOPE / ACCEPTED-TC
PHASE 4B — BUILD UNITS 3–6 JSON / REGISTRY / COLLISION / FIXTURE PACK  COMPLETE WITHIN SCOPE
PHASE 5 — DATA / RESEARCH FOUNDATION                 AUTHORIZED-TC / STACKED DRAFT 7–850; MAIN THROUGH 200
PHASE 6 — FEATURE / METHOD RESEARCH                  NOT AUTHORIZED
PHASE 7 — BOUNDED OFFLINE PILOT                      NOT AUTHORIZED
PHASE 8 — HUMAN REVIEW INTERFACE                     NOT AUTHORIZED
PHASE 9 — CONTROLLED LIVE OBSERVATION                NOT AUTHORIZED
```

## Governing principle

> Build the evidence container before building the market story. Accepting Unit 1 is not authorization of Unit 2.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.
