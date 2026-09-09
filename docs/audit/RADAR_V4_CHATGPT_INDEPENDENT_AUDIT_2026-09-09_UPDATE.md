# Radar V4 — ChatGPT Independent Audit Update (code-level)

**Audit date:** 2026-09-09  
**Kind:** follow-up to `docs/audit/RADAR_V4_CHATGPT_INDEPENDENT_AUDIT_2026-09-09.md`  
**Posted against:** https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/35  
**Authority created by this record:** NONE  
**Horizon 2 authorized:** NO

The first independent disposition on PR #35 was **PASS WITH DECLARED VERIFICATION LIMITATION**, because 317 tests had not been independently re-run. This update records a later code-level pass on items 1 and 2, and leaves items 3–5 as **not yet independently module-opened**.

**Tools verify. Todd authorizes.**

---

## Updated posture

```text
ITEM 1  317 TESTS — INDEPENDENTLY RE-RUN (pytest tests/; 317 passed in 26.33s)
        SOFTWARE CORRECTNESS ON THE TEST SUITE — CONFIRMED
        DATA CORRECTNESS — STILL NOT EARNED

ITEM 2  HISTORICAL/LIVE PACK LOAD REFUSED — CONFIRMED AT CODE
        PACK_ALLOWED_PROVENANCE = {FIXTURE, SYNTHETIC}
        ENFORCED IN load_dataset_pack AT DECLARATION AND OBSERVATION
        REPEATED IN export_lock / pack_export / snapshot_lock / fixture_pack

ITEMS 3–5  FILE LAYOUT CONSISTENT — NOT YET MODULE-OPENED INDEPENDENTLY
           IMPLEMENTER LINE POINTERS BELOW — FOR AUDITOR CONFIRMATION

ITEM 6  NEXT CLASS — TODD-NAMED HISTORICAL SOURCE, OR STOP — REAFFIRMED
```

The earlier limitation **“317 not independently re-run” is closed for the test-suite count.** It is not closed for data correctness. Passing tests means the code behaves as its own tests specify. It does not mean the data are real, current, or historically valid.

---

## Item 1 — independent suite re-run

Auditor executed:

```text
pytest tests/
317 passed in 26.33s
```

That matches the implementer `unittest` count of 317. Two runners, same count.

This is software correctness. Keep the distinction.

---

## Item 2 — pack loader, at the code

Independent findings match the tree:

- `radar_v4/fixture_pack.py` line 11: `PACK_ALLOWED_PROVENANCE = frozenset({"FIXTURE", "SYNTHETIC"})`
- `radar_v4/dataset_pack.py` lines 104–110: declaration provenance not in that set → `PACK_PROVENANCE_NOT_ALLOWED`
- `radar_v4/dataset_pack.py` lines 122–132: accepted observation envelope not in that set → quarantined with the same code
- Loader docstring: HISTORICAL and LIVE are quarantined even if identity-valid; this loader is not a market-data client and does not relabel records
- Same allowed-set gate in `fixture_pack.py` (envelope load), `export_lock.py`, `pack_export.py`, and `snapshot_lock.py`

**Precision, not a contradiction:** in-memory `admit_to_dataset()` matches envelopes to a declaration and does not itself download. If a test constructs a HISTORICAL declaration and HISTORICAL envelopes, admission can succeed in memory. That is not `load_dataset_pack`. There is still no vendor client and no HISTORICAL/LIVE **pack ingest** path. Horizon 2 still needs a separate Todd authorization to admit HISTORICAL through the pack loader.

---

## Items 3–5 — yes, open these specifically

File layout is consistent with the claims. That is not yet the same standard as items 1 and 2.

Independent auditor should open, at minimum:

| Claim | Open | What “verified” looks like |
|---|---|---|
| 3. Distinct refusals | `radar_v4/cadence_lock.py` ~108–118 | `eval_rank < bar_rank` → `CADENCE_OVERRUN` |
| 3. Distinct refusals | `radar_v4/current_claim.py` ~66–72 | `claim_current is True` and stamp after last bar → `FRESH_STAMP_STALE_BARS` |
| 3. Distinct refusals | `radar_v4/horizon_lock.py` ~107–116 | `include_through` after `as_of` → `LOOKAHEAD_WINDOW` |
| 3. Distinct refusals | `radar_v4/horizon_bind.py` ~65–71 | pack last bar after `as_of` → `LOOKAHEAD_BAR` |
| 3. Tests | `tests/test_units_1151_1200.py` | asserts `CADENCE_OVERRUN` |
| 3. Tests | `tests/test_units_1201_1250.py` | asserts `FRESH_STAMP_STALE_BARS` |
| 3. Tests | `tests/test_units_1251_1300.py` | asserts `LOOKAHEAD_WINDOW` and `LOOKAHEAD_BAR` as separate cases |
| 4. Unit 1300 | `tests/test_units_1251_1300.py` `test_highest_unit_is_1300` | `PHASE5_HIGHEST_UNIT == 1300`; status `measured=false`; no `claim_level` |
| 4. Inspectability | `docs/phase5/README_PHASE5.md` units 1251–1300 paragraph | “inspectability only; not a research result”; lookahead is the inverse of freshness, not a wrap |
| 5. Docs-only PR | `git diff main...HEAD --stat` on this branch | documentation files only; no `radar_v4/*.py` |

Implementer already opened those modules for this packet. That does **not** substitute for the independent open. ChatGPT should still read the four lock files and the three test files above, then confirm or refute.

Do not treat `test_units_*.py` growing in blocks of 50 as progress toward data correctness.

---

## Item 6 — reaffirmed

The repo’s own pack gate confirms there is no path to real data without a named source. More Phase 5 unit-batch work would exercise the same refusal machinery against fixtures again. It would not close the gap.

```text
NEXT CLASS OF WORK
  TODD-NAMED HISTORICAL SOURCE, OR STOP
```

---

## What this update does not do

```text
NO IMPLEMENTATION CHANGES
NO VENDOR SELECTED
NO SCOPE ENLARGED
NO HORIZON 2 AUTHORIZED
NO MERGE AUTHORIZED
ITEMS 3–5 NOT PROMOTED TO INDEPENDENT MODULE VERIFICATION
```

**Learning and Earning It.**  
**Stay on course. No drift.**
