# Radar V4 — First 30-Session SPY Historical Extract Packet

```text
TO — Todd C.
FROM — ChatGPT (governance / coordination)
AUTHORITY — Todd C. only
RECORD TYPE — MINIMUM EXACT EXTRACT PACKET
DATE — 2026-09-19
STATUS — DRAFTED / NOT AUTHORIZED FOR EXTRACT
SOURCE — Twelve Data (TEMPORARY only; Todd-authorized for this cycle)
BANKED HARDENING SHA — 6662e28e15942894eb6bf3fb9476aecd6877c4ff
BANKED PRE-EXTRACT STATE SHA — 7bef28443ec3ab2ab7087a7883c72143197a4f03
APPROVED HISTORICAL MEASUREMENT ENTRY POINT — run_dataset_session(...)
CLAIM CEILING — LEVEL 0 — MEASURED
```

This packet freezes the exact bounds and controls for a proposed first real-data learning cycle. Todd separately authorized Twelve Data as the **temporary source only** for this one 30-session SPY cycle on 2026-09-19. That source authorization does **not** authorize an account, API key, purchase, API call, historical extract, market bytes, vendor client, Units 1401+, Phase 6, prediction, signals, edge, paper trading, or live trading.

**Tools verify. Todd authorizes.**

---

## 1. Purpose

The proposed cycle exists only to test whether one bounded real historical dataset can be admitted, checked, frozen, and measured through Radar V4's already-banked controlled session path.

It is **not**:

- a method test;
- a prediction test;
- an edge test;
- a trading-system test;
- a full-year research cycle;
- a permanent vendor selection;
- a production deployment.

---

## 2. Frozen instrument identity

| Field | Frozen value |
|---|---|
| Security | State Street SPDR S&P 500 ETF Trust |
| Ticker | SPY |
| Asset class | ETF |
| Primary listing identity | NYSE Arca |
| MIC | ARCX |
| CUSIP | 78462F103 |
| ISIN | US78462F1030 |

Vendor metadata may be used as supporting identity evidence, but must not override the frozen durable identity above if the vendor catalog contains a conflicting field.

The previously observed Twelve Data SPY catalog CUSIP conflict remains a warning: vendor catalog CUSIP is not trusted as the controlling identity field.

---

## 3. Frozen historical slice

Calendar boundary:

```text
START  2024-11-18
END    2024-12-31
```

Expected completed session count:

```text
30
```

Exact expected session-date manifest, America/New_York:

```text
2024-11-18
2024-11-19
2024-11-20
2024-11-21
2024-11-22
2024-11-25
2024-11-26
2024-11-27
2024-11-29
2024-12-02
2024-12-03
2024-12-04
2024-12-05
2024-12-06
2024-12-09
2024-12-10
2024-12-11
2024-12-12
2024-12-13
2024-12-16
2024-12-17
2024-12-18
2024-12-19
2024-12-20
2024-12-23
2024-12-24
2024-12-26
2024-12-27
2024-12-30
2024-12-31
```

Known weekday closures excluded:

```text
2024-11-28  Thanksgiving
2024-12-25  Christmas
```

Known early-close sessions retained as valid completed sessions:

```text
2024-11-29
2024-12-24
```

This is a bounded frozen manifest, not a general exchange-calendar engine.

---

## 4. Proposed vendor request bounds

Twelve Data is now Todd-authorized as the temporary source for this cycle only. If Todd later separately authorizes the extract, the request must be bounded to:

```text
endpoint             /time_series
symbol               SPY
type                 ETF
interval             1day
start_date           2024-11-18
end_date             2024-12-31
adjust               none
order                asc
format               JSON
previous_close       false
prepost              false
timezone             exchange-local semantics for 1day
mic_code             ARCX REQUIRED — if the request shape cannot constrain ARCX, STOP before any historical-series call
purpose              admission / measurement validation only
```

No intraday request is authorized by this packet.

Daily provider timestamps must be interpreted as exchange-local session dates, not as required 16:00 close-clock timestamps. ARCX is a hard identity constraint for this cycle: if the chosen request shape cannot constrain ARCX, or if returned metadata cannot verify ARCX consistently with the frozen identity, STOP. Do not silently widen to another SPY-labeled listing or venue.

---

## 5. Vendor-call ceiling

For the first cycle:

```text
MAX VENDOR DATA CALLS FOR THE HISTORICAL SERIES = 1
MAX SYMBOLS                                 = 1
SYMBOL                                      = SPY
MAX EXPECTED UNIQUE SESSION DATES           = 30
```

The purpose of the one-call ceiling is to prevent accidental expansion, repeated exploratory pulls, and silent mixing of multiple vendor responses.

If the call fails, truncates, returns malformed data, or produces an unresolved identity/adjustment problem, stop. A retry requires a new explicit operational decision; do not silently fetch again.

Metadata-only checks that do not return historical price series are outside the historical-series-call count only if separately authorized. This packet itself authorizes none.

---

## 6. Row ceiling and completeness gate

The first real cycle has two separate controls:

### 6.1 Unexpected-row refusal

Only dates in the exact 30-session manifest may be admitted.

Any other session date is refused as:

```text
SESSION_DATE_NOT_IN_MANIFEST
```

### 6.2 Expected-row completeness

Before any measurement may be treated as the first historical-cycle result:

```text
EXPECTED UNIQUE SESSION DATES = 30
ACTUAL UNIQUE ADMITTED SESSION DATES = 30
```

and:

```text
ACTUAL SESSION-DATE SET == EXPECTED SESSION-DATE SET
```

If any expected session is absent:

```text
NO LEVEL 0 MEASUREMENT CLAIM
DISPOSITION = INSUFFICIENT_EVIDENCE
```

No missing bar may be synthesized, forward-filled, interpolated, or silently bridged.

This packet therefore converts missing-row completeness from an acknowledged open global gap into a hard control for this one bounded cycle.

---

## 7. Authorized execution path

For this first historical cycle, the only authorized measurement entry point is:

```text
run_dataset_session(...)
```

The historical-cycle audit artifact must record:

```text
measurement_entry_point = run_dataset_session
```

Bare direct use of:

```text
close_to_close_changes(...)
```

is not an authorized historical-cycle path because it does not independently enforce session-date collision detection.

This is a bounded execution rule, not a claim that the bare helper has been globally hardened.

---

## 8. Banked admission controls

At banked SHA:

```text
6662e28e15942894eb6bf3fb9476aecd6877c4ff
```

the controlled session path has banked evidence for:

- symbol mismatch refusal;
- interval mismatch refusal;
- transformation-version mismatch refusal;
- exact duplicate timestamp refusal;
- bounded expected-session manifest refusal;
- 1day same-session-date collision refusal;
- NaN / Infinity / -Infinity refusal via `NON_FINITE_CLOSE`;
- deterministic ordering;
- LEVEL 0 claim ceiling only on valid descriptive measurement.

The global exchange-calendar gap remains open outside the bounded manifest.

---

## 9. Adjustment rule

Requested adjustment:

```text
adjust=none
```

Radar declaration identity:

```text
UNADJUSTED
```

The request parameter alone does not prove vendor adjustment semantics.

The first cycle must record:

```text
ADJUST_NONE_REQUESTED = YES
ADJUSTMENT_SEMANTICS_EMPIRICALLY_PROVEN = NO / UNCLEAR
```

unless evidence from the returned dataset and independent reference can actually establish the distinction.

The known 2024-12-20 distribution boundary must not be misrepresented as proving `none` versus `splits`.

If adjustment semantics become materially inconsistent with the frozen ruler:

```text
INVALID_COMPARISON or UNCLEAR
```

No silent reinterpretation.

---

## 10. Private-storage and public-repository rule

Repository status has been independently checked and is:

```text
PUBLIC
```

Therefore the following must never be committed to this repository:

- raw Twelve Data JSON;
- CSV/JSON OHLCV rows;
- raw close series;
- reconstructable close-to-close series;
- a seed close plus differences that reconstruct the vendor series;
- API keys or credentials;
- vendor-data-bearing backups;
- screenshots or examples containing the actual vendor price series.

Permitted public-repo artifacts are limited to non-price governance material, code, synthetic fixtures, non-reconstructable metadata, and documentation that does not redistribute vendor Data.

The actual vendor response, if later authorized, must remain in a private local location outside the public repository.

Mechanical safeguards now back this policy: `.gitignore` excludes designated vendor-data and credential paths, and `radar_v4.public_repo_guard.scan_public_repo(...)` is exercised by `tests/test_public_repo_guard.py` to fail on forbidden vendor-data locations, credential-like filenames, vendor-data-shaped CSV/JSON names, or obvious embedded secret assignments. These are defense-in-depth controls, not permission to store real vendor data inside an ignored directory; real vendor bytes remain outside the repository root.

Repository privacy may be changed separately by Todd, but this packet does not depend on a privacy change so long as no vendor Data enters the public repository.

---

## 11. Snapshot / checksum rule

If an extract is later authorized:

1. Save the original vendor response privately and unchanged while retention terms permit.
2. Compute a SHA-256 checksum of the exact acquired artifact at acquisition time.
3. Never silently overwrite that artifact.
4. Any later authorized re-fetch is a new version, not a replacement.
5. Record the software commit and transformation version used for admission and measurement.

Important license caveat:

Whether a SHA-256 **of the raw vendor extract** may be retained after required deletion of the underlying Data remains unresolved in the public-terms review.

Therefore do not claim permanent post-deletion retention rights for the raw-extract checksum until that point is resolved.

---

## 12. Retention / deletion rule

Public-terms review disposition remains:

```text
LICENSE FIT = PASS WITH CONDITIONS
```

For the proposed private internal cycle:

- local storage only;
- no redistribution;
- no public vendor Data;
- credentials private;
- raw Data subject to subscription-term/documentation limits;
- after termination or expiration, all vendor Data must be deleted promptly and no later than the documented 30-day outer bound;
- retained Derived Data must be non-reconstructable;
- permanent raw archive is not assumed.

No license review is a license grant.

---

## 13. Measurement definition

Primary metric:

```text
close[t] - close[t-1]
```

Interpretation:

ordinary descriptive close-to-close difference only.

Claim ceiling:

```text
LEVEL 0 — MEASURED
```

Allowed result language:

```text
MEASURED
INSUFFICIENT_EVIDENCE
INVALID_COMPARISON
UNCLEAR
```

Not authorized as claims:

- prediction;
- signal;
- threshold;
- ranking;
- percent-return method;
- edge;
- regime claim;
- trading rule;
- paper-trading readiness;
- live-trading readiness.

---

## 14. Stop conditions

Stop before measurement if any of the following occurs:

- source identity unresolved;
- returned symbol/listing identity inconsistent with frozen SPY identity;
- unexpected session date appears;
- fewer than all 30 expected session dates are admitted or the actual admitted session-date set differs from the frozen 30-date manifest;
- more than one distinct 1day timestamp resolves to the same session date;
- duplicate exact timestamp is present;
- close is NaN / Infinity / -Infinity;
- interval is not 1day;
- timezone/session semantics are inconsistent;
- transformation version mismatches;
- adjustment semantics become materially inconsistent with the frozen ruler;
- raw/reconstructable vendor Data would need to enter the public repository;
- vendor request exceeds the authorized call/row/symbol bounds;
- any required field is ambiguous enough that proceeding would require guessing.

Do not repair, interpolate, average, infer, or silently widen scope.

---

## 15. What this packet does not close

Even if this packet is later authorized and the bounded cycle succeeds, the following remain open:

- general exchange-calendar completeness;
- global missing-session detection beyond the frozen manifest;
- bare `close_to_close_changes(...)` session-date collision enforcement;
- long-history source stability;
- vendor historical revision behavior;
- permanent source adequacy;
- full-year 2024 correctness;
- method validity;
- usefulness;
- edge;
- prediction;
- paper/live trading.

---

## 16. Authorization gates after this packet

This packet is drafted only.

The next gates remain separate:

### Gate A — temporary source authorization — CROSSED

Todd issued:

```text
AUTHORIZE TWELVE DATA AS TEMPORARY SOURCE ONLY
FOR THE FIRST 30-SESSION SPY HISTORICAL LEARNING CYCLE — TC
```

This authorizes the source choice only. It does not authorize account creation, API key creation, purchase, an API call, an extract, or market bytes.

### Gate B — account / key / purchase if required

Must be explicitly authorized if needed. Do not infer from source authorization.

### Gate C — bounded historical extract

Must separately name the exact symbol, dates, interval, adjustment request, call ceiling, and row/session ceiling.

No source or extract is authorized merely because this packet exists.

---

## 17. Current state

```text
PRE-EXTRACT TEST DESIGN                COMPLETED FOR CURRENT BOUNDED SCOPE
MINIMUM PRE-EXTRACT HARDENING          BANKED — PASS WITH CAVEAT
BANKED SHA                             6662e28e15942894eb6bf3fb9476aecd6877c4ff
FULL SUITE AT PRE-EXTRACT STATE        377 / 377
CATALOG AUDIT                          VALID

EXACT EXTRACT PACKET                   DRAFTED
TWELVE DATA TEMPORARY SOURCE           AUTHORIZED — THIS 30-SESSION CYCLE ONLY
ACCOUNT / API KEY / PURCHASE           NOT AUTHORIZED
HISTORICAL EXTRACT                     NOT AUTHORIZED
MARKET BYTES                           NONE
UNITS 1401+                            NOT AUTHORIZED
PHASE 6                                OUT OF SCOPE — NOT OPENED
```

**Research first. Evidence before machinery. Inventory before ingestion. Learning and Earning It. Stay on course. No drift.**
