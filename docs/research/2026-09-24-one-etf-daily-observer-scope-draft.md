# One-ETF Daily Observer — Scope Draft #001

**Date:** 2026-09-24  
**State:** proposed, review-only; no data access, implementation, pilot start, or change to `ROADMAP.md` authority  
**Purpose:** define the smallest supervised daily observation goal separately from Q-011 and later market-method work.

## Observation contract proposed for source qualification

- **Instrument:** SPY (SPDR S&P 500 ETF Trust) as a provisional first symbol. Confirm the source's exact fund/security identity, listing, and ticker history before binding a dataset. This is an ETF, not the S&P 500 Price Return Index in Q-011.
- **Fact:** one vendor-reported **unadjusted regular-session daily close in USD** for one completed U.S. equity trading session. No adjusted-close substitution. If the vendor cannot distinguish close basis, market session, or correction status, hold.
- **Cadence:** one operator-initiated retrieval after the provider publishes that completed session's bar. The provider's documented publication and correction behavior must determine the permissible review time; do not hard-code a market-close clock time as vendor finality. No daemon or scheduler in the first pilot.
- **Provenance:** propose `HISTORICAL` for a completed-session bar fetched after publication, even when the session was today. A same-day retrieval is not automatically `LIVE`. Record market session date, provider-supplied market timestamp and timezone semantics, retrieval UTC, provider identity, interval `1d`, price adjustment policy, transformation version, raw-response digest, and any source revision identifier available. Missing semantics block admission.
- **Payload:** close is required. Open, high, low, and volume are optional only if supplied with the same documented bar identity and definitions; do not invent or infer absent fields. Preserve the exact raw response separately from normalized observation and retain the declared unit/precision.
- **Storage:** private, append-oriented custody outside the public repository, if the applicable license permits it. Never place licensed raw market data, credentials, or authenticated request URLs on a branch or in a PR. Preserve correction versions as distinct evidence; no silent overwrite.
- **Output:** one dated, human-readable observation record with value, provenance, freshness, missingness/correction state, and any refusal reason. Descriptive observation only; no feature, threshold, ranking, signal, edge, forecast, or trade action.

## Source qualification before a call

Choose exactly one provider and document: security identity; daily bar endpoint or export; regular versus extended session basis; unadjusted-close and corporate-action behavior; exchange calendar and timezone semantics; timestamp labeling; publication lag; revisions and correction retrieval; access method; limits; terms for private raw-response retention and derived records; and secret custody. A public example or prior SPY study does not transfer rights or authorization. If any required right or data meaning remains unknown, keep the source on HOLD.

## Manual pilot proposed after separate authorization

The candidate pilot is **20 eligible completed trading sessions**, with a start date fixed before the first retrieval. Record scheduled no-session days without fabricating bars. One manual run per eligible day, then human review of the source identity, date, close, raw artifact hash, and admission/refusal result. A missed day is a documented gap, not a silent backfill. A later backfill requires its own provenance and review. The operator may stop the pilot immediately; a stop preserves all evidence and reasons.

Refuse or quarantine when the source is unreachable, rights are unverified, a bar is missing or incomplete, time/session identity is ambiguous, the response is stale, an adjusted price is substituted, duplicate identity has conflicting payload, a provider correction cannot be distinguished, a raw artifact cannot be preserved, or a validator rejects the record. No retry may silently change the question, source, transformation, or prior result.

## Existing software boundary and proposed engineering review

`EvidenceEnvelope`, `DatasetDeclaration`, `ObservationPayload`, and dataset intake support the relevant identity shapes. They do not constitute a supported vendor workflow. `load_dataset_pack` and `export_snapshot_to_pack` explicitly refuse `HISTORICAL` and `LIVE`; the `session` CLI uses the fixture/synthetic pack route. A source adapter alone will not make this pilot runnable.

Before a code authorization, identify a **separate real-data entry route** that preserves the existing fixture/synthetic refusal, validates a source-specific raw response, writes private append-oriented evidence, and routes one declared observation into existing validation/session logic. Review secret handling, corrections, calendar/finality, failure logging, and rollback. Test refusal cases against representative licensed or source-approved samples without committing raw vendor data. Do not relabel a vendor observation `SYNTHETIC` to pass the existing pack gate.

## Decision gates

1. **Scope review:** Todd accepts or revises this one-symbol, one-fact, manual descriptive boundary.
2. **Source and custody:** exact provider, semantics, access, and retention rights documented; HOLD if unresolved.
3. **Build decision:** named files, narrow tests, private data path, and rollback reviewed and separately authorized.
4. **Pilot start:** completed implementation and refusal checks reviewed; fixed 20-session window and manual operator named; separate authorization before the first market-data call.
5. **Close:** report completeness, gaps, corrections, refusals, and operator experience. Any expansion requires its own decision.

This is **not Phase 9 completion** and does not open Q-011, Phase 6 method research, a backtest, a scheduler, a dashboard, or trading. The closed unmerged SPY study PR #38 remains historical evidence only. A February 2027 learning horizon, if later verified, would not authorize or accelerate this pilot.
