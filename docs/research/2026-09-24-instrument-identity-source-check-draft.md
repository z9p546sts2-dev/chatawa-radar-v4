# Radar V4 — Instrument Identity Source Check #001

**Date:** 2026-09-24
**State:** New educational source check under the coverage ledger; not the recovered original GM-001 lesson or its audit. No market-data download, observation, dataset admission, method, or Phase 9 claim.

## Retrieval outcome

A bounded repository search of default branches for `GM-001` and `IND-014` found no original lessons. The conversation-history retrieval was unavailable on two attempts. A saved-file search did not identify an original lesson file. This establishes only that the original text was **not located by these checks**; it does not prove it never existed. The recovery draft's exact-text and completion claims remain unverified.

## First source-backed identity case: SPY

| Distinct object or measurement | What the source establishes | What must not be conflated |
|---|---|---|
| ETF share | [State Street's SPY fund page](https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy) identifies the State Street SPDR S&P 500 ETF Trust, ticker SPY, listed on NYSE Arca in USD; the page also lists a CUSIP and ISIN, each with a date-qualified listing table. | The ETF share is a tradable security. Its ticker alone is not a globally unique or timeless identifier. |
| Benchmark index | The fund page says the ETF seeks results generally corresponding, before expenses, to the S&P 500 Index. The [SEC ETF investor bulletin](https://www.sec.gov/investor/pubs/etfs.pdf) distinguishes an index-tracking fund from the index it follows. | The ETF's share price is not a level of the S&P 500 Price Return Index. Q-011 remains a different instrument/product question. |
| ETF official closing price | The State Street page labels its closing price as the ETF's official closing price reported by the primary listing exchange. | A third-party vendor's unadjusted `close` cannot be declared equivalent until the vendor specifies source, session, corrections, and corporate-action basis. |
| Fund NAV and bid/ask midpoint | The State Street page reports NAV and the closing bid/ask midpoint separately from the official closing price. The [SEC bulletin](https://www.sec.gov/investor/pubs/etfs.pdf) explains that ETF shares trade at market prices that may differ from NAV. | A midpoint, NAV, and official exchange close answer different questions, even when recorded for the same date. |

The fund page is a **primary fund/identity source**, not the selected price-feed license for Radar. Its current and historic page content may change; this record cites the page and the meanings, without copying a market-value series into the repository.

## Evidence still missing for one daily SPY observation

- The original GM-001 lesson and audit, including exact wording and status.
- A selected provider and applicable terms for the exact proposed dataset and retained raw response.
- Provider confirmation that `SPY` maps to this security and that its daily unadjusted close is the desired regular-session measurement.
- Timezone, completed-session publication cutoff, revision/correction behavior, and exact exchange-close versus consolidated-close semantics.
- A source-specific date-qualified identifier history; today's ticker/CUSIP/ISIN mapping alone does not establish all past dates.

## Generalization test before world coverage

Repeat this identity check separately for each instrument and jurisdiction: security/contract identity, benchmark or underlying, exchange or publisher, currency, effective dates, and the precise observed measure. If a cross-listed instrument, ADR, local share, future continuation, FX pair, or index variant fails one field, mark it UNKNOWN rather than carrying over an apparently similar U.S. mapping.

**Disposition:** SPY fund-versus-index and closing-price-versus-NAV distinctions are source-backed educational facts. GM-001 source recovery is OPEN; source-qualified real observation is HOLD. This note does not complete a lesson or change pilot authority.
