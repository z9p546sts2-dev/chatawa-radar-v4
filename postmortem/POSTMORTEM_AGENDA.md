# Radar V4 — Legacy Forensic Postmortem Agenda

## Status

**ON THE BOOKS — NOT YET STARTED**

This agenda records the approved future review sequence for understanding why the legacy Radar efforts failed, what evidence supports those conclusions, and how the findings should shape Radar V4.

It does not authorize code reuse, implementation, backtesting, live data, trading, execution, or automatic migration.

Todd retains final authority over timing, scope, evidence acceptance, phase advancement, and all future Radar V4 decisions.

## Core question

> What did legacy Radar V1 and legacy Radar V2 claim or intend to do, what did they actually do, why did the gap occur, and what requirements must Radar V4 adopt to avoid repeating those failures?

## Review objective

The review will reconstruct:

1. what V1 was intended to do;
2. what V1 actually did;
3. what V2 changed;
4. what V2 actually did;
5. which V1 failures V2 fixed;
6. which V1 failures V2 repeated;
7. which new failures V2 introduced;
8. which failures were technical, methodological, statistical, architectural, or governance-related;
9. which components should be reused, rebuilt, or permanently rejected;
10. what the Radar V4 roadmap must require before implementation.

## Evidence sources

The review may use:

- `legacy-radar-v1`;
- `legacy-radar-v2`;
- application logs;
- deployment logs;
- error traces;
- backtest outputs;
- configuration files;
- database and schema history;
- commit history;
- branches and abandoned work;
- README and roadmap claims;
- screenshots, exports, and preserved notes;
- prior decision records supplied by Todd.

No conclusion may be presented as verified unless it is tied to direct evidence.

## Division of labor

### Claude lane

Claude may:

- inspect legacy code paths;
- trace execution;
- inspect logs and runtime evidence;
- identify crashes and silent failures;
- compare configuration with actual behavior;
- inventory schemas and dependencies;
- locate unfinished or contradictory components;
- identify security and deployment problems;
- cite exact repositories, paths, commits, and timestamps.

Claude does not authorize reuse or activation.

### Chatawa / ChatGPT lane

This lane will:

- classify findings;
- separate symptoms from root causes;
- compare V1 and V2 directly;
- connect findings to ML, mathematics, validation, systems, and governance principles;
- convert findings into Radar V4 requirements;
- design the targeted learning curriculum;
- draft the replacement roadmap;
- define reuse, rebuild, and reject decisions for Todd's approval.

### Todd

Todd:

- authorizes the review;
- controls scope;
- accepts or rejects findings;
- decides whether any component may move forward;
- approves the replacement roadmap;
- retains final authority.

## Failure taxonomy

Every finding should be assigned to one or more categories:

1. Product-definition failure
2. Data failure
3. ML or statistical failure
4. Backtest or simulation failure
5. Software-system failure
6. Architecture failure
7. Security or deployment failure
8. Observability failure
9. Governance failure
10. Human-process or scope-control failure

## Required finding format

Each finding must include:

```text
Finding ID:
Legacy version: V1 / V2 / both
Observed symptom:
Direct evidence:
Source repository/path:
Commit or log timestamp:
Expected behavior:
Actual behavior:
Root cause:
Failure category:
Confidence:
Impact:
Was this repeated, fixed, or introduced in V2?:
Reuse / rebuild / reject:
Radar V4 requirement created:
Open question:
```

## Planned deliverables

The postmortem package will eventually contain:

```text
postmortem/
  LEGACY_EVIDENCE_INDEX.md
  V1_INTENT_VS_OPERATION.md
  V2_INTENT_VS_OPERATION.md
  V1_TO_V2_CHANGE_MAP.md
  REPEATED_FAILURES.md
  IMPROVEMENTS_THAT_WORKED.md
  FAILURE_TAXONOMY.md
  CLAIMS_VS_OPERATION.md
  ROOT_CAUSE_REGISTER.md
  REUSE_REBUILD_REJECT.md
  LESSONS_FOR_RADAR_V4.md
  RADAR_V4_REQUIREMENTS.md
  TARGETED_LEARNING_CURRICULUM.md
  RADAR_V4_REPLACEMENT_ROADMAP.md
```

## Targeted learning connection

The proposed ML, mathematics, market-structure, risk, systems, and governance question corpus will be designed after the root causes are identified.

The curriculum should repair demonstrated weaknesses rather than become a generic collection of questions.

Examples:

- leakage findings create deeper temporal-validation work;
- unsupported confidence scores create calibration and uncertainty work;
- unrealistic backtests create market-microstructure and simulation-validity work;
- tightly coupled architecture creates systems decomposition and failure-isolation work;
- weak provenance creates data lineage and reproducibility work;
- scope drift creates governance and stop-rule work.

## Sequence

```text
V1 evidence collection
→ V2 evidence collection
→ V1-to-V2 comparison
→ forensic postmortem
→ root-cause register
→ reuse / rebuild / reject decisions
→ Radar V4 requirements
→ targeted ML and math curriculum
→ Radar V4 replacement roadmap
→ bounded offline method
→ implementation only after separate authorization
```

## Boundaries

The postmortem does not authorize:

- copying legacy code;
- modifying legacy repositories;
- running live trading systems;
- creating signals or edge claims;
- brokerage integration;
- production deployment;
- changing historical evidence;
- deciding in advance that a component must be salvaged.

The first question is not, “What can we reuse?”

The first question is:

> What failed, why did it fail, what changed from V1 to V2, and what evidence supports each conclusion?

## Start gate

The agenda is recorded, but execution begins only when Todd explicitly authorizes Phase 1 legacy inspection and identifies the evidence sources available for review.

## Current disposition

- Agenda: RECORDED
- Phase 1 inspection: NOT YET STARTED
- V1 review: PLANNED
- V2 review: PLANNED
- Legacy code reuse: NOT AUTHORIZED
- Learning corpus design: WAITING ON POSTMORTEM FINDINGS
- Radar V4 replacement roadmap: WAITING ON ROOT-CAUSE EVIDENCE

## Governing principle

> Use V1 and V2 as evidence, compare them honestly, and let verified lessons shape Radar V4.

Learning and Earning It.  
Stay on course.  
No drift.
