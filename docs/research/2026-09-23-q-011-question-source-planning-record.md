# Q-011 — Research question and source-planning record

**Recorded:** 2026-09-23  
**Q-011 M0:** closed for question definition  
**Q-011 M1:** in progress; no dataset admitted

This record carries Q-011 research-gate decisions into Radar V4 documentation. It is a decision and provenance record, not a dataset, result, market method, or authority to run one.

## M0 — locked question

For the daily **S&P 500 Price Return Index** over the primary **2014–2023** calendar span, compare the next trading day's simple return after a positive day-`t` simple return with the next trading day's simple return after a negative day-`t` simple return. The primary metric is the **difference in group means** of those next-day returns.

- Unit: an eligible day-`t` to immediately following trading-day `t+1` pair.
- Groups: `r[t] > 0` and `r[t] < 0`, where `r[t]` is the index-level simple return.
- Outcome: `r[t+1] = (P[t+1] / P[t]) - 1` for index level `P`.
- Zero-return day-`t` observations: exclude from both sign groups and report their count.
- The 2023 calendar year is the selected historical endpoint; 2024 onward is reserved from this primary span.
- Claim ceiling: descriptive comparison only. No predictive, causal, profitability, trading, or edge claim follows from this question.

M0 closure locks the question before data acquisition. It does not assert an observed difference, sample count, or result. Product-specific trading-calendar and boundary handling still require documentation before calculation.

## M1 — source and product state

| Item | Decision or status |
|---|---|
| Primary source class | **S-001 — S&P Dow Jones Indices direct**, declared conditionally |
| Alternative source candidate | Alpha Vantage `SPX` held for unresolved exact Price Return identity, lineage, date semantics, and custody |
| Priority access path | **SPICE Advanced Download**, selected for product-level verification, not qualified |
| SPICE product qualification | **HOLD** |
| Entitlement and license evidence | Not verified for Q-011 |
| Historical data | None acquired or admitted for Q-011 |

To qualify an actual product, verify the exact S&P 500 Price Return series and export fields; daily 2014–2023 entitlement and complete delivery; observation-date, timezone, and correction semantics; and the applicable rights to retain the original export, custody record, and derived records. General product literature does not establish a specific subscription's rights. The [S&P 500 index page](https://www.spglobal.com/spdji/en/indices/equity/sp-500/), [SPICE brochure](https://www.spglobal.com/spdji/es/documents/additional-material/spice-brochure.pdf), and [SPICE data-availability FAQ](https://www.spglobal.com/spdji/en/contentAsset/raw-data/0c0154fd-a35a-4fdd-adad-20184e4b0722/fileAsset/) are public supporting materials, not qualification evidence for Q-011.

The evidence route is to review applicable authorized subscription and agreement records, if they exist, then obtain specific S&P DJI documentation for unresolved product questions under a separate decision. This public repository must not contain credentials, contracts, or licensed market data.

## 2026-09-24 public product-evidence check

| Claim checked | Provider evidence | Gate result |
|---|---|---|
| Public index variant identity | On the [S&P 500 index page, Data → Tickers](https://www.spglobal.com/spdji/en/indices/equity/sp-500/), S&P DJI lists **Price Return** as Bloomberg ticker **SPX**, Reuters **.SPX**, and ISIN **US78378X1072**, separately from Total Return **SPXT** and Net Total Return **SPTR500N**. The page displays the USD Price Return variant. | **Public variant identity located.** The SPICE product/series key, exact export field, and account entitlement are still unverified. |
| SPICE product capability | The [SPICE brochure](https://www.spglobal.com/spdji/es/documents/additional-material/spice-brochure.pdf) describes Advanced Download for index-level data and adjustable frequency/period, and describes S&P 500 index-level history dating to 1928. | **General capability located.** This does not establish the exact Price Return export, complete daily 2014–2023 rows, or this account's entitlement. |
| Account-specific scope | The [SPICE subscription and licensing FAQ](https://www.spglobal.com/spdji/en/contentAsset/raw-data/67b43edf-1f23-414a-a922-8259432cb26d/fileAsset/) says subscriptions vary by indices, data type and historical depth, and directs a subscriber to confirm their coverage. | **HOLD.** No account-specific scope was reviewed. |
| Storage and use | The [S&P DJI general disclaimer](https://www.spglobal.com/spdji/en/disclaimers/?indexes=) restricts storing, reproducing and distributing content without prior written permission. | **HOLD.** A relevant agreement or written authorization must establish permitted private retention, research use and derived-record handling. A public download description is not permission. |

**Qualification checklist, in order:** (1) map the public S&P 500 Price Return identity (SPX) to the exact SPICE series/product key and reject total-return variants; (2) index-level daily closing field, calendar/date and timezone meaning, corrections and revision behavior; (3) account entitlement to the complete 2014–2023 span and export format; (4) written rights for the proposed raw-export custody and derived descriptive research records. Keep contracts, account identifiers, credentials and licensed observations outside this public repository. After those checks pass, separately decide whether to acquire and admit one provenance-complete artifact under the controlling gates.

**Disposition:** S-001 direct and SPICE Advanced Download remain conditional selections for investigation. M1 product qualification remains **HOLD**; no Q-011 data, calculation, Phase 6 work or live operation was authorized by this public evidence check.

## 2026-09-24 alternative-source screen (no source switch)

- **Alpha Vantage — targeted candidate / HOLD.** The [official API documentation](https://www.alphavantage.co/documentation/) now names a premium `INDEX_DATA` endpoint with `symbol=SPX`, `interval=daily`, and decades of S&P 500 index OHLC history. This is a closer candidate than applying its equity `TIME_SERIES_DAILY` endpoint to an index. The [premium page](https://www.alphavantage.co/premium/) says historical index data requires a separate personal-use entitlement process; [terms](https://www.alphavantage.co/terms_of_service/) distinguish personal and commercial uses. Still unverified: exact Price Return lineage to S&P DJI, 2014–2023 daily completeness, correction semantics, private retention/derived-output rights, and any future Triton commercial use. No API call or purchase made.
- **Massive Indices Custom Bars — reject for Q-011 period.** Its [published endpoint documentation](https://massive.com/docs/rest/indices/aggregates/custom-bars) says index aggregate records start **February 14, 2023**. That cannot supply Q-011's full 2014–2023 daily primary span even if a plan advertises “all history.” This finding is limited to that documented product.

**Decision:** S-001 direct remains the declared conditional primary source class. Alpha Vantage `INDEX_DATA` is a specific alternative to qualify if the direct path is unavailable or unsuitable. Neither candidate is data-qualified, and Q-011 M1 remains HOLD. Do not substitute an ETF or shorten the locked period to make a source fit.

## Separation from other Radar V4 work

Q-011 concerns the **S&P 500 Price Return Index, 2014–2023**. Closed, unmerged [PR #38](https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/38) concerned a separate bounded **SPY** historical learning cycle and remains preserved as historical evidence. Its source authorization, scope, code, and proposed extract do not transfer to Q-011.

This record does not authorize historical admission, a vendor client or API call, Phase 6 method research, backtesting, a signal, a claim of edge, or trading. The canonical [Radar V4 methodology](../methodology/RADAR_V4_METHODOLOGY_DEFINITION_TC.md) controls later gates. A question-definition record is not a method or an evaluation.

## Decision provenance

The following named Q-011 research-gate decisions were recorded on 2026-09-23:

- **M0 Research Question Gate Closure Audit #001:** question definition closed.
- **M1 Source Selection Decision #001:** S-001 declared as the conditional primary source class.
- **M1 S-001 Access Path Selection Decision #001:** SPICE Advanced Download prioritized for verification.
- **M1 SPICE Product Qualification Decision #001:** product qualification held for missing evidence.

This record preserves those stated decisions; it does not claim that a vendor agreement, export, or independent data audit exists.
