# Radar V4 Build Unit 1 Authorization Review — TC

**Date:** 2026-08-07  
**Authority holder:** Todd C.  
**Reviewed unit:** Build Unit 1 — Evidence Envelope and Provenance Gate  
**Review type:** Pre-execution authorization readiness review  
**Execution authority granted by this review:** No

---

## 1. Question

> Is Build Unit 1 sufficiently bounded, reversible, testable, non-market, and governance-complete for Todd to make an explicit execution-authorization decision?

This review does not authorize implementation.

---

## 2. Controlling evidence

The review relies on:

- `RADAR_V4_METHODOLOGY_DEFINITION_TC.md`;
- `RADAR_V4_BUILD_UNIT_1_PROPOSAL_TC.md`;
- `RADAR_V4_BUILD_UNIT_1_PROPOSAL_TC_AUDIT.md`;
- `V4_CONTROL_REQUIREMENTS.md`;
- `V4_ENGINEERING_REQUIREMENTS.md`;
- the closed V1/V2 forensic findings and pre-build review.

---

## 3. Authorization-readiness checks

### Purpose and scope

```text
ONE BOUNDED UNIT — PASS
PURPOSE CLEAR — PASS
NON-MARKET FOUNDATION — PASS
IN-SCOPE BEHAVIOR DEFINED — PASS
OUT-OF-SCOPE BEHAVIOR DEFINED — PASS
```

Build Unit 1 is limited to an evidence-envelope/provenance-validation substrate. It contains no market feature, strategy, signal, score, threshold, outcome model, or trading logic.

### Methodology boundary

```text
RESEARCH-PROCESS METHODOLOGY EXISTS — PASS
SPECIFIC MARKET METHOD REQUIRED FOR THIS UNIT — NO
MARKET CLAIMS CREATED BY THIS UNIT — NO
METHOD-VALIDITY TESTS REQUIRED — NOT APPLICABLE
```

The unit supports evidence identity only. It does not require a market method because it is intentionally pre-method infrastructure.

### Data boundary

```text
LIVE MARKET DATA — PROHIBITED
HISTORICAL MARKET DATA — PROHIBITED
DATABASE ACCESS — PROHIBITED
FIXTURE/SYNTHETIC EXAMPLES — ALLOWED IF EXPLICITLY LABELED
PROVENANCE-UNKNOWN DATA — MUST FAIL / QUARANTINE
```

PASS.

### Legacy boundary

```text
LEGACY CODE COPY — PROHIBITED
LEGACY IMPORT — PROHIBITED
CHERRY-PICK — PROHIBITED
LEGACY METHODOLOGY REUSE — PROHIBITED
REQUIREMENT/PATTERN LESSONS ONLY — ALLOWED
```

PASS.

### Implementation boundary

The proposed file boundary is small and reviewable:

```text
radar_v4/__init__.py
radar_v4/evidence.py
radar_v4/validation.py
tests/test_evidence_software.py
tests/test_evidence_data.py
README_BUILD_UNIT_1.md
```

Exact names may be refined only if scope remains equivalent. Any expansion beyond this class of files requires STOP and reauthorization.

PASS.

### Test plan

Predeclared SOFTWARE CORRECTNESS tests cover imports, construction, deterministic serialization, round trip, checksums, mismatch detection, and stable result structure.

Predeclared DATA CORRECTNESS tests cover required provenance/source/symbol/time/interval/timezone/transformation/integrity fields and fixture/synthetic identity.

Test criteria are locked before implementation and may not be weakened after results are seen.

PASS.

### Acceptance criteria

The proposal permits:

- COMPLETE WITHIN SCOPE;
- PARTIALLY COMPLETE;
- FAILED;
- STOPPED;
- UNCLEAR.

A green test suite is not required as a governance outcome if the unit honestly fails or stops.

PASS.

### Rollback and reversibility

No external data, migration, database, live system, or irreversible transformation is allowed.

Rollback is source-control reversion to the pre-unit commit.

PASS.

### Tool and write boundary

If Todd explicitly authorizes execution, authority would be limited to:

```text
TARGET — z9p546sts2-dev/chatawa-radar-v4
WRITES — BUILD UNIT 1 SOURCE / TEST / README FILES ONLY
EXECUTION — BUILD UNIT 1 UNIT TESTS + SYNTAX / IMPORT CHECKS ONLY
NETWORK MARKET DATA — NONE
LIVE DATA — NONE
HISTORICAL MARKET DATA — NONE
DATABASE — NONE
SECRETS — NONE
LEGACY REPO WRITES — NONE
LEGACY CODE REUSE — NONE
BROKER / TRADING — NONE
```

PASS AS REQUESTED BOUNDARY. Execution remains unauthorized until Todd explicitly grants it.

### Stop conditions

Stop on:

- scope expansion;
- live/historical market-data requirement;
- feature/indicator/signal/score/threshold introduction;
- legacy code reuse pressure;
- new non-minimal dependency requirement;
- post-result test weakening;
- silent data repair;
- market-methodology drift;
- ambiguous tool/write authority.

PASS.

---

## 4. Review disposition

```text
BUILD UNIT 1 AUTHORIZATION READINESS — PASS
STATUS — READY FOR TODD AUTHORIZATION DECISION
EXECUTION AUTHORIZED BY THIS REVIEW — NO
CODE WRITES — NONE
TEST EXECUTION — NONE
DATA INGESTION — NONE
LEGACY REUSE — NONE
```

The unit has earned a decision point. It has not earned self-execution.

---

## 5. Exact authority required to begin

Execution may begin only after Todd explicitly states authorization equivalent to:

```text
AUTHORIZE BUILD UNIT 1 — TC
```

That authorization would apply only to the bounded Evidence Envelope and Provenance Gate unit and the tool/write/test boundaries recorded above.

It would not authorize Build Unit 2, market data, features, methods, thresholds, backtesting, shadow operation, or trading.

---

## Closing principle

> Ready for authorization is not authorization.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.  
Stay on the roadmap.
