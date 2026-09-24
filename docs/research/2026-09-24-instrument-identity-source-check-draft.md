# Radar V4 — Instrument Identity Source Check #001

**Date:** 2026-09-24
**State:** New educational source check under the coverage ledger; not the recovered original GM-001 lesson or its audit. No market-data download, observation, dataset admission, method, or Phase 9 claim.

## Retrieval outcome

A bounded repository search of default branches for `GM-001` and `IND-014` found no original lessons. Two early conversation-history retrieval attempts failed; a later retrieval returned summaries of the sequences but no full lesson text, audit, or durable original source link. A saved-file search did not identify an original lesson file. This establishes only that the original text was **not located by these checks**; it does not prove it never existed. The recovery draft's exact-text and completion claims remain unverified.

## First source-backed identity case: SPY

| Distinct object or measurement | What the source establishes | What must not be conflated |
|---|---|---|
| ETF share | [State Street's SPY fund page](https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy) identifies the State Street SPDR S&P 500 ETF Trust, ticker SPY, listed on NYSE Arca in USD; the page also lists a CUSIP and ISIN, each with a date-qualified listing table. | The ETF share is a tradable security. Its ticker alone is not a globally unique or timeless identifier. |
| Benchmark index | The fund page says the ETF seeks results generally corresponding, before expenses, to the S&P 500 Index. The [SEC ETF investor bulletin](https://www.sec.gov/investor/pubs/etfs.pdf) distinguishes an index-tracking fund from the index it follows. | The ETF's share price is not a level of the S&P 500 Price Return Index. Q-011 remains a different instrument/product question. |
| ETF official closing price | The State Street page labels its closing price as the ETF's official closing price reported by the primary listing exchange. | A third-party vendor's unadjusted `close` cannot be declared equivalent until the vendor specifies source, session, corrections, and corporate-action basis. |
| Fund NAV and bid/ask midpoint | The State Street page reports NAV and the closing bid/ask midpoint separately from the official closing price. The [SEC bulletin](https://www.sec.gov/investor/pubs/etfs.pdf) explains that ETF shares trade at market prices that may differ from NAV. | A midpoint, NAV, and official exchange close answer different questions, even when recorded for the same date. |

The fund page is a **primary fund/identity source**, not the selected price-feed license for Radar. Its current and historic page content may change; this record cites the page and the meanings, without copying a market-value series into the repository.

## Evidence still missing for one daily SPY observation

- Curriculum reconciliation with the original GM-001 lesson remains a separate open task; it does not itself select or qualify an SPY price source.
- A selected provider and applicable terms for the exact proposed dataset and retained raw response.
- Provider confirmation that `SPY` maps to this security and that its daily unadjusted close is the desired regular-session measurement.
- Timezone, completed-session publication cutoff, revision/correction behavior, and exact exchange-close versus consolidated-close semantics.
- A source-specific date-qualified identifier history; today's ticker/CUSIP/ISIN mapping alone does not establish all past dates.

## Generalization test before world coverage

Repeat this identity check separately for each instrument and jurisdiction: security/contract identity, benchmark or underlying, exchange or publisher, currency, effective dates, and the precise observed measure. If a cross-listed instrument, ADR, local share, future continuation, FX pair, or index variant fails one field, mark it UNKNOWN rather than carrying over an apparently similar U.S. mapping.

**Disposition:** SPY fund-versus-index and closing-price-versus-NAV distinctions are source-backed educational facts. GM-001 source recovery is OPEN; source-qualified real observation is HOLD. This note does not complete a lesson or change pilot authority.


## Second source-backed case: Japanese ordinary share versus U.S. ADS

[Toyota's corporate stock overview](https://global.toyota/en/ir/stock/outline/) identifies its Japanese securities code as `7203`, with Tokyo and Nagoya listings. Its [fiscal 2026 Form 20-F](https://global.toyota/pages/global_toyota/ir/library/sec/20-F_202603_final.pdf) identifies `TM` as the New York Stock Exchange trading symbol for American Depositary Shares (ADSs). Each ADS represents **ten** common shares under that filing; BNY Mellon operates the sponsored facility. The [SEC's ADR bulletin](https://www.sec.gov/files/investor/alerts/adr-bulletin.pdf) explains the general depositary-share structure and that such ratios vary by program.

| Same issuer, distinct security/market identity | Consequence for a future observation |
|---|---|
| Japanese ordinary share, code `7203` | A local share quote needs its Japanese venue, currency, date/session and share basis. |
| U.S. ADS, symbol `TM` | A U.S. quote needs its NYSE venue, USD, ADS unit and the date-effective ten-share ratio. |
| Issuer relationship | Same company exposure does not mean price equality or interchangeable daily closes. A comparison would additionally require synchronized market dates, FX basis, corporate-action treatment and source licensing; no such comparison is performed here. |

**Historical warning:** Toyota's filing describes five unsponsored ADS facilities on Nasdaq before the sponsored NYSE listing in September 1999. This record does not establish their historical share-per-ADS ratios. Never apply the present ratio or listing history to older observations without date-specific evidence. This is an educational identity distinction only; no Toyota price, FX rate or market feed was acquired or admitted.


## Third source-backed case: equity option contract versus underlying share

The [Options Industry Council's basics](https://www.optionseducation.org/optionsoverview/options-basics), published by OCC, defines an equity call/put by **underlying security, right, strike and expiration**. Standard contracts usually represent 100 shares; a quoted premium is on a per-share basis. The [OIC corporate-actions FAQ](https://www.optionseducation.org/referencelibrary/faq/splits-mergers-spinoffs-bankruptcies) explains that a split, merger or spinoff can change the deliverable and that OCC information memos describe specific adjustments.

| Distinct identity | Required before a future observation |
|---|---|
| Underlying share | Actual security identity and date-effective listing/corporate actions. A share price is not an option premium. |
| Option series | Clearing/venue product, option root, underlying, expiration, call/put right, strike, currency, exercise and settlement terms, premium multiplier, date-effective deliverable. |
| Adjusted contract | Exact OCC adjustment memo and effective date; do not assume the ordinary 100-share deliverable from a familiar ticker or strike. |

**Refusal example:** Two contracts showing the same underlying symbol and strike can have different roots and different deliverables after a corporate action. They cannot be treated as identical option observations without the exact series and adjustment state. No option quote, chain or market data was acquired here. Original GM-004 remains unrecovered.
