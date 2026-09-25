# BUILD UNIT — Stooq → strict HISTORICAL pack converter (R1.1 design) — TC

**Status:** DESIGN — authorized by companion AUTHORIZE (accepted with edits — TC 2026-09-24)
**Date:** 2026-09-24 (America/Chicago)
**Revision:** R1.1 — Todd review fixes (America/New_York default; required `--retrieved-at`; no `--force`; whole-file OHLC refuse)
**Authority:** Todd C. (`TC`)
**Repo:** `z9p546sts2-dev/chatawa-radar-v4`
**Operating split:** Grok plans · Cursor codes · Claude audits · Todd authorizes
**Bound AUTHORIZE:** `docs/governance/2026-09-24-authorize-stooq-strict-converter-TC.md`
**Depends on (already IN FORCE on main):**
- HA-1: `docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md` (SPY / STOOQ private Phase 5 LEVEL 0 MEASURED; `session --allow-historical`; close-to-close **difference**)
- Intake hardening (PR 50 merge `34d407c6…`): strict non-FIXTURE intake — decimal-string prices, OHLCV-only keys, required `payload_checksum`, duplicate-key refuse
- Docs recon + intake AUTHORIZE banked (PR 51 merge `436d3f8e…`)

**Challenge (converter already in-repo?): NO.** Code search on main for `stooq` / `converter` / `convert_stooq` finds only governance docs. Repo root has no `tools/` or `scripts/` tree. HA-1 itself assumes private CSV→JSON **outside** `radar_v4/`. This unit fills that gap.

---

## Purpose (one sentence)

Offline CLI **outside** the `radar_v4/` network boundary that converts a **private** Stooq SPY daily CSV (or Stooq native export Todd already uses) into a pack directory that HA-1 + strict intake will admit under `session --allow-historical`.

Maximum honest claim if built and tested: **software conversion correctness for Stooq-shaped CSV → workshop pack layout.** Not market truth. Not LIVE. Not a second symbol. Does not replace HA-1.

---

## Where the tool lives

| Prefer | Why |
|---|---|
| **`tools/stooq_to_strict_pack.py`** (new top-level `tools/`) | Repo has no `tools/` or `scripts/` today; HA-1 and GOVERNANCE forbid vendor/HTTP clients inside `radar_v4/`. Offline converter belongs at repo root under `tools/`, runnable as a script, **not** as a `radar_v4` public API. |
| Acceptable alt | `scripts/stooq_to_strict_pack.py` if Cursor prefers that layout later — still **outside** `radar_v4/`. |

**Hard placement rule:** no HTTP client, no urllib/requests/httpx, no Stooq URL constants inside `radar_v4/` or inside this tool. Tool may **import** pure `radar_v4` types (`EvidenceEnvelope`, `Observation`, `ObservationPayload`) to compute checksums identically — that is not a network client.

Suggested invocation (illustrative; Cursor may adjust flag names but must keep required semantics):

```text
python tools/stooq_to_strict_pack.py \
  --csv /PRIVATE/path/spy_d.csv \
  --out /PRIVATE/path/spy_stooq_pack \
  --symbol SPY \
  --provider STOOQ \
  --retrieved-at 2026-09-24T15:30:00-05:00
```

`--retrieved-at` is **required** (ISO-8601 timezone-aware). It is the private CSV download/capture time, written into every observation's `retrieval_timestamp`. Converter wall-clock must **not** be used for `retrieval_timestamp`. Refuse if omitted or unparseable.

Output pack path must be **outside** the git work tree for real runs (tests may use temp dirs). If `--out` exists and is non-empty → **refuse** (no `--force`).

---

## Inputs

1. **Private Stooq daily CSV** (Todd-held; never committed):
   - Expected Stooq-shaped columns (header row, case-insensitive): `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.
   - Date forms accepted: `YYYY-MM-DD` or Stooq `YYYYMMDD`.
   - Optional Stooq ticker / `<TICKER>` column: if present, every row must be SPY (or Stooq SPY.US form Todd documents in the PR); mismatch → refuse.
   - Encoding: UTF-8 (refuse if undecodable).
2. **CLI constants for this entitlement** (defaults matching HA-1 + signed AUTHORIZE):
   - `symbol` / declaration `universe` = `SPY`
   - `provider` = `STOOQ`
   - `provenance_class` = `HISTORICAL`
   - `interval` = `1d`
   - `adjustment_policy` = CLI/declaration value Todd supplies for the private pack (common candidates: `UNADJUSTED` or a documented Stooq-adjusted label). **Do not treat UNADJUSTED as verified.** Before first MEASURED acceptance, Todd verifies Stooq closes vs official SPY closes around a recent window and a quarterly dividend date, then records the verified policy in the runbook / report handoff.
   - `locked_question` = `ordinary close-to-close changes for one symbol`
   - `primary_metric` = `close-to-close difference`  ← Phase 5 metric = **difference**
   - `transformation_version` = `stooq-daily-ohlcv-v1` (converter identity; must match every envelope)
   - `timezone` = **`America/New_York`** (signed default; UTC rejected — UTC 14:00 stamped closes before they exist)

---

## Outputs — pack layout

One directory:

```text
<pack>/
  declaration.json
  obs_0001.json
  obs_0002.json
  …
```

- **No** `.csv`, `.parquet`, `.pkl`, or other unexpected suffixes in the pack (HA-1: `.csv` fails `unexpected-files`; does not alone fail `session`).
- Observation filenames: `obs_NNNN.json` zero-padded, chronological by `market_timestamp` (same pattern as `tests/test_ha1_historical_admission.py`).
- `declaration.json` required fields (as emitted by HA-1 helper / `DatasetDeclaration` on main):  
  `dataset_id`, `provenance_class`, `provider`, `universe`, `interval`, `timezone`, `transformation_version`, `adjustment_policy`, `locked_question`, `primary_metric`  
  Optional: `max_staleness` only if Todd supplies a value; default omit.

### declaration.json (HA-1 binding values)

| Field | Value |
|---|---|
| `dataset_id` | e.g. `spy-stooq-ha1-private` (stable slug; not a claim) |
| `provenance_class` | `HISTORICAL` |
| `provider` | `STOOQ` |
| `universe` | `SPY` |
| `interval` | `1d` |
| `timezone` | `America/New_York` |
| `transformation_version` | `stooq-daily-ohlcv-v1` |
| `adjustment_policy` | Todd-supplied / verified before MEASURED (see Inputs) |
| `locked_question` | `ordinary close-to-close changes for one symbol` |
| `primary_metric` | `close-to-close difference` |

Auditor procedural check (HA-1 R1.3, not a code gate): `universe=SPY` and `provider=STOOQ` match the HA-1 AUTHORIZE memo **exactly**.

### Each `obs_NNNN.json` (strict non-FIXTURE shape)

Matches what `tests/test_ha1_historical_admission.py` `_write_obs` emits after intake hardening:

```json
{
  "envelope": "<EvidenceEnvelope.serialize() string OR equivalent object>",
  "payload": {
    "close": "<decimal string>",
    "high": "<decimal string>",
    "low": "<decimal string>",
    "open": "<decimal string>",
    "volume": "<decimal string>"
  },
  "payload_checksum": "<sha256 hex>"
}
```

- Payload keys **only** from the OHLCV canonical set `close` / `open` / `high` / `low` / `volume` (extras → `EXTRA_PAYLOAD_KEY`).
- All five values are **decimal strings** (JSON numbers refused: `JSON_NUMBER_NOT_STRING`). Prefer normalized decimal text without scientific notation (e.g. `"472.23"`, `"1234567"`).
- `payload_checksum` **required** (missing → `MISSING_PAYLOAD_CHECKSUM`).
- Duplicate JSON keys refused at parse (`duplicate JSON key`).

### Envelope fields (per row)

Use `EvidenceEnvelope.create(...)` (or byte-identical manual construction). Live create kwargs on main:

| Field | Rule |
|---|---|
| `provenance_class` | `HISTORICAL` |
| `provider` | `STOOQ` |
| `symbol_or_universe` | `SPY` (must equal declaration `universe`) |
| `market_timestamp` | Timezone-aware ISO-8601 **with microseconds and numeric offset**. Under signed `America/New_York`: that calendar date at **16:00:00.000000** with the **correct DST offset** via `ZoneInfo` (do **not** hard-code `-04:00`). Offset must satisfy `timezone_offset_matches` vs declared timezone. **Do not use UTC 14:00** (lookahead). |
| `retrieval_timestamp` | From required `--retrieved-at` (same value for all rows in one convert run, or Todd-documented per-file capture time). Timezone-aware; must not precede that row's `market_timestamp`. **Not** converter wall-clock. |
| `interval` | `1d` |
| `timezone` | `America/New_York` (same string as declaration) |
| `transformation_version` | `stooq-daily-ohlcv-v1` |
| `checksum` | From `EvidenceEnvelope.create` / `compute_checksum` (canonical envelope JSON, checksum field excluded) |

**Windows / ZoneInfo:** if `ZoneInfo("America/New_York")` fails, document that `tzdata` (`pip install tzdata`) is required. Fail closed (refuse), do not fall back to UTC.

---

## `payload_checksum` algorithm (from code — do not invent)

Verified on main in `radar_v4/observation.py` (`ObservationPayload.compute_checksum` via `canonical_payload`):

1. Build canonical payload dict with keys exactly: `close`, `high`, `low`, `open`, `volume` (values are `str | None`).
2. `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True)`.
3. Encode UTF-8.
4. SHA-256 hex digest.

```python
# Equivalent to ObservationPayload.compute_checksum on main
encoded = dumps(
    {"close": close, "high": high, "low": low, "open": open_, "volume": volume},
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=True,
).encode("utf-8")
payload_checksum = sha256(encoded).hexdigest()
```

Prefer calling `Observation.create(envelope, payload)` so envelope + payload checksums stay library-identical. Converter tests must assert equality against `ObservationPayload.compute_checksum()` (which hashes `canonical_payload()`).

---

## Refusal cases (converter exits nonzero; writes no partial pack, or leaves pack untouched)

| Case | Behavior |
|---|---|
| Missing/unreadable CSV | Refuse |
| Missing required columns | Refuse |
| Undecodable / non-UTF-8 | Refuse |
| Ticker column present and ≠ SPY (or documented Stooq SPY form) | Refuse |
| Empty series | Refuse |
| Duplicate dates | Refuse |
| Non-decimal / blank OHLC or volume | Refuse |
| JSON-number temptation: never emit numeric JSON for prices | N/A (emitter rule) |
| OHLC contradiction (high < low, open/close outside high/low) | **Whole-file refuse** (no partial pack) |
| Negative volume | Refuse |
| `--out` exists and is non-empty | **Refuse** (no `--force`) |
| Missing / invalid `--retrieved-at` | Refuse |
| Any network attempt | Not implemented — static refuse if someone adds it |
| Symbol/provider CLI args ≠ SPY/STOOQ under this AUTHORIZE | Refuse (second symbol needs a new AUTHORIZE) |
| `ZoneInfo` unavailable for America/New_York | Refuse (install `tzdata`; do not fall back to UTC) |

---

## Tests (synthetic / fixture Stooq-shaped CSV only)

| Path | Rule |
|---|---|
| `tests/test_stooq_to_strict_pack.py` (name flexible) | Unit tests for converter |
| Fixture CSV | **Synthetic only** — e.g. `tests/fixtures/stooq_shaped/spy_synthetic_daily.csv` with obviously fake decimals (`100.00`, `101.50`, …). **No real SPY/Stooq market bytes in git.** |
| Assert | Pack loads with `load_dataset_pack(..., allow_historical=True)`; strict intake accepts; `payload_checksum` matches library; `unexpected-files` clean; optional tiny `session --allow-historical` MEASURED on synthetic closes (difference metric); `market_timestamp` uses America/New_York 16:00 + ZoneInfo offset; `retrieval_timestamp` equals `--retrieved-at`. |
| Assert refuse | Bad headers, missing `--retrieved-at`, nonempty `--out`, duplicate dates, ticker mismatch, OHLC contradiction (whole-file), ZoneInfo fallback attempts. |

Do **not** add network tests. Do **not** commit Todd’s private CSV.

---

## NON-ALLOWS (design ceiling)

- `prepare-observation` CLI / custody writer  
- Network / HTTP / Stooq download inside `radar_v4/` (or inside this tool)  
- Commit of real Stooq/SPY market bytes  
- LIVE provenance  
- Second symbol (VTI, QQQ, …)  
- Widening HA-1 entitlement or replacing HA-1 AUTHORIZE  
- Snapshot / export of HISTORICAL packs  
- Q-011, Phase 6–9, commercial redistribution  
- UTC 14:00 market_timestamp default  
- Converter wall-clock as `retrieval_timestamp`  
- `--force` on nonempty `--out`  
- Treating converter success as market-correctness or MEASURED acceptance (Claude still accepts the first real run; `adjustment_policy` verified first)

---

## Implementation notes for Cursor (after signed AUTHORIZE)

1. Implement tool + tests only; no docs claim of MEASURED completion.  
2. Reuse `EvidenceEnvelope.create` + `Observation.create` for checksum identity.  
3. Keep CSV out of pack; converter reads CSV from private path, writes JSON pack only.  
4. Claude audits diff against this design + AUTHORIZE NON-ALLOWS before Todd accepts land.

**Tools verify. Cursor codes after AUTHORIZE. Claude audits. Todd authorizes.**
