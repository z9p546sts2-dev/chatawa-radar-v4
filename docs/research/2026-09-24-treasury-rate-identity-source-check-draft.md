# Radar V4 — Treasury Security, Auction and Curve Identity Check #001

**Date:** 2026-09-24
**State:** New educational source check for sovereign rates in the coverage ledger. Not a recovered GM-006 lesson, a market-data admission, or a rate signal.

## Three different things called a Treasury rate

| Object | Primary-source meaning | Identity needed before comparison |
|---|---|---|
| Individual Treasury security | A [Treasury offering announcement](https://www.treasurydirect.gov/instit/annceresult/press/preanre/2022/A_20220602_3.pdf) identifies a particular note by CUSIP, term, issue and maturity dates. | Exact issue/CUSIP, coupon, remaining maturity, quotation side, price versus yield, date and venue. |
| Auction result | The auction concerns a named issue at a specific auction time. Its result is an issuance event, not a daily secondary-market quote. [TreasuryDirect pricing explanation](https://www.treasurydirect.gov/marketable-securities/understanding-pricing/) separates auction-determined price/rate from later ownership. | Auction date, result type (e.g. high yield versus issue price), issue/reopening identity and publication status. |
| Constant-maturity par yield | [Treasury's daily rates explanation](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve) says CMT yields are read at fixed maturities from an estimated par curve based on indicative bid-side quotes for recently auctioned securities. A 10-year point need not correspond to a bond with exactly 10 years remaining. | Series/maturity, nominal versus real, par-yield methodology and version, quote/source time, observation and release dates. |

**Refusal example:** A daily 10-year CMT series is not the auction yield or trading yield of one named 10-year note. A direct equality check would compare different objects. Likewise, a bill discount rate and its investment yield differ in day-count and denominator conventions, which Treasury distinguishes on its rates page.

**Historical custody:** Treasury's page describes a change in nominal par-curve method on 2021-12-06. This is a documented series-method boundary. A historical comparison must retain the applicable methodology rather than silently treating every vintage as one unchanged measurement.

## Open

Original GM-006 text/audit; source terms and product rights for any future series; exact revision policy; eligibility of the chosen time/series for a declared question. No Treasury values, auction results or price feeds have been downloaded into Radar by this check.

**Disposition:** Security, auction and constant-maturity curve distinctions are source-backed educational facts. Rates source qualification and operational observation remain HOLD.
