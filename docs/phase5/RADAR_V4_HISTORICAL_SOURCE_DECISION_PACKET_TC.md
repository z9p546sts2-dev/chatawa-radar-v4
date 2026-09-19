# Radar V4 — HISTORICAL Source Decision Packet

```text
TO — Todd C.
FROM — Cursor (bounded implementer)
AUTHORITY — Todd C. only
RECORD TYPE — READ-ONLY DECISION PACKET
DATE — 2026-09-19
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4
MAIN HEAD REVIEWED — 5bbb726 (units 7–1300 on main)
BANKED STACK — draft PR #36 (units 1301–1350) + draft PR #37 (units 1351–1400)
PR #37 SOFTWARE HEAD 1fbda42f74f6b3701812caa3806cb9244295a428
INDEPENDENT AUDIT — PASS (2026-09-12)
SOFTWARE CORRECTNESS — earned only for local FIXTURE/SYNTHETIC workshop scope
DATA CORRECTNESS — not earned
METHOD VALIDITY — not defined
USEFULNESS / EDGE — not shown
```

PR #37 later branch-head movement after 1fbda42 was audit/documentation-only; no production Python changed between the audited software head and the current PR #37 head.

This packet is documentation. It does not implement a client, buy a feed, download market data, change dataset admission, create Units 1401+, open Phase 6, or authorize a source.

**Availability is not authorization.**

**Tools verify. Todd authorizes.**

---

## What this packet is

A read-only briefing so Todd can decide whether — and only later, if separately authorized — a first HISTORICAL US-stock source may be considered.

It answers five questions:

1. What exact controls Radar already requires before a HISTORICAL dataset can be admitted.
2. What Todd must specify before selecting a source.
3. What later gates still stand between license/source review and any historical bytes, measurement, or revision.
4. Which 3–5 candidate HISTORICAL US-stock sources exist for later review, documented without ranking.
5. The smallest next decisions Todd must make before any source is authorized.

## What this packet is not

- not a vendor selection;
- not a purchase recommendation;
- not a download instruction;
- not an extract authorization; license or source review still does not move historical bytes;
- not a change to `PACK_ALLOWED_PROVENANCE`;
- not a network client;
- not Units 1401+;
- not Phase 6, paper trading, Product B, or method research;
- not DATA CORRECTNESS, METHOD VALIDITY, or usefulness;
- not a claim that a listed source is licensed, sufficient, or honest.

No price series was fetched for this packet. Public product and terms pages were reviewed only to describe candidates. That review is not a data extract.

---

## Current controlling state

```text
PHASE 5 LOCAL SOFTWARE     banked through Unit 1400 on the stacked PR path
WORKSHOP PACK PATH         FIXTURE / SYNTHETIC only
HISTORICAL / LIVE          identity class exists; workshop admission remains refused
VENDOR / PURCHASE / API    not authorized
LOCKED QUESTION            ordinary close-to-close difference, one symbol, 1d
CLAIM LEVEL AVAILABLE      LEVEL 0 — MEASURED only
IN-REPO MEASUREMENT PACK   fixtures/synthetic_one_symbol_1d/  (SYNTHETIC)
```

`admit_to_dataset()` can identity-match a HISTORICAL envelope to a HISTORICAL declaration. That is a schema test. The only operational workshop path still refuses HISTORICAL labels even when identity-valid.

A JSON `authorized: true` flag is `ADMISSION_CLAIM`. A JSON `purchase_authorized: true` flag is `PURCHASE_CLAIM`. Neither is Todd authorization.

---

# 1. Controls Radar already requires before a HISTORICAL dataset can be admitted

These controls already exist. This packet does not add any.

Two layers must not be collapsed:

| Layer | What it does today | Does it admit HISTORICAL market data? |
|---|---|---|
| A. Identity / declaration | `admit_to_dataset()` accepts an identity-valid envelope that matches a HISTORICAL declaration | No. Schema match only. Proven by `tests/test_dataset.py`. |
| B. Workshop pack / lock path | loaders, export, snapshot lock, source lock, and need lock refuse HISTORICAL, LIVE, self-authorization, and purchase claims | No. This is the only path the workshop can run. |

A HISTORICAL dataset is not admitted until **both** layers, plus Todd’s separate authorization, are satisfied. Layer A being green does not open Layer B.

## 1.1 Human authorization — currently closed

From `GOVERNANCE.md`, `V4_CONTROL_REQUIREMENTS.md`, and `docs/phase5/RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`:

1. Todd alone approves data-source use. Tools may verify; they may not authorize.
2. Phase 5 local FIXTURE/SYNTHETIC software is authorized. Phase 5 vendor / HISTORICAL access is not.
3. Ready for authorization is not authorization.
4. Software correctness is not data correctness. Data correctness is not method validity. Method validity is not usefulness.
5. SYNTHETIC or FIXTURE numbers may not be treated as HISTORICAL evidence.
6. A purchased API, live download, or HISTORICAL purchase is not authorized by unit completion, PR #37 PASS, or this packet.
7. Invalid evidence is quarantined. It is not repaired into validity.

Stop language already on the books: current workshop work must stop if live or purchased historical market data becomes necessary without a new explicit Todd authorization.

## 1.2 Identity and declaration — required fields

Control 8 and engineering requirement 7, implemented in `radar_v4/evidence.py`, `radar_v4/validation.py`, `radar_v4/dataset.py`, and `radar_v4/declaration_json.py`.

Every stored evidence envelope must carry, and must not invent defaults for:

- `provenance_class` — one of `LIVE`, `HISTORICAL`, `BACKFILL`, `SYNTHETIC`, `FIXTURE`, `REPLAY`, `MANUALLY_EDITED`;
- `provider`;
- `symbol_or_universe`;
- `market_timestamp` — timezone-aware; UTC is not inferred;
- `retrieval_timestamp` — timezone-aware; UTC is not inferred;
- `interval`;
- `timezone` — known IANA name or `UTC`; offset must match the declared zone;
- `transformation_version`;
- SHA-256 checksum of the canonical payload.

Missing timezone is not replaced with UTC.

A dataset declaration must name all of:

```text
dataset_id
provenance_class
provider
universe
interval
timezone
transformation_version
adjustment_policy
locked_question
primary_metric
```

`max_staleness` is optional on the declaration. On the banked need-lock path it must still be declared; `NONE` means no live freshness SLA.

`admit_to_dataset()` then requires the envelope to match the declaration on:

```text
provenance_class
provider
symbol_or_universe  (declaration field: universe)
interval
timezone
transformation_version
```

Mismatch is `DATASET_DECLARATION_MISMATCH` and is quarantined.

Not matched by that function today:

- `adjustment_policy` (declaration / ruler / need-lock only; not an envelope field);
- `locked_question`;
- `primary_metric`;
- `max_staleness`;
- date range (not a declaration field);
- corporate-action or survivorship identity.

The measurement ruler (`radar_v4/ruler.py`) is:

```text
provenance_class
provider
universe
interval
timezone
transformation_version
adjustment_policy
locked_question
primary_metric
```

`dataset_id` is a name, not the ruler. `max_staleness` is operational, not ruler identity. Baseline and candidate sides must use the same ruler.

## 1.3 Observation, series, and ordinary baseline

From `radar_v4/observation.py`, `radar_v4/observation_validation.py`, `radar_v4/series.py`, `radar_v4/baseline.py`, `radar_v4/session.py`, and the locked question.

An observation is an envelope plus payload. Required payload:

- `close` as a decimal string;
- optional `open` / `high` / `low` / `volume` as decimal strings if present;
- payload checksum;
- high ≥ low, and close inside high/low when those fields exist.

Series rules:

- market timestamps unique (`DUPLICATE_MARKET_TIMESTAMP`);
- observations identity-valid;
- ordered by market timestamp;
- missing bars are not invented;
- exchange calendars are not applied.

Session keep-rule: the observation envelope must already be admitted (`OBSERVATION_NOT_ADMITTED` otherwise). Contradictory identity or payload is quarantined (`CONTRADICTORY_IDENTITY`, `CONTRADICTORY_PAYLOAD`).

Ordinary baseline, already locked:

> In one declared daily dataset for one symbol, what are the ordinary close-to-close differences when every observation uses the same interval, timezone, and transformation version?

- primary metric: `close[t] - close[t-1]` as a decimal string;
- not percent, not a score, not a signal;
- at least two observations or `INSUFFICIENT_EVIDENCE`;
- LIVE provenance is `INVALID_COMPARISON`;
- mixed symbol / interval / timezone / transformation is `INVALID_COMPARISON` (“observations do not share the same ruler”);
- allowed statuses: `MEASURED`, `INSUFFICIENT_EVIDENCE`, `INVALID_COMPARISON`, `UNCLEAR`;
- claim level available now: `LEVEL 0 — MEASURED` only.

A MEASURED SYNTHETIC baseline is still not HISTORICAL evidence.

## 1.4 Workshop path — HISTORICAL remains refused

These refusals already fire on the only path the workshop can run.

| Control | Where | Refusal / effect |
|---|---|---|
| Pack provenance | `radar_v4/dataset_pack.py`, `radar_v4/fixture_pack.py` | `PACK_ALLOWED_PROVENANCE = {FIXTURE, SYNTHETIC}`. HISTORICAL / LIVE declarations and observations are quarantined even if identity-valid. |
| Pack export / snapshot lock | `radar_v4/pack_export.py`, `radar_v4/export_lock.py`, `radar_v4/snapshot_lock.py` | HISTORICAL snapshots and packs are not workshop-locked or exported. |
| Certify | `radar_v4/certify.py` | Local workshop label must be SYNTHETIC (`FIXTURE_LABEL_REFUSED`). |
| Cadence | `radar_v4/cadence_lock.py` | Evaluation cadence may not outrun bar interval (`CADENCE_OVERRUN`). Known tokens: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`. |
| Freshness | `radar_v4/freshness_lock.py`, `radar_v4/current_claim.py` | A later stamp may not claim stale bars are current (`FRESH_STAMP_STALE_BARS`). Honest `claim_current: false` is valid. |
| Horizon | `radar_v4/horizon_lock.py`, `radar_v4/horizon_bind.py` | `include_through` after `as_of` is `LOOKAHEAD_WINDOW`. A pack bar after `as_of` is `LOOKAHEAD_BAR`. Inverse of freshness, not a wrap of it. |
| No network | `radar_v4/workshop_bounds.py` | Vendor-style HTTP/WebSocket imports are refused. The workshop must not grow a client by import. |
| Status | `radar_v4/workshop_check.py` | `historical_evidence: false`, `vendor_authorized: false`, `measured: false`. |

Cadence, freshness, and lookahead are three distinct refusals. They are not one inspector.

## 1.5 Banked units 1301–1400 — source lock and need lock

Banked on draft PR #36 and draft PR #37. Independent audit of PR #37: PASS. Still not HISTORICAL authorization.

Source lock (`radar_v4/source_lock.py`, `radar_v4/source_bind.py`):

- a workshop source must be named (`SOURCE_UNNAMED`);
- `authorized: true` is `ADMISSION_CLAIM` — a JSON flag is not Todd authorization and does not open the pack loader;
- `provenance_class: HISTORICAL` is `HISTORICAL_ADMISSION_NOT_AUTHORIZED`;
- `provenance_class: LIVE` is `LIVE_ADMISSION_NOT_AUTHORIZED`;
- source bind cannot attach to a HISTORICAL or LIVE pack;
- naming a source is not a download.

Need lock (`radar_v4/need_lock.py`, `radar_v4/need_bind.py`):

- `bounded_file_sufficient: false` is `BOUNDED_FILE_SKIPPED` — skipping the local file does not earn a vendor;
- `purchase_authorized: true` is `PURCHASE_CLAIM` — a JSON flag is not a data purchase;
- empty adjustment is `ADJUSTMENT_UNDECLARED`;
- empty max-staleness is `STALENESS_UNDECLARED`;
- need bind must match the pack declaration’s `adjustment_policy` and `max_staleness` (`NONE` if the pack omitted staleness).

`source.json` and `need.json` are skipped as observation files. They are control documents, not bars.

## 1.6 Required before ingestion, not yet a HISTORICAL path

These bind if HISTORICAL ingestion is ever separately authorized. They do not exist as a vendor client today.

From `V4_CONTROL_REQUIREMENTS.md` and `V4_ENGINEERING_REQUIREMENTS.md`:

- **Control 2 / cadence declaration** — feature or evaluation use must declare interval, update cadence, maximum staleness, approved use, and prohibited use. Decision cadence may not outrun source cadence.
- **Control 4 / timestamp consistency** — price, feature, retrieval, interval, and freshness state travel together. A fresh price may not conceal stale features.
- **Control 8 / provenance** — any stored HISTORICAL set still needs the identity fields in §1.2 plus integrity.
- **Control 9 / shared access** — all retrieval must use one documented access layer and one fallback table. No hidden second client. Fallback must be visible. Not implemented; not authorized.
- **Engineering §6** — any future retrieval record must include provider, endpoint or data type, requested vs actual interval, market timestamp, retrieval timestamp, timezone, adjustment status, fallback used, freshness state, and request outcome.
- **Methodology M0–M3** — one locked question, identity/provenance, cadence/timing, and ordinary baseline before any later comparison. M4–M8 (candidate comparison, thresholds, historical method validation, replication, promotion) are not opened by a source decision.

No calendar fill, no invented bars, no silent repair.

## 1.7 Software gaps that still do not admit a source

Radar does **not** currently enforce, as admission software:

- a start date or end date on the declaration;
- exchange calendar completeness;
- survivorship or delisting identity;
- corporate-action event identity beyond the declared `adjustment_policy` string;
- a shared vendor client;
- DATA CORRECTNESS against a market tape.

Those gaps are why Todd must specify the items in §2 before any source is even a candidate for authorization. They are not permission to invent defaults. They also do not authorize universe or survivorship machinery. §3 records later extract, freeze, and revision gates; it does not close these software gaps.

---

# 2. Information Todd must specify before selecting a source

Specify these eight items first. Do not pick a vendor in order to discover the question.

The in-repo locked question and SYNTHETIC pack (`interval=1d`, `timezone=UTC`, `adjustment_policy=UNADJUSTED`, no `max_staleness`) are workshop fixtures. They are not a HISTORICAL declaration.

## 2.1 One research question

Already locked for the local workshop:

> In one declared daily dataset for one symbol, what are the ordinary close-to-close differences when every observation uses the same interval, timezone, and transformation version?

Todd must say whether that exact question remains the question for the first HISTORICAL extract, or whether a new question will be locked first.

A new question would be a new lock, not a silent edit after seeing data. Methodology: question before calculation. One primary comparison. Explicit non-goals.

Out of scope unless Todd later locks a different question: prediction, entry/exit, thresholds, ranking, edge, percent returns, a second asset class.

## 2.2 One instrument / market

One symbol or one declared universe identity.

Must later become `declaration.universe` / `envelope.symbol_or_universe` exactly.

Todd must name:

- the instrument (ticker or other permanent identity);
- the listing market (for example NYSE or Nasdaq);
- whether identity is ticker, FIGI, or another id;
- that this is a US common stock (or another listed US equity type, if that is the question).

The locked question forbids a second asset class. This packet’s candidates are US stocks only because that is the asked review set, not because a symbol has been chosen.

## 2.3 Date range

Not a current declaration field. Still required from Todd before a source can be judged.

Name inclusive start date, inclusive end date, and whether weekends/holidays are expected to be absent.

Radar will not fill missing sessions. A source that silently fills them is a transformation and needs a new `transformation_version`.

The range must be short enough that a later bounded extract, if ever authorized, can stay inside the locked question. A long history is not more honest if the question is ordinary close-to-close difference on one symbol.

## 2.4 Cadence / interval

Locked question: `1d`.

Cadence lock: evaluation cadence may not be finer than the bar (`CADENCE_OVERRUN`).

Todd must name:

- bar interval (expected: `1d`);
- evaluation cadence (must not outrun `1d` if the bar is daily);
- that this extract is not an intraday decision series.

Daily bars used as if they were intraday was a V1/V2 failure. That reuse is already a refusal, not a score.

## 2.5 Timezone

Required on declaration and every envelope. Not defaulted to UTC.

Todd must name the IANA zone or `UTC`, and whether market timestamps are:

- session-close in US/Eastern (or America/New_York);
- midnight UTC labeled as the session date;
- or another declared convention.

The offset on each timestamp must match that zone. A vendor that emits naive dates or mixed offsets cannot be admitted without a declared transformation.

The SYNTHETIC pack uses `UTC`. That is a fixture convention, not a HISTORICAL decision.

## 2.6 Adjustment policy

Required on the declaration and the ruler. Required on the banked need lock. Not stored on the envelope. Not checked by `admit_to_dataset()`.

Todd must name one policy, for example:

- `UNADJUSTED` — raw session close;
- `SPLIT_ADJUSTED`;
- `SPLIT_AND_DIVIDEND_ADJUSTED`;
- another exact string, if a later source uses a named vendor method.

The same policy must apply to every bar in the series. Mixing adjusted and unadjusted closes is a ruler change, not a convenience.

The SYNTHETIC pack declares `UNADJUSTED`. That does not decide the HISTORICAL policy.

## 2.7 Maximum staleness

Optional on the declaration. Required on the banked need lock. `NONE` means no live freshness SLA.

Todd must name:

- the maximum acceptable age of the last bar relative to `as_of` / retrieval;
- or `NONE` if this extract is a frozen historical file with no live freshness claim.

A later retrieval stamp may not claim a stale daily series is current (`FRESH_STAMP_STALE_BARS`). A bar after `as_of` is lookahead (`LOOKAHEAD_BAR`).

For a first frozen extract, `NONE` is the honest operational value unless Todd is asking a freshness question. Freshness is not the locked question.

## 2.8 Ordinary baseline

Already defined. Todd must confirm it remains the baseline:

- ordinary close-to-close **difference**, not percent;
- same ruler on every bar;
- no threshold, signal, or edge;
- `NO EDGE SHOWN` is not applicable because no edge was asked;
- at least two admitted bars or the result is `INSUFFICIENT_EVIDENCE`.

If Todd wants a different ordinary baseline, lock that question first. Do not change the metric after seeing HISTORICAL numbers.

---

# 3. Later gates between review and any historical bytes

These gates are packet requirements. They are not implemented here. They do not authorize a source, a purchase, an extract, a vendor client, Units 1401+, or Phase 6.

They exist so a later license or source review cannot be mistaken for permission to move historical bytes, measure, or silently rewrite a file.

Existing Radar language already forbids silent repair (Control 8 / engineering requirement 7: a repair or transformation must produce a new versioned artifact). This section names the HISTORICAL-class applications. It does not add universe or survivorship infrastructure. Those remain the gaps already recorded in §1.7.

## 3.1 Extract-class change is a separate authorization

```text
HISTORICAL EXTRACT CLASS CHANGE REQUIRES A SEPARATE TODD AUTHORIZATION.
Source review and license review do not authorize an extract.
```

`AUTHORIZE LICENSE REVIEW ONLY` is not an extract. Reading terms is not moving bytes. Naming a candidate is not a download. A JSON flag still cannot close this gate.

No historical bytes may move — into the repository, a local pack, a snapshot, or any other Radar artifact — until Todd records a separate extract authorization.

## 3.2 Bounded-extract authorization must state hard bounds

If Todd later authorizes a bounded extract, that authorization record must state:

- maximum symbols;
- inclusive start date and inclusive end date;
- maximum rows/sessions or an equivalent hard bound;
- optionally maximum file size when the delivery form makes size the honest bound.

An extract that exceeds those bounds is outside the authorization, even if the source and license were previously reviewed. Bounds are not a quality score. They keep the first extract inside one locked question.

This packet does not authorize that extract.

## 3.3 Historical-revision rule

If a first extract is ever acquired under a later separate authorization:

- that first acquired extract is preserved immutably by snapshot and checksum;
- a vendor correction or revision becomes a new version;
- no historical file may be silently overwritten in place.

A later file that “looks corrected” is not the same dataset. Overwrite is not repair.

## 3.4 Freeze before measurement

Before any measurement of a HISTORICAL extract, freeze and record:

- research question;
- instrument identity;
- date range;
- interval / evaluation cadence;
- timezone convention;
- adjustment policy;
- ordinary baseline;
- dataset snapshot / checksum;
- as-of boundary.

Do not measure first and freeze afterward. A measurement without this freeze is not a LEVEL 0 result on that extract.

This requirement does not authorize a measurement. The locked workshop question remains SYNTHETIC-only until a later extract class is separately authorized and then frozen.

## 3.5 Correction linkage

Any later correction or revision record must identify:

- the affected dataset snapshot (identity and checksum);
- the measurement and/or disposition that snapshot supported;
- whether the new version supersedes or invalidates that measurement/disposition.

A revision that does not name what it replaces is an unlinked file, not a correction. Unlinked revisions may not silently inherit a prior MEASURED status.

---

# 4. Candidate HISTORICAL US-stock sources for later review

Not ranked. Not selected. Listed so Todd can see different delivery and provenance shapes.

Inclusion is not a quality score. Public availability is not authorization. Cost notes are public list prices or license classes as of this writing and must be re-read before any later purchase decision. No extract was taken. A later license review of any candidate still does not authorize an extract (§3.1).

## Candidate A — CRSP Daily Stock File (via WRDS or CRSP delivery)

| Item | Record |
|---|---|
| Provider / source | Center for Research in Security Prices (CRSP) US Stock Databases, commonly accessed through Wharton Research Data Services (WRDS) or CRSP/Morningstar delivery. |
| Static-file vs API | Institutional research file (SAS/ASCII/R/cloud). WRDS also offers query access. Not a casual public CSV. |
| Provenance quality | Research-grade US listing history with permanent identifiers (PERMNO / PERMCO). Publicly described as covering active and inactive securities. Vendor of record is identifiable. |
| Adjustment support | Returns and corporate-action files are part of the product. Split/dividend/delisting handling is documented in CRSP guides. Exact field set depends on SIZ vs CIZ format and must be read before a policy string is chosen. |
| Timestamp / cadence clarity | Daily and monthly products exist. Daily date convention and timezone still need a declared mapping into Radar’s timezone-aware timestamps. |
| Survivorship / corporate actions | Designed to retain inactive names and corporate actions. That is a stated product purpose, not a Radar check. Completeness still depends on the licensed vintage. |
| Cost / licensing | Institutional subscription. Not a self-serve retail cart. Redistribution is typically contract-restricted. Exact price and permitted research use are unknown here. |
| Small bounded extract possible? | In principle, yes: one PERMNO and a short date range via a licensed WRDS/CRSP query. Not possible from this repository. Not done. |
| What remains unknown | Whether Todd has or wants institutional access; which file vintage (SIZ vs CIZ); exact close vs return fields for an `UNADJUSTED` or adjusted policy; timezone of `date`; license text for storing a Radar pack; whether a one-symbol extract is contract-allowed. |

## Candidate B — Stooq daily US files

| Item | Record |
|---|---|
| Provider / source | Stooq (stooq.com / stooq.pl). Public historical pages and regional bulk ASCII/CSV archives. |
| Static-file vs API | Primarily static CSV / ZIP files. A CSV query URL also exists. Third-party notes describe CAPTCHA / API-key friction; current gate state was not exercised. |
| Provenance quality | Vendor is named, but the upstream exchange/feed lineage is not a CRSP-class research record. Identity is usually ticker-plus-suffix (for example `.US`). Revision history and error-correction policy are not fully documented here. |
| Adjustment support | Public documentation reviewed for this packet does not give a Radar-grade split/dividend policy. Whether “Close” is raw, split-adjusted, or total-return-adjusted must be treated as unknown until the file header and terms are read against a locked policy. |
| Timestamp / cadence clarity | Daily, weekly, and monthly files are offered. Dates appear as calendar dates without a declared IANA timezone. Mapping to Radar timestamps would be a transformation. |
| Survivorship / corporate actions | Bulk US files include many names; delisted coverage, ticker reuse, and action tables are not established in this packet. Do not assume survivorship-free. |
| Cost / licensing | Files are publicly offered without a ticket price. Stooq terms (Polish/English) restrict some redistribution and may change without notice. “Free to download” is not a Radar license. |
| Small bounded extract possible? | In principle, yes: one US symbol CSV or a dated slice. That would be a download. Not authorized. Not done. |
| What remains unknown | Current terms for research storage; adjustment rule; timezone; ticker-reuse handling; whether a one-symbol file is sufficient without the bulk ZIP; captcha/key requirements on the day of any later extract. |

## Candidate C — Tiingo End-of-Day

| Item | Record |
|---|---|
| Provider / source | Tiingo End-of-Day stock prices (tiingo.com). |
| Static-file vs API | HTTPS API. One ticker, `startDate` / `endDate`, JSON or CSV. Also a documented IEX real-time/intraday product, which is a different class and is not this candidate. |
| Provenance quality | Named commercial vendor with a published cleansing/error-check description. Not an exchange of record. Coverage claims include long US history; independent tape-match is not in this repo. |
| Adjustment support | Documented raw OHLC plus `adjOpen` / `adjHigh` / `adjLow` / `adjClose` / `adjVolume` (split and dividend). A Radar declaration could name either series, not both in one ruler. |
| Timestamp / cadence clarity | Daily bars with a date field; resample options exist for weekly/monthly/annual. Timezone of the date field must still be declared. Holiday handling is documented for daily resample; that is vendor language, not a Radar calendar. |
| Survivorship / corporate actions | Adjusted fields exist. Delisted-name completeness and ticker-reuse policy were not verified here. Do not assume CRSP-like inactive coverage. |
| Cost / licensing | Published plans include a free individual starter tier and paid individual/commercial plans. API data is for internal consumption; redistribution needs separate permission. Organizational use requires a commercial plan per Tiingo terms reviewed for this packet. Prices change. |
| Small bounded extract possible? | In principle, yes: one ticker and a short date range. Requires an account/token. Not authorized. Not done. |
| What remains unknown | Exact license applicable to a Radar evidence pack; delisted coverage for the chosen symbol; timezone; whether the free tier’s terms fit Todd’s use; fallback-feed behavior if Tiingo revises a past bar. |

## Candidate D — Yahoo Finance historical daily

| Item | Record |
|---|---|
| Provider / source | Yahoo Finance historical quotes / chart pages. Yahoo is the site operator, not an exchange of record. |
| Static-file vs API | Interactive CSV/history UI. Programmatic chart endpoints used by third parties are unofficial and unsupported. Yahoo’s former public Finance API is not a current supported product. |
| Provenance quality | Convenient and widely scraped. Upstream contributor and revision policy are opaque. Suitable as a named website observation only if Todd accepts that opacity. Not research-grade provenance. |
| Adjustment support | Yahoo documents “adjusted close” as split- and dividend-adjusted, described as following CRSP-style multipliers. Raw close and adjusted close can both appear. That is vendor help-text, not a Radar validation. |
| Timestamp / cadence clarity | Daily history is date-labeled. Intraday intervals have short retention. Timezone and session-close convention still need a declared mapping. Unofficial endpoints can change shape without notice. |
| Survivorship / corporate actions | Current-ticker history is the common path. Delisted names, ticker reuse, and point-in-time listings are weak or absent. Do not treat a surviving ticker as a universe. |
| Cost / licensing | No ticket price for browser viewing. Yahoo Terms of Service and API terms restrict automated and commercial reuse. “It downloaded” is not a license. Unsupported endpoints can be throttled or withdrawn. |
| Small bounded extract possible? | In principle, a short one-symbol history is easy to request. That ease is a hazard, not a virtue. Not authorized. Not done. |
| What remains unknown | Whether any later use would be inside Yahoo’s current terms; which close field matches Todd’s adjustment policy; timezone; corporate-action completeness; legal fitness for a stored Radar pack. |

## Candidate E — Norgate Data US Equities

| Item | Record |
|---|---|
| Provider / source | Norgate Data, US stock-market packages (Silver / Gold / Platinum / Diamond). |
| Static-file vs API | Local database via Norgate Data Updater (Windows). Python access is a local package talking to that updater, not a hosted market API. |
| Provenance quality | Named specialist vendor. Public materials emphasize backtest-oriented EOD US data. Not an exchange of record. Independent tape-match is not in this repo. |
| Adjustment support | Public API notes describe unadjusted close plus selectable capital/dividend adjustment modes. A Radar `adjustment_policy` string could be bound to one mode. Event-detail completeness still needs a later read of the current library docs. |
| Timestamp / cadence clarity | Daily EOD is the product. Weekly/monthly resampling is offered by the local library. Timezone and session-close mapping still need a declaration. |
| Survivorship / corporate actions | Platinum/Diamond tiers advertise delisted US names and historical index constituents; Silver/Gold are current listings only. Norgate states the delisted database is extensive, not complete, especially early decades. |
| Cost / licensing | Paid subscription. Public 12-month US package prices (re-read before any decision) have been in the low hundreds to high hundreds of USD depending on tier. Redistribution and research-pack storage terms were not fully reviewed here. Requires Windows updater software. |
| Small bounded extract possible? | In principle, yes: one symbol and a date range from the local database after a paid install. That is still a purchase-plus-download path. Not authorized. Not done. |
| What remains unknown | Exact current license for storing Radar packs; whether Todd will operate Windows updater software; which tier is required if the locked symbol later delists; timezone; whether local-library access would pressure Radar toward a forbidden network/vendor client. |

## Candidates noted only to keep them off the silent list

These were considered and **not** added as the 3–5 review set. Omission is not a ranking.

- Exchange raw tape / TAQ — not a daily one-symbol close series for this question; cost and complexity are a different class.
- SEC EDGAR — filings, not daily OHLCV.
- Polygon, Nasdaq Data Link / Sharadar, EODHD, FirstRate, Kibot, IEX Cloud — other commercial APIs/files; adding them would widen the packet without changing the eight Todd decisions or the §3 later gates.
- Kaggle or anonymous CSVs — provenance-unknown; Control 8 would quarantine them.

---

# 5. Explicit non-decisions of this packet

1. No winner. No preference order. The A–E labels are identifiers, not ranks.
2. No source is authorized because it is available, cheap, documented, or familiar.
3. No admission rule is changed. `PACK_ALLOWED_PROVENANCE` remains `{FIXTURE, SYNTHETIC}`.
4. No vendor client, token, or download is created.
5. No Units 1401+. No Phase 6. No method. No paper. No Product B.
6. PR #37 PASS does not earn DATA CORRECTNESS and does not open Horizon 2.
7. Recording later gates in §3 is not authorization of an extract, a measurement, or a revision.

---

# NEXT DECISION REQUIRED FROM TODD

Smallest decisions, in this order. Stop after any `PAUSE` or `REJECT`. Do not skip ahead to a vendor because a later item looks easy.

1. **Keep or re-lock the research question.**  
   Confirm that the first HISTORICAL extract, if ever authorized, still answers the existing locked ordinary close-to-close question — or write a new locked question first.

2. **Name one instrument and listing market.**  
   One US stock identity. No second symbol to “see what happens.”

3. **Name the date range.**  
   Inclusive start, inclusive end. Short enough for the locked question.

4. **Confirm interval and evaluation cadence.**  
   Expected: bar `1d`, evaluation not finer than `1d`.

5. **Name the timezone convention.**  
   IANA zone or `UTC`, plus how a vendor date becomes a timezone-aware close timestamp.

6. **Name the adjustment policy.**  
   One string. Unadjusted or a named adjustment. Not “whatever the vendor sends.”

7. **Name maximum staleness.**  
   For a frozen extract, `NONE` is the honest default unless Todd is asking a freshness question.

8. **Confirm the ordinary baseline.**  
   Close-to-close difference on the same ruler. Not percent. Not a threshold. Not an edge.

9. **Only after 1–8: say whether any candidate in §4 may be reviewed for license text.**  
   Review means read current terms. It does not mean buy, download, admit, or extract. If Todd wants a candidate that is not in §4, name it; do not treat this list as closed because it is short.

10. **Authorization remains a separate sentence.**  
    After 1–9, the next possible record is still one of:

    ```text
    DO NOT AUTHORIZE A HISTORICAL SOURCE
    AUTHORIZE LICENSE REVIEW ONLY — <named candidate> — TC
    ```

    There is no authorization in this packet to ingest, purchase, extract, or open the pack loader.

    Source review and license review do not authorize an extract. A later extract-class change, if Todd ever writes one, is a new sentence and must include the §3.2 hard bounds. That sentence is not written here.

Until Todd records those decisions, Radar stays on the local FIXTURE/SYNTHETIC workshop. The bounded file remains sufficient. A JSON flag cannot close this list.

---

## Current disposition

```text
PACKET                          READ-ONLY / COMPLETE
IMPLEMENTATION                  NONE
MARKET DATA DOWNLOADED          NONE
DATASET ADMISSION CHANGED       NO
UNITS 1401+                     NOT CREATED
PHASE 6                         NOT OPENED
VENDOR CLIENT                   NONE
HISTORICAL SOURCE AUTHORIZED    NO
HISTORICAL EXTRACT AUTHORIZED   NO
LATER GATES                     RECORDED / NOT IMPLEMENTED
WINNER SELECTED                 NO
NEXT ACTOR                      TODD ONLY
```

> Research first. Evidence before machinery. One question before one dataset interpretation.

**Tools verify. Todd authorizes.**

Learning and Earning It.  
Stay on course.  
No drift.
