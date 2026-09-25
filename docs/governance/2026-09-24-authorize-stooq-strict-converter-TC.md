# AUTHORIZE — Stooq → strict pack converter ONLY — TC

**Status:** IN FORCE (accepted with edits — TC)
**Accepted:** Accepted with edits — TC — 2026-09-24
**PATCH AUTHOR:** tool at Todd's direction (Cursor)
**Date drafted:** 2026-09-24 (America/Chicago)
**Date signed:** 2026-09-24 (America/Chicago)
**Authority:** Todd C. (`TC`)
**Style:** AUTHORIZE (same custody pattern as `docs/governance/2026-09-24-authorize-observation-intake-hardening-TC.md`)
**Repo:** `z9p546sts2-dev/chatawa-radar-v4`
**Bound BUILD UNIT design:** `docs/governance/2026-09-24-build-unit-stooq-strict-converter-TC.md` (bank with this memo)

**Does not authorize:** `prepare-observation`, network in `radar_v4/`, commit of real Stooq bytes, LIVE, second symbol, HA-1 replacement/widening, Q-011, Phase 6–9, snapshot/export of HISTORICAL, commercial redistribution.

**Challenge (converter already in-repo?): NO.** Main has no Stooq→pack converter (`stooq` hits are governance-only; no `tools/` or `scripts/` tree). HA-1 already requires private CSV→JSON outside `radar_v4/`. This AUTHORIZE charters that missing offline tool — it does **not** invent or replace HA-1.

**Edits vs UNSIGNED candidate (Todd 2026-09-24 review):**
1. Timezone default is **America/New_York** (not UTC). Market timestamps use that date at **16:00:00** local with DST offset from `ZoneInfo`. UTC 14:00 was rejected as lookahead (stamping closes before they exist).
2. `retrieval_timestamp` is **not** converter wall-clock. Required CLI `--retrieved-at` = time the private CSV was downloaded/captured; refuse if omitted.
3. `adjustment_policy` remains a **pre-MEASURED data check** (not assumed UNADJUSTED in the first real run). Converter may emit a Todd-chosen declaration value; verification vs official SPY closes / dividend dates is required before first MEASURED acceptance (runbook).

---

## Relation to banked authority

| Item | Relation |
|---|---|
| HA-1 IN FORCE | `docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md` — SPY / STOOQ private Phase 5 LEVEL 0 MEASURED via `session --allow-historical`; close-to-close **difference**; CSV→JSON outside `radar_v4/`; no market bytes in git. **This converter AUTHORIZE implements the conversion step HA-1 already assumed; it does not replace HA-1.** |
| Intake hardening | PR 50 merge `34d407c6…` — strict non-FIXTURE intake (decimal-string prices, OHLCV-only keys, required `payload_checksum`, duplicate-key refuse). Converter **must** emit that shape. |
| Docs recon + intake AUTHORIZE | PR 51 merge `436d3f8e…` — claim-ceiling docs; intake AUTHORIZE banked. No change to those ceilings here. |
| VTI | Untouched side path. Converter is SPY/STOOQ only. |

Claude order item 3 (converter → first SPY run): this AUTHORIZE covers **converter build only**. First MEASURED run uses the separate runbook stub and still needs Claude accept under HA-1 hygiene — not a blank check in this memo.

---

## DECISION block (SIGNED)

```text
DECISION: AUTHORIZE STOOQ → STRICT PACK CONVERTER — TC
          (OFFLINE CLI OUTSIDE radar_v4/; SPY/STOOQ ONLY)

SCOPE:
  - Offline converter CLI/script (prefer tools/stooq_to_strict_pack.py;
      scripts/ acceptable) that reads a private Stooq-shaped SPY daily CSV
      and writes a pack directory (declaration.json + obs_NNNN.json) matching
      HA-1 + strict intake on main.
  - payload_checksum = SHA-256 hex of
      json.dumps(canonical OHLCV dict, sort_keys=True, separators=(",", ":"),
      ensure_ascii=True).encode("utf-8")
      identically to ObservationPayload.compute_checksum on main
      (hashes ObservationPayload.canonical_payload()).
  - Decimal-string OHLCV only; no JSON numbers; no extra payload keys;
      required payload_checksum; duplicate-key refuse at emit/parse.
  - declaration: provenance_class=HISTORICAL, provider=STOOQ, universe=SPY,
      interval=1d, primary_metric=close-to-close difference,
      transformation_version=stooq-daily-ohlcv-v1 (or Todd-initialed alternate),
      timezone=America/New_York (default; not UTC).
  - market_timestamp: that calendar date at 16:00:00.000000 in
      America/New_York with DST offset from ZoneInfo (not hard-coded -04:00).
      Windows note: ZoneInfo needs the tzdata package (pip install tzdata)
      or every row fails timezone_offset_matches (safe fail, confusing).
  - retrieval_timestamp: required CLI --retrieved-at (ISO-8601 timezone-aware)
      = private CSV download/capture time. Refuse if omitted. Must not
      precede market_timestamp for any row. Not converter wall-clock.
  - Tests: synthetic/fixture Stooq-shaped CSV only; no real market bytes in git.
  - May import pure radar_v4 types for checksum identity; must not add HTTP
      to radar_v4/ or to the tool.
  - --out must be empty or nonexistent; no --force override.
  - OHLC contradiction: whole-file refuse (no partial pack).

CLAIM CEILING:
  Software conversion correctness only. Not market truth. Not MEASURED
  acceptance. Phase 5 primary metric remains close-to-close difference.
  Does not widen HA-1. Does not authorize the first private MEASURED run
  beyond what HA-1 already authorized (run still needs HA-1 hygiene +
  Claude accept). adjustment_policy must be verified against official SPY
  closes / a dividend date before first MEASURED acceptance — not assumed.

EXPLICIT NON-ALLOWS:
  - prepare-observation CLI route and custody writer
  - Network / HTTP client / Stooq download inside radar_v4/ or inside this tool
  - Commit of real Stooq / SPY market bytes (CSV or JSON packs with real series)
  - LIVE provenance
  - Second symbol (VTI, QQQ, or any non-SPY)
  - Replacing, widening, or reinterpreting HA-1 AUTHORIZE
  - Snapshot / export of HISTORICAL packs
  - Q-011 data authorization
  - Phase 6–9
  - Commercial redistribution of Stooq data
  - Treating converter green tests as MEASURED market acceptance
  - Defaulting market_timestamp to UTC 14:00 (lookahead)
  - Using converter wall-clock as retrieval_timestamp
  - --force on nonempty --out

PATCH AUTHOR:      tool at Todd's direction (Cursor)
                   (commits may appear as Chatawa Labs / Cursor account)

TIMEZONE DEFAULT:  America/New_York
TODD OVERRIDE TZ:  America/New_York  (signed; UTC rejected)

RELATION TO HA-1:
  Implements private CSV→JSON conversion HA-1 already required outside
  radar_v4/. Does not replace docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md.

RELATION TO INTAKE HARDENING:
  Output must satisfy PR 50 strict non-FIXTURE intake (decimal strings,
  OHLCV-only keys, required payload_checksum, duplicate-key refuse).

DATE OF THIS MEMO: 2026-09-24
TODD:              TC
```

---

## Acceptance (Todd)

- [x] Accepted with edits attached — TC — date 2026-09-24
- [ ] Accepted as written
- [ ] Hold
- [ ] Reject — do not build converter

**Todd signature / date:** TC / 2026-09-24

**Edits attached (controlling):** America/New_York default + 16:00 ZoneInfo market_timestamp; required `--retrieved-at`; no `--force`; whole-file OHLC refuse; adjustment_policy verification deferred to pre-MEASURED (runbook), not assumed UNADJUSTED for acceptance.

---

## Banking path

Bank at:

`docs/governance/2026-09-24-authorize-stooq-strict-converter-TC.md`

Also bank the BUILD UNIT design:

`docs/governance/2026-09-24-build-unit-stooq-strict-converter-TC.md`

Point the Cursor PR body at the banked AUTHORIZE path. Do not bank MEASURED-run acceptance under this filename.

**Tools verify. Cursor codes converter only after this signed AUTHORIZE. Claude audits. Todd authorizes.**
