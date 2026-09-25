# Runbook stub — first SPY/STOOQ MEASURED (after converter exists) — TC

**Status:** STUB — steps only; not an AUTHORIZE; no fabricated prices
**Date:** 2026-09-24 (America/Chicago)
**Revision:** R1.1 — record verified `adjustment_policy` in Claude handoff (Todd review)
**Repo:** `z9p546sts2-dev/chatawa-radar-v4`
**Authority already in force for the run shape:** HA-1 `docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md`
**Converter charter:** companion BUILD UNIT + AUTHORIZE (IN FORCE with edits — America/New_York; required `--retrieved-at`)
**Metric:** close-to-close **difference** (Phase 5 LEVEL 0)
**Operating split:** Grok plans · Cursor codes · Claude audits · Todd authorizes

This page does **not** invent prices, does **not** authorize LIVE, and does **not** replace HA-1.

---

## Preconditions (stop if any fail)

1. Converter AUTHORIZE signed and banked; converter landed on main; Claude audit of converter PR clean enough for Todd to proceed.  
2. HA-1 still IN FORCE (SPY / STOOQ only).  
3. Private Stooq SPY daily CSV exists **outside** the repo (Todd’s machine or private path).  
4. Capture time for that CSV is known (will be passed as `--retrieved-at`).  
5. **`adjustment_policy` verified** — compare several recent Stooq closes to official SPY closing prices, and check a date around a quarterly dividend; declare what Stooq actually is (do not assume `UNADJUSTED`). Record the verified label for the pack declaration and for Claude.  
6. No real market bytes staged for commit.

---

## Steps

1. **Private capture** — Obtain/retain Stooq SPY daily CSV privately. Record download/capture time. Do not copy it into the git work tree.  
2. **Convert** — Run the authorized offline converter, e.g.  
   `python tools/stooq_to_strict_pack.py --csv <PRIVATE.csv> --out <PRIVATE_PACK_DIR> --symbol SPY --provider STOOQ --retrieved-at <CAPTURE_ISO8601>`  
   Pack dir stays outside the repo. Confirm converter exit 0. Expect America/New_York 16:00 market timestamps (ZoneInfo DST). On Windows, ensure `tzdata` is installed if ZoneInfo fails.  
3. **unexpected-files** — Workshop CLI:  
   `unexpected-files --pack <PRIVATE_PACK_DIR>`  
   Must be clean (no `.csv` or other unexpected suffixes in the pack).  
4. **session** —  
   `session --pack <PRIVATE_PACK_DIR> --allow-historical --report <PATH_OUTSIDE_REPO>/spy_stooq_session_report.json`  
   Do **not** pass snapshot/export flags. Report path must be outside the repo.  
5. **Sanity (human)** — Confirm report shows LEVEL 0 MEASURED (or honest non-MEASURED with reasons); declaration `universe=SPY`, `provider=STOOQ`, `timezone=America/New_York`; quarantine count zero or every quarantined row explained (HA-1 first-run hygiene).  
6. **Claude accept** — Hand Claude: converter AUTHORIZE path, HA-1 memo path, report path (or redacted summary **without** pasting market series into git), unexpected-files result, **and the verified `adjustment_policy` label plus how it was checked** (official closes / dividend-date note). Claude audits claim language + provenance.  
7. **Todd** — Accept, hold, or STOP. Do not treat green software tests as market acceptance.

---

## Explicit non-steps

- No network download from inside `radar_v4/`.  
- No `prepare-observation`.  
- No commit of CSV, pack, or report that contains real Stooq series.  
- No second symbol. No LIVE. No HA-1 rewrite.  
- No assuming `UNADJUSTED` without the pre-MEASURED check above.

**Tools verify. Cursor does not run the private MEASURED for Todd. Claude audits. Todd accepts.**
