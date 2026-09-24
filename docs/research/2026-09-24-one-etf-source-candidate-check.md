# One-ETF Observer — Source Candidate Check #001

**Date:** 2026-09-24  
**Candidate:** Alpha Vantage `TIME_SERIES_DAILY` for provisional SPY  
**Disposition:** CANDIDATE / HOLD — documentation review only; no API request, credential, subscription, or data admitted

## What the provider documents

- The [official API documentation](https://www.alphavantage.co/documentation/) describes `TIME_SERIES_DAILY` as raw (as-traded) daily open, high, low, close and volume, distinct from its adjusted-daily product. Its compact output covers the latest 100 points and is documented for free and premium keys; full history is described as premium. The documentation refers to stock, ETF and mutual-fund symbol support, but this review did not verify a live SPY response or an exact symbol lookup.
- [State Street's SPY fund page](https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy) supports the provisional fund identity. A vendor's `SPY` mapping still needs confirmation before declaration.
- The [Alpha Vantage terms of service](https://www.alphavantage.co/terms_of_service/) distinguish personal, private, non-commercial use from uses on behalf of an association or involving third-party access. The intended Chatawa Labs account/use classification must be checked against the applicable agreement; a research-only first pilot does not settle later product rights. This is a qualification question, not a legal conclusion.
- The public documentation reviewed here does not give a project-specific, explicit answer for how long the exact daily raw response may be stored privately or retained after access ends; nor does it establish the publication/finality time, historical correction signal, or SPY-specific daily bar timestamp and exchange-session semantics needed by the proposed runbook.

## Questions to resolve before a call

1. Which agreement/tier covers the actual account and private, possibly future business-oriented Chatawa Labs research use?
2. May the exact JSON response, hash, normalized daily fact, correction versions and human review record be retained privately for the full pilot and audit period? What happens after subscription termination?
3. Does `TIME_SERIES_DAILY` return SPY as the intended ETF, with unadjusted regular-session closing price in USD, and how are session date and timestamp defined?
4. At what documented point after the close is a session's daily bar available, and how can later corrections or corporate-action-related historical changes be detected without silently overwriting custody?
5. Are API limits and access terms adequate for one manual daily retrieval, with credential handling outside the repo?

## Decision

The endpoint is a technically plausible first candidate for **one unadjusted completed-session bar**. The source is **not selected or qualified** until access rights, exact instrument mapping, bar semantics, publication/correction behavior and retention are resolved. Do not purchase a tier or invoke the endpoint based on this note. A later source decision should cite the applicable actual agreement and a bounded response check under separate authorization.

This note does not change the one-ETF scope draft's decision gates or Radar's current fixture/synthetic-only supported CLI route.
