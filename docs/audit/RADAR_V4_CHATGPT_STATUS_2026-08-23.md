# Status report for ChatGPT — Radar V4 as of 2026-08-23

```text
TO — ChatGPT (independent auditor)
FROM — Cursor (bounded implementer)
AUTHORITY — Todd C. (toddmcraft@gmail.com) only
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4
SOFTWARE HEAD — cb4936a (main)
DATE — 2026-08-23
RECORD TYPE — IMPLEMENTER STATUS FOR INDEPENDENT AUDIT
NOT — a method claim, performance report, or authorization of the next class of work
```

Todd asked for a current-status report you can use. This is implementer-reported. It is not your independent audit.

**Tools verify. Todd authorizes.**

---

## 1. Where we are

Radar V4 is a human-controlled local evidence workshop. It is not a trader, execution engine, broker, signal factory, or a revival of Radar V1/V2.

`main` now carries Build Units 1–6 and Phase 5 units **7–1300**. Open pull requests: none. Last merges: #31 (freshness / current-claim) and #32 (lookahead horizon).

Product order Todd locked:

1. **Product A** — evidence system first (later packagable as SaaS that sells records and refusals, not trades).
2. **Product B** — a separately named autonomous trading program, only if a method is later earned. “Best trades” is a prohibited claim.

The locked Phase 5 question is already written in `docs/phase5/RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`:

> In one declared daily dataset for one symbol, what are the ordinary close-to-close differences when every observation uses the same interval, timezone, and transformation version?

That is LEVEL 0 — MEASURED only. Difference, not percent. LIVE refused. Allowed statuses: `MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`.

---

## 2. What is earned vs not earned

Four classes stay separate. Do not collapse them.

| Class | State |
|---|---|
| Software correctness | Implementer suite on this HEAD: **317 passed**, 0 failed. Reason-code catalog valid (**279**). Document-kind catalog valid (**351**). `python -m radar_v4 status` reports `highest_unit=1300`, `measured=false`, no `claim_level`. |
| Data correctness | **Not earned.** The only loadable measurement pack in-repo is SYNTHETIC (`fixtures/synthetic_one_symbol_1d/`). `HISTORICAL` and `LIVE` remain quarantined in the pack loader even if identity-valid. |
| Method validity | **Not defined.** No feature, threshold, score, ranking, or inherited V1/V2 method. |
| Usefulness / edge | **Not shown.** `NO EDGE SHOWN` remains a valid later ending. It was not asked by the locked question. |

Authorization of Phase 5, and completion of units 7–1300, do **not** authorize a vendor API, Phase 6, paper trading, or Product B. There is no unit count that unlocks a paid API.

---

## 3. What the local workshop can actually do

On SYNTHETIC / FIXTURE only, the workshop can:

- admit a declared one-symbol daily pack and refuse a bad record without repair;
- describe ordinary close-to-close difference;
- persist, verify, export, and compare snapshots;
- journal refusals;
- lock and re-verify custody by `source_path` + `source_digest`;
- name changed / extra / missing members;
- refuse evaluation cadence that outruns bar interval (`CADENCE_OVERRUN`);
- refuse a later stamp that claims the series is current (`FRESH_STAMP_STALE_BARS`);
- refuse a window or pack bar after `as_of` (`LOOKAHEAD_WINDOW` / `LOOKAHEAD_BAR`).

Those last three are distinct refusals, not wrappers of one inspector:

- cadence: decision clock faster than the bars;
- freshness: later clock claiming stale bars are current;
- lookahead: using a bar that would not have been known at `as_of`.

Stdlib only. Command: `PYTHONPATH=. python3 -m unittest discover -s tests -v`.

---

## 4. Independent-audit gap

Your only completed independent audit is PR #8 / units 7–100: **PASS WITH MATERIAL OPEN ITEMS**. The two recorded open items (branch-custody headlines; `verify` must recompute) were implementer-repaired after that audit.

Units **101–1300** are inspectability continuation. They have **not** had a ChatGPT independent audit. Treat later implementer snapshots as claims to verify, not as findings.

If you audit next, start from `main` at `cb4936a`. Do not treat unit count as research progress. A useful audit would check whether:

- `status` is still a capability statement (`measured: false`, no `claim_level`);
- SYNTHETIC numbers are still not treated as HISTORICAL evidence;
- `HISTORICAL` / `LIVE` still cannot load through the pack loader;
- no network client or vendor adapter was added;
- freshness and lookahead remain inverse refusals, not one lock renamed;
- completing unit 1300 is still not being used as authorization of a later class.

The running handoff with earlier slice snapshots is `docs/audit/RADAR_V4_CHATGPT_AUDIT_HANDOFF.md`.

---

## 5. What is required to go further

Further work is a **class change**, not more Phase 5 unit slices.

Horizon 2 is still open: one real historical series, one already-locked question, an honest measured / unclear / invalid result.

Already present for that gate:

- locked question, metric, interval (`1d`), one-symbol scope;
- ordinary close-to-close baseline on admitted series;
- provenance and quarantine machinery;
- refusal of unknown provenance, cadence overrun, stale-as-current, and lookahead.

Still required before any purchase or download:

1. **Todd names the source.** A specific vendor/API, or a bounded static historical file. Free Yahoo / Stooq / Alpha Vantage is still a vendor/download. Do not invent a vendor.
2. **Written reason** a paid or downloaded source is required instead of a smaller bounded file.
3. **Declared adjustment policy and maximum staleness** for that source. Do not invent a market calendar or fill missing bars.
4. **Separate authorization** to admit `HISTORICAL` through the pack loader. That quarantine is intentional.
5. Then run the locked question on that series. Allowed endings remain `MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`.

Todd has held the vendor. Until he names it, the honest next step is stop or continue local refusal/custody work. Continuing units does not finish Horizon 2.

Still unauthorized after that, unless Todd separately authorizes them:

- Phase 6 method research;
- paper trading (Horizon 4A, only after a locked historical pilot);
- Product B;
- treating a successful HISTORICAL measurement as edge.

---

## 6. Ask to ChatGPT

Please treat this as a status packet, not as proof.

If you audit: confirm or refute the earned/not-earned table, the three distinct refusals, and the claim that unit 1300 does not change the claim class.

If you advise Todd on “what is left”: the remaining work is a named HISTORICAL source plus an honest result on the locked question. It is not a remaining unit quota.

```text
SOFTWARE CORRECTNESS — IMPLEMENTER-REPORTED AT 317 TESTS ON cb4936a
DATA CORRECTNESS — NOT EARNED
METHOD VALIDITY — NOT DEFINED
USEFULNESS / EDGE — NOT SHOWN
VENDOR / LIVE / PAPER / PHASE 6 / PRODUCT B — NOT AUTHORIZED
INDEPENDENT AUDIT THROUGH UNIT 100 ONLY
UNITS 101–1300 — INSPECTABILITY; AWAITING CHATGPT REVIEW
NEXT CLASS OF WORK — TODD-NAMED HISTORICAL SOURCE, OR STOP
```

Learning and Earning It.  
Stay on course.  
No drift.
