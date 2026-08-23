# Radar V4 — Legacy V1 and V2 Review Roadmap

## Status

**APPROVED FOR PLANNING — REVIEW NOT YET STARTED**

This roadmap defines how `legacy-radar-v1` and `legacy-radar-v2` will be examined before any legacy component is considered for Radar V4.

The review is evidence-first. It does not authorize code copying, migration, backtesting, live data, trading, execution, or production deployment.

Todd retains final authority over scope, evidence acceptance, reuse decisions, curriculum direction, and Radar V4 activation.

## Purpose

The purpose of the review is to determine:

1. what V1 and V2 were intended to do;
2. what they actually did;
3. why each system failed, stalled, or produced weak confidence;
4. what improved from V1 to V2;
5. what problems repeated across both systems;
6. which ideas remain valuable;
7. which implementations are technically salvageable;
8. which components should be rebuilt from requirements rather than copied;
9. which components should be permanently rejected and preserved only as evidence;
10. what Radar V4 must require before implementation.

## Review principles

1. Evidence before salvage.
2. Intent and operation must be compared separately.
3. V1 and V2 must be reviewed independently before comparison.
4. A working component is not automatically a trustworthy component.
5. A useful idea does not require reuse of old code.
6. Exact repository, path, commit, dependencies, and tests are required for reuse consideration.
7. Missing logs or evidence must be recorded honestly.
8. No claim of edge, signal quality, or predictive value may be inferred from architecture alone.
9. Learning findings must shape the future curriculum.
10. No drift.

# Stage 0 — Evidence preservation and access plan

Objective:

Identify the evidence available without changing the legacy systems.

Required inventory:

- repository branches;
- tags and commit history;
- README and architecture claims;
- source directories;
- configuration files;
- dependency files;
- database schemas and migrations;
- test suites;
- logs and error traces;
- backtest outputs;
- deployment records;
- screenshots and exports;
- old planning notes supplied by Todd.

Deliverable:

- `postmortem/LEGACY_EVIDENCE_INDEX.md`

Exit criteria:

- available evidence is identified;
- missing evidence is listed;
- no legacy file has been modified;
- read-only review method is documented.

# Stage 1 — V1 independent review

Objective:

Reconstruct V1 before interpreting it through V2.

Questions:

- What was V1's primary purpose?
- What user decision was it intended to support?
- What data entered the system?
- How was data transformed?
- What outputs were produced?
- What did the system call a score, ranking, signal, alert, or opportunity?
- What tests existed?
- What logs show successful and failed behavior?
- What assumptions were undocumented?
- Which components were simple and reliable?
- Which components were incomplete, brittle, or misleading?

Deliverables:

- `postmortem/V1_INTENT_VS_OPERATION.md`
- `postmortem/V1_COMPONENT_MAP.md`
- `postmortem/V1_DATA_AND_PROVENANCE_MAP.md`
- `postmortem/V1_FAILURE_REGISTER.md`
- `postmortem/V1_CANDIDATE_COMPONENTS.md`

# Stage 2 — V2 independent review

Objective:

Reconstruct V2 without assuming it solved V1.

Questions:

- What V1 problems was V2 intended to fix?
- Which new components were added?
- Which old assumptions were retained?
- Did complexity increase faster than verification?
- Were data quality, provenance, validation, and observability improved?
- Did V2 introduce new failure modes?
- Which components worked more reliably than V1?
- Which claims exceeded the evidence?

Deliverables:

- `postmortem/V2_INTENT_VS_OPERATION.md`
- `postmortem/V2_COMPONENT_MAP.md`
- `postmortem/V2_DATA_AND_PROVENANCE_MAP.md`
- `postmortem/V2_FAILURE_REGISTER.md`
- `postmortem/V2_CANDIDATE_COMPONENTS.md`

# Stage 3 — V1-to-V2 comparison

Objective:

Separate true improvement from added complexity.

Comparison categories:

- product purpose;
- data architecture;
- provenance;
- feature generation;
- labels and targets;
- scoring and ranking;
- ML use;
- backtesting;
- validation;
- observability;
- security;
- deployment;
- governance;
- human review.

Deliverables:

- `postmortem/V1_TO_V2_CHANGE_MAP.md`
- `postmortem/REPEATED_FAILURES.md`
- `postmortem/IMPROVEMENTS_THAT_WORKED.md`
- `postmortem/COMPLEXITY_WITHOUT_EVIDENCE.md`

# Stage 4 — Root-cause analysis

Objective:

Identify causes rather than merely list symptoms.

Failure categories:

1. Product-definition
2. Data and provenance
3. ML and statistics
4. Backtest and simulation
5. Software systems
6. Architecture
7. Observability
8. Security and deployment
9. Governance
10. Scope and human process

Deliverables:

- `postmortem/FAILURE_TAXONOMY.md`
- `postmortem/ROOT_CAUSE_REGISTER.md`
- `postmortem/CLAIMS_VS_OPERATION.md`

Every finding must cite direct evidence and include a confidence level.

# Stage 5 — Reuse, rebuild, reject

Objective:

Classify every candidate idea or component.

## Reuse

Allowed only when the component is:

- narrowly defined;
- technically sound;
- independently testable;
- supported by evidence;
- free of unacceptable security risk;
- maintainable;
- easier to reuse than rebuild;
- approved by Todd.

## Rebuild

Used when the requirement or idea is valuable but the old implementation is too coupled, brittle, undocumented, insecure, or untested.

Radar V4 receives the requirement, not the old code.

## Reject and preserve

Used when a component is unsupported, misleading, unsafe, unmaintainable, unnecessary, or incompatible with Radar V4 principles.

Deliverables:

- `postmortem/REUSE_REBUILD_REJECT.md`
- `postmortem/SALVAGE_CANDIDATE_REGISTER.md`
- `postmortem/REJECT_AND_PRESERVE_REGISTER.md`

# Stage 6 — Radar V4 requirements

Objective:

Translate verified lessons into requirements.

Required areas:

- purpose and human decision;
- canonical records;
- provenance;
- labels and target definitions;
- ranking definitions;
- uncertainty;
- temporal validation;
- backtest realism;
- baselines;
- observability;
- failure handling;
- security;
- rollback;
- human authority;
- stop rules.

Deliverables:

- `postmortem/LESSONS_FOR_RADAR_V4.md`
- `postmortem/RADAR_V4_REQUIREMENTS.md`
- `postmortem/RADAR_V4_REPLACEMENT_ROADMAP.md`

# Stage 7 — Targeted 3,000-unit learning corpus

Objective:

Build a Radar V4 educational corpus that directly repairs weaknesses found in V1 and V2.

The corpus will cover:

- machine learning;
- probability and statistics;
- MIT-style mathematics;
- time series;
- optimization;
- market structure;
- risk;
- validation;
- software systems;
- governance and failure control.

The corpus is not a signal library, strategy library, or proof of edge.

Deliverables:

- `learning/RADAR_V4_3000_UNIT_CURRICULUM.md`
- unit index and category map;
- concept prerequisites;
- failure-mode links;
- Radar V4 relevance statement for each unit;
- review and verification status.

# Stage 8 — Decision gate

Todd reviews:

- verified failures;
- root causes;
- salvage candidates;
- rebuild requirements;
- rejected components;
- curriculum plan;
- replacement roadmap.

Possible decisions:

- proceed with curriculum only;
- proceed with a bounded offline design phase;
- request more evidence;
- preserve findings and stop;
- reject Radar V4 activation.

## Current authorization

Authorized:

- roadmap creation;
- postmortem planning;
- Claude handoff preparation;
- curriculum architecture planning.

Not yet authorized:

- legacy code copying;
- modification of V1 or V2;
- runtime execution;
- live data;
- backtesting;
- signal design;
- trading or execution;
- Radar V4 implementation.

## Main principle

> Use V1 and V2 to discover requirements before deciding what Radar V4 should inherit.

Learning and Earning It.  
Stay on course.  
No drift.
