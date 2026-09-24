# One-ETF Observer — Engineering Boundary and Manual Runbook Draft #001

**Date:** 2026-09-24  
**State:** review-only; no implementation or vendor run authorized  
**Parent:** [scope draft](2026-09-24-one-etf-daily-observer-scope-draft.md)

## File-level boundary found on current `main`

| Existing path | Relevant behavior | Pilot implication |
|---|---|---|
| `radar_v4/evidence.py`, `dataset.py`, `observation.py` | Represent provider/symbol/time/interval provenance, one declaration, and a checksummed close payload. | Reuse identity models after qualifying real source semantics. |
| `radar_v4/observation_validation.py`, `session.py` | Validate close and checksums; `run_dataset_session` can receive supplied observations and can be called with `measure=False`. | A descriptive run can reuse validation without a market-method or baseline claim. |
| `radar_v4/dataset_pack.py`, `pack_export.py` | Explicitly refuse `HISTORICAL` and `LIVE`. | Preserve this refusal; do not widen the fixture pack by changing an allowlist. |
| `radar_v4/local_session.py`, `cli.py` | `session --pack` enters via the fixture/synthetic loader; replay reads a snapshot, not a vendor raw response. | The present CLI cannot execute the proposed real-data workflow. |
| `radar_v4/snapshot_files.py` | Writes local snapshot with replace control, but is not by itself an append-only raw-response custody system. | Design private raw custody, immutable run identity and correction linkage separately. |

The eventual narrow build proposal should identify an isolated **real-response translation and intake route**, a manual command, a private storage layout, fail-closed behavior, and a rollback. It must leave fixture behavior unchanged. It should prove that a source JSON with multiple historical rows results in **exactly one eligible session observation** and preserves the whole licensed response privately if permitted. If provider terms do not permit that custody, revise source or scope before a call.

## Proposed operator sequence

1. **Before day one:** confirm the source qualification and authorized account, fixed symbol, exact data field, timezone/session definition, raw-retention rights, start date, 20-session limit, private storage path, and who operates the pilot.
2. **Per eligible trading session:** after the provider's documented publication point, initiate one manual command. No clock-based claim of finality without source evidence. Do not infer a bar on exchange holidays or unscheduled closures.
3. **On response:** preserve the exact response bytes and digest privately under a new run ID; record sanitized request parameters, retrieval UTC and status, without key or authenticated URL. Select only the requested session row. Refuse if response semantics or row identity are unclear.
4. **At intake:** construct a `HISTORICAL` envelope and payload from the documented fields, check source/date/adjustment identity against the locked declaration, and run existing validation with no repair. Do not coerce an absent or malformed value to zero.
5. **Human review:** show date, close, units, provider, raw digest, data freshness, acceptance/refusal, and any correction link. The operator records an explicit accept/refuse decision. This is a data-custody decision, not a trade view.
6. **On missing/conflict/correction:** record a gap or quarantine with reason. A later corrected bar is a new evidence version linked to the old; no silent overwrite or synthetic replacement. Stop and review if the provider changes meaning or entitlement.
7. **At 20 eligible sessions or earlier stop:** count scheduled, retrieved, accepted, missing, quarantined and corrected sessions. State exactly what worked and what failed. Do not infer market usefulness or a method.

## Acceptance checks for a later build review

- One valid qualified response yields one correct session date and unchanged raw close, with consistent envelope/payload checksums and private artifact digest.
- An already seen identical bar is idempotent; a changed value for the same session triggers explicit correction handling rather than overwrite.
- Missing row, adjusted field substitution, unexpected symbol, future/incomplete session, stale response, malformed JSON, timestamp mismatch, and raw-custody failure all refuse visibly.
- Secrets do not appear in logs, stored request URLs, source files, reports or PRs.
- Existing fixture/synthetic pack and CLI tests continue to enforce their real-data refusal.
- No scheduler, scoring, prediction, signal, broker, or Phase 9 claim appears in the run output.

The source and rights HOLD remains upstream of this build. No implementation file is proposed for change by this review record.
