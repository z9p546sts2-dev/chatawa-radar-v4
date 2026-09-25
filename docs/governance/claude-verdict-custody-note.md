# Claude verdict custody note — 2026-09-24

**Purpose:** One-page bank pointer. Claude audited from GitHub; this note records disposition only. It does **not** restate or re-litigate Claude’s finding text.

**Repo:** `z9p546sts2-dev/chatawa-radar-v4`  
**Audit date:** 2026-09-24 (America/Chicago)  
**Executor drafting this note:** Grok Bot (custody pointer only)

## What Claude audited (sources)

- Live GitHub `main` after HA-1 #47 (`a7451e4605ffb6914d4b1541add086c11fb1c2bb`)
- HA-1 AUTHORIZE memo `docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md`
- VTI after-the-fact AUTHORIZE `docs/governance/2026-09-24-vti-private-date-observe-authorize-TC.md` / Item 1c memo↔code lane
- Open PR 43 (observation integrity + `prepare-observation`) at head `76737024e69f348132abf1317f4b7bdac21b8375`

## Verdicts / dispositions (custody)

| Lane | Claude disposition (controlling) | Todd next |
|---|---|---|
| Docs vs HA-1 | Stale “historical not authorized / session refuses HISTORICAL” claims remain on `main` (GOVERNANCE ~60/~66/~322; ROADMAP ~187; README ~7/~18). **Docs-only reconciliation required**; cite `docs/governance/2026-09-24-ha1-authorize-spy-stooq-TC.md` + `a7451e4605ffb6914d4b1541add086c11fb1c2bb`. Keep claim ceiling: SPY/STOOQ private MEASURED + `--allow-historical` only; LIVE refused. | Accept/edit `2026-09-24-docs-recon-ha1-historical-TC.md` then docs PR |
| VTI memo factual line | Session-refuse HISTORICAL wording is stale after HA-1 — **ADDENDUM or patch note**; do not silently rewrite signed AUTHORIZE fence | Initial addendum |
| PR 43 | **Do not merge as-is.** Split: KEEP intake hardening + HA-1 test helper fix (not assertions); SPLIT OUT `prepare-observation` (no AUTHORIZE; Tiingo Starter hold) | Sign/reject intake-hardening AUTHORIZE candidate; narrowing PR |
| VTI Item 1c | Follow-ups remain open (receipt Date cross-check; status vocabulary; `marketPrice` TBD; N=10 + refuse-storm TBD). **Not audit-closed** | Answer TODD gaps in named fix item |
| Metric / sides | Phase 5 metric remains **difference**. VTI is side path. No Q-011 / Phase 6–9 from these lanes | Hold |

## Drafts banked for Todd (this folder)

1. `2026-09-24-docs-recon-ha1-historical-TC.md`
2. `2026-09-24-authorize-observation-intake-hardening-TC.md` (UNSIGNED)
3. `2026-09-24-vti-followups-named-fix-item-TC.md`
4. This custody note

## Non-actions (binding for tools)

- No PR merge, no PR review comments, no clone required for this custody bank, no cloud-agent launch from this note.
- No fabricated SHAs — HA-1 `a7451e4605ffb6914d4b1541add086c11fb1c2bb` verified via GitHub commit API (node_id decodes to same hex); PR 43 head `76737024e69f348132abf1317f4b7bdac21b8375` from pull object.

**Tools verify. Claude audits. Todd authorizes.**
