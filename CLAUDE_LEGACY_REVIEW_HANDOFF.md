# Claude Handoff — Controlled Legacy Radar V1 and V2 Review

## Status

**SUPERSEDED — LEGACY FORENSIC REVIEW COMPLETE**

This handoff is retained as the original review request. The bounded forensic review has been completed and banked in `postmortem/RADAR_V1_V2_FINAL_FINDINGS.md`. Current Radar V4 program status is in `README.md`.

The body below remains the original request text. It does not restart the review and does not authorize implementation.

## Repositories

Review these historical repositories independently:

- `z9p546sts2-dev/legacy-radar-v1`
- `z9p546sts2-dev/legacy-radar-v2`

Use `z9p546sts2-dev/chatawa-radar-v4` only as the destination for approved documentation and future requirements. Do not copy code into Radar V4.

## Core mission

Determine:

1. what V1 and V2 were intended to do;
2. what the code, configuration, logs, and outputs show they actually did;
3. why each system failed, stalled, or did not earn sufficient confidence;
4. which failures repeated across both versions;
5. which changes from V1 to V2 were genuine improvements;
6. which changes only added complexity;
7. which ideas or components may be candidates for reuse;
8. which ideas should be rebuilt from clean requirements;
9. which components should be rejected and preserved only as evidence;
10. what Radar V4 must require to avoid repeating the same failures.

## What we would like to find

### Product and purpose

- the intended user;
- the intended decision;
- the claimed purpose of each system;
- whether the purpose changed over time;
- whether dashboards or interfaces were built before the core method was proven;
- whether “signal,” “ranking,” “opportunity,” “confidence,” and similar labels had operational definitions.

### Data and provenance

- every data source;
- ingestion paths;
- timestamps and time zones;
- raw-versus-transformed data boundaries;
- handling of missing, stale, duplicate, or conflicting records;
- provenance retention;
- whether sources were silently blended;
- evidence of look-ahead, survivorship, selection, or revision bias.

### ML and statistics

- features;
- labels and targets;
- model types;
- training and validation splits;
- temporal validation rules;
- baselines;
- calibration;
- sample sizes;
- metric selection;
- overfitting controls;
- leakage risks;
- claims unsupported by out-of-sample evidence.

### Backtesting and simulation

- test periods;
- frozen dataset identity;
- transaction costs;
- spreads and slippage;
- execution assumptions;
- latency;
- fill logic;
- rule changes during testing;
- reproducibility;
- comparison with simple baselines;
- whether results were selected after viewing outcomes.

### Software and architecture

- service and component map;
- command and scheduler paths;
- database schemas;
- dependencies;
- coupling;
- state management;
- idempotency;
- error handling;
- retry behavior;
- rollback;
- unfinished or unreachable code;
- duplicate responsibilities;
- complexity added without evidence of need.

### Observability and operations

- available logs;
- missing logs;
- silent failures;
- health checks versus actual function;
- deployment history;
- runtime configuration;
- environment drift;
- backup and restore capability;
- security and secret-management problems.

### Governance and human process

- where scope changed without a recorded decision;
- where claims outran evidence;
- where implementation began before tests were written;
- where stop conditions were absent;
- where research, backtest, production, and presentation responsibilities were mixed;
- where momentum appears to have replaced a deliberate gate.

## Required evidence standard

For every important finding, provide:

```text
Finding ID:
Repository:
Path:
Commit or timestamp:
Observed evidence:
Expected behavior:
Actual behavior:
Root-cause hypothesis:
Failure category:
Confidence level:
Impact:
Reuse / rebuild / reject recommendation:
Radar V4 requirement suggested:
Open question:
```

Distinguish clearly between:

- verified fact;
- strong inference;
- tentative hypothesis;
- unknown due to missing evidence.

Do not treat comments, README claims, labels, or filenames as proof of runtime behavior.

## Requested review order

1. Preserve and inventory evidence.
2. Review V1 independently.
3. Review V2 independently.
4. Compare V1 and V2.
5. Identify repeated and newly introduced failures.
6. Produce root-cause findings.
7. Produce reuse / rebuild / reject candidates.
8. Recommend Radar V4 requirements.
9. Identify learning gaps that should shape the 3,000-unit curriculum.

## Requested outputs

Please return findings suitable for these future files:

```text
postmortem/LEGACY_EVIDENCE_INDEX.md
postmortem/V1_INTENT_VS_OPERATION.md
postmortem/V2_INTENT_VS_OPERATION.md
postmortem/V1_TO_V2_CHANGE_MAP.md
postmortem/REPEATED_FAILURES.md
postmortem/IMPROVEMENTS_THAT_WORKED.md
postmortem/COMPLEXITY_WITHOUT_EVIDENCE.md
postmortem/FAILURE_TAXONOMY.md
postmortem/ROOT_CAUSE_REGISTER.md
postmortem/REUSE_REBUILD_REJECT.md
postmortem/RADAR_V4_REQUIREMENTS.md
postmortem/TARGETED_LEARNING_NEEDS.md
```

## Salvage standard

Do not recommend code reuse merely because a component runs.

A reuse candidate should include:

- exact repository;
- exact path;
- exact commit;
- narrow purpose;
- dependencies;
- data assumptions;
- security review;
- test status;
- known defects;
- maintenance burden;
- reason reuse is superior to rebuilding;
- rollback implications.

A useful idea may be marked **rebuild** even when the implementation is rejected.

## Boundaries

Do not:

- modify V1 or V2;
- copy files into Radar V4;
- repair systems during the review;
- run live trading;
- connect brokerage accounts;
- create or promote signals;
- claim edge;
- change historical evidence;
- decide in advance that any component must be saved.

## Relationship to the 3,000-unit learning corpus

The future curriculum will contain ML, trading-system, probability, statistics, MIT-style mathematics, time-series, optimization, market-structure, risk, software-systems, and governance units.

Please identify demonstrated learning gaps such as:

- leakage;
- temporal validation;
- calibration;
- optimization misuse;
- unrealistic backtests;
- weak provenance;
- model-risk misunderstanding;
- architecture coupling;
- observability gaps;
- scope-control failures.

The curriculum should be targeted to verified weaknesses rather than generic volume.

## Final requested summary

At the end, provide a plain-language answer to:

1. Why did V1 fail or stall?
2. Why did V2 fail or stall?
3. What did V2 genuinely improve?
4. What problems repeated?
5. What should never be reused?
6. What ideas are worth rebuilding?
7. What code, if any, deserves controlled reuse review?
8. What must Radar V4 do differently?
9. What should the 3,000-unit curriculum emphasize?
10. Is there enough evidence to proceed, or should the program remain parked?

## Authority

Claude verifies and reports.

Todd authorizes.

Radar V4 remains pre-build. This handoff does not authorize implementation. See `README.md` for current program status.

Learning and Earning It.  
Stay on course.  
No drift.
