# Radar V4 Engineering Requirements

**Scope:** Evidence-backed engineering requirements only  
**Implementation authorized:** Phase 5 local workshop only; vendor, Phase 6, and paper trading remain unauthorized  
**Methodology defined:** Research methodology documented; no market method defined

---

## 1. Purpose

This document defines only the minimum engineering qualities directly supported by the verified V1/V2 forensic findings.

It does not define:

- a trading method;
- a feature set;
- a score;
- a threshold;
- a market-data vendor;
- a dashboard;
- a broker connection;
- an autonomous trader;
- a future derivative system.

Reasonable defaults that were not directly established by the postmortem are identified separately and are not treated as forensic requirements.

---

## 2. Core engineering objective

Radar V4 must be able to answer, at any moment:

1. Did the process run?
2. Did valid data arrive?
3. Was the data fresh enough for the claimed use?
4. Did the feature layer use the correct cadence?
5. Did the method execute deterministically?
6. Was the output stored safely?
7. Can the result be reproduced later?
8. Can a human identify why the system stopped or degraded?

A single generic `SUCCESS` or `HEALTHY` state is not sufficient.

---

## 3. Operational defaults not derived from the postmortem

The following may be sensible future defaults, but they are not presented as findings earned from V1/V2:

- Python may be used as the initial implementation language because both legacy systems were Python and the ecosystem supports inspectable research and testing.
- General security hygiene and dependency review remain necessary engineering practice.
- Conservative failure behavior is a reasonable design preference.

These points require separate operational approval if implementation is ever authorized. They do not carry the same evidentiary status as the requirements below.

---

## 4. Entry-point integrity

**Evidence basis:** V1 contained a primary entrypoint that failed to parse and multiple unresolved imports across both entrypoints.

Every executable entrypoint must:

- parse;
- import;
- declare its configuration requirements;
- fail clearly when dependencies are missing;
- expose a smoke test;
- identify its version at runtime.

A repository is not considered runnable merely because individual modules parse in isolation.

**Stop condition:** Any syntax error, unresolved import, or non-loading entrypoint blocks promotion.

---

## 5. Configuration discipline

**Evidence basis:** V2 embedded unevidenced methodological thresholds directly in code.

Configuration must be separated from code, and each value must identify whether it is:

- operational;
- architectural;
- methodological.

Methodological values must not be hidden inside ordinary operational configuration.

Examples:

- API timeout: operational configuration.
- Data interval: architectural configuration with cadence implications.
- Score threshold: methodological configuration requiring evidence.

**Stop condition:** An unexplained methodological value may not be introduced through ordinary configuration.

---

## 6. Shared data-access layer

**Evidence basis:** V2 used inconsistent vendors and fallback behavior across adjacent pipelines, and the later shared price client fixed only part of that problem.

All market-data retrieval must pass through a shared access layer.

The access layer must record:

- provider;
- endpoint or data type;
- requested interval;
- actual interval returned;
- market timestamp;
- retrieval timestamp;
- timezone;
- adjustment status;
- fallback used;
- freshness state;
- request outcome.

No feature, regime, outcome, or reporting module may independently implement hidden vendor logic.

Fallback must be visible. A fallback response may not silently masquerade as primary-source data.

**Stop condition:** A new pipeline may not introduce independent vendor or fallback logic outside the shared layer.

---

## 7. Data provenance and integrity

**Evidence basis:** V2 contained an outcome file whose live, synthetic, fixture, or replay status could not be established and whose timing conflicted with the system’s own rule.

Every stored dataset must carry provenance sufficient to distinguish:

- live;
- historical;
- backfilled;
- synthetic;
- fixture;
- replay;
- manually edited.

Data must be validated for:

- schema;
- interval;
- timestamp order;
- duplicates;
- missing records;
- stale records;
- inconsistent symbols;
- impossible timing;
- provenance completeness.

Invalid data must be quarantined rather than silently accepted.

Any repair or transformation must produce a new versioned artifact rather than overwrite the original evidence.

**Stop condition:** Provenance-unknown or internally contradictory data may not enter research, reporting, or validation.

---

## 8. Cadence enforcement

**Evidence basis:** V1 and V2 operated at intraday scan cadence while core feature and regime inputs remained daily-resolution.

The system must distinguish:

- source-data cadence;
- feature-update cadence;
- method-evaluation cadence;
- output-publication cadence;
- outcome-resolution cadence.

These may differ, but the difference must be deliberate and documented.

The system must block or degrade output when:

- feature age exceeds its declared limit;
- source interval is coarser than the approved use;
- a daily context value is used as an intraday decision input without approval;
- price freshness and feature freshness materially diverge.

**Stop condition:** Decision cadence may not outrun the cadence of load-bearing data or features.

---

## 9. Determinism and reproducibility

**Evidence basis:** V2’s frozen replay test provided real regression value, while also demonstrating that determinism is not market validity.

Given the same:

- code version;
- configuration;
- input dataset;
- feature version;
- method version;

Radar V4 must produce the same output unless nondeterminism is explicitly declared and controlled.

Every replayable output must identify:

- code version;
- input checksum;
- configuration version;
- method version;
- runtime environment;
- output checksum.

A regression replay confirms consistency. It does not confirm market validity.

---

## 10. Persistence and recovery

**Evidence basis:** V2’s V25.2 atomicity fix addressed the risk of partially applied database operations.

Persistence must be atomic for every logical operation.

The system must prevent:

- partial writes;
- half-applied updates;
- silent corruption;
- duplicate replay results;
- untraceable manual edits.

Minimum future tests must include:

- interrupted write;
- crash during transaction;
- restart after failure;
- duplicate request;
- replay of already processed input;
- corrupted-record handling.

Storage technology must remain proportional to scale.

---

## 11. Structured logging

**Evidence basis:** V2’s structured logging made operational state and failures more visible than V1.

Logs must be machine-readable and human-readable.

Every material event should include:

- timestamp;
- severity;
- component;
- event type;
- run ID;
- method version where applicable;
- symbol or universe where applicable;
- data source;
- status;
- reason;
- error details without secrets.

---

## 12. Honest health states

**Evidence basis:** V2’s V25.3 fix distinguished a process running from a scan actually succeeding.

Health must be component-specific.

At minimum, a future running system must separately report:

- process health;
- provider health;
- data-arrival health;
- data-freshness health;
- feature-computation health;
- cadence-alignment health;
- method-execution health;
- persistence health;
- output-validity health.

A process may be operational while the output is invalid.

The overall state must support at least:

- `HEALTHY`;
- `DEGRADED`;
- `BLOCKED`;
- `FAILED`;
- `NOT EVALUATED`.

No overall `HEALTHY` state may be emitted when a load-bearing input is stale, missing, invalid, or provenance-unknown.

---

## 13. Failure behavior

**Evidence basis:** Legacy failures remained hidden or appeared healthy because failure states were not consistently surfaced across pipelines.

When a critical dependency fails, the system must:

1. stop or block the affected output;
2. record the reason;
3. preserve available evidence;
4. disclose any fallback or degraded input;
5. require human review when the failure changes decision meaning.

The system must not silently change vendors, intervals, symbols, or assumptions to preserve the appearance of continuity.

---

## 14. Test architecture

**Evidence basis:** V2’s 89 passing tests established software correctness and regression discipline, but zero tests established statistical validity or market correctness.

Tests must be labeled by category:

### Software correctness

- syntax;
- imports;
- unit behavior;
- integration;
- persistence;
- recovery;
- deterministic replay.

### Data correctness

- provenance;
- schema;
- interval;
- freshness;
- timestamp alignment;
- fallback consistency;
- missing and duplicate data.

### Method validity

Reserved for future authorized methodology work. Passing software and data tests cannot substitute for this category.

### Operational resilience

- provider failure;
- restart;
- timeout;
- partial outage;
- stale-data blocking;
- degraded-state reporting.

Every status report must show results by category.

**Stop condition:** No report may state only that “all tests passed” without identifying which categories were covered.

---

## 15. Evidence-backed non-goals

Radar V4 must not initially optimize for capabilities that do not address any verified V1/V2 failure, including:

- ultra-low latency;
- high-frequency trading;
- distributed systems;
- multi-cloud deployment;
- unlimited provider abstraction;
- advanced user interfaces;
- maximum feature count;
- maximum model complexity.

The evidence-backed optimization targets are:

- correctness;
- traceability;
- reproducibility;
- cadence alignment;
- visible failure;
- accurate test claims.

---

## 16. Current disposition

```text
Legacy postmortem: CLOSED
V4 control requirements: DOCUMENTED
V4 engineering requirements: ACCEPTED WITH REDUCTION
V4 research methodology: DEFINED / AUDITED
SPECIFIC MARKET METHOD: NOT DEFINED
PHASE 5 LOCAL WORKSHOP: STACKED DRAFT UNITS 7–850 COMPLETE WITHIN SCOPE; MAIN THROUGH 200
VENDOR / HISTORICAL ACCESS: NOT AUTHORIZED
Sebastian methodological gate: STILL BINDS
```

No vendor, Phase 6, or paper-trading document is authorized at this time.

---

## Closing principle

> Radar V4 must be engineered so that failure is visible, evidence is traceable, and software success can never be mistaken for methodological success.

Learning and Earning It.  
Stay on course.  
No drift.
