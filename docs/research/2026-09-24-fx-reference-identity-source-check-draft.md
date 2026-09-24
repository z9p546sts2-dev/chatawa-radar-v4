# Radar V4 — FX Pair and Reference-Rate Identity Check #001

**Date:** 2026-09-24
**State:** New educational source check for the FX row in the coverage ledger. Not the recovered GM-007 lesson, a selected Radar data source, or an admitted observation.

## Example: ECB euro reference rate for USD

The [ECB reference-rates page](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) explicitly quotes currencies **against the euro as base currency**. Thus an ECB EUR/USD reference-rate entry is a number of U.S. dollars per one euro. A source reporting USD/EUR reverses the numerator and denominator; it is a distinct quote identity, not an equivalent numeric observation.

The [ECB's June 2026 methodology framework](https://www.ecb.europa.eu/stats/pdf/exchange/Frameworkfortheeuroforeignexchangereferencerates.en.pdf) says the rates are set around 14:10 Central European Time and published around 16:00. They are informational reference rates, not intended as transaction prices. The ECB may use transaction information, firm quotes or cross rates depending on available liquidity. It may also amend/republish a rate in a bounded subsequent window; its framework says no republication after the same currency's following-business-day rate is published.

| Required identity field | This example | Unresolved for a future Radar use |
|---|---|---|
| Currency direction and unit | EUR base, USD quote, units USD per EUR. | A provider's pair naming and reciprocal/rounding policy. |
| Statistic | ECB informational reference rate, not a guaranteed executable bid, ask, trade, or closing price. | Whether the question needs a reference fixing or an actual market quote. |
| Time and calendar | Setting and publication are distinct events; the ECB's operating-day calendar controls the source. | Timezone-aware release availability for any comparison with U.S. or Asian sessions. |
| Revision | Methodology permits bounded amendments and republications. | Source-specific version capture and comparison if a future feed is licensed. |
| Rights and custody | Public methodology and page were read for definitions only. | Product-specific data terms and private retention before any feed is selected. |

**Refusal example:** If a dataset declaration expects USD per EUR but a response supplies EUR per USD, quarantine it. Do not silently take a reciprocal, infer a same-time quote, or call the ECB fixing the FX market's close.

**Disposition:** The quote-direction, statistic and publication distinctions are source-backed educational knowledge. GM-007 original text remains unrecovered. FX ingestion, conversion code, method research and cross-asset comparison remain outside this draft.
