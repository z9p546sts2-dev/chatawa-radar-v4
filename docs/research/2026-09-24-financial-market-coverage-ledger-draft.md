# Radar V4 — Financial-Market Coverage Ledger Draft #001

**Date:** 2026-09-24
**State:** Review draft. A map of questions and missing evidence, not verified mastery, dataset admission, Phase 6 research, or live operation.
**Relationship:** Companion to the GM/IND recovery draft in PR #40. It does not replace `ROADMAP.md` or the four-to-five-year horizon roadmap. February 2027 remains an unverified recollection.

## Purpose

Build an expandable understanding of U.S. and world markets. Coverage is earned per instrument, venue, jurisdiction, and time period. A topic appearing here means it is **in scope for learning**, not that Radar has current knowledge or a usable feed. More facts help only when identity, provenance, definitions, timing, gaps, and revisions can be checked. A descriptive fact is not a signal or causal explanation.

## Common questions for every market family

1. **Identity:** instrument and economic claim, issuer/underlying, identifiers, lifecycle, corporate action or contract roll, currency and unit.
2. **Venue and rules:** where it trades or is published, jurisdiction, market hours/holidays, clearing, settlement, access restrictions.
3. **Observation:** price/quote/fixing/index versus executed transaction, close definition, volume or open interest, adjusted versus unadjusted, timestamp and timezone.
4. **Context:** rates, policy, economic releases, earnings, supply/demand, events, and calendar; distinguish contemporaneous from later-known information.
5. **Custody:** source authority and terms, permitted storage/display, revision history, provenance, completeness, latency and correction method.
6. **Claim:** what can be described, what comparison is valid, what is unknown, and what evidence could contradict it.

## Coverage inventory

All rows start **UNVERIFIED AS OPERATIONAL KNOWLEDGE**. The GM/IND recovery draft supplies a partial educational topic outline, but the original lessons and audit are not yet recovered. No row below implies a provider entitlement or ingested dataset.

| Family | U.S. and global questions to cover | First evidence gap to close |
|---|---|---|
| Listed equities | Shares, corporate actions, classes, listings and cross-listings, ADRs/GDRs, delistings; major domestic and foreign venue/session differences. | Verified instrument identity and historical listing/adjustment rules per venue. |
| Funds and ETPs | ETFs, mutual funds, ETNs and other ETP structures; holdings, NAV versus traded price, creation/redemption, distributions and domicile. | Distinguish one ETF's trade close from its benchmark index and fund NAV. |
| Equity indexes | Price, total-return and net-return variants; constituent rules, rebalances, licensing and publication times worldwide. | Exact index product/version, methodology and retention rights for each proposed series. |
| Sovereign and local rates | Bills, notes, bonds, inflation-linked debt, auctions, benchmark curves, calendars, day-count, yield conventions and debt-market structure. | Same-date, same-convention rate/yield identity and revision records. |
| Credit and structured debt | Corporate, municipal, agency, securitized and emerging-market debt; ratings, spreads, defaults and liquidity. | Separately identify traded price, evaluated price, yield and spread; note sparse trading. |
| Foreign exchange | Spot, forwards, swaps, NDFs, crosses and fixes; currencies, settlement and local market conventions. | Quote direction, venue/fixing, market date and executable versus indicative rate. |
| Commodities and physical markets | Energy, metals and agriculture; grade, delivery location, units, inventories, logistics, seasonality and physical versus financial prices. | Contract/product specification and physical-location identity before comparison. |
| Futures and options | Underlying, expiry, strike, exercise/settlement, margin, rolls, implied volatility and term structure across venues. | Exact contract identity and whether a continuous series is vendor-constructed. |
| Money markets and funding | Overnight rates, repos, short-term instruments, collateral, benchmarks and central-bank facilities. | Publication versus observation date and benchmark methodology. |
| Digital assets | Spot crypto, tokens, stablecoins and derivatives; chains, custody, exchanges, forks and fragmented venue prices. | Asset/chain and venue identity, timestamp, trade-quality and custody risks. |
| Private and less-liquid markets | Private equity/credit, real estate and other infrequently valued assets, where reliable public observations may be limited. | Valuation date, appraisal/model basis, delay and permission to use the record. |
| Economic and policy context | Inflation, labor, growth, trade, fiscal and central-bank events across countries; release calendars and vintages. | First-release versus revised values, historical availability and country definitions. |
| Market plumbing and cross-asset links | Exchanges, clearing, settlement, holidays, capital flows, correlation regimes and transmission mechanisms. | Keep observed co-movement separate from a supported causal claim. |
| Data quality and comparability | Identifiers, source authority, adjustments, unit conversion, survivorship, stale values, missing sessions and revisions across all families. | A per-source refusal and correction record, including licensing/custody conditions. |

## Status vocabulary for each eventual topic/source pair

- **MAPPED:** questions named, no source-qualified answer.
- **SOURCE-LOCATED:** authoritative source named; exact product/rights and semantics may be open.
- **LEARNING-VERIFIED:** original educational source and interpretation audited; no real-data permission implied.
- **DATA-QUALIFIED:** exact product, access, semantics, retention and correction handling documented for a bounded use.
- **OBSERVED:** separately authorized real observation with provenance and human review.
- **VALIDATED QUESTION:** one predeclared comparison tested under its own method/validation gates; no automatic transfer to other markets.

Track status for each **family × instrument × venue/jurisdiction × source/product × interval × period**, not as a single global completion percentage. Mark unavailable or contradictory coverage as **UNKNOWN**. Do not fill an evidence gap with a neighboring market proxy without naming and reviewing the substitution.

## First bounded work

1. Recover original GM-001–GM-015 and IND-001–IND-014 lesson texts and audits. Reconcile exact scope and status; do not invent missing IND titles.
2. Pick the first educational subtopic, instrument identity, and fill a row with source citations and unresolved terms. Use it to test whether this ledger captures real gaps without new code.
3. Keep the provisional SPY one-close observer in PR #41 as a separate source and operational decision. It is one narrow example, not a prerequisite for learning every family and not proof of global readiness.
4. Expand one family at a time only when a specific learning or research question needs it. Maintain an explicit map of missing countries, instruments and periods.

Atlas and World Almanac may later supply source-checked economic and geographic context, but their inventories do not become Radar market observations or market understanding by linkage alone.

This ledger grants no vendor access, purchase, raw-data admission, method, feature, score, threshold, ranking, backtest, dashboard, broker connection or execution. Todd retains the separate decisions named in `GOVERNANCE.md`.

Learning and Earning It.
Stay on course.
No drift.


## First-pass source checks recorded on this draft branch

These checks explain meanings; they are **SOURCE-LOCATED for educational examples only**. No original GM lesson was recovered, and no row is DATA-QUALIFIED or OBSERVED.

| Family touched | Example and source check | Remaining decisive gap |
|---|---|---|
| Funds/indexes | [SPY ETF, index, close and NAV](2026-09-24-instrument-identity-source-check-draft.md) | Vendor close semantics and fund-versus-index source rights. |
| Listed equities/global receipts | [Toyota ordinary share versus U.S. ADS](2026-09-24-instrument-identity-source-check-draft.md) | Date-qualified foreign security mapping for any selected price source. |
| Options | [Underlying versus option series and adjusted deliverable](2026-09-24-instrument-identity-source-check-draft.md) | Exact contract/adjustment memo for a specific date and source. |
| FX | [ECB EUR-base informational reference rate](2026-09-24-fx-reference-identity-source-check-draft.md) | Fixing versus executable quote; terms and time alignment for an actual question. |
| Sovereign rates | [Treasury note versus auction versus CMT curve](2026-09-24-treasury-rate-identity-source-check-draft.md) | Exact series/issue, methodology vintage and rights. |
| Commodities/futures | [WTI spot versus delivery-month futures](2026-09-24-crude-spot-futures-identity-source-check-draft.md) | Product grade/location, contract month, roll and source rights. |

## First-pass audit disposition (2026-09-24)

The six example rows were reviewed for source identity, measurement identity, historical qualification, and unsupported operational implications. The cited issuer, regulator, publisher, and exchange materials support the bounded **educational distinctions** described in the linked notes. This is not an audit of the unrecovered GM/IND lessons or a qualification of any market-data product.

| Audit finding | Disposition |
|---|---|
| Toyota's pre-1999 ADS facilities do not establish their historical share-per-ADS ratios in this check. | Wording corrected; historical ratio remains UNKNOWN. |
| The linked CME chapter is not by itself a dated verification of rules at a future observation time. | “Current” removed; then-applicable rules remain OPEN. |
| The Treasury security row uses an offering announcement and its auction row initially used a general pricing explanation. | The [official June 7, 2022 auction result](https://www.treasurydirect.gov/instit/annceresult/press/preanre/2022/R_20220607_1.pdf) now matches CUSIP `91282CEU1` and the issue date. A date-qualified secondary-market quotation and source rights remain OPEN. |
| SPY, FX, Treasury, and WTI references describe distinct objects or measurements. | Examples only; feed semantics, effective dates, corrections, rights, and access remain OPEN. |
| The common questions cover identity, rules, observation, context, custody, and claim; a future data comparison additionally needs explicit **as-of availability** and transformation lineage. | Record both fields for any proposed comparison before data qualification. |

**Next priority:** recover the original GM/IND texts and audits, then reconcile their scope with this ledger. For any bounded example proposed for actual data, identify exact product terms, historical semantics, correction path, as-of availability, and transformations before an observation. More educational examples alone do not establish market evaluation ability.
