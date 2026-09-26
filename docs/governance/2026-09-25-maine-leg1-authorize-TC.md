# AUTHORIZE — Maine Leg 1: three-symbol HISTORICAL universe (amends HA-1)

**Status:** IN FORCE — Accept as written — TC (2026-09-25)  
**Date:** 2026-09-25  
**Authority:** Todd C. (`-TC`)  
**Route:** Maine Leg 1 only (not Leg 2–5; not LIVE; not Phase 6)

## What this authorizes

Amend the HA-1 HISTORICAL admission path from **SPY-only** to a **named three-symbol universe** for private Stooq daily packs:

| Symbol | Provider | Interval | Provenance |
|---|---|---|---|
| SPY | STOOQ | 1d | HISTORICAL |
| QQQ | STOOQ | 1d | HISTORICAL |
| IWM | STOOQ | 1d | HISTORICAL |

**Claim ceiling:** LEVEL 0 — MEASURED descriptive close-to-close **difference** only (Phase 5 metric). No method, signal, threshold, edge, or trading decision.

**Converter:** expand `tools/stooq_to_strict_pack.py` allowlist from SPY-only to exactly `{SPY, QQQ, IWM}` with provider STOOQ. Keep existing guards (required `--retrieved-at`, required `--adjustment-policy`, America/New_York 16:00 ZoneInfo, refuse nonpositive OHLC, refuse `--out` inside tool git work tree). One symbol per pack / per convert invocation.

**Workshop:** existing `session --allow-historical` path; no LIVE; no `prepare-observation`; no vendor HTTP in `radar_v4/`.

## Exit for Leg 1

1. Cursor lands allowlist + tests (docs AUTHORIZE banked).  
2. Private packs for QQQ and IWM (SPY may reuse existing custody if span/policy still apply; otherwise re-run).  
3. Adjustment check per symbol vs Yahoo Close (split-adjusted, not dividend-adjusted), including **one ex-div date each**.  
4. One combined Claude audit packet (claim + provenance; no OHLC series in git).  
5. Todd locks three MEASURED custodies (or STOP).

## Explicit non-allows

- Not LIVE provenance. Daily after-close downloads remain HISTORICAL.  
- Not intraday. Not paid feeds. Not cloud/hosting. Not Task Scheduler (Leg later).  
- Not VTI path. Not Q-011. Not Phase 6 noticing.  
- No method / signal / trading decision authorized or informed by these MEASURED runs.  
- No market CSV/pack/report bytes in public git.

## Binding to existing custody

- First SPY/STOOQ MEASURED custody remains in force (private SHA `00bd9d54accb0728a20c88445612307a0c79a6f563061a0b30ab95bcbb289ef1`).  
- This memo does not reopen HA-1 R1.3 mechanism; it only names the universe for converter + private runs.

## Sign-off

- Todd (TC): Accept as written — TC  DATE: 2026-09-25  
- Claude: audit after Cursor land + combined MEASURED packet (not a pre-sign gate for this AUTHORIZE draft)

```
AUTHORIZE MAINE LEG 1 — SPY/QQQ/IWM STOOQ DAILY HISTORICAL — IN FORCE
```


## Locked

Accept as written — TC. AUTHORIZE Maine Leg 1 IN FORCE 2026-09-25 (America/Chicago).
