# Chatawa Radar V4 — 4–5 Year Horizon Roadmap

**Later record (2026-08-22):** Phase 5 units 7–150 later completed on the local workshop path. This file remains a long-horizon companion. It does not authorize Phase 6, a vendor API, paper trading, or a market method.

**Status:** RECORDED HORIZON — NOT AN IMPLEMENTATION AUTHORIZATION  
**Authority holder:** Todd C.  
**Horizon:** four to five years of sequenced evidence gates  
**Trading method defined:** No  
**Autonomous trading authorized:** No  
**Build Unit 1 authorized by this record:** No

This document is the long-horizon companion to `ROADMAP.md` at the repository root.

`ROADMAP.md` remains the controlling near-term foundation roadmap. This file does not replace it, speed it up, or authorize any phase.

---

## 1. What this roadmap is

Todd asked for a 4–5 year Radar V4 roadmap after locking this product order:

1. **First product:** a quant **evidence** system, later packagable as SaaS.
2. **Later program, if ever earned:** a separately authorized autonomous trading program.

This roadmap records that order as a horizon, not as a delivery promise.

A year mark does not unlock the next stage. A stage advances only when its evidence exists and Todd separately authorizes the next bounded unit.

## 2. What this roadmap is not

This is not:

- a guarantee that Radar V4 will work as a trader;
- a schedule for stocks, futures, forex, crypto, and options;
- a commitment to buy a market-data API;
- permission to open a paper-trading or simulated-broker account;
- a claim of edge, best trades, or AI authority;
- permission to revive V1 or V2 code;
- authorization of Build Unit 1;
- a second methodology;
- a substitute for `AUTHORIZE BUILD UNIT 1 — TC`.

If the evidence ends at `NO EDGE SHOWN`, the 4–5 year program can still be complete. That is a valid ending, not a missed launch.

## 3. Two-product rule

Keep these products apart for the entire horizon.

### Product A — Radar V4 Evidence System

Human-controlled quant evidence and, only later, evidence SaaS.

It may:

- represent and validate evidence identity;
- admit one provenance-complete dataset at a time;
- run one predeclared research question at a time;
- show uncertainty, missing data, and counterevidence;
- sell or share **records, tests, and refusals**.

It may not:

- place live or paper orders as a way to start;
- connect to a broker so the project looks alive;
- call itself a signal service;
- promise best trades;
- treat paper P&L as proof of edge;
- hide a failed primary question behind a dashboard.

### Product B — Later Autonomous Trading Program

A different program with a different name and a later gate.

It may be considered only after Product A has:

- one market;
- one method;
- one historical validation against a declared baseline, including costs where the claim requires them;
- written kill criteria;
- explicit Todd authorization to open a separate program review.

Product B is not scheduled. Year 5 does not create it. Radar V4 does not become Product B by maturity or momentum.

## 4. Governing horizon rules

1. Evidence before interface.
2. One question before one dataset interpretation.
3. One dataset before one vendor expansion.
4. One market before one asset-class expansion.
5. Software correctness is not method validity.
6. Method validity is not usefulness.
7. Usefulness is not permission to trade.
8. A paid API is a dataset source, not a method.
9. SaaS packages evidence. It does not create edge.
10. Autonomous execution is a later program, not a Radar V4 phase.
11. Years do not authorize work. Todd authorizes work.
12. No drift.

## 5. Horizon map

Years are outer sequencing buckets. They are not start dates, staffing plans, or earned status.

```text
HORIZON 0     NOW            Authorization and first unit
HORIZON 1     YEARS 0–1      Evidence software bones
HORIZON 2     YEARS 1–2      One dataset, one question
HORIZON 3     YEARS 2–4      Evidence SaaS for humans
HORIZON 4     YEARS 3–5      One method, or honest stop
HORIZON 4A    IF EARNED      Bounded paper / simulated execution
HORIZON 5     IF EARNED      Separate Product B review
```

Existing foundation phases map as follows:

```text
ROADMAP PHASES 0–3     already complete / awaiting Todd decision
ROADMAP PHASE 4        Horizon 0–1   Build Unit 1 execution
ROADMAP PHASE 5        Horizon 2     data / research foundation
ROADMAP PHASE 6        Horizon 2–4   candidate feature / method research
ROADMAP PHASE 7        Horizon 4     bounded offline pilot
ROADMAP PHASE 8        Horizon 3–4   human review interface
ROADMAP PHASE 9        Horizon 4–4A  controlled live observation, then paper only if earned
PRODUCT B              not a Radar V4 phase
```

# Horizon 0 — Now: authorization, not architecture

**Objective:** Decide whether the first code unit may begin.

**In scope**

- confirm `main` has not drifted from the approved pre-build state;
- accept Python for Build Unit 1 only, unless Todd states otherwise;
- keep the Unit 1 file and test boundary unchanged;
- lock the pre-start rules already identified:
  - canonical serialization;
  - allowed provenance classes only;
  - contradictory records fail and are not repaired;
  - no price, volume, score, or signal fields;
  - no dependency beyond the standard library and test runner;
- explicit authorization equivalent to `AUTHORIZE BUILD UNIT 1 — TC`.

**Out of scope**

- market-data API purchase;
- SaaS architecture;
- multi-asset venue lists;
- autonomous-agent design;
- curriculum generation;
- additional foundation documents created only to keep moving.

**Exit**

Todd authorizes, revises, pauses, or rejects Build Unit 1.

**Stress test**

The tabletop already due: Unit 1 must still hold under V1/V2 pressures — unloadable entrypoints, “all tests passed,” mystery datasets, unevidenced numbers, and scope creep.

# Horizon 1 — Evidence software bones

**Objective:** Implement only Build Unit 1 — Evidence Envelope and Provenance Gate.

**What “done” means**

- envelopes can be constructed, validated, serialized, and fingerprinted;
- invalid provenance fails in the open;
- fixtures are labeled `FIXTURE` or `SYNTHETIC`;
- tests are reported as SOFTWARE CORRECTNESS and DATA CORRECTNESS;
- METHOD VALIDITY remains `NOT APPLICABLE`;
- audit confirms the unit did not grow into market logic.

**What “done” does not mean**

- a valid market dataset;
- a vendor relationship;
- a feature, method, or dashboard;
- SaaS readiness;
- authorization of Build Unit 2.

**Stress test**

Predeclared Unit 1 tests plus `python -m compileall` and import gates on the exact commit. No load test. No venue test. No “best trade” test.

**Stop**

Stop if implementation needs live or historical market data, a threshold, legacy code, or a new non-minimal dependency.

# Horizon 2 — One dataset, one question

**Objective:** Admit the first real historical dataset only after the envelope can refuse a bad record.

**Required before any API or file purchase**

- one narrow predeclared question;
- one primary metric;
- one ordinary baseline plan;
- one instrument class — the default first class is **US stocks**, not five asset classes;
- declared interval, timezone, adjustment policy, and maximum staleness;
- written reason a paid source is required instead of a smaller bounded file.

A historical-stock API may be considered here as a **named source**, not earlier. Buying it does not prove usefulness. It must still populate provenance fields and survive quarantine rules.

**In scope**

- one provider or one static historical extract;
- provenance validation at write and read;
- ordinary baseline measurement under the same ruler;
- result language limited to measured / described / unclear / invalid.

**Out of scope**

- futures, forex, crypto, and options expansion;
- feature libraries;
- scoring;
- backtests used as marketing;
- broker accounts;
- paper trading.

**Stress test**

- unknown provenance is quarantined;
- asked interval vs returned interval is visible;
- retrieval time cannot hide a stale market time;
- a revised vendor history cannot silently overwrite the first stored extract;
- the primary question cannot be swapped after seeing results.

**Exit**

One of: `NO EDGE SHOWN`, `UNCLEAR`, `INSUFFICIENT EVIDENCE`, `INVALID COMPARISON`, or “descriptive difference only — not a method.” Any of those may end Horizon 2 cleanly.

# Horizon 3 — Evidence SaaS for humans

**Objective:** Package Radar V4 as a product that sells evidence, not trades.

**Required before SaaS work**

- Horizon 1 complete within scope;
- at least one Horizon 2 dataset and question cycle completed honestly;
- a stated user and a stated decision the product supports;
- no ranking rule until failure cases, missing-data rules, and stop conditions are written.

**The product may show**

- underlying evidence;
- provenance;
- freshness;
- uncertainty;
- missing data;
- counterevidence;
- why an item was included or refused;
- human disposition.

**The product may not show**

- a trade button, including paper;
- a “best trade” rank;
- a confidence number without entitlement;
- a green health light that means only “the process ran.”

**Stress test**

- a customer cannot mistake a software-test report for method validity;
- a quarantined record cannot appear as a live opportunity;
- a failed primary question cannot be rescued by a secondary chart;
- multi-tenant access cannot leak another user’s dataset or secrets;
- the product still works if the honest answer is `NO EDGE SHOWN`.

**Stop**

Stop if SaaS design requires a broker, a signal feed, or a second asset class to look complete.

# Horizon 4 — One method, or honest stop

**Objective:** Either earn one historically validated candidate method in one market, or stop the method line.

**Required**

- locked question, dataset identity, method version, and untouched evaluation period;
- declared baseline;
- leakage / look-ahead protections;
- costs and constraints if the claim needs them;
- nearby-value sensitivity;
- predeclared success, failure, partial, unclear, and invalid outcomes;
- a kill / retirement rule.

**In scope**

- one bounded offline pilot;
- one human review surface for that method;
- read-only live observation only after a separate Todd authorization.

**Out of scope**

- paper or simulated broker orders (that is Horizon 4A, and only if earned);
- autonomous orders;
- portfolio authority;
- “AI finds the best trades”;
- expanding to futures, forex, crypto, and options because stocks were inconclusive.

**Stress test**

- the method cannot be saved by changing the metric after results;
- daily context cannot silently gate an intraday decision;
- frozen replay proves consistency only, not market validity;
- stop rules are testable before any shadow period.

**Exit**

```text
REJECT AND PRESERVE
RESEARCH ONLY
NEEDS MORE EVIDENCE
READY FOR SHADOW-OPERATION DECISION
HORIZON COMPLETE — NO EDGE SHOWN
```

`HORIZON COMPLETE — NO EDGE SHOWN` is a successful evidence program.

# Horizon 4A — Bounded paper / simulated execution

**Objective:** Rehearse one already-specified method against live or delayed quotes **without capital**, after historical validation, not instead of it.

Paper trading is operational rehearsal. It is not a backtest, not a method-discovery lab, and not a safer form of Product B.

**Required before any paper account or simulator**

- Horizon 4 completed with either `READY FOR SHADOW-OPERATION DECISION` or an explicit Todd exception that still names one locked method;
- the same question, method version, and kill rule used in the offline pilot;
- a written fill model: delay, spread, size, partials, rejects, and what the simulator is known to fake;
- a fixed paper window and a stop that does not move after seeing P&L;
- no parameter changes during the window unless the window is restarted and recorded;
- separate Todd authorization for this window only.

**In scope**

- simulated orders for one market and one method;
- logs of intended action, simulated fill, provenance, and freshness;
- comparison of paper outcome with the historical pilot **as a process check**;
- human review and an explicit shutoff.

**Out of scope**

- using paper P&L to invent a threshold;
- using a broker’s “guaranteed fill” book as evidence the method is tradable;
- opening stocks, futures, forex, crypto, and options paper books at once;
- connecting paper so Horizon 1–3 can be skipped;
- autonomous live orders.

**How to report paper results**

```text
SOFTWARE CORRECTNESS     did the paper path run and record
DATA CORRECTNESS         were quotes identified and fresh enough
OPERATIONAL RESILIENCE   did stop, reject, and shutoff work
METHOD VALIDITY          not earned by paper P&L
MARKET USEFULNESS        not earned by paper P&L
```

A profitable paper book with an honest fill model is still only rehearsal. A profitable paper book with fantasy fills is noise.

**Stress test**

- stale features cannot ride a fresh last price into a simulated order;
- a rejected or partial fill cannot be rewritten as a full fill;
- the window cannot be extended because the curve looks good;
- closing the paper account is tested, not assumed.

**Stop**

Stop if a paper account is opened to make Radar V4 feel alive, to justify a data API, or to tune rules after seeing results.

# Horizon 5 — Separate Product B review, if earned

**Objective:** Decide whether a **different** autonomous-trading program should even be scoped.

**This horizon does not start because four years have passed.**

It may open only after Horizon 4 produces `READY FOR SHADOW-OPERATION DECISION` and Todd still wants a second program review.

The review would have to answer, with evidence:

- what exact rule would be automated;
- what the system is forbidden to do;
- how a human shuts it off;
- what kill criterion retires it without debate;
- why autonomy is safer than continued human review;
- why “best trades” is still a prohibited phrase.

Until those answers exist, Product B remains unscoped. Radar V4 stays Product A.

# 6. Explicitly refused during this horizon

Do not schedule the following as year-N deliverables:

1. An all-asset execution book (stocks + futures + forex + crypto + options).
2. A purchased data platform as a substitute for a question.
3. Revival of V1 or V2 scoring, confidence, or feature pipelines.
4. An AI agent authorized to place orders.
5. A dashboard before a method.
6. The 3,000-unit curriculum as a gate in front of Build Unit 1.
7. Any claim that SaaS revenue proves the method.
8. Paper trading as a substitute for historical validation or as the first “real” test.

Those items may be discussed later as separate programs. They are not Radar V4 milestones.

# 7. Program-level stop rules

The 4–5 year horizon itself must stop or return to Todd if:

- Build Unit 1 expands into market logic;
- a data API is purchased, or a paper broker is opened, before Horizon 2’s question is locked;
- “all tests passed” is reported without categories;
- SaaS work starts so the project looks alive;
- a second asset class is added to rescue a weak first result;
- autonomous trading is treated as the real roadmap and the evidence system as prelude;
- test criteria are weakened after results are seen;
- pressure to continue is based only on elapsed years.

# 8. Immediate next action

Do not implement this horizon.

Do not buy historical data.

Do not open a paper-trading account.

Do not design the SaaS.

The only current action remains the Horizon 0 decision already recorded in `ROADMAP.md`:

```text
AUTHORIZE BUILD UNIT 1 — TC
```

or `REVISE`, `PAUSE`, or `REJECT`.

## Current disposition

```text
HORIZON ROADMAP — RECORDED
NEAR-TERM ROADMAP — STILL CONTROLLING
BUILD UNIT 1 EXECUTION — NOT AUTHORIZED
HISTORICAL DATA API — NOT AUTHORIZED
PAPER TRADING — NOT AUTHORIZED
EVIDENCE SAAS — NOT AUTHORIZED
SPECIFIC MARKET METHOD — NOT DEFINED
AUTONOMOUS TRADING PROGRAM — NOT SCOPED
YEARS ELAPSED — DO NOT AUTHORIZE
```

## Governing principle

> Four or five years can hold an evidence system. They cannot buy an edge. Stay on Product A until evidence, not the calendar, earns a later question.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.
