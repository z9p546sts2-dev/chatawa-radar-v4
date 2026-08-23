# ChatGPT Audit Handoff — Radar V4 through Unit 1300

```text
CURRENT SNAPSHOT DATE — 2026-08-23
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4
CURRENT BRANCH — cursor/phase-5-units-1251-1300-9fd5
CURRENT PR — https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/32
CURRENT SOFTWARE HEAD — 2ebf070
IMPLEMENTATION HEAD — 2ebf070 (units 1251–1300)
TEST-COUNT HEAD — pending this commit
BASE — cursor/phase-5-units-1201-1250-9fd5 at cfdbb72 (draft #31; units 7–1250)
STACKED OPEN PRS — #31 and #32
AUTHORITY — Todd C. (toddmcraft@gmail.com) only
IMPLEMENTER — Cursor (bounded engineer)
INDEPENDENT AUDITOR — ChatGPT
IMPLEMENTER-EXECUTED DISPOSITION — SOFTWARE PATH VERIFIED AT 317 TESTS; CLAIM CLASS UNCHANGED
FIRST INDEPENDENT AUDIT (PR #8 / units 7–100) — PASS WITH MATERIAL OPEN ITEMS
```

The block below is the original first-audit identity. Keep it as history. Do not treat it as current HEAD.

```text
FIRST AUDIT DATE — 2026-08-22
FIRST AUDIT BRANCH — cursor/phase-5-dataset-session-9fd5
FIRST AUDIT PR — https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/8
AUDITED SOFTWARE HEAD — 053fc2808d6fe3b53de984b20f2e9ef6a1a3c15a
HANDOFF-ONLY HEAD — 9851692131c925a8576c6971a6fe984b6a209a50
REMEDIATION SOFTWARE HEAD — 7edc0eeedb21a619d93373390b1581da6c921cbe
FIRST-AUDIT BASE / main — 1ff2333 (then Phase 5 units 7–11 only)
```

This record is for independent audit. It is not a method claim, not a performance report, and not authorization of the next class of work.

**Tools verify. Todd authorizes.**

---

## Implementer-executed snapshot — units 1251–1300

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-1251-1300-9fd5` at `2ebf070`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 317 passed, 0 failed |
| Reason-code catalog | valid; 279 codes |
| Document-kind catalog | valid; 351 kinds |
| `status` | `highest_unit=1300`, `measured=false`, no `claim_level` |
| Window `as_of == include_through == last bar` | `horizon_lock` valid; `horizon_bind` valid |
| `include_through` after `as_of` | `LOOKAHEAD_WINDOW` |
| Pack last bar after `as_of` | `LOOKAHEAD_BAR` |

Completing unit 1300 does **not** authorize a vendor API, Phase 6, paper trading, or Product B. It does **not** treat a later bar as known at an earlier clock.

---

## Implementer-executed snapshot — units 1201–1250

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-1201-1250-9fd5` at `97e2d89`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 312 passed, 0 failed |
| Reason-code catalog | valid; 271 codes |
| Document-kind catalog | valid; 341 kinds |
| `status` | `highest_unit=1250`, `measured=false`, no `claim_level` |
| Honest later stamp (`claim_current: false`) | `freshness_lock` valid; `current_claim` valid |
| Later stamp claiming current | `FRESH_STAMP_STALE_BARS` |
| Stamp equal to last bar claiming current | `current_claim` valid |

Completing unit 1250 does **not** authorize a vendor API, Phase 6, paper trading, or Product B. It does **not** treat a clock as a current series.

---

## Implementer-executed snapshot — units 1151–1200

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-1151-1200-9fd5` at `aa9ccae`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 307 passed, 0 failed |
| Reason-code catalog | valid; 264 codes |
| Document-kind catalog | valid; 331 kinds |
| `status` | `highest_unit=1200`, `measured=false`, no `claim_level` |
| Daily eval on daily bars | `cadence_lock` valid; `cadence_bind` to SYNTHETIC pack valid |
| Intraday eval on daily bars | `CADENCE_OVERRUN` |
| Hourly cadence on daily pack | lock valid; bind `CADENCE_MISMATCH` |

Completing unit 1200 does **not** authorize a vendor API, Phase 6, paper trading, or Product B. It does **not** revive V1/V2 scores.

---

## Implementer-executed snapshot — units 1101–1150

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-1101-1150-9fd5` at `5de5974`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 301 passed, 0 failed |
| Reason-code catalog | valid; 256 codes |
| Document-kind catalog | valid; 321 kinds |
| `status` | `highest_unit=1150`, `measured=false`, no `claim_level` |
| Member locks from copied packs | `member_set` valid |
| Same digest, different members | `content_set` valid; `member_set` `MEMBER_BIND_MISMATCH` |
| Align lock of pack A to copy B | valid; `verify_member_record` of A still valid |
| Changed copy B | `MEMBER_ALIGN_MISMATCH`; original verify still valid |

Completing unit 1150 does **not** authorize a vendor API, Phase 6, paper trading, or Product B.

---

## Implementer-executed snapshot — units 1051–1100

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-1051-1100-9fd5` at `9bacaee`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 295 passed, 0 failed |
| Reason-code catalog | valid; 248 codes |
| Document-kind catalog | valid; 312 kinds |
| `status` | `highest_unit=1100`, `measured=false`, no `claim_level` |
| Two pack copies | `compare_member_lock` valid |
| Changed observation file | `MEMBER_MISMATCH` names `obs_2026-08-08.json`; `compare_content_lock` is `CONTENT_MISMATCH` |
| Added file | `MEMBER_EXTRA` |
| Removed file | `MEMBER_ABSENT` |
| Same digest, different members | `content_bind` valid; `member_bind` `MEMBER_BIND_MISMATCH` |

Completing unit 1100 does **not** authorize a vendor API, Phase 6, paper trading, or Product B.

---

## Implementer-executed snapshot — units 1001–1050

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-1001-1050-9fd5` at `c074334`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 289 passed, 0 failed |
| Reason-code catalog | valid; pending count |
| Document-kind catalog | valid; pending count |
| `status` | `highest_unit=1050`, `measured=false`, no `claim_level` |
| Locks from copied packs | `content_set` valid; `lock_set` `LOCK_BIND_MISMATCH` |
| Pack copy directories | `copy_set` valid; that folder is `CONTENT_SET_EMPTY` |
| Lock-record folder | `copy_set` `COPY_SET_EMPTY` |
| Two such lock folders | `compare_content_set` valid; `compare_lock_set` invalid |
| Mixed content | `CONTENT_BIND_MISMATCH` / `CONTENT_MISMATCH` |

Completing unit 1050 does **not** authorize a vendor API, Phase 6, paper trading, or Product B.

---

## Implementer-executed snapshot — units 951–1000

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-951-1000-9fd5` at `c21fde1` (recorded at `5b70b78`):

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 283 passed, 0 failed |
| Reason-code catalog | valid; 230 codes |
| Document-kind catalog | valid; 293 kinds |
| `status` | `highest_unit=1000`, `measured=false`, no `claim_level` |
| Two copies of the same pack | `compare_content_lock` valid; `compare_digest_lock` invalid (path in serialize) |
| Safety locks from those copies | `content_bind` valid; `bind_lock_records` `LOCK_BIND_MISMATCH` |
| Different content | `CONTENT_MISMATCH` / `CONTENT_BIND_MISMATCH` |

Completing unit 1000 does **not** authorize a vendor API, Phase 6, paper trading, or Product B.

---

## Implementer-executed snapshot — units 901–950

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-901-950-9fd5` at `e6f282c`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 277 passed, 0 failed (at `e6f282c`) |
| Reason-code catalog | valid; 224 codes |
| Document-kind catalog | valid; 284 kinds |
| `status` | `highest_unit=950`, `measured=false`, no `claim_level` |
| Same-source lock bind / lock-set | valid |
| Mixed-source locks | `LOCK_BIND_MISMATCH` |

Completing unit 950 does **not** authorize a vendor API, Phase 6, paper trading, or Product B.

---

## Implementer-executed snapshot — units 851–900

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

Commands run from `cursor/phase-5-units-851-900-9fd5` at `5c157dc`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m radar_v4 status
PYTHONPATH=. python3 -m radar_v4 digest-lock --path fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 digest-status --path fixtures/synthetic_one_symbol_1d
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 271 passed, 0 failed (at `5c157dc`) |
| Reason-code catalog | valid; 216 codes |
| Document-kind catalog | valid; 274 kinds |
| Network-import scan | valid; no vendor/network client imports |
| `status` | `highest_unit=900`, `measured=false`, no `claim_level`, vendor/paper/method/historical all false |
| `digest-lock` | valid on the SYNTHETIC fixture; details include `source_digest` |
| Same-path clean-pack swap | stale safety/digest lock verify fails with `RECORD_MISMATCH` |

Those SYNTHETIC numbers are software-test material. They are **not** market evidence.

Units 851–900 add source-digest custody so path alone is not identity. Completing unit 900 does **not** authorize a vendor API, Phase 6, paper trading, or Product B.

---

## ChatGPT independent audit of PR #22 — remediations

ChatGPT disposition on `2991557`: **PASS WITH MATERIAL OPEN ITEMS**. Merge not recommended until the two open items were repaired. Cursor repaired only. No unit 851. No new claim class.

### OPEN ITEM A — branch custody in controlling headlines

README, ROADMAP, and GOVERNANCE headlines now say this is a **stacked draft branch** through unit 850 and that **`main` is currently through unit 200**.

### OPEN ITEM B — `verify` must recompute

`verify_safety_record`, `verify_leftover_record`, `verify_inventory_record`, `verify_layout_record`, and `verify_manifest_record` no longer accept `document_kind` + `valid: true` alone.

They now require `details.source_path`, recompute the lock from that path, and compare canonical bytes. A fabricated `{document_kind, valid: true}` object is refused. A record written against a pack that later gains leftovers is refused.

A later repair-only pass applied the same recompute+`source_path` rule to the remaining lock-record verifies (`audit`, `chain`, `bundle`, `export`, `sidecar`, `snapshot`, `disposition`, `report`, `ruler`, `journal`, `path`, `name`, `kind`, `stamp`, `byte`, `freeze`). No unit 851. Highest unit remains **850**. Claim class unchanged. Not merged.

---

## Implementer-executed audit snapshot — 2026-08-23

This is a Cursor verification record for ChatGPT. It is **not** ChatGPT’s independent audit, not a method claim, and not authorization of a later class of work.

### Verified on this branch

Commands run from `cursor/phase-5-units-801-850-9fd5` at `b15f8de`:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -c "catalog + status + bounds + stop + network scan"
PYTHONPATH=. python3 -m radar_v4 status
PYTHONPATH=. python3 -m radar_v4 pack-describe --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 session --pack fixtures/synthetic_one_symbol_1d --require-manifest
PYTHONPATH=. python3 -m radar_v4 determinism --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 pack-verify --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 safety-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 leftover-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 safety-status --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 leftover-status --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 inventory-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 layout-lock --pack fixtures/synthetic_one_symbol_1d
```

Observed:

| Check | Result |
|---|---|
| Unittest suite | 264 passed, 0 failed (at `0895354`) |
| Reason-code catalog | valid; 213 codes; no `CATALOG_GAP` |
| Document-kind catalog | valid; 268 kinds; no unknown kinds |
| Network-import scan | valid; no vendor/network client imports |
| `status` | `highest_unit=850`, `measured=false`, no `claim_level`, vendor/paper/method/historical all false |
| `session` on SYNTHETIC pack | `MEASURED`, claim `LEVEL 0 — MEASURED`, changes `0.50`, `-0.50`, ruler `403b2863229368350ac8f20a07a800a6927dc017f0efa6ec0b15305234fc9cee` |
| `determinism` | equal; snapshot `33c25a654b07a7f4adc3f7f0b5ee9a9050ca203caba11aec500010b7a0d78e53` |
| `pack-verify` | stored manifest matches |
| `safety-lock` / `leftover-lock` | valid on the fixture; leftover details `tmp_files=[]`, `orphans=[]` |
| `safety-status` / `leftover-status` | valid; locked unit 850 |
| `inventory-lock` / `layout-lock` | valid |

Those SYNTHETIC numbers are software-test material. They are **not** market evidence.

### Claim-class table now

| Class | Status now |
|---|---|
| Software correctness | Local SYNTHETIC path plus inspectability locks: 264 tests implementer-executed. Not independently re-run by ChatGPT yet. |
| Data correctness | **Not earned.** No HISTORICAL records. Fixture is SYNTHETIC. |
| Method validity | **Not defined.** No Phase 6 authorization. |
| Usefulness / edge | **Not asked. Not shown.** |

### What units 801–850 added

Inspectability wrappers only:

- `radar_v4.safety_lock` wraps `inspect_pack_safety` (BOM, symlink, empty, nested JSON, casefold, UTF-8, size).
- `radar_v4.leftover_lock` wraps `inspect_leftovers` (`.tmp` leftovers, orphan `.sha256`).
- Write/verify/status binds. Highest-unit lock at 850.

They do not measure a market, define a method, or change provenance.

### Merge / authorization facts

- `main` = `56db82f` (units 7–200 only).
- Units 201–850 live on stacked draft PRs #10–#22. **Not merged.**
- Completing unit 850 does **not** authorize a vendor API, Phase 6, paper trading, or Product B.
- `enough_for_close_to_close: true` on pack-describe is descriptive readiness, not a measurement.

### Press these if auditing

1. Unit count 850 can be misread as research progress. It is inspectability.
2. Repeated `MEASURED` on the SYNTHETIC fixture is not a result.
3. Later lock commands wrap earlier inspectors. Ask whether each new lock refuses a new misread, or only restates an old refusal.
4. Older handoff paragraphs still mention first-audit PR #8. Current HEAD is PR #22.

---

## Auditor assignment

Review this repository as an independent auditor. Do not implement. Do not enlarge scope. Do not treat software tests as market evidence.

Answer:

1. Did the implementer stay inside Todd-authorized Phase 5 evidence-ops?
2. Are the earned-claim statements honest?
3. Did later units (especially 43–100) add integrity, or only decorative surface area?
4. Is V1/V2 correctly excluded from inheritance?
5. What, if anything, is overclaimed in README / ROADMAP / GOVERNANCE / this handoff?
6. What is the smallest next authorization that would change the claim class?

Do not recommend buying a vendor API, opening paper trading, or starting Phase 6 unless Todd has already named that authorization.

---

## Roles and control

| Role | Bound |
|---|---|
| Todd C. | Sole authority. Accepts, authorizes, stops. |
| Cursor | Bounded implementer. May write only inside authorized units. |
| ChatGPT | Independent auditor. Verifies claims. Does not authorize. |
| Tests / CLI | Verify software behavior. Do not authorize. |

Exact authorizations used on this path include:

- `AUTHORIZE BUILD UNIT 1 — TC`
- `Accepted-TC` (Units 1 and 2)
- `AUTHORIZE PHASE 5 — TC`
- continued-build phrases (`Lets keep building`, `You can continue to build and not stop after building the units -TC`)
- `Go ahead and do up too 100 units-TC`
- `Lets do 50 more units-TC`
- `I'm back..lets continue`

Ready / complete-within-scope of a unit is **not** authorization of the next *class* of work (vendor API, Phase 6 method, paper trading, Product B).

---

## What Radar V4 is

A **human-controlled local evidence workshop** for one locked Phase 5 question.

It can:

- represent evidence identity and provenance;
- refuse invalid, contradictory, or wrong-provenance records without repair;
- admit a declared local dataset;
- describe ordinary close-to-close **difference** (not percent) for one symbol, interval `1d`;
- persist snapshots, rulers, checksums, manifests, journals, registries, and reports;
- inspect and compare those artifacts locally.

It is **not**:

- a trader, broker, or execution engine;
- a signal factory;
- a revival of Radar V1 or V2;
- Product B (a separately named autonomous trading program);
- a claim of edge.

Intended product order still locked by Todd:

1. **Product A** — evidence system first (later packagable as records/refusals, not trades).
2. **Product B** — only if a method is later earned. Year 5 does not create it. “Best trades” is a prohibited claim.

---

## Governing claim classes

These remain separate. Passing one does not earn the next.

| Class | Status now |
|---|---|
| Software correctness | Core local SYNTHETIC path strongly supported. 166 tests were implementer-reported at `053fc28` and were not independently executed by the auditor. Full software correctness is not yet audit-clean until remediations below are re-verified. |
| Data correctness | **Not earned.** No real HISTORICAL records are in the workshop. |
| Method validity | **Not defined.** No Phase 6 authorization. |
| Usefulness / edge | **Not asked. Not shown.** |

Allowed Phase 5 result language: `MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`.

Claim level available now: `LEVEL 0 — MEASURED` only.

`NO EDGE SHOWN` is not applicable because no edge was asked.

---

## Locked Phase 5 question

Source: `docs/phase5/RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`

> In one declared daily dataset for one symbol, what are the ordinary close-to-close differences when every observation uses the same interval, timezone, and transformation version?

Primary metric: `close[t] - close[t-1]` as a decimal string. Not percent. Not a score.

Provenance classes: `LIVE`, `HISTORICAL`, `BACKFILL`, `SYNTHETIC`, `FIXTURE`, `REPLAY`, `MANUALLY_EDITED`.

Pack loaders (`load_fixture_pack`, `load_dataset_pack`, pack export) allow **only FIXTURE/SYNTHETIC**. HISTORICAL/LIVE labels are quarantined as `PACK_PROVENANCE_NOT_ALLOWED`. In-memory `admit_to_dataset` may admit HISTORICAL if the declaration says so. Nothing in this repo downloads HISTORICAL or LIVE data.

The in-repo pack `fixtures/synthetic_one_symbol_1d/` is labeled **SYNTHETIC**. On that pack the session reports:

- 3 admitted daily bars;
- baseline status `MEASURED`;
- claim level `LEVEL 0 — MEASURED`;
- changes `0.50`, `-0.50`;
- ruler checksum `403b2863229368350ac8f20a07a800a6927dc017f0efa6ec0b15305234fc9cee`.

Those numbers are software-test material. They are **not** market evidence.

---

## Legacy V1 / V2 (closed)

Banked in `postmortem/RADAR_V1_V2_FINAL_FINDINGS.md`.

- V1: REJECT AND PRESERVE.
- V2: stronger software (89/89 tests historically) but no method validity; daily features on an intraday clock; 30+ unevidenced thresholds; `outcome_history.csv` is not trustworthy as performance evidence.

V4 does **not** inherit V1/V2 code or trading methodology. No legacy file may be copied merely because it exists.

---

## What was built (units)

### Build units 1–6 (foundation)

Evidence envelope, intake/quarantine, JSON document intake, in-memory registry, identity collision gate, fixture pack loader.

Units 1 and 2 were separately accepted by Todd. Units 3–6 were built under continued-build authorization without per-unit stop.

### Phase 5 units 7–22 (measurement path)

Dataset declaration and admission, observation payload, ordinary close-to-close description, series integrity (no calendar fill), snapshot, session composition, observation/declaration JSON, local pack, local session, session report, snapshot compare, pack identity collision, CLI, SYNTHETIC fixture pack.

This is the only slice that can produce `MEASURED` on a valid series.

### Phase 5 units 23–42 (record identity)

Change records, snapshot checksum, pack session report, CLI replay, reason-code catalog, snapshot verify, pack export, registry files, change continuity, measurement ruler (`dataset_id` is a name, not the ruler), quarantine journal, checksum sidecar, replay ruler lock, pack artifact skip list, pack manifest verify, ruler sidecar, session-report `document_kind`.

### Phase 5 units 43–57 (integrity workshop)

Atomic write (temp sibling, then replace), manifest gate on load, `session --require-manifest` / `--expect-ruler`, pack-compare, `MANIFEST_REQUIRED`, overwrite refusal (`FILE_EXISTS` unless `--replace`), pack inventory, bundle write/verify, journal/registry document kinds, inventory digests.

### Phase 5 units 58–100 (inspect / compare / status)

Document-kind detect, show declaration/snapshot/observation, provenance mix, admission without measurement, compare rulers/reports/inventories, journal summary, report-to-snapshot bind, determinism (run twice, compare snapshot checksums), snapshot inventory, pack layout, canonical JSON check, pack identities/describe/readiness, reason-code lookup, workshop `status`.

`python -m radar_v4 status` is a **workshop capability statement**, not proof that a dataset was measured in that invocation. After remediation it reports `measured: false` and `available_claim_level: LEVEL 0 — MEASURED`. It does not emit `claim_level` as if a measurement occurred.

Honest auditor note: units 58–100 do not change the claim class. They make the workshop inspectable. Completing unit 100 is not a research result.

### Phase 5 units 101–150 (inspectability continuation)

Authorized by `Lets do 50 more units-TC`. These units press the open-item class from the independent audit: claim-level consistency, readiness semantics, stored-arithmetic recompute, locked one-symbol/`1d` scope, extra payload keys, forbidden method-field names, timestamp gaps without calendar fill, pack safety (BOM/symlink/empty/nested/UTF-8), evidence-chain binding, three-way filesystem/inventory/manifest compare, journal reconcile, and a local audit-directory copy.

They do **not** change the claim class. Completing unit 150 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 151–200 (inspectability continuation)

Authorized by `I'm back..lets continue`. These units add record checks (OHLC, retrieval order, ruler fields), refuse percent fields / unexpected files / pack URLs, verify replay and export round-trips, audit catalogs, bind the locked question file, and publish a workshop stop record.

They do **not** change the claim class. Completing unit 200 is not a research result.

### Phase 5 units 201–250 (inspectability continuation)

Authorized by `Lets keep building and Learning and Earning..`. These units add source hygiene, pack hygiene, decimal-string closes, admission/lineage describe, reserved-name and UTF-16 refusal, command catalog, local self-test, and pack certify compose.

They do **not** change the claim class. Completing unit 250 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 251–300 (inspectability continuation)

Authorized by `Lets keep building... Lets Earn and Learn...No drift!!`. These units add byte-level pack identity, filename-date and count checks, claim-word value refusal, certify/lineage/self-test determinism, a README unit lock, and a workshop freeze compose/verify.

They do **not** change the claim class. Completing unit 300 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 301–350 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add path lock, journal-code catalog bind, freeze-versus-status bind, byte-record write/verify, close-sign and retrieval-unique describe, and export portable byte-check.

They do **not** change the claim class. Completing unit 350 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 351–400 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add reserved-stem / leading-hyphen / double-json / empty-pack name lock, path/name/freeze/package determinism, snapshot-count bind, and path-lock record write/verify.

They do **not** change the claim class. Completing unit 400 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 401–450 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add unlabeled/unknown/unreadable JSON kind lock, name-lock verify/compare, workshop stamp compose/determinism/write/verify, name-status bind, and export portable name/kind check.

They do **not** change the claim class. Completing unit 450 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 451–500 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add journal kind/entry/source lock, journal-lock determinism/write/verify, kind-lock equality/write/verify, and stamp-status bind.

They do **not** change the claim class. Completing unit 500 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 501–550 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add session-report kind/checksum/measured lock, ruler kind/object/checksum lock, report-ruler bind, and report-status bind.

They do **not** change the claim class. Completing unit 550 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 551–600 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add snapshot shape/row/provenance lock, snapshot-lock determinism/write/verify, disposition lock, and disposition-status bind.

They do **not** change the claim class. Completing unit 600 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 601–650 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add pack-manifest kind/files/digest lock, pack-manifest verify against pack files, checksum-sidecar digest lock, sidecar-snapshot bind, and status binds.

They do **not** change the claim class. Completing unit 650 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 651–700 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add snapshot-bundle sidecar/ruler lock, portable FIXTURE/SYNTHETIC export lock, and status binds.

They do **not** change the claim class. Completing unit 700 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 701–750 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add local audit-copy kind/files/verify lock, pack three-way chain lock, and status binds.

They do **not** change the claim class. Completing unit 750 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 751–800 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add pack inventory role lock, pack layout declaration/observations/manifest lock, and status binds.

They do **not** change the claim class. Completing unit 800 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 801–850 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add pack safety inspectability lock, leftover tmp/orphan sidecar lock, and status binds.

They do **not** change the claim class. Completing unit 850 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 851–900 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add source-digest custody on lock records so a same-path clean-pack swap cannot keep an old lock verified.

They do **not** change the claim class. Completing unit 900 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

### Phase 5 units 901–950 (inspectability continuation)

Authorized by `Tools verify. Todd authorizes. Stay on course.`. These units add lock-record bind and lock-set: two lock files, or a folder of lock files, must name the same source. Mixing locks from different packs is refused.

They do **not** change the claim class. Completing unit 950 is not a research result, not data correctness, and not authorization of a vendor or Phase 6.

---

## Software facts at HEAD

```text
LANGUAGE — Python 3.12, stdlib only
TEST COMMAND — PYTHONPATH=. python3 -m unittest discover -s tests -v
TESTS AT 053fc28 — 166 passed (implementer-reported)
TESTS AFTER REMEDIATION — 167 passed at 4318a5c87e8385643fbf2dbd9f61dc854b5b67e6
TESTS AFTER UNITS 101–150 — 178 passed at 3074cf5ee51d9baebeebefcb8b59a33fd0c71c82
TESTS AFTER UNITS 151–200 — 185 passed at b78c071b87701cfba0686799670b99352bf35ac9
TESTS AFTER UNITS 201–250 — 192 passed at d842cb6
TESTS AFTER UNITS 251–300 — 198 passed at fe30854
TESTS AFTER UNITS 301–350 — 204 passed at 2c18597
TESTS AFTER UNITS 351–400 — 210 passed at ffa8df6
TESTS AFTER UNITS 401–450 — 216 passed at 8cf9086
TESTS AFTER UNITS 451–500 — 222 passed at f13d7e9
TESTS AFTER UNITS 501–550 — 228 passed at 4ceca2b
TESTS AFTER UNITS 551–600 — 234 passed at 931e5fd
TESTS AFTER UNITS 601–650 — 240 passed at d658c64
TESTS AFTER UNITS 651–700 — 246 passed at 3fff5fb
TESTS AFTER UNITS 701–750 — 252 passed at 4e30ef0
TESTS AFTER UNITS 751–800 — 258 passed at dd43d7f
TESTS AFTER UNITS 801–850 — 264 passed at 0895354
TESTS AFTER UNITS 851–900 — 271 passed at 5c157dc
TESTS AFTER UNITS 901–950 — 277 passed at e6f282c
REASON CODES — catalog present (python -m radar_v4 codes)
CLI — python -m radar_v4
NETWORK — none in this package
VENDOR CLIENT — none
BROKER / PAPER — none
```

CLI command groups:

- run: `session`, `replay`, `admission`, `determinism`
- persist: `export-pack`, `write-bundle`, `pack-manifest`, `quarantine`, `registry-write`
- verify: `verify`, `pack-verify`, `bundle-verify`, `canonical-check`, `report-bind`, `inventory-manifest`
- compare: `compare`, `pack-compare`, `compare-rulers`, `compare-reports`, `compare-inventories`
- inspect: `pack-inventory`, `pack-layout`, `pack-identities`, `pack-describe`, `provenance-mix`, `readiness`, `snapshot-inventory`, `detect-kind`, `show-*`, `journal-summary`, `code`, `codes`, `status`

Serialization rules still bind:

- sorted-key compact JSON;
- timestamps ISO-8601 with microseconds and offset;
- missing timezone is **not** defaulted to UTC;
- provenance stored as `ProvenanceClass.value`.

The workshop will not invent market calendars, exchange hours, or missing bars.

---

## Still unauthorized

These remain unauthorized even though units 7–950 exist:

- purchased historical-stock API or any named vendor;
- live capture;
- labeling SYNTHETIC/FIXTURE prices as HISTORICAL;
- Phase 6 method research;
- indicators, scores, thresholds, ranking;
- backtesting as method validation;
- paper trading / simulated orders (Horizon 4A, only after a locked historical pilot);
- Product B;
- copying V1/V2 implementation.

Paper trading is not a start method.

Do not buy a historical-stock API until a question is locked **and** Todd names the vendor/API. Phase 5 software may *admit* `HISTORICAL` records in memory; it must not download them.

---

## Controlling-record honesty

`main` HEAD is `56db82f` — Phase 5 units **7–200** merged. Units **201–950** are stacked open draft PRs and are **not** on `main`.

Current software under this snapshot is the 851–900 stacked draft on PR #22 (`cursor/phase-5-units-801-850-9fd5`), not on `main`.

If a controlling record on `main` disagrees with this branch, the auditor should report the conflict rather than choose an interpretation. Do not treat PR #8 as current HEAD.

---

## How to verify independently

From the PR branch:

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m radar_v4 status
PYTHONPATH=. python3 -m radar_v4 pack-describe --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 session --pack fixtures/synthetic_one_symbol_1d --require-manifest
PYTHONPATH=. python3 -m radar_v4 determinism --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 pack-verify --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 safety-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 leftover-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 digest-lock --path fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 digest-status --path fixtures/synthetic_one_symbol_1d
```

Expected on the current 901–950 branch:

- full unittest suite: **277 passed** at `e6f282c` (implementer-executed);
- `status` reports `highest_unit: 950`, `measured: false`, and does not emit `claim_level`;
- `status` denies method, vendor, historical evidence, and paper trading;
- `session` on the fixture pack is `MEASURED` with SYNTHETIC changes `0.50`, `-0.50`;
- `determinism` is equal;
- `pack-verify` matches the stored manifest;
- `safety-lock`, `leftover-lock`, and `digest-lock` are valid on the SYNTHETIC fixture;
- a same-path clean-pack swap fails `verify` because `source_digest` changed;
- two lock records from the same pack bind; mixed-source locks refuse `LOCK_BIND_MISMATCH`.

If any command invents a session for a missing pack, downloads data, or prints an edge claim, that is a fail.

---

## Risks the auditor should press

1. **Claim-class drift.** Unit-count completion can be misread as research progress. Units 43–100 are workshop integrity/inspectability. They do not earn data correctness.
2. **SYNTHETIC familiarity.** Repeated `MEASURED` output on the fixture pack can start to feel like a result. It is not.
3. **Decorative surface.** Many CLI commands now exist. Ask whether each one refuses something a human could otherwise misread.
4. **Authorization breadth.** Continued-build phrases plus “up to 100 units” are wide. Confirm the implementer did not use that width to add indicators, vendors, or methods.
5. **`main` now carries the merged workshop.** After the stop-point merge, later unit work continues on a new branch. Completing more units still does not earn data correctness.

---

## Honest current claim

The local evidence workshop on this 851–900 stacked draft can load, refuse, measure LEVEL 0 close-to-close on a SYNTHETIC one-symbol daily pack, lock a ruler, journal refusals, snapshot, verify, export, tamper-check, inspect, compare, certify, hygiene/lineage/decimal-check, freeze, path/name/kind lock, stamp, journal lock, report/ruler lock, snapshot/disposition lock, manifest/sidecar lock, bundle/export lock, audit/chain lock, inventory/layout lock, safety/leftover lock, source-digest custody, and bind counts/records.

**No edge. No HISTORICAL measurement. No vendor. No method. No paper trading.**

Completion of units 7–950 does not authorize a data purchase or Phase 6. Unit-count completion is inspectability, not a research result.

---

## Independent audit and remediations

ChatGPT audited PR #8 as verifier only. Disposition: **PASS WITH MATERIAL OPEN ITEMS**.

Remediations applied after that audit (this commit):

1. Named the actual audited software head (`053fc28`) and the handoff-only head (`9851692`).
2. Reconciled stale GOVERNANCE language: Phase 5 local software is authorized; vendor/historical data access is not. Stop rules now describe the current workshop, not a pre-Unit-1 freeze.
3. `workshop_status()` is a capability statement (`measured: false`, `available_claim_level` only). Baseline refusals use `claim_level=NONE`; only `MEASURED` may say `LEVEL 0 — MEASURED`.
4. Canonical JSON requires exact sorted-key compact bytes plus one newline. Leading whitespace or extra newlines fail.
5. Pack readiness counts declaration-admitted observations, not merely pack-loader accepted files.

## Authorization does not earn a claim

Naming a vendor/API would authorize access. It would **not** make data correctness earned.

The smallest later evidence exercise, if Todd separately authorizes one, would be one named source, one symbol, interval `1d`, one fixed period, the locked close-to-close question unchanged, and no feature, threshold, signal, Phase 6, backtest, or paper trading.

That is not authorized now.

---

## Continuation — units 201–400

Units 201–250 added local hygiene, decimal-string closes, lineage, and certify compose.

This branch continues the same Phase 5 evidence-ops class: byte-level pack identity, filename-date and count checks, claim-word value refusal, certify/lineage/self-test determinism, a README unit lock, and a workshop freeze.

Units 351–400 add reserved-stem / leading-hyphen / double-json / empty-pack name lock, path/name/freeze/package determinism, snapshot-count bind, and path-lock record write/verify.

Units 401–450 add unlabeled/unknown/unreadable JSON kind lock, name-lock verify/compare, workshop stamp compose/determinism/write/verify, name-status bind, and export portable name/kind check.

Units 451–500 add journal kind/entry/source lock, journal-lock determinism/write/verify, kind-lock equality/write/verify, and stamp-status bind.

Units 501–550 add session-report kind/checksum/measured lock, ruler kind/object/checksum lock, report-ruler bind, and report-status bind.

Units 551–600 add snapshot shape/row/provenance lock, snapshot-lock determinism/write/verify, disposition lock, and disposition-status bind.

Units 601–650 add pack-manifest kind/files/digest lock, pack-manifest verify, checksum-sidecar digest lock, sidecar-snapshot bind, and status binds.

Units 651–700 add snapshot-bundle sidecar/ruler lock, portable FIXTURE/SYNTHETIC export lock, and status binds.

Units 701–750 add local audit-copy kind/files/verify lock, pack three-way chain lock, and status binds.

Units 751–800 add pack inventory role lock, pack layout declaration/observations/manifest lock, and status binds.

Units 801–850 add pack safety inspectability lock, leftover tmp/orphan sidecar lock, and status binds.

Units 851–900 add source-digest custody on lock records and refuse a same-path clean-pack swap that would otherwise keep an old lock verified.

Units 901–950 add lock-record bind and lock-set: two lock files, or a folder of lock files, must name the same source.

Passing `bind-locks` or `lock-set` on SYNTHETIC lock files is inspectability. It is not market evidence, not a method, and not authorization to buy data or open Phase 6.

Units 1151–1200 record the V1/V2 cadence lesson as `CADENCE_OVERRUN`. Units 1201–1250 refuse a later stamp that claims the daily series is current (`FRESH_STAMP_STALE_BARS`). An honest later stamp is not a current series. Units 1251–1300 refuse a window or pack bar after `as_of` (`LOOKAHEAD_WINDOW` / `LOOKAHEAD_BAR`). That is the inverse comparison, not a wrap of freshness.

---

## Disposition for ChatGPT

```text
RECORD TYPE — IMPLEMENTATION AUDIT HANDOFF + OPEN-ITEM REMEDIATION
SCOPE — UNITS 1–6 + PHASE 5 UNITS 7–1300
INDEPENDENT AUDIT THROUGH UNIT 100 — PASS WITH MATERIAL OPEN ITEMS
UNITS 101–1300 — INSPECTABILITY CONTINUATION; NOT A RESEARCH RESULT
CORE SYNTHETIC PATH — STRONGLY SUPPORTED
166 TESTS AT 053fc28 — IMPLEMENTER-REPORTED
167 TESTS AT 4318a5c — IMPLEMENTER-REPORTED AFTER REMEDIATION
178 TESTS AT 3074cf5 — IMPLEMENTER-REPORTED AFTER UNITS 101–150
185 TESTS AT b78c071 — IMPLEMENTER-REPORTED AFTER UNITS 151–200
192 TESTS AFTER UNITS 201–250 — IMPLEMENTER-REPORTED
198 TESTS AFTER UNITS 251–300 — IMPLEMENTER-REPORTED
204 TESTS AFTER UNITS 301–350 — IMPLEMENTER-REPORTED
210 TESTS AFTER UNITS 351–400 — IMPLEMENTER-REPORTED
216 TESTS AFTER UNITS 401–450 — IMPLEMENTER-REPORTED
222 TESTS AFTER UNITS 451–500 — IMPLEMENTER-REPORTED
228 TESTS AFTER UNITS 501–550 — IMPLEMENTER-REPORTED
234 TESTS AFTER UNITS 551–600 — IMPLEMENTER-REPORTED
240 TESTS AFTER UNITS 601–650 — IMPLEMENTER-REPORTED
246 TESTS AFTER UNITS 651–700 — IMPLEMENTER-REPORTED
252 TESTS AFTER UNITS 701–750 — IMPLEMENTER-REPORTED
258 TESTS AFTER UNITS 751–800 — IMPLEMENTER-REPORTED
264 TESTS AFTER UNITS 801–850 — IMPLEMENTER-REPORTED ON PR #22
271 TESTS AFTER UNITS 851–900 — IMPLEMENTER-REPORTED ON PR #23
277 TESTS AFTER UNITS 901–950 — IMPLEMENTER-REPORTED ON THIS BRANCH
312 TESTS AFTER UNITS 1201–1250 — IMPLEMENTER-REPORTED ON PR #31
317 TESTS AFTER UNITS 1251–1300 — IMPLEMENTER-REPORTED ON PR #32
DATA CORRECTNESS — NOT EARNED
METHOD VALIDITY — NOT DEFINED
USEFULNESS / EDGE — NOT SHOWN
VENDOR / LIVE / PAPER — NOT AUTHORIZED
V1/V2 INHERITANCE — FORBIDDEN
NEXT CLASS OF WORK — NOT AUTHORIZED BY UNIT 600
```

Learning and Earning It.  
Stay on course.  
No drift.
