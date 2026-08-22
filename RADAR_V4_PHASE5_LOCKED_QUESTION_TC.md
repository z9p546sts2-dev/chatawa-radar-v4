# Radar V4 Phase 5 — Locked Question

**Authorization:** `AUTHORIZE PHASE 5 — TC`  
**Date:** 2026-08-22  
**Trading method defined:** No  
**Vendor API authorized:** No  
**Live data authorized:** No

## Locked question

> In one declared daily dataset for one symbol, what are the ordinary close-to-close differences when every observation uses the same interval, timezone, and transformation version?

## Locked comparison

Ordinary variation of close-to-close **difference** (not percent, not a score) on the admitted series, ordered by market timestamp.

## Primary metric

`close[t] - close[t-1]` as a decimal string.

## Unit of observation

One daily bar for one symbol, attached to an evidence envelope.

## In-scope universe / period

One symbol. One interval: `1d`. One timezone, declared. No second asset class.

## Explicit non-goals

- prediction;
- entry/exit;
- thresholds;
- ranking;
- edge;
- paper trading;
- a purchased market-data API;
- using SYNTHETIC values as HISTORICAL performance.

## Allowed result language

`MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`.

`NO EDGE SHOWN` is not applicable because no edge was asked.

## Claim level available now

`LEVEL 0 — MEASURED` only.

Software tests may use `FIXTURE` or `SYNTHETIC` payloads. Those results are not market evidence. A `HISTORICAL` series may be admitted only when the records truly are historical and the dataset declaration says so.
