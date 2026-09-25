# AUTHORIZE — observation intake hardening ONLY (SIGNED) — TC

**Status:** AUTHORIZED — IN FORCE (AFTER-THE-FACT CUSTODY) — intake hardening half of PR 43 only
**Accepted:** Accept as written — TC (2026-09-24)
**PATCH AUTHOR:** tool at Todd's direction (Chatawa Labs / Cursor account commits under Todd direction)  
**Date drafted:** 2026-09-24 (America/Chicago)  
**Authority required:** Todd C. (`TC`)  
**Style:** After-the-fact AUTHORIZE memo (same custody pattern as `docs/governance/2026-09-24-vti-private-date-observe-authorize-TC.md`)  
**Repo:** `z9p546sts2-dev/chatawa-radar-v4`  

**Does not authorize:** `prepare-observation` CLI, Tiingo Starter custody, real-data admission, network in `radar_v4/`, market bytes in git, Q-011, Phase 6–9, HA-1 entitlement expansion, withdrawn SPY carve-out revival.

Claude controlling audit (2026-09-24): **do not merge PR 43 as-is.** Split. Keep intake hardening + fix HA-1 test helper only; leave `prepare-observation` out pending separate decision / Tiingo Starter hold.

---

## Relation to PR 43

| Item | Value |
|---|---|
| PR | https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/43 |
| Title | Validate, inspect, and privately prepare manual observations |
| Head (at audit) | `76737024e69f348132abf1317f4b7bdac21b8375` (`codex/observation-numeric-integrity`) |
| Base at open | `4a4902c74e538465021b998533db99bc3c36c76f` (behind HA-1/VTI — **must rebase** onto `main` including `a7451e4605ffb6914d4b1541add086c11fb1c2bb`) |
| Disposition | **DO NOT MERGE AS-IS** |

### KEEP (this AUTHORIZE candidate’s scope)

1. **Strict non-FIXTURE / non-SYNTHETIC observation JSON intake** (`radar_v4/observation_json.py` + tests):
   - prices as **decimal strings** (refuse JSON numbers);
   - **OHLCV-only** payload keys (refuse extras);
   - **required** `payload_checksum` on non-FIXTURE/non-SYNTHETIC;
   - duplicate-key refusal as in the PR.
2. **Observation validation** (`radar_v4/observation_validation.py` + tests): refuse nonfinite OHLCV, negative volume, open outside high/low.
3. **`show-observation` exit semantics**: nonzero when intake is not clean (parse/integrity only — not admission/freshness/calendar).
4. **HA-1 test helper fix only** (`tests/test_ha1_historical_admission.py` pack emitter): emit **strict-valid** HISTORICAL observation JSON so tests stay green under stricter intake. **Do not weaken assertions.**

### SPLIT OUT (explicit non-allows)

- Entire `prepare-observation` CLI route and `radar_v4/manual_observation.py` custody writer.
- Tiingo Starter (or trial) persistent custody — **hold** until paid/licensed retention is separately verified.
- Real-data pack admission beyond existing HA-1, network in `radar_v4/`, market bytes in git, Q-011, Phase 6–9.

**Landing plan:** rebase hardening-only commits onto current `main` (`a7451e4605ffb6914d4b1541add086c11fb1c2bb` or newer); strip `prepare-observation` from #43 or open a narrowing PR; bank this memo under `docs/governance/` after Todd signs; merge hardening half only.

---

## DECISION block (UNSIGNED — Todd fills)

```text
DECISION: AUTHORIZE OBSERVATION INTAKE HARDENING — TC
          (AFTER-THE-FACT CANDIDATE FOR PR 43 HARDENING HALF)

SCOPE:
  - Strict non-FIXTURE/non-SYNTHETIC observation JSON intake:
      decimal-string prices; OHLCV-only payload keys; required payload_checksum;
      duplicate-key refusal as implemented in the hardening commits.
  - Observation validation refusals for nonfinite OHLCV, negative volume,
      open outside high/low (as in PR 43 hardening).
  - show-observation exit semantics tied to intake_clean (parse/integrity only).
  - HA-1 test helper emits strict-valid packs (helper only; assertions unchanged).

CLAIM CEILING:
  Software-correctness / intake-integrity only. No MEASURED entitlement change.
  No HISTORICAL admission change beyond what HA-1 already authorized.
  Phase 5 primary metric remains close-to-close difference.
  VTI remains a separate side path.

EXPLICIT NON-ALLOWS:
  - prepare-observation CLI route and manual_observation custody writer
  - Tiingo Starter (or trial) persistent custody / retention
  - Real-data admission beyond existing HA-1 SPY/STOOQ private MEASURED gate
  - Network / HTTP client inside radar_v4/
  - Market bytes or licensed series in git
  - Q-011 data authorization
  - Phase 6–9
  - Withdrawn SPY one-ETF daily observe carve-out revival
  - Treating intake_clean as freshness, calendar, or pack-admission proof

PATCH AUTHOR:      tool at Todd's direction
                   (commits may appear as Chatawa Labs / Cursor account)

RELATION TO PR 43:
  Land hardening half after rebase onto main including HA-1 a7451e4605ff….
  prepare-observation stays out / awaits separate future decision + license check.

RELATION TO HA-1 / VTI:
  Does not widen HA-1 (docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md).
  Does not change VTI (docs/governance/2026-09-24-vti-private-date-observe-authorize-TC.md).

OPEN ITEMS (Claude-flagged; signing does not close them):
  - Rebase risk vs HA-1/VTI CLI and reason-code catalogs on main
  - Tiingo ToS persistent-storage hold must remain visible if prepare-observation returns later
  - Windows ACL privacy non-claim if any custody code returns later
  - Confirm show-observation exit change has no silent overclaim in docs
  - Confirm HA-1 helper fix does not relax production gates

DATE OF THIS CANDIDATE MEMO: 2026-09-24
TODD:                        TC
```

---

## Acceptance (Todd)

- [x] Accepted as written — TC — date 2026-09-24
- [ ] Accepted with edits attached
- [ ] Hold
- [ ] Reject — do not land hardening half

**Todd signature / date:** TC / 2026-09-24

---

## Banking path (after signature)

Suggest bank at:

`docs/governance/2026-09-24-authorize-observation-intake-hardening-TC.md`

Then point the narrowing PR body at that path. Do not bank an AUTHORIZE for `prepare-observation` under this filename.

**Tools verify. Cursor codes hardening only after Todd signs. Claude audits. Todd authorizes.**
