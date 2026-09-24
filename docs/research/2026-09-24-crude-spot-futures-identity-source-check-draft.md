# Radar V4 — Crude Spot and Futures Identity Check #001

**Date:** 2026-09-24
**State:** New educational source check for commodity and derivative coverage. Not original GM-005/GM-008 lessons, vendor qualification, or market-data admission.

## Related oil markets, distinct observations

| Object | Primary-source definition | Required identity |
|---|---|---|
| EIA WTI spot series | [EIA's spot-price table](https://www.eia.gov/dnav/pet/PET_PRI_SPT_S1_D.htm) labels West Texas Intermediate at **Cushing, Oklahoma** as a daily spot-price series in U.S. dollars per barrel. Its note says weekly/monthly/annual prices are unweighted averages of daily closing spot prices. | Product/grade, Cushing location, date, spot statistic, USD/barrel, source release and revision. |
| NYMEX light sweet crude futures | [CME's current Chapter 200 rulebook](https://www.cmegroup.com/content/dam/cmegroup/rulebook/NYMEX/2/200.pdf) specifies physical delivery in Cushing, a 1,000-U.S.-barrel trading unit, USD cents-per-barrel quotation and trading in separate calendar delivery months. CME's [education page](https://www.cmegroup.com/education/courses/introduction-to-energy/introduction-to-crude-oil/discover-wti-a-global-benchmark) explains the delivery point and contract size. | Exchange/product, exact contract month and expiry, quote versus settlement, trading/session date, delivery terms, USD/barrel and data rights. |
| Vendor continuous future | A continuous series would combine or choose observations across contract months under a vendor-specific roll rule. This is a conceptual transformation, not an observation made by either EIA or a single listed futures contract. | Vendor method/version, roll trigger, adjustment/back-adjustment, original contracts and source timestamps before any comparison. |

**Refusal example:** A WTI spot close and a nearby CL futures settlement can both use USD/barrel and refer to Cushing, but they are different measurements with different time and delivery meaning. Do not mark them equal merely because the unit and commodity name match. A bare symbol `CL` without a delivery month is incomplete futures identity.

**Geography lesson:** Global commodity prices need grade, location and logistics context. The label “oil price” alone cannot identify WTI spot at Cushing, a NYMEX delivery-month contract or a different benchmark such as Brent.

## Open

Recover original GM lessons; obtain exact EIA statistic/release and revision policy for a future specific series; choose a licensed price product before any operational data; verify the then-current CME rules and specific contract at any later observation date. No spot or futures prices were copied into this record.

**Disposition:** The two product identities and essential contract dimensions are source-backed educational distinctions. Commodity/derivative admission and cross-market inference remain HOLD.
