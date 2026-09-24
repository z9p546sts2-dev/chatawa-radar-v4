# One-ETF Observer — Source Candidate Check #001

**Date:** 2026-09-24  
**Candidate:** Alpha Vantage `TIME_SERIES_DAILY` for provisional SPY  
**Disposition:** CANDIDATE / HOLD — documentation review only; no API request, credential, subscription, or data admitted

## What the provider documents

- The [official API documentation](https://www.alphavantage.co/documentation/) describes `TIME_SERIES_DAILY` as raw (as-traded) daily open, high, low, close and volume, distinct from its adjusted-daily product. Its compact output covers the latest 100 points and is documented for free and premium keys; full history is described as premium. The documentation refers to stock, ETF and mutual-fund symbol support, but this review did not verify a live SPY response or an exact symbol lookup.
- [State Street's SPY fund page](https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy) supports the provisional fund identity. A vendor's `SPY` mapping still needs confirmation before declaration.
- The [Alpha Vantage terms of service](https://www.alphavantage.co/terms_of_service/) distinguish personal, private, non-commercial use from uses on behalf of an association or involving third-party access. The intended Chatawa Labs account/use classification must be checked against the applicable agreement; a research-only first pilot does not settle later product rights. This is a qualification question, not a legal conclusion.
- The public documentation reviewed here does not give a project-specific, explicit answer for how long the exact daily raw response may be stored privately or retained after access ends; nor does it establish the publication/finality time, historical correction signal, or SPY-specific daily bar timestamp and exchange-session semantics needed by the proposed runbook.

## Further public-document check — 2026-09-24

| Requirement | Documented finding | Disposition |
|---|---|---|
| Raw price shape | The API docs describe `TIME_SERIES_DAILY` as raw as-traded OHLCV and explicitly separate its adjusted endpoint. | Plausible for an unadjusted close; still verify exact SPY response. |
| Volume of requests | [Official support](https://www.alphavantage.co/support/) states a free-service limit of 25 requests per day. One manual retrieval per trading session is below that published number, subject to actual account eligibility and unchanged terms. | Published request capacity appears adequate; no account entitlement claimed. |
| Raw response scope | The documented compact mode returns up to 100 recent data points, not a server-side request for only one named date. | A single pilot call may contain other dates; full-response custody and one-row selection must be documented. |
| Account/use category | The [terms](https://www.alphavantage.co/terms_of_service/) distinguish individual private research from use on behalf of an association and third-party access. | HOLD for the actual Chatawa Labs account and intended use. |
| Retention and post-termination custody | No explicit project-specific raw-response retention duration or post-termination right located in the public terms reviewed. | HOLD; request written clarification or applicable agreement. |
| Session close/finality and corrections | No published guarantee located here for regular-session-only SPY close, bar publication cutoff, or a correction/version marker. | HOLD; request exact vendor semantics. |
| Symbol mapping | State Street identifies the fund as SPY; the vendor response and its mapping were not checked. | HOLD until an authorized bounded response or provider confirmation. |

The provider [support page](https://www.alphavantage.co/support/) offers a contact route. No message has been sent, and a public URL containing anyone's API key is not evidence for this review.

## Questions to resolve before a call

1. Which agreement/tier covers the actual account and private, possibly future business-oriented Chatawa Labs research use?
2. May the exact JSON response, hash, normalized daily fact, correction versions and human review record be retained privately for the full pilot and audit period? What happens after subscription termination?
3. Does `TIME_SERIES_DAILY` return SPY as the intended ETF, with unadjusted regular-session closing price in USD, and how are session date and timestamp defined?
4. At what documented point after the close is a session's daily bar available, and how can later corrections or corporate-action-related historical changes be detected without silently overwriting custody?
5. Does the applicable account/tier include this endpoint for the proposed one-call-per-day use, and does any exchange or third-party condition add restrictions?

## Decision

The endpoint is a technically plausible first candidate for **one unadjusted completed-session bar**. The source is **not selected or qualified** until access rights, exact instrument mapping, bar semantics, publication/correction behavior and retention are resolved. Do not purchase a tier or invoke the endpoint based on this note. A later source decision should cite the applicable actual agreement or provider's written answer and a bounded response check under separate authorization. The shortest provider inquiry is a single request covering questions 1–4 and the account entitlement in 5, with no API key or authenticated URL included.

This note does not change the one-ETF scope draft's decision gates or Radar's current fixture/synthetic-only supported CLI route.
