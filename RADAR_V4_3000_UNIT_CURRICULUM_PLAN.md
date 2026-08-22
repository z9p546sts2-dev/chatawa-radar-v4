# Radar V4 — 3,000-Unit Learning Curriculum Plan

## Status

**PLANNED — CONTENT NOT YET GENERATED**

The V1/V2 forensic review that this architecture waited on is complete. See `postmortem/RADAR_V1_V2_FINAL_FINDINGS.md`. Curriculum content has still not been generated, and this document does not authorize generation.

This document defines the architecture for a 3,000-unit educational corpus supporting future Radar V4 design judgment.

The curriculum is educational only. It is not a signal library, strategy library, backtest library, or proof of market edge.

Todd controls scope, pacing, acceptance, and any later connection to Radar V4 implementation.

## Purpose

The curriculum will build the knowledge required to:

- understand the failures found in legacy Radar V1 and V2;
- evaluate data, models, rankings, and backtests critically;
- design tests before implementation;
- recognize leakage, overfitting, and false confidence;
- understand the mathematics behind ML methods;
- reason about markets, risk, and uncertainty;
- design reliable human-controlled systems;
- reject weak or unsupported ideas before code is written.

## Design rule

The 3,000 units will be divided into two layers:

1. **Core curriculum** — timeless principles required regardless of postmortem findings.
2. **Targeted repair curriculum** — units selected or emphasized because V1/V2 evidence reveals a weakness.

The final distribution may be adjusted after Claude completes the forensic review.

## Proposed unit distribution

### Block 1 — Mathematical foundations: 500 units

- arithmetic and algebra for model reasoning;
- functions and transformations;
- vectors and matrices;
- linear algebra;
- calculus;
- multivariable calculus;
- gradients and Jacobians;
- optimization foundations;
- numerical methods;
- proof and reasoning habits.

### Block 2 — Probability and statistics: 450 units

- probability foundations;
- conditional probability;
- Bayes reasoning;
- random variables;
- distributions;
- expectation and variance;
- sampling;
- estimation;
- confidence intervals;
- hypothesis testing;
- multiple comparisons;
- Bayesian inference;
- uncertainty and calibration.

### Block 3 — Machine learning foundations: 500 units

- supervised learning;
- unsupervised learning;
- feature design;
- labels and targets;
- model capacity;
- bias and variance;
- regularization;
- tree methods;
- linear models;
- neural networks;
- ensembles;
- representation learning;
- interpretability;
- model selection.

### Block 4 — Time series and temporal ML: 350 units

- temporal ordering;
- stationarity;
- autocorrelation;
- seasonality;
- regime change;
- rolling windows;
- walk-forward validation;
- temporal leakage;
- forecasting;
- online versus batch learning;
- concept drift;
- revision and vintage handling.

### Block 5 — Trading systems and market structure: 350 units

- order books;
- spreads;
- liquidity;
- slippage;
- transaction costs;
- latency;
- fills;
- corporate actions;
- survivorship bias;
- market data quality;
- execution assumptions;
- portfolio construction boundaries;
- market-impact limitations.

### Block 6 — Backtesting, validation, and experiment design: 300 units

- baseline design;
- frozen datasets;
- preregistration;
- train/validation/test separation;
- out-of-sample testing;
- cross-validation limitations;
- walk-forward testing;
- robustness checks;
- sensitivity analysis;
- ablation;
- reproducibility;
- false discovery;
- stop rules.

### Block 7 — Risk, uncertainty, and decision theory: 200 units

- loss functions;
- asymmetric risk;
- drawdown;
- tail risk;
- volatility;
- calibration;
- confidence versus probability;
- decision thresholds;
- expected utility;
- uncertainty communication;
- human review.

### Block 8 — ML systems engineering: 200 units

- data contracts;
- provenance;
- pipelines;
- idempotency;
- observability;
- testing;
- deployment boundaries;
- rollback;
- drift monitoring;
- failure isolation;
- security;
- reproducibility.

### Block 9 — Governance, postmortem, and failure control: 150 units

- claims versus operation;
- scope control;
- change control;
- model risk;
- auditability;
- human authority;
- stop conditions;
- incident review;
- reuse/rebuild/reject decisions;
- ethical and legal boundaries;
- no-drift discipline.

**Total: 3,000 units**

## Unit format

Every unit should contain:

```text
Unit number and title
Concept
Prerequisites
Learning objective
Core explanation
Worked reasoning or derivation
Trading-system relevance
Radar V4 relevance
Common mistake
Failure mode
Boundary or limitation
Reflection questions
Looking ahead
Review status
Source or derivation record
```

## Quality gates

A unit is not complete merely because text exists.

Each unit should pass:

1. Concept accuracy
2. Clear terminology
3. Correct mathematics
4. Explicit assumptions
5. Failure-mode explanation
6. Radar V4 relevance
7. No unsupported signal or edge claim
8. No hidden implementation authorization
9. Review status recorded
10. No duplication without purpose

## Postmortem linkage

Each verified V1/V2 finding should link to one or more curriculum areas.

Example mapping:

```text
Temporal leakage finding
→ temporal validation units
→ data-vintage units
→ walk-forward testing units

Unsupported confidence score
→ calibration units
→ probability interpretation units
→ decision-threshold units

Unrealistic backtest
→ market structure units
→ slippage and fill units
→ reproducibility units

Weak provenance
→ data-contract units
→ lineage units
→ revision handling units

Architecture coupling
→ decomposition units
→ failure isolation units
→ rollback units
```

## Storage plan

Do not create one unmanageable 3,000-unit file.

Preferred structure:

```text
learning/
  README.md
  CURRICULUM_INDEX.md
  POSTMORTEM_TO_CURRICULUM_MAP.md
  block-01-mathematics/
  block-02-probability-statistics/
  block-03-machine-learning/
  block-04-time-series/
  block-05-market-structure/
  block-06-validation/
  block-07-risk-decision/
  block-08-ml-systems/
  block-09-governance/
```

Units may be grouped into bounded chapter files, while the index preserves one-to-one unit identity.

## Sequencing

The proposed order is:

```text
Postmortem evidence
→ targeted learning-needs map
→ final curriculum allocation
→ curriculum index
→ unit generation in bounded batches
→ review and correction
→ completion checkpoint
→ Radar V4 design gate
```

## Boundaries

The curriculum does not authorize:

- live trading;
- model deployment;
- signal generation;
- brokerage integration;
- use of old code;
- backtesting with live capital;
- a claim that completing 3,000 units proves an edge;
- automatic activation of Radar V4.

## Completion meaning

Completing the curriculum would mean:

- the educational corpus exists;
- concepts and failure modes have been studied;
- Radar V4 requirements can be evaluated more intelligently.

It would not mean:

- Radar V4 is profitable;
- a model is validated;
- a signal exists;
- production use is safe;
- implementation is authorized.

## Governing principle

> The curriculum strengthens judgment; evidence still decides whether a system deserves to be built.

Learning and Earning It.  
Stay on course.  
No drift.
