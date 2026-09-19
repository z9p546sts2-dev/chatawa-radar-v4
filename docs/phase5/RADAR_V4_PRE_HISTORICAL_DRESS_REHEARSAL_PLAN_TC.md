# Radar V4 — Pre-HISTORICAL Dress Rehearsal Plan

```text
TO — Todd C.
FROM — Cursor (bounded implementer)
AUTHORITY — Todd C. only
RECORD TYPE — TEST-ONLY PLAN / AUTHORIZED-TC
DATE — 2026-09-19
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4
PACKET PR — https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/38
WORKSHOP SOFTWARE — existing FIXTURE/SYNTHETIC path
AUTHORIZATION — AUTHORIZE DRESS REHEARSAL TEST PLAN — TC
```

This rehearsal uses the existing local FIXTURE/SYNTHETIC workshop. Phase 5 local software is banked through Unit 1400 on the stacked PR path. This document does not say Phase 5 ends at Unit 1300, does not raise or lock `PHASE5_HIGHEST_UNIT`, and does not create Units 1401+.

This is not HISTORICAL evidence. It does not authorize a source, license review, extract, vendor client, Units 1401+, or Phase 6.

No historical market data is used or downloaded. No vendor is an implementation dependency.

**Tools verify. Todd authorizes.**

---

## Purpose

Exercise the existing local workshop against the frozen first-cycle *shape* recorded in Decisions #1–#8, using SYNTHETIC bars only.

The dress rehearsal asks:

> Can the already-authorized FIXTURE/SYNTHETIC workshop admit, measure, refuse, and checksum a one-security daily pack whose declaration matches the first-cycle ruler — without any market bytes?

A passing rehearsal is SOFTWARE CORRECTNESS (and synthetic-label DATA CORRECTNESS) only. It does not earn HISTORICAL DATA CORRECTNESS, method validity, or usefulness.

## Frozen shape under test

| Item | First-cycle record | Dress-rehearsal stand-in |
|---|---|---|
| Question | existing locked close-to-close question | same locked question text |
| Security scope | one security (SPY identity) | one synthetic symbol `SYN:ONE` — not SPY, not a ticker alias |
| Interval | `1d` | `1d` |
| Evaluation | no finer than one completed U.S. regular session | pack contains only `1d` bars; no intraday rows |
| Timezone | `America/New_York` session-date | every envelope `timezone` is `America/New_York`; offsets match that zone |
| Date window shape | `2024-01-01`–`2024-12-31` inclusive NY calendar bounds; `2024-01-01` is a bound, not an expected bar | synthetic session dates fall on or after `2024-01-02` and on or before `2024-12-31` |
| Adjustment | `UNADJUSTED` | declaration `adjustment_policy: UNADJUSTED` |
| Staleness | `NONE` | declaration `max_staleness: "NONE"` |
| Metric | `close[t] - close[t-1]` | existing `close_to_close_changes` |
| Provenance | HISTORICAL not authorized | `SYNTHETIC` only |

`SYN:ONE` represents one-security scope. It is not SPY, not CUSIP `78462F103`, and not market evidence.

The existing pack `fixtures/synthetic_one_symbol_1d/` stays as-is (`UTC`, `SYN:AAA`, three bars). This rehearsal does not replace it.

## What this plan will not do

- download or embed market prints;
- use SPY / CUSIP / ISIN as observation identity;
- name a vendor as a test or runtime dependency;
- add a network client;
- change `PACK_ALLOWED_PROVENANCE`;
- create Units 1401+ or move `PHASE5_HIGHEST_UNIT`;
- implement an exchange calendar, holiday table, or survivorship list;
- treat a MEASURED synthetic baseline as HISTORICAL evidence.

---

## Authorized files

| Path | Role | Created now? |
|---|---|---|
| `docs/phase5/RADAR_V4_PRE_HISTORICAL_DRESS_REHEARSAL_PLAN_TC.md` | this plan | yes |
| `fixtures/synthetic_dress_rehearsal_1d/README.md` | SYNTHETIC / `PRE_HISTORICAL_DRESS_REHEARSAL` label; not market evidence | yes — authorized |
| `fixtures/synthetic_dress_rehearsal_1d/IDENTITY.txt` | durable `SYNTHETIC` + `PRE_HISTORICAL_DRESS_REHEARSAL` artifact identity | yes — authorized |
| `fixtures/synthetic_dress_rehearsal_1d/declaration.json` | one-security `1d` / `America/New_York` / `UNADJUSTED` / `max_staleness: NONE` | yes — authorized |
| `fixtures/synthetic_dress_rehearsal_1d/obs_2024-01-02.json` | first golden bar | yes — authorized |
| `fixtures/synthetic_dress_rehearsal_1d/obs_2024-01-03.json` | second golden bar | yes — authorized |
| `fixtures/synthetic_dress_rehearsal_1d/obs_2024-01-04.json` | third golden bar | yes — authorized |
| `fixtures/synthetic_dress_rehearsal_1d/manifest.json` | optional file digests, same as existing pack | yes — authorized |
| `tests/test_dress_rehearsal.py` | all required categories | yes — authorized |

Full-year-shaped bars are **generated inside the test**, not committed as hundreds of observation files. That keeps the repo inspectable and avoids a silent calendar catalog.

No new `radar_v4/*.py` modules. No CLI commands. Tests call existing functions:

- `load_dataset_pack`
- `run_session_from_pack`
- `close_to_close_changes`
- `inspect_series`
- `check_pack_determinism`
- `validate_envelope` / `admit_to_dataset` as needed

Helpers stay local to `tests/test_dress_rehearsal.py` unless a tiny constructor is needed. `tests/helpers.py` currently stamps UTC; the rehearsal must not reuse UTC defaults for these bars.

## Proposed declaration (golden pack)

```text
dataset_id              synthetic.dress-rehearsal.1d
provenance_class        SYNTHETIC
provider                PHASE5_SOURCE
universe                SYN:ONE
interval                1d
timezone                America/New_York
transformation_version  phase5-v1
adjustment_policy       UNADJUSTED
locked_question         ordinary close-to-close changes for one symbol
primary_metric          close-to-close difference
max_staleness           NONE
```

## Proposed golden bars

Session-close convention for this SYNTHETIC pack: `16:00:00` in `America/New_York`. January 2024 is standard time (`-05:00`). Retrieval is one hour later. Closes are invented decimals.

| File | Market timestamp | Close |
|---|---|---|
| `obs_2024-01-02.json` | `2024-01-02T16:00:00.000000-05:00` | `100.00` |
| `obs_2024-01-03.json` | `2024-01-03T16:00:00.000000-05:00` | `100.25` |
| `obs_2024-01-04.json` | `2024-01-04T16:00:00.000000-05:00` | `99.75` |

These dates are synthetic session labels inside the Decision #3 window. They are not a claim that 2024-01-02 was an exchange session.

---

## Required test categories and expected outcomes

All tests: `PYTHONPATH=. python3 -m unittest tests.test_dress_rehearsal -v`

Category labels stay separate: SOFTWARE CORRECTNESS for session/determinism/checksum; DATA CORRECTNESS only for synthetic identity, timezone-offset match, and decimal arithmetic. No METHOD VALIDITY tests.

### A. Golden arithmetic

| Proposed test | Action | Expected outcome |
|---|---|---|
| `test_golden_pack_is_usable_synthetic` | `load_dataset_pack` on the committed 3-bar pack | usable; provenance `SYNTHETIC`; universe `SYN:ONE`; interval `1d`; timezone `America/New_York`; adjustment `UNADJUSTED`; `max_staleness == "NONE"` |
| `test_golden_envelope_offsets_match_new_york` | validate each envelope | valid; no `TIMEZONE_MISMATCH`; offsets equal `America/New_York` on that civil date |
| `test_golden_close_to_close_arithmetic` | `run_session_from_pack` / `close_to_close_changes` | status `MEASURED`; claim `LEVEL 0 — MEASURED`; changes exactly `("0.25", "-0.50")` |
| `test_golden_is_not_historical` | read declaration and session notes | provenance is not `HISTORICAL`; notes still say SYNTHETIC is not HISTORICAL evidence |
| `test_existing_utc_fixture_pack_still_measures` | session on `fixtures/synthetic_one_symbol_1d/` | unchanged MEASURED path; rehearsal does not break the UTC fixture |

### B. Full-year-shaped synthetic pack

Generated in-test. Convention name: `SYNTHETIC_WEEKDAY_SPAN`. Include one `1d` bar for each Monday–Friday whose date is `>= 2024-01-02` and `<= 2024-12-31` in `America/New_York`. DST offsets come from `ZoneInfo("America/New_York")`, not a hand table.

This is a year-shaped generator. It is **not** an NYSE/Nasdaq holiday calendar. Full-market holidays that fall on weekdays will have a synthetic bar. That is the known gap, and category F probes it.

Closes: a deterministic invented series, for example `close[i] = 100 + (i % 7) * 0.01` as a decimal string, so arithmetic is reproducible without market data.

| Proposed test | Action | Expected outcome |
|---|---|---|
| `test_year_shaped_pack_measures` | build temp pack; `run_session_from_pack` | usable; `MEASURED`; change_count = observation_count - 1; first stamp on/after 2024-01-02; last stamp on/before 2024-12-31; no bar dated 2024-01-01 |
| `test_year_shaped_is_one_symbol_1d` | inspect envelopes | every bar `SYN:ONE`, `1d`, `America/New_York`, `UNADJUSTED` ruler fields match declaration |
| `test_year_shaped_has_no_intraday_rows` | intervals | only `1d` |
| `test_year_shaped_is_not_an_exchange_calendar` | README/test note plus count | test records that weekday span ≠ holiday-aware completeness; no code claims NYSE sessions |

Approximate size: on the order of 260 weekday bars. Committed files remain the 3-bar golden pack only.

### C. Refusal / mutation cases

| Proposed test | Mutation | Expected outcome |
|---|---|---|
| `test_historical_label_still_refused` | declaration or observation `HISTORICAL` | `PACK_PROVENANCE_NOT_ALLOWED`; pack not usable or observation quarantined |
| `test_live_baseline_refused` | two LIVE observations into `close_to_close_changes` | `INVALID_COMPARISON`; claim `NONE` |
| `test_utc_offset_refused_on_new_york_declaration` | `America/New_York` declared; timestamp `+00:00` | `TIMEZONE_MISMATCH` / not admitted |
| `test_interval_mismatch_quarantined` | one bar `1h` | `DATASET_DECLARATION_MISMATCH` or baseline `INVALID_COMPARISON` |
| `test_second_symbol_is_invalid_comparison` | mix `SYN:ONE` and `SYN:TWO` | `INVALID_COMPARISON` |
| `test_duplicate_session_timestamp_refused` | two bars, same market timestamp | `DUPLICATE_MARKET_TIMESTAMP`; series not valid; no MEASURED baseline |
| `test_single_bar_insufficient` | one observation | `INSUFFICIENT_EVIDENCE` |
| `test_naive_timestamp_refused` | timestamp without offset | `INVALID_MARKET_TIMESTAMP`; UTC is not inferred |

No test invents a bar to “repair” a refusal.

### D. Deterministic rerun

| Proposed test | Action | Expected outcome |
|---|---|---|
| `test_golden_pack_determinism` | `check_pack_determinism` on committed pack | `equal is True`; left checksum == right checksum |
| `test_year_shaped_pack_determinism` | build the same generated pack twice; session each | snapshot `integrity_checksum()` identical |

Equality is not a method and not HISTORICAL evidence.

### E. Snapshot / checksum change after one-value mutation

| Proposed test | Action | Expected outcome |
|---|---|---|
| `test_one_close_change_changes_checksum` | measure golden pack; copy; change only `obs_2024-01-03` close `100.25` → `100.26` and recompute payload checksum; measure again | both sessions MEASURED; checksums differ; changes become `("0.26", "-0.51")` |
| `test_unchanged_copy_keeps_checksum` | byte-copy the golden pack to a temp dir; measure both | checksums equal |

A one-value edit is a new snapshot. That is the rehearsal of the packet’s revision rule, still on SYNTHETIC bytes.

### F. Explicit probe of the exchange-calendar-completeness gap

Already documented in the decision packet §1.7 and `inspect_series`: “Missing bars are not invented. Exchange calendars are not applied.”

These tests must **prove the gap is still open**. They must not add a holiday table or a new refusal code.

| Proposed test | Action | Expected outcome |
|---|---|---|
| `test_gap_weekend_bar_is_not_calendar_refused` | golden pack plus a Saturday `2024-01-06T16:00:00-05:00` synthetic bar | series `valid`; no calendar/holiday reason code; MEASURED (4 observations, 3 changes). Document: Decision #4 says weekends produce no bar; software does not yet enforce that. |
| `test_gap_missing_weekday_is_not_flagged` | year-shaped weekday pack with one interior Wednesday omitted | series `valid`; no missing-session reason code; MEASURED with one fewer change. Document: Decision #4 says unexplained missing expected sessions must be flagged; software does not yet flag them. |
| `test_gap_weekday_holiday_shaped_bar_is_accepted` | insert a synthetic bar on a date the test *labels only in comments* as a full-market holiday weekday (do not fetch a holiday API; hard-code one civil date in the test comment, e.g. 2024-07-04, as a gap example) | series `valid`. Document: Decision #4 says full-market holidays produce no bar; software cannot know that. |

Pass language for F: `CALENDAR_GAP_STILL_OPEN`. Failure would be a new undocumented calendar refusal. Closing the gap would require a later Todd-authorized unit, not this rehearsal.

---

## Implementation boundary

`AUTHORIZE DRESS REHEARSAL TEST PLAN — TC` is recorded.

1. Add only the files listed above.
2. Do not edit `radar_v4/` production modules unless a test cannot construct `America/New_York` envelopes with current helpers — and then only `tests/helpers.py` or the test module.
3. Do not add Units 1401+.
4. Do not change `PHASE5_HIGHEST_UNIT` or root `README.md` unit lock.
5. Do not open HISTORICAL admission.
6. Keep `fixtures/synthetic_one_symbol_1d/` unchanged.

## Claim class

```text
MAXIMUM HONEST PASS      LOCAL FIXTURE/SYNTHETIC DRESS REHEARSAL PASSED WITH KNOWN GAPS
HISTORICAL DATA CORRECTNESS   NOT EARNED
METHOD VALIDITY               NOT DEFINED
USEFULNESS / EDGE             NOT SHOWN
HISTORICAL EVIDENCE           still false
```

This is not historical readiness, source validation, market-data correctness, predictive validity, or edge.

---

# NEXT DECISION REQUIRED FROM TODD

The authorized dress rehearsal has been implemented and run. Remaining HISTORICAL-source decisions stay on the decision packet: license review, source, and extract remain unauthorized.

This result is not:

- license review;
- a HISTORICAL source;
- an extract;
- movement of historical bytes;
- a vendor or API;
- Units 1401+;
- Phase 6.

---

## Results (2026-09-19)

Command: `PYTHONPATH=. python3 -m unittest tests.test_dress_rehearsal -v`

| Category | Tests | Result |
|---|---|---|
| A. Golden arithmetic | 5 | PASS |
| B. Full-year-shaped pack | 4 | PASS |
| C. Refusal / mutation | 8 | PASS |
| D. Deterministic rerun | 2 | PASS |
| E. One-value checksum mutation | 2 | PASS |
| F. Calendar-completeness gap probe | 3 | PASS (`CALENDAR_GAP_STILL_OPEN`) |
| **Dress-rehearsal total** | **24** | **24 passed, 0 failed** |

Full workshop suite after the same revision: `PYTHONPATH=. python3 -m unittest discover -s tests -v` → **341 passed, 0 failed**.

Exact measured stand-ins:

- golden `SYN:ONE` changes `("0.25", "-0.50")`;
- one-value mutation `100.25` → `100.26` changes `("0.26", "-0.51")` and a different snapshot checksum;
- existing UTC `SYN:AAA` pack still measures `("0.50", "-0.50")` and was not edited;
- `SYNTHETIC_WEEKDAY_SPAN` generated 261 Monday–Friday bars from `2024-01-02` through `2024-12-31`.

Known gaps still open (category F proved them; no holiday table was added):

- a Saturday `2024-01-06` bar is admitted and MEASURED;
- omitting Wednesday `2024-06-12` is not flagged;
- weekday `2024-07-04` is included by the weekday generator.

`radar_v4/` production modules were not edited. `PHASE5_HIGHEST_UNIT` was not moved. Units 1401+ were not created.

```text
MAXIMUM HONEST PASS      LOCAL FIXTURE/SYNTHETIC DRESS REHEARSAL PASSED WITH KNOWN GAPS
HISTORICAL DATA CORRECTNESS   NOT EARNED
METHOD VALIDITY               NOT DEFINED
USEFULNESS / EDGE             NOT SHOWN
HISTORICAL EVIDENCE           still false
```

This is not historical readiness, source validation, market-data correctness, predictive validity, or edge.

---

## Current disposition

```text
PLAN                            AUTHORIZED-TC AND IMPLEMENTED
CALENDAR_GAP_STILL_OPEN         YES
DATE_WINDOW_GAP_STILL_OPEN      YES
SESSION_DATE_COLLISION_GAP_STILL_OPEN  YES
DECIMAL_SPECIAL_VALUE_GAP_STILL_OPEN   YES
CLAIM                           LOCAL FIXTURE/SYNTHETIC DRESS REHEARSAL PASSED WITH KNOWN GAPS
HISTORICAL DATA CORRECTNESS     NOT EARNED
METHOD VALIDITY                 NOT DEFINED
USEFULNESS / EDGE               NOT SHOWN
HISTORICAL BYTES                NONE
SOURCE / LICENSE / EXTRACT      NOT AUTHORIZED
UNITS 1401+                     NOT CREATED
PHASE 6                         NOT OPENED
NEXT ACTOR                      TODD
```

> Research first. Evidence before machinery. Tools verify. Todd authorizes.

Learning and Earning It.  
Stay on course.  
No drift.
