# Chatawa Radar V4 Governance

## Status

**PARKED — FOUNDATION DOCUMENTATION ONLY**

This document defines the future governance of Radar V4 without activating implementation.

Todd retains final authority over activation, scope, architecture, data use, testing, pilot approval, deployment, shutdown, and any future operational role.

## Purpose

Radar V4 may eventually become a human-controlled intelligence and opportunity-ranking system that:

- organizes verified evidence;
- compares expectations with observed outcomes;
- preserves provenance and uncertainty;
- ranks items for human review;
- separates evidence from interpretation;
- remains advisory rather than autonomous.

## Prohibited interpretations

The existence of this repository, roadmap, or governance document does not mean:

- the program is active;
- code is authorized;
- legacy Radar code is approved for reuse;
- a signal exists;
- an edge has been established;
- live data is authorized;
- trading or execution is allowed;
- a dashboard is justified;
- production status has been earned.

## Authority model

### Todd

Todd alone controls:

- activation;
- phase advancement;
- pilot authorization;
- data-source approval;
- legacy component review;
- implementation approval;
- deployment approval;
- any future market-facing or operational use;
- acceptance or rejection of findings.

### Tools and assistants

Tools and assistants may:

- inspect repositories after explicit authorization;
- inventory files and components;
- draft documentation;
- identify unsupported claims;
- propose bounded methods;
- verify evidence;
- summarize findings.

Tools and assistants may not independently:

- activate Radar V4;
- create ranking logic;
- connect live data;
- migrate legacy code;
- declare a signal or edge;
- authorize a backtest;
- connect to a broker;
- make portfolio decisions;
- override Todd.

## Current authorized scope

Authorized now:

1. README maintenance.
2. Roadmap maintenance.
3. Governance documentation.
4. Postmortem planning.
5. Future evidence requirements.
6. High-level legacy inventory planning.

Not authorized now:

1. Runtime code.
2. Schemas.
3. Live data.
4. Backtests.
5. Ranking algorithms.
6. Signals or edge claims.
7. Brokerage integration.
8. Trading or execution.
9. Portfolio authority.
10. Copying code from legacy repositories.

## Evidence rules

1. Source evidence must remain distinguishable from interpretation.
2. Every claim must retain source, time, and confidence information.
3. Missing and conflicting evidence must remain visible.
4. Historical outcomes may not be rewritten to fit a narrative.
5. A ranking is not valid until its decision purpose is defined.
6. A score is not evidence of predictive value.
7. A backtest is not authorization for live use.
8. One successful example does not establish a pattern.
9. No causal claim may be made from correlation alone.
10. No label outruns operation.

## Controlled legacy-review rules

The repositories `legacy-radar-v1` and `legacy-radar-v2` are historical evidence sources.

They may be reviewed to determine:

- original intent;
- actual operation;
- changes from V1 to V2;
- repeated failures;
- improvements that worked;
- components that may deserve reuse, rebuild, or rejection.

The review must remain read-only unless Todd separately authorizes otherwise.

No legacy component may be considered for reuse until the record includes:

- exact repository;
- exact path;
- exact commit;
- component purpose;
- observed behavior;
- dependencies;
- data assumptions;
- security concerns;
- test coverage;
- known defects;
- maintenance burden;
- reason to reuse instead of rebuild;
- rollback method;
- Todd authorization.

No file may be copied merely because it already exists.

## Reuse, rebuild, reject framework

### Reuse

Allowed only when the component is narrowly defined, technically sound, independently testable, maintainable, and safer to reuse than rebuild.

### Rebuild

Used when the underlying idea remains valid but the legacy implementation is too coupled, brittle, undocumented, insecure, or untested.

### Reject and preserve

Used when the component should remain only as historical evidence and should not enter Radar V4.

A component may not be placed into one of these categories before evidence review.

## Ranking-method rules

Before any future ranking method is built, documentation must define:

- what is being ranked;
- who uses the ranking;
- what decision it supports;
- what evidence is required;
- what time horizon applies;
- how uncertainty is represented;
- how missing data is handled;
- how contradictions are handled;
- exclusion rules;
- false-positive review;
- stop conditions.

A ranking method may not silently become a trading signal.

## Pilot rules

Any future pilot must be:

- offline;
- bounded;
- based on a fixed dataset;
- based on preregistered rules;
- human-reviewed;
- non-executing;
- reversible;
- stopped at a predefined endpoint.

No code changes may occur during the test window unless the test is restarted and the change is documented.

## Interface rules

No dashboard or review interface should be built before the underlying method is defined and tested.

Any future interface must show:

- underlying evidence;
- provenance;
- freshness;
- uncertainty;
- missing data;
- counterevidence;
- ranking reason;
- human disposition.

The interface may not hide limitations to create confidence.

## Security and access rules

- No secrets may be committed.
- No production credentials may be reused from legacy repositories.
- Read-only access is preferred during evidence review.
- Least privilege is required.
- No broker credentials are permitted.
- Any exposed credential must be revoked.

## Stop rules

Work must stop when:

- scope exceeds foundation documentation;
- a request implies live data, code, schema, backtest, or ranking logic;
- evidence is insufficient;
- legacy reuse is being assumed rather than reviewed;
- pressure to continue is based only on momentum;
- a proposed step crosses into trading or execution;
- rollback is not available.

The default response to uncertainty is preserve, document, and review.

## Phase 0 disposition

Phase 0 requirements are satisfied by:

- `README.md` — purpose and current boundary;
- `ROADMAP.md` — phased future plan and authorization limits;
- `GOVERNANCE.md` — authority, evidence rules, prohibited uses, controlled legacy-review rules, pilot rules, and stop conditions;
- `POSTMORTEM_AGENDA.md` — future forensic review sequence.

**Phase 0 result: COMPLETE**

This completion does not activate Phase 1 or authorize code reuse.

## Governing principle

> Use V1 and V2 as evidence first; only verified components may be considered for Radar V4.

Learning and Earning It.  
Stay on course.  
No drift.
