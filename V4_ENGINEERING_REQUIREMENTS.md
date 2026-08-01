# Radar V4 Engineering Requirements

**Status:** Foundation documentation  
**Scope:** Engineering requirements only  
**Implementation authorized:** No  
**Methodology defined:** No

---

## 1. Purpose

This document defines the minimum engineering qualities Radar V4 must satisfy if implementation is later authorized.

It does not define:

- a trading method;
- a feature set;
- a score;
- a threshold;
- a market-data vendor;
- a dashboard;
- a broker connection;
- an autonomous trader.

The requirements below are derived from verified V1/V2 failures and strengths.

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

## 3. Language posture

### Initial language

Python is the default initial language because Radar V4’s first engineering needs are:

- inspectability;
- testability;
- reproducibility;
- data analysis;
- historical replay;
- clear failure diagnosis.

### Restrictions

- No C++ or Rust component may be introduced without a measured requirement.
- No multi-language architecture may be introduced for prestige or theoretical speed.
- A new language requires a written bottleneck or reliability case, measured evidence, and explicit approval.

### Stop condition

A proposed language addition is rejected when the same requirement can be met clearly and safely in the existing language without a demonstrated performance or safety deficit.

---

## 4. Repository and change discipline

Any future codebase must include:

- protected primary branch;
- reviewable commits;
- clear commit messages;
- no direct secret storage;
- no unexplained generated files;
- no unreviewed binary artifacts;
- versioned configuration;
- release notes tied to actual changes.

Every change must be traceable to one of:

- a verified requirement;
- a documented defect;
- an approved experiment;
- an approved operational need.

No change may be justified only by “making the system smarter,” “adding capability,” or “improving confidence.”

---

## 5. Entry-point integrity

Every executable entrypoint must:

- parse;
- import;
- declare its configuration requirements;
- fail clearly when dependencies are missing;
- expose a smoke test;
- identify its version at runtime.

A repository is not considered runnable merely because individual modules parse in isolation.

---

## 6. Configuration discipline

Configuration must be separated from code.

Every configuration value must identify:

- name;
- type;
- default behavior;
- allowed range where applicable;
- whether it is operational or methodological;
- source of authority;
- whether changing it requires evidence.

Methodological values must not be hidden inside ordinary operational configuration.

Examples:

- API timeout: operational configuration.
- Data interval: architectural configuration with cadence implications.
- Score threshold: methodological configuration requiring evidence.

---

## 7. Shared data-access layer

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

---

## 8. Data provenance and integrity

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

Invalid data must be quarantined rather than silently repaired and accepted.

Any repair or transformation must produce a new versioned artifact rather than overwriting the original evidence.

---

## 9. Cadence enforcement

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
- a daily context value is being used as an intraday decision input without approval;
- price freshness and feature freshness materially diverge.

---

## 10. Determinism and reproducibility

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

## 11. Persistence and recovery

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
- corrupted record handling.

Storage technology must remain proportional to scale. A larger database is not automatically a better database.

---

## 12. Structured logging

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

Logs must never contain:

- API keys;
- passwords;
- tokens;
- broker credentials;
- private certificates;
- unrestricted personal data.

---

## 13. Honest health states

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

The overall state must therefore support at least:

- `HEALTHY`;
- `DEGRADED`;
- `BLOCKED`;
- `FAILED`;
- `NOT EVALUATED`.

No overall `HEALTHY` state may be emitted when any load-bearing input is stale, missing, invalid, or provenance-unknown.

---

## 14. Failure behavior

Radar V4 must fail visibly and conservatively.

When a critical dependency fails, the default response is:

1. stop the affected output;
2. record the reason;
3. preserve the available evidence;
4. avoid substituting stale or lower-quality data without disclosure;
5. require human review when the failure changes decision meaning.

The system must not invent continuity by silently changing vendors, intervals, symbols, or assumptions.

---

## 15. Test architecture

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

---

## 16. Security baseline

Before any external data or unattended operation, the system must include:

- secrets outside source control;
- least-privilege credentials;
- separate development and operational credentials;
- credential rotation plan;
- dependency review;
- audit logging for configuration changes;
- no broker credentials in Radar V4.

Radar V4 is not authorized to hold execution authority.

---

## 17. Dependency discipline

Every dependency must have:

- a stated purpose;
- version control or lock file;
- license review where relevant;
- maintenance status review;
- security review proportional to risk;
- removal path.

No dependency may be added solely because it is popular or convenient.

Prefer the standard library and small, well-understood dependencies where practical.

---

## 18. Documentation required before implementation

Before any future code is authorized, the following must exist and agree:

1. `RADAR_V1_V2_FINAL_FINDINGS.md`
2. `V4_CONTROL_REQUIREMENTS.md`
3. `V4_ENGINEERING_REQUIREMENTS.md`
4. a bounded statement of purpose;
5. an explicit non-goals list;
6. an approved first engineering unit;
7. a stop condition for that unit.

This list does not authorize the first engineering unit. It defines readiness documentation only.

---

## 19. Non-goals

Radar V4 engineering must not initially optimize for:

- ultra-low latency;
- high-frequency trading;
- autonomous execution;
- distributed systems;
- multi-cloud deployment;
- unlimited provider abstraction;
- advanced user interfaces;
- broad asset-class coverage;
- maximum feature count;
- model complexity.

The initial optimization target is correctness, traceability, reproducibility, and honest failure behavior.

---

## 20. Future relationship to Chatawa Labs AI Trader

Radar V4 must remain an independent, human-controlled intelligence system.

A future Chatawa Labs AI Trader may be created only from a frozen, approved V4 release and must exist in a separate repository with separate governance.

Radar V4 must not contain:

- broker adapters;
- order placement;
- portfolio authority;
- autonomous capital allocation;
- execution credentials.

The future trader may inherit only components that have independently earned approval.

---

## 21. Current disposition

```text
Legacy postmortem: CLOSED
V4 control requirements: DOCUMENTED
V4 engineering requirements: DOCUMENTED
V4 purpose refinement: NEXT ELIGIBLE DOCUMENTATION UNIT
V4 methodology: NOT DEFINED
V4 implementation: NOT AUTHORIZED
V4 code: NOT STARTED
V4 data ingestion: NOT STARTED
Chatawa Labs AI Trader: FUTURE, SEPARATE, NOT STARTED
```

---

## Closing principle

> Radar V4 must be engineered so that failure is visible, evidence is traceable, and software success can never be mistaken for methodological success.

Learning and Earning It.  
Stay on course.  
No drift.
