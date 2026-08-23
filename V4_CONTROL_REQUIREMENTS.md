# Radar V4 Control Requirements

**Status:** Foundation control record  
**Scope:** Documentation only  
**Implementation authorized:** Phase 5 local workshop only; vendor, Phase 6, and paper trading remain unauthorized  
**Purpose:** Convert verified V1/V2 failures and strengths into enforceable controls for any future Radar V4 work.

**Later current status (2026-08-23):** Phase 5 units 7–400 are complete within scope on the local FIXTURE/SYNTHETIC workshop. This control record still binds. It does not authorize vendor data, Phase 6, paper trading, or a market method.

---

## 1. Governing posture

This document does not authorize vendor data ingestion, feature design, backtesting, live observation, broker connectivity, or autonomous trading. Later Phase 5 local-workshop authorization did not lift those bans.

The controls below were earned from the bounded forensic review of `legacy-radar-v1` and `legacy-radar-v2`.

They exist to prevent known failure modes from recurring.

### Governing principles

1. A process that runs is not automatically a valid system.
2. Software correctness, data correctness, methodological validity, and market usefulness are separate claims.
3. Decision cadence must not outrun data and feature cadence.
4. No threshold may outrun its evidence.
5. No dataset may outrun its provenance.
6. A fresh price may not conceal stale features.
7. Tools verify; Todd authorizes.
8. `NO EDGE SHOWN` is an acceptable and complete outcome.

---

## 2. Control classification

Each control is assigned to one of the following stages:

- **REQUIRED BEFORE ANY CODE**
- **REQUIRED BEFORE DATA INGESTION**
- **REQUIRED BEFORE METHOD RESEARCH**
- **REQUIRED BEFORE SHADOW OPERATION**
- **OPTIONAL LATER**

No stage label authorizes work. It identifies the latest point by which the control must exist if that stage is ever separately authorized.

---

# Control 1 — Syntax and import gate

**Legacy failure addressed:** V1 shipped with an entrypoint that failed to parse and multiple imports that did not resolve.

**Classification:** REQUIRED BEFORE ANY CODE

**Requirement:** Every committed Python file must parse, and every declared entrypoint must import successfully.

**Minimum implementation:**

- Run `python -m compileall .`.
- Run one smoke-import test for every entrypoint.
- Block merge on failure.

**Required evidence:** A green automated check tied to the exact commit under review.

**Review mode:** Automated.

**Stop condition:** Any syntax error, unresolved import, or non-loading entrypoint blocks merge.

**Excessive at this stage:** Strict static typing across the entire repository, mandatory coverage percentages, or a large CI-platform evaluation.

---

# Control 2 — Feature cadence declaration

**Legacy failure addressed:** V1 and V2 operated on an intraday schedule while computing core features from daily bars.

**Classification:** REQUIRED BEFORE DATA INGESTION

**Requirement:** Every feature must declare:

- feature name;
- decision horizon;
- required source interval;
- expected update cadence;
- maximum acceptable staleness;
- approved use;
- prohibited use.

**Minimum implementation:** A reviewed Markdown or YAML cadence table.

**Required evidence:** A cadence-alignment record linking each feature to the decision process it serves.

**Review mode:** Human design review once per feature version.

**Stop condition:** A feature whose source interval is coarser than the claimed decision cadence may not be called responsive or used to gate a time-sensitive decision without an explicit documented exception.

**Excessive at this stage:** A full streaming-data freshness platform.

---

# Control 3 — Context versus decision-input separation

**Legacy failure addressed:** Daily regime context became a load-bearing multiplier in intraday decisions.

**Classification:** REQUIRED BEFORE METHOD RESEARCH

**Requirement:** Every input must be designated as either:

- **CONTEXT** — descriptive or higher-timeframe information; or
- **DECISION INPUT** — directly affects ranking, gating, scoring, promotion, or execution status.

A context input may not silently become a decision input.

**Minimum implementation:** A naming or tagging convention plus a one-page data-flow record.

**Required evidence:** A reviewed dependency map showing which inputs affect which decisions.

**Review mode:** Human design review.

**Stop condition:** A context-only variable may not directly multiply, gate, or promote a decision without separate evidence and explicit approval.

**Excessive at this stage:** A formal dataflow type system.

---

# Control 4 — Price and feature timestamp consistency

**Legacy failure addressed:** Fresh execution prices masked stale daily-derived scoring features.

**Classification:** REQUIRED BEFORE DATA INGESTION

**Requirement:** Every decision record must carry, at minimum:

- price timestamp;
- feature timestamp;
- regime timestamp where applicable;
- retrieval timestamp;
- source interval;
- freshness state.

**Minimum implementation:** Log the timestamps together and calculate their age difference.

**Required evidence:** A test showing that stale features cannot be presented as current merely because the last price is fresh.

**Review mode:** Automated check with human review when closing a freshness incident.

**Stop condition:** A freshness defect cannot be marked resolved until all affected pipelines pass timestamp-consistency checks.

**Excessive at this stage:** A general-purpose enterprise data-lineage platform.

---

# Control 5 — No threshold without evidence

**Legacy failure addressed:** V2 contained more than 30 hardcoded score, confidence, regime, momentum, relative-volume, ATR, risk/reward, and decay values without a documented derivation.

**Classification:** REQUIRED BEFORE METHOD RESEARCH

**Requirement:** Every new or changed threshold, multiplier, cutoff, weight, decay rule, promotion rule, or confidence band must have a linked evidence record.

The evidence record must include:

- rule name;
- exact value;
- decision purpose;
- derivation source;
- baseline;
- validation period;
- out-of-sample result when applicable;
- nearby-value sensitivity;
- known failure cases;
- retirement or kill condition;
- approval status.

**Minimum implementation:** A CSV, YAML, or Markdown threshold registry plus a required review-template field.

**Required evidence:** A unique evidence ID linked from the rule or configuration.

**Review mode:** Human approval for every threshold introduction or change.

**Stop condition:** No unexplained threshold may merge.

**Unresolved dependency:** The exact standard for “meaningfully different” remains to be earned through the active methodological work; this document does not invent that standard.

**Excessive at this stage:** Automated threshold optimization or auto-tuning.

---

# Control 6 — Historical validation before promotion

**Legacy failure addressed:** Neither V1 nor V2 contained a backtesting or historical-validation layer, despite repeated changes to trading logic.

**Classification:** REQUIRED BEFORE METHOD RESEARCH

**Requirement:** No method, scoring rule, confidence rule, or promotion rule may advance beyond research status without historical evaluation against a declared baseline and an untouched evaluation period.

**Minimum implementation:** A bounded historical replay process using fixed data, fixed rules, and a stated baseline.

**Required evidence:** A reproducible report containing:

- question;
- dataset identity;
- time split;
- baseline;
- method version;
- assumptions;
- costs where relevant;
- results;
- sensitivity findings;
- limitations;
- disposition.

**Review mode:** Human review.

**Stop condition:** No promotion without linked historical-validation evidence.

**Unresolved dependency:** Metrics, pass/fail thresholds, baseline selection, and kill standards are not defined here and must not be invented casually.

**Excessive at this stage:** A distributed backtesting platform or commercial quant stack before one bounded method exists.

---

# Control 7 — Test-category labeling

**Legacy failure addressed:** V2’s 89 passing software tests could easily be mistaken for proof of market or methodological validity.

**Classification:** REQUIRED BEFORE ANY CODE

**Requirement:** Every test and every test report must identify its category:

- **SOFTWARE CORRECTNESS**
- **DATA CORRECTNESS**
- **METHOD VALIDITY**
- **OPERATIONAL RESILIENCE**

**Minimum implementation:** Test markers or named test groups, with separate counts in every status report.

**Required evidence:** A test report that states category counts and failures separately.

**Review mode:** Automated grouping; human responsibility for accurate reporting language.

**Stop condition:** No report may say “tested” or “all tests passed” without identifying the categories covered.

**Excessive at this stage:** A separate governance platform for test taxonomy.

---

# Control 8 — Mandatory dataset provenance

**Legacy failure addressed:** `outcome_history.csv` appeared fixture-like or generated, but lacked metadata declaring whether it was live, synthetic, replay, or test data.

**Classification:** REQUIRED BEFORE DATA INGESTION

**Requirement:** Every stored dataset must declare at minimum:

- provenance class: `LIVE`, `HISTORICAL`, `BACKFILL`, `SYNTHETIC`, `FIXTURE`, `REPLAY`, or `MANUALLY_EDITED`;
- source vendor;
- symbol or universe identity;
- market timestamp;
- retrieval timestamp;
- interval;
- timezone;
- transformation version;
- checksum or equivalent integrity identifier.

**Minimum implementation:** A required provenance field and a simple schema-validation function.

**Required evidence:** Automated validation at write and read time.

**Review mode:** Automated.

**Stop condition:** Any dataset missing provenance or violating its own timing rules is quarantined and may not enter research, reporting, or validation.

**Excessive at this stage:** A commercial data catalog or enterprise lineage product.

---

# Control 9 — Shared data-access and fallback policy

**Legacy failure addressed:** Different V2 pipelines used inconsistent vendors and fallback logic, producing contradictory data behavior.

**Classification:** REQUIRED BEFORE DATA INGESTION

**Requirement:** All data retrieval must use a shared access layer with a single documented fallback order for each data type.

**Minimum implementation:** One shared client per data type, imported by all consuming modules.

**Required evidence:**

- a source-of-truth fallback table;
- integration tests for provider failure;
- logs identifying which source served each request.

**Review mode:** Human approval of the fallback policy; automated execution thereafter.

**Stop condition:** No pipeline may introduce independent vendor-fallback logic outside the shared layer.

**Excessive at this stage:** A universal plugin framework for providers that are not in use.

---

# Control 10 — Stop rule and kill criterion

**Legacy failure addressed:** V1 and V2 had no governed rule defining when a method, threshold, or system behavior should be retired.

**Classification:** REQUIRED BEFORE SHADOW OPERATION

**Requirement:** Every approved method or threshold must have a written stop or kill criterion before shadow operation.

The record must identify:

- monitored condition;
- observation window;
- failure threshold;
- required evidence;
- review owner;
- human authorization requirement;
- allowed responses;
- retirement status.

**Minimum implementation:** A structured stop-rule register maintained in Markdown, YAML, CSV, or a spreadsheet.

**Required evidence:** A complete stop-rule entry linked to the approved method or threshold.

**Review mode:** Human-controlled. Tools may monitor and recommend; Todd authorizes retirement or continuation.

**Stop condition:** No method enters shadow operation without an approved stop rule.

**Excessive at this stage:** An autonomous kill system acting without human authorization.

---

# Preserved engineering requirement 1 — Honest health states

**Legacy strength preserved:** V2’s V25.3 distinction between a process running and a scan actually succeeding.

**Classification:** REQUIRED BEFORE SHADOW OPERATION

Any future health model must distinguish at least:

- process started;
- provider responded;
- data arrived;
- data was fresh;
- expected symbols were present;
- features computed;
- feature cadence matched decision cadence;
- method executed;
- output passed validity checks;
- output was stored.

A single generic `HEALTHY` state is insufficient.

**Minimum implementation:** Structured JSON-line events and explicit health-state transitions.

**Excessive at this stage:** A full application-performance-monitoring platform.

---

# Preserved engineering requirement 2 — Atomic persistence and deterministic replay

**Legacy strengths preserved:** V2’s atomic SQLite transaction fix and frozen-baseline replay test pattern.

**Classification:** REQUIRED BEFORE ANY CODE

Any future persistence layer must use atomic writes suitable for the selected storage system.

Any future method engine must support deterministic replay against an explicitly provenance-labeled frozen input.

Deterministic replay proves behavioral stability. It does not prove methodological correctness.

**Minimum implementation:**

- atomic transaction boundaries;
- crash-consistency test;
- frozen-input replay test;
- provenance metadata on the frozen input.

**Excessive at this stage:** Distributed databases or event sourcing without a demonstrated scale requirement.

---

## 3. Minimum viable V4 quality gate

No future change may merge unless all applicable conditions below are satisfied:

1. The code parses and required entrypoints import.
2. Any new or changed threshold links to an evidence record.
3. Any new dataset carries valid provenance.
4. Any new feature declares required cadence and approved use.
5. Test output is reported by category.
6. Any persistence change preserves atomicity.
7. Any shared-data change follows the documented access and fallback policy.

This gate is deliberately small and directly tied to verified legacy failures.

---

## 4. Controls that may remain simple initially

The following do not require specialized platforms at the beginning:

- cadence table — Markdown or YAML;
- threshold evidence registry — CSV, YAML, or Markdown;
- provenance tag — required schema field;
- stop-rule register — spreadsheet or text record;
- structured logging — JSON lines;
- syntax/import gate — standard Python tooling;
- test taxonomy — pytest markers or named groups.

---

## 5. Overengineering to avoid

Do not introduce the following without an evidenced requirement:

1. Distributed or cloud-scale backtesting infrastructure.
2. Enterprise observability or application-performance monitoring.
3. Autonomous kill systems without human authorization.
4. General-purpose provider plugin frameworks.
5. Heavy database architecture before scale requires it.
6. Multiple programming languages before profiling identifies a real need.
7. Automated threshold optimization before threshold evidence standards exist.
8. Full repository folder taxonomies for features or methods that do not yet exist.

---

## 6. Explicitly unresolved

This document does not define:

- a trading method;
- a feature set;
- a scoring formula;
- a confidence formula;
- a market-data vendor;
- a backtest metric suite;
- a success threshold;
- an edge claim;
- a live or shadow operating schedule;
- a broker or execution path;
- an autonomous trader.

The standard for determining whether a result is meaningfully different from baseline or noise remains unresolved here and must not be silently replaced by a convenient number.

---

## 7. Current disposition

```text
Legacy V1/V2 postmortem: CLOSED
Failure-to-control matrix: ACCEPTED
V4 control requirements: DOCUMENTED
V4 research methodology: DEFINED / AUDITED
SPECIFIC MARKET METHOD: NOT DEFINED
PHASE 5 LOCAL WORKSHOP: UNITS 7–400 COMPLETE WITHIN SCOPE
VENDOR / HISTORICAL ACCESS: NOT AUTHORIZED
Radar V4: LOCAL EVIDENCE WORKSHOP — NOT A TRADER
Sebastian: NOT DISPLACED
```

---

## Closing principle

> V1 and V2 taught us what failed. These controls define what must prevent recurrence. They do not, by themselves, prove that Radar V4 has a valid market method or authorize a new build.

Learning and Earning It.  
Stay on course.  
No drift.
