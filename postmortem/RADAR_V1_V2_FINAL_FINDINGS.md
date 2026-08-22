# Radar V1 / V2 Final Findings

**Review type:** Bounded forensic readiness review (read-only)  
**Reviewer:** Claude, external auditor role  
**Repositories reviewed:** `legacy-radar-v1-main`, `legacy-radar-v2-main`  
**Status:** CLOSED  
**Subsequent V4 program status:** See `README.md` — PRE-BUILD / BUILD UNIT 1 AWAITING TODD AUTHORIZATION

The forensic disposition `V4 — PARKED` below is the postmortem conclusion at close of review. Later separately recorded methodology and Build Unit 1 planning work advanced the program to pre-build. This file does not authorize implementation.

---

## 1. Scope and evidence reviewed

- Full uploaded source snapshots for V1 and V2.
- V2 changelog through V25.7.
- V2 test suite, executed directly: **89/89 tests passed**.
- V2 frozen baseline artifacts and outcome files.
- All Python files in both repositories, syntax-checked directly.

### Evidence gaps

- No `.git` history in either export.
- No independently verifiable commit sequence, authorship, or release timing.
- No backtest module or backtest artifacts in either repository.
- No corroborating live runtime logs.

---

## 2. Verified V1 findings

### Confirmed

- `engine/run_radar.py` fails to parse with an `IndentationError`.
- The primary entrypoint imports `features.relative_strength`, which is absent.
- `dashboard/app.py` imports five additional missing modules, including an absent `logger/` package.
- Supporting modules parse individually, but integration points are broken.
- V1 contains only two smoke-level test files.
- No logs, backtest output, or run history were found.

### Strong inference

The number of missing modules across both entrypoints suggests the export represents a structurally incomplete state, not a single typo-level regression.

### Unresolved

Whether V1 ever had a fully runnable earlier state cannot be established without repository history.

---

## 3. Verified V2 findings

### Confirmed

- All Python files parse cleanly.
- **89/89 tests pass** when dependencies are installed.
- V2 added genuine engineering controls absent from V1, including:
  - structured JSON logging;
  - HEALTHY / DEGRADED states;
  - SQLite persistence with WAL mode;
  - atomic transaction fixes;
  - scheduled execution and restart support;
  - integration and regression tests.
- V25.2 documents an atomicity fix.
- V25.3 documents an honest-health-state fix.
- No backtesting module or backtest artifact exists anywhere in V2.

### Strong inference

V2 is materially stronger software than V1, but stronger software does not establish stronger trading methodology.

### Unresolved

The changelog cannot be independently reconciled against actual commit history from the uploaded snapshot.

---

## 4. Confirmed flat-score root cause

### Confirmed

- V1 and V2 core feature pipelines request daily bars.
- V2 regime computation also uses daily bars.
- Polygon integration also requests one-day bars for the scoring path.
- V2 later introduced fresher last-price lookup for outcome and execution handling, but this did not change the daily feature or regime pipeline.
- No resampling or true intraday feature-refresh mechanism was found.

### Root cause

> The system operated at intraday scan cadence while its load-bearing feature and regime inputs remained daily-resolution.

This caused repeated scans to reuse the same or nearly identical inputs, producing flat scores during the session.

### Important limit

Intraday data would likely improve responsiveness. It would not, by itself, prove usefulness, predictive value, or edge.

---

## 5. Test-suite findings and limits

### Confirmed

The 89 passing V2 tests primarily cover:

- software behavior;
- integration;
- deterministic replay;
- data handling;
- operational resilience.

They do **not** cover:

- statistical validity;
- market correctness;
- out-of-sample performance;
- leakage or look-ahead bias;
- threshold sensitivity;
- calibration;
- profitability after costs.

### Governing conclusion

> V2’s tests prove the software does what the code says. They do not prove that what the code says is right.

---

## 6. Hardcoded-threshold finding

More than 30 hardcoded numeric thresholds and multipliers were found across decision, signal-quality, momentum, regime, confidence, risk/reward, and decay logic.

No backtest reference, derivation record, sensitivity study, or partial evidence was found for those values.

**Disposition:** `UNEVIDENCED`

---

## 7. Outcome-data provenance finding

### Confirmed

- `outcome_history.csv` contains 250 rows resolving at an exact one-minute cadence.
- The relevant module states the current application does not use that CSV path and warns against synthetic seeding.
- The observed cadence conflicts with the tracker’s stated 15-minute minimum-resolution-age rule.

### Strong inference

The file is likely generated, fixture-like, or archival sample data rather than reliable live trading-performance evidence.

### Unresolved

The exact code path that produced the file was not found.

---

## 8. Dispositions

| Component | Disposition |
|---|---|
| V1 codebase | REJECT AND PRESERVE |
| V1 data and feature pipeline | REJECT AND PRESERVE |
| V2 SQLite persistence pattern | REUSE CANDIDATE, pending explicit authorization |
| V2 structured logging pattern | REUSE CANDIDATE, pending explicit authorization |
| V2 health monitoring pattern | REUSE CANDIDATE, pending explicit authorization |
| V2 price client | CONDITIONAL REUSE CANDIDATE for price lookup only |
| V2 frozen replay practice | PRESERVE AS A PATTERN, not as proof of market validity |
| V2 feature and regime pipeline | REJECT AND PRESERVE |
| V2 scoring, confidence, and decision engines | REJECT AND PRESERVE |
| Outcome tracking design | REBUILD FROM REQUIREMENT |
| Outcome-history data | NOT TRUSTWORTHY AS PERFORMANCE EVIDENCE |
| Scheduler and deployment scripts | REBUILD FROM REQUIREMENT |
| News and alerting | INSUFFICIENT EVIDENCE |

No component is authorized for reuse without Todd’s explicit, component-level approval.

---

## 9. Requirements earned for any future Radar V4

1. Decision cadence must not outrun feature or data cadence.
2. No threshold may ship without a documented, evidenced derivation.
3. Historical validation against a declared baseline must precede promotion.
4. Every dataset must self-declare provenance.
5. Software correctness, data correctness, method validity, and market usefulness must be reported separately.
6. Fresh prices may not conceal stale features.
7. Entry points must pass automated syntax and import gates.
8. Structured logging, honest health states, atomic persistence, and deterministic replay should be preserved as engineering requirements.
9. Stop rules and kill criteria must exist before shadow operation.
10. `NO EDGE SHOWN` must remain an acceptable final outcome.

---

## 10. Final disposition

```text
V1 — REJECT AND PRESERVE
V2 — PRESERVE ENGINEERING LESSONS; DO NOT INHERIT TRADING METHODOLOGY
V4 — PARKED
Sebastian — NOT DISPLACED
```

---

## 11. Boundaries

This record does not authorize:

- Radar V4 implementation;
- code migration;
- data ingestion;
- backtesting;
- feature or scoring design;
- live operation;
- broker connectivity;
- autonomous trading.

---

## Closing statement

> This postmortem earned verified findings, a confirmed root cause, and a short list of requirements and preserved engineering lessons. It did not earn a new build.
