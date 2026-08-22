# Radar V4 Reactivation Review — TC

**Date:** 2026-08-22  
**Authority holder:** Todd C.  
**Review type:** Bounded pre-execution reactivation check  
**Controlling branch reviewed:** `main` at `cc2af9a` (2026-08-08)  
**New phase created:** No  
**Implementation started:** No  
**Execution authorized by this record:** No

This is the small reactivation check required by `ROADMAP.md` before any Build Unit 1 decision. It is not a new phase, not a second methodology, and not authorization.

---

## 1. Question

> Has the approved pre-build state remained intact enough that Build Unit 1 is still the correct next unit, with the same file, test, data, and legacy boundaries?

---

## 2. Checklist

```text
REPOSITORY STATE             PASS
ROADMAP / CONTROL DRIFT      PASS WITH NOTED SUPERSESSION
BUILD UNIT 1 SCOPE           UNCHANGED
TEST PLAN STILL VALID        YES
PYTHON / RUNTIME ASSUMPTION  PYTHON 3.12.3 PRESENT; UNIT-ONLY DEFAULT
NEW DEPENDENCIES             NONE
LEGACY REUSE                 NONE
MARKET DATA                  NONE
PAPER TRADING / BROKER       NONE
ROLLBACK STILL CLEAN         YES
AUTHORIZATION READINESS      STILL VALID — NOT AUTHORIZATION
```

---

## 3. Findings

### Repository state — PASS

`origin/main` contains documentation and the closed V1/V2 forensic record only.

Confirmed absent from `main`:

- no `radar_v4/` package;
- no `tests/` tree;
- no `.py` files;
- no `requirements.txt`, `pyproject.toml`, or other dependency manifest;
- no market-data client;
- no broker, paper, dashboard, or scheduler code.

The August 8 controlling status remains:

```text
PHASE 0 — PURPOSE / AUTHORITY                     COMPLETE
PHASE 1 — LEGACY V1/V2 FORENSIC REVIEW           COMPLETE
PHASE 2 — RESEARCH METHODOLOGY                    COMPLETE / AUDITED
PHASE 3 — BUILD UNIT 1 PROPOSAL / READINESS       COMPLETE / PASS
PHASE 4 — BUILD UNIT 1 EXECUTION                  NOT AUTHORIZED
PHASE 5–9                                         NOT AUTHORIZED
```

### Roadmap / control drift — PASS WITH NOTED SUPERSESSION

`README.md`, `ROADMAP.md`, and `GOVERNANCE.md` on `main` agree: research methodology is defined and audited; Build Unit 1 is ready for a Todd decision; execution is not authorized.

Older disposition blocks still on `main` are stale and are superseded by those August 8 records:

- `V4_CONTROL_REQUIREMENTS.md` still says `V4 methodology: NOT DEFINED` and `Radar V4: PARKED`;
- `V4_ENGINEERING_REQUIREMENTS.md` still says `V4 methodology: NOT DEFINED` and pauses further foundation documents.

That contradiction is documentation drift, not a change to Build Unit 1 scope. It does not reopen methodology design. It does not park the program behind Phase 2.

Unmerged companion work exists and is **not** part of controlling `main`:

- PR 1 — status reconcile of those stale disposition blocks;
- PR 2 — 4–5 year horizon roadmap, including later paper-trading placement as Horizon 4A.

Neither PR adds source code, market data, or a wider Unit 1 file list. Neither is required before authorization. Neither is authorization.

### Build Unit 1 scope — UNCHANGED

The only first-code boundary remains:

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

Exact names may be refined only if scope stays equivalent.

Still prohibited in this unit:

- live or historical market data;
- features, indicators, scores, thresholds, rankings, signals;
- backtesting, ML, dashboards, schedulers;
- brokerage, paper trading, simulated orders;
- copy, import, or adaptation of V1/V2 source.

### Test plan — STILL VALID

The August 7 predeclared tests are still the right tests. They have not been weakened.

SOFTWARE CORRECTNESS remains: import, construction, deterministic serialization, round trip, checksum stability, checksum mismatch, stable validation result.

DATA CORRECTNESS remains: missing/unknown provenance, missing source, missing symbol/universe, bad timestamps, missing interval/timezone/transformation, bad integrity identity, visible `FIXTURE` / `SYNTHETIC` labels.

METHOD VALIDITY remains `NOT APPLICABLE`.

If execution is later authorized, first-commit lock rules already identified by the pre-build tabletop should travel with the unit and do not enlarge it:

- canonical serialization (key order, timestamp format, omitted optionals);
- allowed provenance classes only: `LIVE`, `HISTORICAL`, `BACKFILL`, `SYNTHETIC`, `FIXTURE`, `REPLAY`, `MANUALLY_EDITED`;
- contradictory records fail and are not repaired;
- no price, volume, score, or signal field;
- no dependency beyond the standard library and test runner;
- `python -m compileall` plus import gates on the exact commit.

### Python / runtime — UNIT-ONLY DEFAULT CONFIRMED

This environment provides **Python 3.12.3**. Standard-library modules required by the proposal (`dataclasses`, `json`, `hashlib`, `datetime`) import.

Python remains an operational default for Build Unit 1 only. Authorization of the unit would accept that default unless Todd states otherwise.

### New dependencies — NONE

No third-party package is present or required for the proposed unit.

### Legacy reuse — NONE

No legacy path is proposed for copy or import. V1/V2 remain evidence only.

### Market data — NONE

No API, download, or historical extract is in scope. A later stock-data purchase belongs to a separately authorized Phase 5 / Horizon 2 unit, after one locked question.

### Rollback — CLEAN

There is no database, no artifact store, and no external side effect. Rollback of a future Unit 1 commit is source-control reversion to `cc2af9a` (or the then-current pre-unit `main`).

### Authorization readiness — STILL VALID

The August 7 authorization-readiness review remains PASS for boundedness, reversibility, test plan, legacy boundary, data boundary, and stop conditions.

Ready for authorization is not authorization.

---

## 4. What this review does not do

This review does not:

- authorize Build Unit 1;
- start implementation;
- admit World Almanac, weather, or any other later evidence-family lesson into this unit;
- authorize Phase 5 or a data API;
- authorize paper trading;
- authorize Product B or autonomous trading;
- rewrite the methodology.

Those later lessons remain useful for a future bounded data-research unit. They are not Build Unit 1.

---

## 5. Disposition

```text
RADAR V4 REACTIVATION REVIEW — PASS
BUILD UNIT 1 READINESS — STILL VALID
SCOPE — UNCHANGED / NON-MARKET
TEST PLAN — UNCHANGED
CONTROLLING COMMIT — cc2af9a
CODE — NONE
EXECUTION AUTHORITY — NONE
```

The repository is again at the decision that was intentionally left for Todd:

```text
AUTHORIZE BUILD UNIT 1 — TC
```

or `REVISE BUILD UNIT 1 — TC`, `PAUSE BUILD UNIT 1 — TC`, or `REJECT BUILD UNIT 1 — TC`.

No action follows automatically from this review.

---

## Closing principle

> Confirm the container is still the container. Then Todd decides. Do not start the market story to warm up the tools.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.
