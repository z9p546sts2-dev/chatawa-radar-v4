# Radar V4 Methodology Definition — TC

**Date:** 2026-08-07  
**Authority holder:** Todd C.  
**Methodology type:** Evidence-first research methodology  
**Trading method defined:** No  
**Signal formula defined:** No  
**Thresholds defined:** No  
**Implementation authorized:** No  
**Build Unit 1 authorized:** No

---

## 1. Purpose

Radar V4 will use an evidence-first methodology for deciding whether a market observation, candidate feature, candidate method, or future system behavior has earned a stronger claim.

The methodology answers:

> What evidence must exist before Radar V4 may move from observation to research claim, from research claim to method candidate, and from method candidate to any later operational consideration?

It does **not** answer:

- what security to trade;
- when to enter or exit;
- what feature to use;
- what score to calculate;
- what threshold to set;
- what return target is acceptable;
- what constitutes an edge by numerical fiat;
- whether live or shadow operation should occur.

Those require future evidence and separate Todd authorization.

---

## 2. Governing methodological principles

1. **Ordinary before exceptional.** A candidate effect cannot be interpreted until ordinary variation is measured under the same metric and data rules.
2. **Question before calculation.** Each unit begins with one narrow predeclared research question.
3. **Identity before analysis.** Dataset, source, interval, timestamps, transformations, and provenance must be known before results are interpreted.
4. **Same ruler on both sides.** Baseline and candidate/event observations use the same metric, timing convention, transformations, and eligibility rules.
5. **Direction is not magnitude.** Repeated direction may be described separately from effect size.
6. **Magnitude is not usefulness.** A large observed difference does not automatically become a useful, predictive, or tradable effect.
7. **Thresholds require entitlement.** No cutoff, score, weight, multiplier, confidence band, or promotion rule may be introduced merely because it appears reasonable.
8. **Software correctness is not method validity.** Passing code tests cannot substitute for evidence about the market claim.
9. **No rescue after seeing results.** A failed or unclear primary question cannot be rescued by changing the metric, sample, threshold, or comparison after results are known.
10. **Negative results count.** `NO EDGE SHOWN`, `NOT DIFFERENT`, `UNCLEAR`, `INSUFFICIENT EVIDENCE`, and `INVALID COMPARISON` are valid outcomes.
11. **Human authority remains explicit.** Tools may collect, calculate, compare, test, and report. Todd authorizes promotion, reopening, implementation, shadow operation, or retirement.
12. **Claims remain bounded to the evidence actually observed.**

---

## 3. Research object hierarchy

Radar V4 distinguishes five different objects that must not be collapsed into one another.

### A. Observation

A measured fact about a declared dataset under a declared metric.

An observation earns description only.

### B. Baseline

A bounded record of ordinary variation produced under the same measurement rules intended for later comparison.

A baseline is a reference distribution or comparison set, not a prediction and not a threshold by itself.

### C. Candidate effect

A predeclared comparison showing how a candidate condition differs from its baseline.

A candidate effect may be descriptive even when direction or magnitude appears strong.

### D. Candidate method

A fully specified rule or transformation proposed for historical evaluation.

A candidate method must identify its inputs, timing, cadence, assumptions, outputs, and prohibited interpretations before testing.

### E. Approved method

A candidate method that has passed all separately authorized methodological gates required for its intended research status.

Approval for research status does not authorize shadow operation, trading, broker connectivity, or capital allocation.

---

## 4. Methodological stage gates

### M0 — Research question gate

Required:

- one narrow question;
- one primary comparison;
- one primary metric;
- declared unit of observation;
- declared in-scope universe/time period;
- explicit non-goals.

Stop if the question cannot be stated before looking at the answer.

### M1 — Data identity and provenance gate

Required before calculation:

- provenance class;
- provider/source;
- symbol/universe;
- market timestamp;
- retrieval timestamp;
- interval;
- timezone;
- transformation version;
- integrity identifier/checksum where stored;
- missing/duplicate handling rule;
- source fallback disclosure.

Any provenance-unknown or internally contradictory dataset is quarantined.

### M2 — Cadence and timing gate

Required:

- source-data cadence;
- feature/update cadence if a feature exists;
- evaluation cadence;
- outcome horizon if applicable;
- maximum acceptable staleness;
- context versus decision-input designation.

A decision/evaluation cadence may not outrun a load-bearing input cadence.

### M3 — Ordinary baseline gate

Before interpreting a candidate condition, establish bounded ordinary comparison data using the same ruler.

The baseline record must state:

- selection rule;
- observation count;
- metric;
- distribution summaries appropriate to the question;
- visible variation;
- exclusions;
- limitations.

The baseline does not automatically create a threshold.

### M4 — Candidate comparison gate

The candidate/event/method comparison must use the locked rules from M0-M3.

Required outputs:

- direction;
- magnitude;
- distribution/shape notes where relevant;
- denominator/sample size;
- missing observations;
- comparison validity status.

Result language must distinguish:

- descriptive difference;
- repeated pattern;
- predictive claim;
- method-validity claim;
- market-usefulness claim.

Only the first two may arise from simple bounded comparisons. Stronger claims require later gates.

### M5 — Threshold entitlement gate

A numerical threshold may be proposed only after the evidence class capable of entitling it is declared before threshold selection.

Required before a threshold can become a method parameter:

- why a threshold is necessary;
- evidence class used to derive it;
- baseline/noise comparison;
- training/derivation sample separated from evaluation sample;
- nearby-value sensitivity;
- failure cases;
- multiple-comparison discipline where applicable;
- kill/retirement condition;
- explicit Todd approval.

Practice numbers, visually convenient cutoffs, legacy Radar constants, and post-hoc values are not entitlement evidence.

### M6 — Historical validation gate

No candidate method advances beyond research status without a separately authorized historical evaluation.

Required design before execution:

- fixed dataset identity;
- fixed method version;
- declared baseline;
- untouched evaluation period;
- leakage/look-ahead protections;
- relevant costs/constraints if the claim requires them;
- predeclared primary metric;
- sensitivity plan;
- null/placebo or ordinary comparison where appropriate;
- success, failure, partial, unclear, and invalid outcomes;
- stop rule.

Historical validation can reject a method. It cannot authorize live use by itself.

### M7 — Replication and robustness gate

A method that survives one historical evaluation must still demonstrate that the finding is not dependent on one sample, one regime, one instrument, one provider, or one convenient parameter neighborhood.

The exact replication design is method-dependent and must be declared before execution.

### M8 — Promotion review gate

Promotion is a human governance decision after evidence review.

Possible dispositions:

- `REJECT AND PRESERVE`;
- `RESEARCH ONLY`;
- `NEEDS MORE EVIDENCE`;
- `READY FOR SHADOW-OPERATION DECISION`.

There is no automatic promotion from test results.

Shadow operation would require separate controls, stop rules, monitoring, and explicit Todd authorization.

---

## 5. Multiple-comparison discipline

Every research unit has one locked primary question and primary comparison.

Secondary analyses may be predeclared, but they cannot rescue a failed primary result.

Exploratory findings must be labeled exploratory and must become a new predeclared unit before they can support a stronger claim.

Searching many symbols, windows, features, thresholds, or transformations until something looks interesting does not establish evidence.

---

## 6. Reproducibility rule

Every result intended for preservation must be reproducible from:

- source/data identity;
- input checksum where stored;
- code version when code is used;
- configuration version;
- transformation/feature version;
- methodology version;
- declared parameters;
- runtime environment where material.

Deterministic replay establishes behavioral consistency only. It does not establish market validity.

---

## 7. Claim ladder

Radar V4 uses the following claim ladder:

```text
LEVEL 0 — MEASURED
LEVEL 1 — DESCRIBED
LEVEL 2 — REPEATED WITHIN BOUNDED SCOPE
LEVEL 3 — HISTORICALLY VALIDATED WITHIN PREDECLARED SCOPE
LEVEL 4 — REPLICATED / ROBUST WITHIN PREDECLARED SCOPE
LEVEL 5 — READY FOR SEPARATE SHADOW-OPERATION DECISION
```

No level implies the next.

No level means profitable, causal, safe, or tradable unless those exact claims have separately earned evidence.

---

## 8. Relationship to Sebastian Protocol

Sebastian Protocol remains a separate evidence-first research discipline and is not displaced by Radar V4.

Radar V4 may adopt compatible methodological lessons already earned through ordinary-baseline literacy, threshold-entitlement literacy, bounded event-vs-baseline comparison, and no-rescue discipline.

This does not convert Sebastian into software, reopen old Radar, or authorize implementation of any Sebastian premise.

---

## 9. Relationship to legacy Radar

Legacy V1/V2 may supply:

- failure evidence;
- requirements;
- bounded engineering patterns explicitly approved for reconsideration.

Legacy V1/V2 may not supply by inheritance:

- feature logic;
- scoring formulas;
- thresholds;
- confidence formulas;
- promotion rules;
- outcome-history claims;
- trading methodology.

Any future reuse requires component-level Todd authorization.

---

## 10. Methodology non-goals

This document does not define or authorize:

- a signal;
- an edge;
- a trading strategy;
- a feature set;
- a scoring system;
- a threshold value;
- a market-data vendor;
- a symbol universe;
- a backtest;
- data ingestion;
- live observation;
- shadow operation;
- broker integration;
- automated execution;
- capital allocation;
- autonomous trading.

---

## 11. Current disposition

```text
RADAR V4 RESEARCH METHODOLOGY — DEFINED
TRADING METHOD — NOT DEFINED
FEATURE SET — NOT DEFINED
THRESHOLDS — NONE
IMPLEMENTATION — NOT AUTHORIZED
BUILD UNIT 1 — NOT AUTHORIZED BY THIS RECORD
DATA INGESTION — NOT AUTHORIZED
BACKTESTING — NOT AUTHORIZED
LEGACY CODE REUSE — NOT AUTHORIZED
RADAR V4 — PRE-BUILD ELIGIBLE FOR BOUNDED FOUNDATION PROPOSAL REVIEW
```

The methodology blocker from the 2026-08-07 Pre-Build Authorization Review is closed only at the **research-process level**. A specific market method remains future evidence work.

---

## Closing principle

> Measure ordinary first. Lock the question before the answer. Preserve provenance. Separate direction from magnitude, software from method, and method from usefulness. Claim only what the evidence earned.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.  
Stay on the roadmap.
