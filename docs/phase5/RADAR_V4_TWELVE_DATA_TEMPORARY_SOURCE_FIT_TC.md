# Radar V4 — Temporary Twelve Data Source-Fit Review

```text
TO — Todd C.
FROM — Cursor (bounded implementer)
AUTHORITY — Todd C. only
RECORD TYPE — READ-ONLY TEMPORARY SOURCE-FIT REVIEW
DATE — 2026-09-19
CANDIDATE — Twelve Data (TEMPORARY only)
TERMS REVIEWED — https://twelvedata.com/terms  (Last updated: January 1, 2026)
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4  (PUBLIC)
```

This is a public-documentation review. It does not download market bytes, create an API key, add a vendor client, modify production `radar_v4` modules, authorize a license, authorize a source, authorize an extract, create Units 1401+, or open Phase 6.

**Availability is not authorization.**

A temporary source does not have to be the permanent archive source. Retention limits are not hidden.

**Tools verify. Todd authorizes.**

---

## Frozen ruler under review

| Item | Frozen requirement |
|---|---|
| Security | State Street SPDR S&P 500 ETF Trust; SPY; NYSE Arca primary listing; CUSIP `78462F103`; ISIN `US78462F1030` |
| Window | `2024-01-01` through `2024-12-31` |
| Interval | `1d` |
| Session convention | `America/New_York` |
| Adjustment | `UNADJUSTED` |
| Metric | `close[t] - close[t-1]` |
| max_staleness | `NONE` |
| Repository | PUBLIC |

---

## Sources read (public pages only)

- Terms of Use, last updated 2026-01-01: https://twelvedata.com/terms
- Time series API: https://twelvedata.com/docs/llms/market-data/time-series.md
- ETF catalog: https://twelvedata.com/docs/llms/asset-catalogs/etf-list.md
- Earliest timestamp: https://twelvedata.com/docs/llms/discovery/earliest-timestamp.md
- Historical prices FAQ (2026-01-12): https://support.twelvedata.com/en/articles/5656039-how-to-get-historical-prices
- Are prices adjusted? (2025-05-04): https://support.twelvedata.com/en/articles/5179064-are-the-prices-adjusted
- US equities (2026-08-18): https://support.twelvedata.com/en/articles/9935903-us-equities-market-data
- EOD pricing (2026-08-18): https://support.twelvedata.com/en/articles/12682324-end-of-day-eod-pricing-market-data
- Commercial and personal usage (2026-08-04): https://support.twelvedata.com/en/articles/5332349-commercial-and-personal-usage
- Attribution guidelines (2026-01-12): https://support.twelvedata.com/en/articles/12647398-attribution-guidelines-for-using-twelve-data
- Public SPY product page (no API call): https://twelvedata.com/markets/568728/etf/nyse/spy

No `/time_series` call was made. No API key was created.

---

# A. Source-fit matrix

Classifications: `PASS` / `PASS WITH CONDITION` / `UNRESOLVED` / `FAIL`.

## TECHNICAL FIT

| # | Item | Class | Evidence / condition |
|---|---|---|---|
| 1 | SPY / ETF historical EOD support | PASS WITH CONDITION | Public catalog and market page list `SPY` as an ETF. US historical/EOD is documented from the Basic plan and is described as covering 100% of US trading volume (distinct from the ~5% real-time default feed). Condition: no live extract was run; listing name is `NYSE` not `NYSE Arca`. |
| 2 | Exact 2024 date-range support | PASS WITH CONDITION | `/time_series` documents inclusive `start_date` + `end_date`. Daily history is described as complete since first trade for most symbols. A 2024 window is far below the 5000-row cap. Condition: `/earliest_timestamp` was not queried; confirm 2024 coverage at extract time. |
| 3 | `1d` bars | PASS | Documented interval value is `1day`. |
| 4 | Raw / unadjusted close | PASS WITH CONDITION | Current API documents `adjust=none`. Default is `splits`. A 2025-05-04 FAQ still says daily/weekly/monthly prices are split-adjusted. Condition: any later extract must request `adjust=none` and verify the returned closes are unadjusted. |
| 5 | Explicit `adjust=none` capability | PASS WITH CONDITION | Current time-series docs: `adjust` ∈ {`all`,`splits`,`dividends`,`none`}, default `splits`. Condition: same stale-FAQ conflict as #4. |
| 6 | Daily timezone / session-date semantics | PASS WITH CONDITION | For `1day`, `timezone` is ignored. `datetime` is “local exchange time referring to when the bar … was opened.” EOD samples use a date-only stamp (`YYYY-MM-DD`), not a 16:00 close timestamp. Condition: treat the daily `datetime` as the exchange session date, not a close clock. |
| 7 | America/New_York / exchange-local | PASS WITH CONDITION | US stock default location is where the exchange is located (`America/New_York` in docs/examples). `meta.exchange_timezone` is documented. The public SPY page states America/New_York. Condition: do not rely on passing `timezone=America/New_York` for `1day`; it is ignored. |

## LICENSE FIT

| # | Item | Class | Evidence / condition |
|---|---|---|---|
| 9 | Local persistent storage rights | PASS WITH CONDITION | Terms §2.2(a) permit store for Internal Use during the subscription term. §2.3(g) forbids storing/caching beyond timeframes in the Documentation. Historical FAQ tells users to cache once and update later, but no numeric historical TTL was found. §16.1 limits retention to subscription duration, regulatory need, or third-party rules. |
| 10 | Organizational internal research / development | PASS WITH CONDITION | Individual plans (Basic/Grow/Pro/Ultra) allow personal or internal use, including organizational internal tools, academic research, and non-production development. Free/Basic commercial use is forbidden (§2.3(l); Free Trial §5.6). Paid individual internal research is the documented path. Business plans are for commercial display. |
| 11 | Raw-data redistribution restrictions | PASS WITH CONDITION | Redistribution is any publication, distribution, or provision of Data to third parties. Individual plans forbid redistribution and commercial third-party display. Redistribution requires a Redistribution Rights Add-On or a separate written agreement (`sales@twelvedata.com`). |
| 12 | Public-GitHub restrictions | FAIL (for raw Data in this repo) | This repository is public. Committing Twelve Data OHLCV, reconstructable closes, or an API key would be publication to third parties. Docs forbid exposing API keys in public repositories. Attribution is required for public display and is not a redistribution license. Internal/private use needs no attribution. Raw extract must stay off this public repo. |
| 17 | Account / plan requirement | PASS WITH CONDITION | An Account and API key are required. US historical/EOD is documented as available from Basic. ISIN/CUSIP request parameters require a Data add-on. FIGI request parameter requires Ultra (individual) or Enterprise (business). `/profile` starts at Grow / Venture. One trial page still says Basic lacks “deep historical data”; that phrase is not reconciled against the US-EOD Basic statement. |
| 18 | Sales / custom contracting | PASS WITH CONDITION | Not required for internal US historical/EOD on a standard plan. Sales/custom terms are required for redistribution, white-label, full-market real-time, or custom SLA. Contact points: `sales@twelvedata.com`, `legal@twelvedata.com`. |

## AUDIT / RETENTION FIT

| # | Item | Class | Evidence / condition |
|---|---|---|---|
| 8 | Security / exchange identity metadata | PASS WITH CONDITION | Catalog fields include symbol, name, currency, exchange, `mic_code`, country, FIGI, ISIN, CUSIP. Public ETF example: `SPY`, `SPDR S&P 500 ETF Trust`, exchange `NYSE`, `mic_code` `ARCX` (NYSE Arca), ISIN `US78462F1030`. Condition: the same official example lists CUSIP `037833100` (Apple), which does not match frozen CUSIP `78462F103`. Name omits “State Street”. Exchange label is `NYSE`, not “NYSE Arca”. Do not trust catalog CUSIP until independently confirmed. |
| 13 | Subscription-termination deletion | PASS (obligation is explicit) | Terms §12.5: access ends; Customer must delete all Data. §16.2: all Data must be deleted within 30 days of termination or expiration; certification of deletion required if requested. Audit-trail data may be retained for compliance. **Raw Twelve Data bytes cannot be kept as a permanent archive after the subscription ends.** |
| 14 | Derived-data retention restrictions | PASS WITH CONDITION | Derived Data is data that cannot be reverse-engineered to the underlying Data. Customer retains rights to compliant Derived Data (§6.2). Creating derivative works for redistribution is prohibited (§17.1(g)). Close-to-close differences stored with raw closes reconstruct the series. Whether MEASURED differences without raw closes may be retained after deletion is UNRESOLVED and is a later license question, not a production-code change. |
| 15 | Corrections / revisions behavior | UNRESOLVED | EOD docs mention unconfirmed then confirmed daily prices. No public extract-version ID, correction-linkage field, or immutable historical-revision API was found. Terms provide Data AS IS and allow Twelve Data to modify or remove Data. Radar’s later gate still applies: a later file is a new version, never an in-place overwrite. |
| 16 | Freeze / checksum one bounded extract | PASS WITH CONDITION | A local snapshot can be checksummed by existing Radar workshop software after a later authorized extract. The vendor does not document freeze-before-measurement or an immutable extract handle. A later re-fetch may differ. |

---

## Fit summaries

```text
TECHNICAL FIT          PASS WITH CONDITION
LICENSE FIT            PASS WITH CONDITION for temporary internal local use
                       FAIL for raw Data on this public GitHub repo
AUDIT / RETENTION FIT  PASS WITH CONDITION
                       raw Data must later be deleted if the subscription ends
```

This is not HISTORICAL DATA CORRECTNESS, METHOD VALIDITY, USEFULNESS, or EDGE.

---

# B. Hard blockers

None that forbid naming Twelve Data as a **temporary** candidate for a later, separately authorized, local, bounded first cycle.

Hard blockers for **this public repository** and for **permanent archive** use:

1. Raw Twelve Data, reconstructable OHLCV, and API keys must not be committed to this public GitHub repo.
2. Twelve Data is not a keep-forever archive. On termination or expiration, **all Data must be deleted within 30 days**. If Todd requires a permanent raw archive that survives vendor off-boarding, Twelve Data fails that permanent-archive requirement.

Those are use-path blockers. They are not hidden.

---

# C. Temporary-use limitations

- License is limited, revocable, and subscription-term only.
- Internal use only on individual plans. No redistribution. No commercial third-party display.
- Free/Basic commercial use is forbidden.
- **If the subscription ends, raw Data must be deleted within 30 days.** Certification may be required.
- Derived-data keep is only for values that cannot reconstruct the original series.
- Default prices are split-adjusted. `adjust=none` must be explicit and later verified.
- Daily `timezone=` is ignored. Session date is exchange-local, not a 16:00 stamp.
- Catalog CUSIP in the official SPY example is not trustworthy.
- Exchange is labeled `NYSE` with MIC `ARCX`.
- Vendor may change or remove Data. Re-fetch is not the same extract.
- No documented vendor freeze / correction-linkage handle.
- ISIN/CUSIP query parameters need a Data add-on; FIGI query needs a higher plan.
- Attribution is required if any Twelve Data is displayed publicly; attribution is not a redistribution license.

No architecture change is recommended.

---

# D. Fields / settings we would eventually request

Only if Todd later authorizes a source **and** a separate extract. Not a request now.

```text
endpoint           /time_series
symbol             SPY
type               ETF
mic_code           ARCX
country            United States
interval           1day
adjust             none
start_date         2024-01-01
end_date           2024-12-31
order              asc
format             JSON
previous_close     false
prepost            false
timezone           Exchange   (ignored for 1day; expect America/New_York session dates)
```

Identity cross-check, still without downloading a price series until extract is authorized:

```text
/etf?symbol=SPY&mic_code=ARCX
expected name      SPDR S&P 500 ETF Trust / State Street SPDR S&P 500 ETF Trust
expected isin      US78462F1030
expected cusip     78462F103   (do not accept catalog 037833100)
expected mic       ARCX
/earliest_timestamp?symbol=SPY&interval=1day&mic_code=ARCX
```

Do not put the response bytes in this public repository.

---

# E. Temporary first-historical-source verdict

```text
CAN TWELVE DATA SERVE AS A TEMPORARY FIRST HISTORICAL SOURCE?
  YES — WITH CONDITIONS — SUBJECT TO LATER TODD AUTHORIZATIONS

NOT AUTHORIZED NOW
NOT A PERMANENT ARCHIVE
NOT A PUBLIC-REPO DATA FEED
```

Technical shape (one US ETF, `1day`, dated window, explicit `adjust=none`, exchange-local daily dates) is documented well enough to remain a temporary candidate.

License and retention allow temporary **local internal** research use on an eligible plan, and require deletion of raw Data after the subscription ends.

This review does not authorize Twelve Data.

---

# F. Still required before an extract could be authorized

1. Todd license review of these terms (this file is not that review).
2. Todd source authorization (separate sentence).
3. Account/plan decision. Do not create a key in this public repo.
4. Written local-only storage rule: extract stays off GitHub; no reconstructable closes in the public tree.
5. Written deletion/off-boarding rule: raw Data deleted within 30 days if the subscription ends.
6. Confirm `adjust=none` versus the stale split-adjusted FAQ.
7. Confirm SPY identity (ISIN `US78462F1030`, CUSIP `78462F103`, MIC `ARCX`) without trusting the catalog CUSIP example.
8. Confirm 2024 daily coverage via `/earliest_timestamp` only after extract/source authorization, or as a later bounded identity probe Todd separately authorizes.
9. Packet later gates still closed: extract-class authorization; hard extract bounds; immutable first extract / new-version revision; freeze-before-measurement; correction linkage.
10. No vendor/API/client. No Units 1401+. No Phase 6. No HISTORICAL admission change.

---

# NEXT DECISION REQUIRED FROM TODD

This review is complete. Remaining decisions stay unauthorized: license review, source, extract, account/key, and historical bytes.

```text
CANDIDATE                       TWELVE DATA — TEMPORARY ONLY
TECHNICAL FIT                   PASS WITH CONDITION
LICENSE FIT                     PASS WITH CONDITION (local internal)
PUBLIC-REPO RAW STORAGE         FAIL
RETENTION                       DELETE RAW DATA WITHIN 30 DAYS AFTER END
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
