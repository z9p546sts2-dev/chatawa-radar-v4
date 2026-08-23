# Radar V4 Build Unit 1 Proposal — TC

**Date:** 2026-08-07  
**Authority holder:** Todd C.  
**Proposal status:** READY FOR TODD DECISION  
**Execution authorized by this record:** No  
**Implementation started:** No

---

## 1. Unit name

**Build Unit 1 — Evidence Envelope and Provenance Gate**

This is a deliberately non-market first build slice.

It does not calculate signals, features, scores, confidence, entries, exits, rankings, predictions, or trading decisions.

---

## 2. Purpose

Implement the smallest software foundation required to make future Radar V4 research inputs traceable and reject provenance-unknown or internally contradictory records before any method logic exists.

The unit exists to prove that Radar V4 can accept a small declared research record, validate its identity/provenance/timing fields, preserve it deterministically, and report validation results honestly by test category.

---

## 3. Why this is Build Unit 1

The controlling V4 records require several controls **before any code** and **before data ingestion**:

- syntax/import integrity;
- test-category labeling;
- deterministic replay;
- dataset provenance;
- visible validation failure;
- versioned configuration/identity sufficient for reproduction.

This unit implements only the minimum shared substrate necessary to satisfy those controls before any market feature or method is introduced.

---

## 4. In scope

A future authorized implementation may create only the minimal files needed for:

1. **Evidence-envelope data model** containing required identity fields:
   - provenance class;
   - provider/source;
   - symbol or universe identity;
   - market timestamp;
   - retrieval timestamp;
   - interval;
   - timezone;
   - transformation version;
   - integrity identifier/checksum;
   - optional declared context/decision-use tag reserved for future use.
2. **Validation function** that returns structured results and rejects/quarantines records with missing or contradictory required identity fields.
3. **Deterministic serialization** for the evidence envelope.
4. **Checksum generation/verification** over the canonical serialized record or preserved payload reference.
5. **Small fixture-only examples** explicitly labeled `FIXTURE` or `SYNTHETIC`; no live market data.
6. **Categorized tests** covering software correctness and data correctness separately.
7. **Syntax/import gate** for the files introduced by the unit.
8. **One bounded README/usage note** explaining what the unit proves and does not prove.

---

## 5. Explicitly out of scope

Build Unit 1 must not include:

- live market-data calls;
- historical market-data downloads;
- provider selection or fallback logic beyond placeholder interfaces;
- market features;
- indicators;
- regime logic;
- event logic;
- scoring;
- confidence;
- thresholds;
- ranking;
- signals;
- entry/exit logic;
- outcome tracking;
- backtesting;
- statistical tests of market effects;
- machine learning;
- dashboards;
- schedulers;
- notifications;
- broker connectivity;
- trading;
- autonomous operation;
- migration or copying of legacy Radar code.

---

## 6. Legacy reuse boundary

No legacy source file may be copied, imported, cherry-picked, or adapted during Build Unit 1.

The unit may use only **requirements/pattern lessons** already preserved in the V1/V2 forensic records.

Even the SQLite or logging patterns listed as reuse candidates are out of scope for this unit unless separately authorized later.

---

## 7. Proposed implementation language

Python is proposed for Build Unit 1 as an operational default, not as a forensic requirement.

Reason:

- small inspectable code surface;
- direct support for dataclasses/typing/JSON/hash utilities/testing;
- compatible with the current evidence-backed engineering direction;
- no measured requirement for another language.

Todd approval of Build Unit 1 would also approve Python **for this unit only**, unless explicitly stated otherwise.

---

## 8. Proposed minimal file boundary

Exact names may be refined before execution, but the implementation boundary should remain approximately:

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

No broader repository taxonomy is authorized by this proposal.

---

## 9. Predeclared validation rules

A valid evidence envelope must, at minimum:

- use an allowed provenance class;
- identify a provider/source;
- identify a symbol or universe;
- carry parseable market and retrieval timestamps;
- carry an explicit interval;
- carry a timezone;
- carry a transformation version;
- carry or generate an integrity checksum;
- serialize deterministically;
- preserve provenance identity through serialize/deserialize round trip.

Invalid records must return a structured invalid result or be rejected. They must not be silently corrected into validity.

The unit should not attempt to decide whether the market value itself is true.

---

## 10. Test plan — predeclared before implementation

### SOFTWARE CORRECTNESS

Required tests:

1. module imports;
2. valid envelope construction;
3. deterministic serialization of identical input;
4. serialization round trip preserves required fields;
5. checksum generation is deterministic;
6. checksum mismatch is detected;
7. validation result has stable structured form.

### DATA CORRECTNESS

Required tests:

1. missing provenance class rejected;
2. unknown provenance class rejected;
3. missing source/provider rejected;
4. missing symbol/universe rejected;
5. invalid timestamp rejected;
6. missing interval rejected;
7. missing timezone rejected;
8. missing transformation version rejected;
9. contradictory or malformed integrity identity rejected where detectable;
10. fixture and synthetic records remain explicitly identifiable as such.

### METHOD VALIDITY

```text
NOT APPLICABLE — ZERO METHOD LOGIC IN BUILD UNIT 1
```

### OPERATIONAL RESILIENCE

Only minimal import/failure visibility is in scope. Provider outages, persistence recovery, schedulers, and runtime operations are future units.

---

## 11. Acceptance criteria

Build Unit 1 can be declared **COMPLETE WITHIN SCOPE** only if:

1. all introduced Python files parse;
2. all declared package entry imports succeed;
3. required tests pass and are reported by category;
4. no test report uses passing software/data tests as a method-validity claim;
5. invalid provenance records fail visibly;
6. deterministic serialization/checksum behavior is demonstrated;
7. fixture/synthetic examples are visibly labeled;
8. no market feature, signal, threshold, or live-data path is introduced;
9. exact implementation commit and test output are preserved;
10. audit confirms the unit did not expand beyond scope.

Allowed outcomes:

- `COMPLETE WITHIN SCOPE`;
- `PARTIALLY COMPLETE`;
- `FAILED`;
- `STOPPED`;
- `UNCLEAR`.

A green test suite is not the only acceptable outcome; honest stopping is allowed.

---

## 12. Stop conditions

Stop immediately if:

- implementation requires live or historical market data;
- a feature, indicator, score, threshold, or signal is proposed;
- legacy code reuse becomes necessary;
- scope expands beyond the bounded evidence/provenance layer;
- a dependency beyond the minimal standard/testing stack becomes necessary without separate review;
- test criteria are changed after results are seen;
- invalid data is silently repaired rather than rejected/versioned;
- implementation begins to define market methodology rather than support evidence identity;
- tool/write authority becomes ambiguous.

---

## 13. Rollback / recovery

The implementation should occur as a small reviewable commit or bounded commit series.

Rollback is source-control reversion to the pre-unit commit.

No external data, database migration, historical artifact rewrite, or irreversible transformation is allowed, so rollback must not require data repair.

---

## 14. Tool and write boundary requested for future execution

This proposal does **not** grant these permissions. If Todd later authorizes Build Unit 1 execution, the requested authority would be limited to:

```text
TARGET REPOSITORY — z9p546sts2-dev/chatawa-radar-v4
WRITES — NEW/EDITED BUILD UNIT 1 SOURCE, TEST, AND UNIT README FILES ONLY
CODE EXECUTION — UNIT TESTS + SYNTAX/IMPORT CHECKS ONLY
NETWORK DATA CALLS — NONE
LIVE DATA — NONE
HISTORICAL MARKET DATA — NONE
DATABASE ACCESS — NONE
SECRETS — NONE
LEGACY REPO WRITES — NONE
LEGACY CODE COPY — NONE
BROKER / TRADING — NONE
```

A separate specialist publish workflow may be used only if Todd explicitly authorizes execution and publishing.

---

## 15. What completion would earn

Successful completion would earn only:

- a small Radar V4 code foundation exists;
- provenance identity can be represented and validated;
- deterministic evidence envelopes can be reproduced;
- software/data test categories are demonstrated in practice;
- the repository can enforce a small portion of the pre-code/data controls.

It would **not** earn:

- a valid market dataset;
- data-provider approval;
- a feature set;
- a method;
- a signal;
- a threshold;
- an edge claim;
- a backtest;
- shadow-operation readiness;
- trading readiness.

---

## 16. Proposal disposition

```text
BUILD UNIT 1 PROPOSAL — COMPLETE
UNIT — EVIDENCE ENVELOPE AND PROVENANCE GATE
SCOPE — BOUNDED / NON-MARKET
TEST PLAN — PREDECLARED
ROLLBACK — DEFINED
STOP CONDITIONS — DEFINED
LEGACY REUSE — PROHIBITED
LIVE/HISTORICAL MARKET DATA — PROHIBITED
IMPLEMENTATION AUTHORITY — NONE
STATUS — READY FOR TODD DECISION
```

Todd may later choose:

- `AUTHORIZE BUILD UNIT 1 — TC`;
- `REVISE BUILD UNIT 1 — TC`;
- `PAUSE BUILD UNIT 1 — TC`;
- `REJECT BUILD UNIT 1 — TC`.

No action follows automatically from this proposal.

---

## Closing principle

> Build the evidence container before building the market story.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.  
Stay on the roadmap.
