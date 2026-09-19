# Radar V4 — Twelve Data License Review Only

```text
TO — Todd C.
FROM — Cursor (bounded implementer)
AUTHORITY — Todd C. only
AUTHORIZATION — AUTHORIZE LICENSE REVIEW ONLY — TWELVE DATA — TC
RECORD TYPE — PUBLIC-TERMS LICENSE REVIEW
DATE — 2026-09-19
CANDIDATE — Twelve Data (TEMPORARY only)
PROPOSED CYCLE — one symbol SPY; 30 completed trading sessions;
                  1day; America/New_York session dates; adjust=none;
                  private local storage only;
                  admission and measurement validation only
TERMS REVIEWED — https://twelvedata.com/terms  (Last updated: January 1, 2026)
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4  (PUBLIC)
```

This is a public-terms review. It does **not** authorize a source, authorize an extract, create an account, create an API key, purchase, call an API, download market bytes, add a vendor client, modify production `radar_v4` modules, create Units 1401+, or open Phase 6.

No sales contact was made. No account was created. No API key was created. No market bytes were downloaded.

**A license review is not a license grant.**

**Availability is not authorization.**

**Tools verify. Todd authorizes.**

---

## Proposed cycle under review

These bounds are the object of this license reading. They are not an extract authorization.

```text
SYMBOL                         SPY only
INTERVAL                       1day
SESSIONS                       30 completed trading sessions only
SESSION DATES                  America/New_York exchange-local
ADJUST                         none
STORAGE                        private local only
PUBLIC REPO                    no raw Twelve Data
                               no reconstructable price series
                               no API keys
PURPOSE                        admission and measurement validation only
NOT REQUESTED                  full-year research
                               method validation
                               prediction / signals / edge
                               paper or live trading
                               production
                               redistribution
                               public display
                               permanent archive
```

Exact civil start and end dates for those 30 sessions are not named here. Naming them would invent an exchange calendar or require a download. Both remain out of scope.

Decision #3 still records `2024-01-01` through `2024-12-31` as the later first-cycle date-range identity. This review does **not** amend Decision #3.

Thirty sessions are sufficient only for software / data-admission learning. They are **not** sufficient to claim HISTORICAL DATA CORRECTNESS beyond a later bounded extract, METHOD VALIDITY, USEFULNESS, EDGE, PREDICTIVE VALUE, REGIME ROBUSTNESS, or LIVE READINESS.

---

## Sources read (public pages only)

| Page | URL | Dated |
|---|---|---|
| Terms of Use | https://twelvedata.com/terms | Last updated 2026-01-01 |
| Commercial and personal usage | https://support.twelvedata.com/en/articles/5332349-commercial-and-personal-usage | 2026-08-04 |
| US equities market data | https://support.twelvedata.com/en/articles/9935903-us-equities-market-data | 2026-08-18 |
| End-of-day (EOD) pricing | https://support.twelvedata.com/en/articles/12682324-end-of-day-eod-pricing-market-data | 2026-08-18 |
| How to get historical prices | https://support.twelvedata.com/en/articles/5656039-how-to-get-historical-prices | 2026-01-12 |
| Attribution guidelines | https://support.twelvedata.com/en/articles/12647398-attribution-guidelines-for-using-twelve-data | 2026-01-12 |
| Pricing (Individual) | https://twelvedata.com/pricing | fetched 2026-09-19 |
| Time series documentation | https://twelvedata.com/docs/llms/market-data/time-series.md | fetched 2026-09-19 |
| API documentation (key hygiene) | https://twelvedata.com/docs | fetched 2026-09-19 |

No `/time_series` call was made. `sales@twelvedata.com` was not contacted.

Related workshop records, not license grants:

- Temporary source-fit (technical / license / audit matrices): `docs/phase5/RADAR_V4_TWELVE_DATA_TEMPORARY_SOURCE_FIT_TC.md`
- Decision packet: `docs/phase5/RADAR_V4_HISTORICAL_SOURCE_DECISION_PACKET_TC.md`

---

# 1. LICENSE FIT

```text
LICENSE FIT     PASS WITH CONDITIONS
```

Public terms do **not** forbid ONE temporary private internal 30-session SPY admission/measurement cycle, provided every condition below is kept.

This finding is a reading of public text. It is not source authorization, extract authorization, a purchase decision, or Todd’s grant of a license.

### Conditions that keep this from FAIL

1. Use is Internal Use only: Customer’s internal business / personal / organizational-internal / non-production purpose. Not redistribution. Not external commercial display.
2. The cycle is not treated as a commercial product, client-facing feed, or Free-tier commercial use.
3. An eligible Account / Subscription Tier is used. US historical/EOD is documented from Basic. Individual plans (Basic / Grow / Pro / Ultra) document personal or internal, non-production use. Free/Basic commercial use is forbidden.
4. Storage is private and local only, during the subscription term, for Internal Use.
5. Raw Data, reconstructable OHLCV, and Credentials stay off this public GitHub repository.
6. No Redistribution Rights Add-On is assumed. None is needed only because this cycle does not publish Data to third parties.
7. After subscription termination or expiration, all Data is deleted within 30 days. Certification of deletion is supplied if requested.
8. Any retained Derived Data cannot be reverse-engineered to the underlying Data.
9. `adjust=none` is a later extract setting, not a license grant. It does not change retention or redistribution rules.
10. Sales, custom contracting, white-label, and exchange add-ons are not used and were not requested.

### Immediate FAIL paths (not this cycle, if the conditions hold)

| Path | Result |
|---|---|
| Raw Twelve Data, reconstructable closes, or an API key in this public repo | FAIL (Redistribution / Credentials) |
| Free/Basic data used for commercial purposes | FAIL (§2.3(l); Free Trial §5.6) |
| Keep-forever raw archive after off-boarding | FAIL (§12.5; §16.2) |
| Public display or client redistribution without a Redistribution Rights Add-On | FAIL |

Those are use-path blockers. They do not, by themselves, block a private local internal 30-session cycle.

---

# 2. Exact internal-use conditions

Quoted definitions and grants from Terms last updated 2026-01-01.

**Internal Use** (§1):

> use solely for Customer's internal business purposes and not for redistribution or external commercial purposes.

**Authorized User** (§1):

> all of Customer's employees, contractors, and computerized systems expressly authorized by Customer to use the Platform.

**Platform access license** (§2.1):

> a limited, revocable, non-exclusive, non-transferable, non-sublicensable license to access and use the Platform solely for Internal Use during the subscription term, except as otherwise expressly permitted by your Subscription Tier, Data add-ons, or a separate written agreement with Twelve Data.

**Data license** (§2.2) permits Customer to:

- (a) Access, receive, process, and store Data solely for Internal Use (or as otherwise permitted by Subscription Tier or add-ons);
- (b) Display Data to Authorized Users in accordance with the Agreement, or to third parties only as expressly permitted;
- (c) Create Derived Data that cannot be reverse-engineered to recreate the original Data;
- (d) Use Data for Non-Display Use only as permitted by subscription tier;
- (e) Redistribute or provide external display only if expressly authorized by a Redistribution Rights Add-On or separate written agreement.

**Restrictions that bind Internal Use** (§2.3), as relevant here:

- (b) no redistribute, resell, sublicense, or transfer of Data except as expressly permitted;
- (f) no derivative financial products without explicit written permission;
- (g) no store or cache beyond Documentation timeframes;
- (l) no Free Tier data for commercial purposes;
- (m) no sharing Credentials or unauthorized access.

**Acceptable-use** (§17.1(g), (h)): no derivative works for redistribution; no high-frequency trading without an appropriate license. Neither is requested for this cycle.

**Individual-plan usage** (Commercial and personal usage, 2026-08-04):

> Individual plans are intended strictly for personal or internal use. Acceptable non-commercial use cases include internal tools for personal or organizational use, educational projects like student apps or academic research, and development or testing phases of applications (non-production).

Those plans do not permit redistribution of data or commercial display of data to third parties.

**Attribution** (Attribution guidelines, 2026-01-12): attribution is **not** required for internal or private use (analytics, risk models, internal dashboards, internal APIs not exposed to end users). Attribution **is** required when Data is displayed publicly. Attribution is not a redistribution license.

**Applied to this cycle:** a private local admission/measurement validation of 30 completed SPY `1day` sessions, not shown to third parties and not used as a commercial product, matches documented Internal Use / personal-or-internal / non-production development. Display, if any, is only to Authorized Users. Public GitHub is not an Authorized-User display channel for Data.

---

# 3. Exact plan / tier constraints

Public list-price and coverage pages as fetched 2026-09-19. Not a purchase recommendation.

| Constraint | Public text | Applied to this cycle |
|---|---|---|
| Account required | Terms §1 Account; §4.1 registration; API docs: personal API key required for full access | Later, if Todd authorizes source **and** extract. Not created now. |
| Individual tiers | Basic (Free), Grow, Pro, Ultra. Pricing: “personal, internal, and non-commercial purposes.” | Eligible class for this cycle if use stays non-commercial internal / non-production. |
| US historical / EOD coverage | Available starting with the Basic plan; no additional licensing; covers 100% of US trading volume (US equities, 2026-08-18) | SPY `1day` EOD is inside documented Basic historical/EOD. Distinct from the ~5% real-time default feed. |
| Free / Basic commercial ban | §2.3(l) Free Tier data may not be used for commercial purposes. §5.6 Free Trial: evaluation only; no commercial use. | If Todd later uses Basic (Free), the cycle must remain non-commercial. A commercial product needs a paid plan (and still no redistribution on individual plans). |
| EOD personal-plan wording | EOD page (2026-08-18): “Personal Plans: Data is restricted to individual, non-commercial use only.” | Tension with the usage page’s “organizational internal tools” language. Recorded in §9. This cycle’s stated purpose is non-commercial validation, not a client product. |
| Redistribution | Individual plans forbid it. Requires Redistribution Rights Add-On or written agreement. Terms §2.2(e), §2.4. | Not needed if Data never leaves private local storage / Authorized Users. |
| Non-display | Basic lists “Internal non-display usage.” Grow lists “Internal display data access.” Ultra lists “Internal non-display data access.” Terms §2.2(d). | Local workshop processing without third-party display fits documented internal non-display / Authorized-User display. |
| Credits / volume | `/time_series` costs 1 API credit per symbol. Basic: 8 credits/minute, 800/day. `outputsize` 1–5000; default 30 when no date parameters. | Thirty `1day` SPY bars are far below documented caps. Not a plan blocker. |
| Identity query add-ons | `isin` / `cusip` request parameters need a Data add-on. `figi` needs Ultra (individual) or Enterprise (business). | Not required if a later extract uses `symbol=SPY` (plus `type=ETF` / `mic_code=ARCX` as later specified). Add-ons are not a cycle blocker. |
| `prepost` | Pro (individual) / Venture (business) and above; intraday US only. | Not requested. Daily `1day` cycle does not need it. |
| Sales / custom | Required for redistribution, white-label, full-market real-time, custom SLA. | Not required for internal US historical/EOD on a standard plan. Sales was not contacted. |
| Business plans | Venture / Enterprise / Enterprise+: commercial display and internal usage, still subject to exchange licensing. Redistribution still needs a separate agreement. | Not required for this private cycle. |

No public term says a 30-session SPY EOD extract requires Grow, Pro, Ultra, or a business plan **if** the use stays personal-or-internal, non-commercial, non-production, and non-redistributing.

---

# 4. Storage rights while subscribed

**Grant** — Terms §2.2(a): Customer may “Access, receive, process, and store Data solely for Internal Use” during the subscription term.

**Cap** — Terms §2.3(g): Customer shall not “Store or cache Data beyond permitted timeframes specified in the Documentation.”

**Retention limits** — Terms §16.1: Customer may retain Data only:

- (a) for duration permitted by subscription;
- (b) as required for regulatory compliance;
- (c) subject to any Third-Party Provider restrictions.

**Documentation cache text found:**

- Historical-prices FAQ (2026-01-12): “Try to get it once, cache and update it later with the real-time data.”
- API documentation: “Cache responses for frequently accessed data to reduce API calls and improve performance.”

No numeric historical-EOD TTL (hours / days / bars) was found in the public Documentation reviewed. Intraday depth limits exist; they are not a storage-license number for `1day` history.

**Applied to this cycle:** private local storage of one 30-session SPY extract, while an eligible subscription is active, for Internal Use only, is inside §2.2(a) and §16.1(a). It is **not** a permanent archive right. It is **not** a right to publish the file. The missing numeric Documentation TTL is recorded in §9.

---

# 5. Deletion requirements after subscription ends

**Effect of termination** — Terms §12.5:

- (a) all access rights cease immediately;
- (b) Customer must delete all Data;
- (c) Fees remain due;
- (d) survival provisions continue.

**Data deletion** — Terms §16.2, upon termination **or expiration**:

- (a) all Data must be deleted within 30 days;
- (b) certification of deletion required if requested;
- (c) audit trail data may be retained for compliance.

**Confidentiality** — Terms §7.1(d): return or destroy Confidential Information upon termination.

**Cancellation access** — Terms §5.4(e) and pricing FAQ: after cancel, access continues until the end of the paid period. Deletion clocks in §16.2 run from termination or expiration, not from the cancel click.

**Reading for this cycle:** when the subscription ends, **all Data** (Market Data received from the Platform, including a local 30-session SPY OHLCV extract) must be deleted. §12.5 states the duty without a grace window; §16.2 supplies a 30-day outer bound and a possible certification. Conservative operational reading: delete promptly; finish within 30 days; keep proof if asked.

Twelve Data is not a keep-forever raw archive.

---

# 6. What audit / checksum / provenance records may remain

**Explicit keep** — Terms §16.2(c): “Audit trail data may be retained for compliance.”

**Derived-data keep** — Terms §6.2: “Customer retains rights to Derived Data created in compliance with this Agreement.” Derived Data exists only if it cannot be reverse-engineered to the underlying Data (§1, §2.2(c)).

**Likely retainable after deletion of Data** (public-text reading, not a vendor ruling):

| Record | Why it may remain |
|---|---|
| Radar workshop provenance that names source class, symbol identity, interval, session-count bound, `adjust=none`, and “Twelve Data” without prices | Not Market Data |
| SHA-256 / sidecar checksums of workshop artifacts that do **not** contain OHLCV | Digest is not the price series; fits audit-trail use |
| Refusal journals, reason codes, ruler identity, declaration fields that do not embed closes | Workshop software records, not Data |
| This public license-review document | Public terms research; no Data |

**Must go with the Data:**

| Record | Why |
|---|---|
| Raw `/time_series` JSON or CSV | Data |
| Local observation files, snapshots, or packs that store open/high/low/close/volume | Data |
| Close-to-close differences stored **with** raw closes | Reconstructs the series; not compliant Derived Data |
| One seed close plus a difference series | Reconstructs the series |
| API keys, tokens, dashboard exports of Credentials | Credentials (§2.3(m)); not an audit exception for secrets |
| Public-repo copies of any of the above | Redistribution plus deletion failure |

**UNRESOLVED keep** (see §9): MEASURED `close[t] - close[t-1]` values stored **without** any raw close, seed close, or reconstructable companion. Differences alone do not recover absolute price levels. Public terms do not say whether that residue is Data, Derived Data, or audit trail.

Until Todd resolves that question, the conservative rule for any later extract is: after off-boarding, delete every file that contains Twelve Data prices **or** can reconstruct them. Keep only non-reconstructable provenance, checksums of non-price artifacts, and this public documentation.

§16.2(c) is not a license to keep a shadow copy of the extract under an “audit” filename.

---

# 7. Derived-data / reconstructability restrictions

**Definition** — Terms §1:

> "Derived Data" means data created by Customer from the Data, provided such data cannot be reverse-engineered to arrive at the underlying Data.

**Grant** — Terms §2.2(c): create Derived Data that cannot be reverse-engineered to recreate the original Data.

**Ownership** — Terms §6.2: Customer retains rights to compliant Derived Data.

**Hard limits:**

- §2.3(f): no derivative financial products without explicit written permission;
- §2.3(k): no combining Data with other sources to create competing products without permission;
- §17.1(g): no derivative works for redistribution.

**Applied to Radar’s ordinary baseline** (`close[t] - close[t-1]`, Decision #8):

| Stored object | Reconstructable to underlying Data? | License class |
|---|---|---|
| Raw closes | Yes (it is the Data) | Data — delete on end |
| Differences **plus** raw closes | Yes | Not Derived Data — delete on end |
| Differences **plus** one seed close | Yes | Not Derived Data — delete on end |
| Differences only, no seed, no raw close | No absolute levels | UNRESOLVED — do not treat as cleared Derived Data |
| Pass/fail admission flags, reason codes, checksums without prices | No | Not Data |

A later LEVEL 0 MEASURED result is a workshop computation. It is not automatically compliant Derived Data.

Public GitHub must not hold a reconstructable price series, even if labeled “derived.”

This cycle’s purpose (admission and measurement validation) is not a derivative financial product. Using the same numbers later as a traded product, signal, or client feature would leave this Internal Use reading.

---

# 8. Public GitHub restrictions

This repository is public: `github.com/z9p546sts2-dev/chatawa-radar-v4`.

**Redistribution** — Terms §1:

> any publication, distribution, or provision of Data to third parties.

Committing Twelve Data OHLCV, or a series that reconstructs it, to a public repository is publication to third parties. Individual plans forbid that. Terms §2.3(b) and §2.2(e) require an express Redistribution Rights Add-On or written agreement. None is proposed.

**Credentials** — Terms §2.3(m): do not share Credentials or allow unauthorized access. API documentation:

> Store your API key securely and never expose it in client-side code or public repositories.

**Attribution is not permission.** Public display requires “Data provided by Twelve Data” (dofollow to twelvedata.com) unless a contract says otherwise. Attribution does **not** authorize putting Data in this repo.

**Attribution is not required** for internal or private use.

**Allowed in this public repo:** this review; citations of public terms; workshop software; FIXTURE/SYNTHETIC packs; provenance language that does not contain Data.

**Forbidden in this public repo:**

```text
raw Twelve Data OHLCV
reconstructable close / difference series
subscriber-only contract text
API keys, tokens, dashboard secrets
unnecessary account PII
```

LICENSE FIT for **raw Data on this public GitHub repo** remains **FAIL**. That FAIL is a storage location, not a ban on a private local cycle.

---

# 9. Unresolved licensing questions

These are open because public text is silent, in tension, or because sales contact was forbidden.

1. **Historical cache TTL.** §2.3(g) points at Documentation timeframes. Public docs tell users to cache historical responses. No numeric EOD store/cache limit was found.
2. **MEASURED differences without raw closes.** After deletion, may `close[t]-close[t-1]` values remain if no seed close is kept? Public Derived Data text does not decide it.
3. **Checksum of the raw extract.** A SHA-256 of deleted OHLCV cannot reconstruct prices. Unresolved whether the vendor treats that digest as Data, audit trail, or neither.
4. **Personal-plan wording tension.** EOD page: personal plans are “individual, non-commercial use only.” Usage page: individual plans include “internal tools for personal or **organizational** use” and non-production development. Both pages are current public text (2026-08). This cycle’s stated purpose fits both if it stays non-commercial and private. A later commercial or multi-user product would not.
5. **Basic (Free) versus paid individual.** US EOD is documented from Basic. Free-tier commercial use is forbidden. Unresolved whether an organizational-internal workshop **must** use a paid individual plan, or whether Basic remains enough while the cycle stays non-commercial.
6. **Third-party / exchange side letters for US EOD SPY.** Public US-equities text says historical/EOD needs no additional licensing and covers 100% of US volume. Terms §3 still say Customer is solely responsible for Third-Party Provider compliance. No extra public SPY EOD add-on was found. Not confirmed with sales.
7. **§12.5 versus §16.2 timing.** Immediate “delete all Data” versus “within 30 days.” Conservative reading recorded in §5; vendor preference not asked.
8. **Regulatory-retention exception** (§16.1(b)). No Radar-specific regulatory keep-raw duty is claimed here. If one later exists, it is a Todd legal question, not an implementer expansion of storage.
9. **Catalog / plan footnotes outside this cycle.** ISIN/CUSIP query add-ons; FIGI plan floors; a trial note that Basic lacks “deep historical data.” Thirty daily bars are not a deep-history request. Still unresolved as general plan text, not as a 30-session blocker.

No sales email was sent to close these.

---

# 10. Does any term block ONE temporary private 30-session SPY cycle?

```text
PUBLIC-TERM BLOCK ON THIS CYCLE     NO
```

No reviewed public term forbids **one** temporary, private, local, Internal Use, non-redistributing, non-production cycle of **30 completed SPY `1day` sessions** with `adjust=none` and America/New_York exchange-local session dates, used only for admission and measurement validation, **if** the conditions in §1 are kept.

What public terms **do** block, even for this cycle:

- putting the extract, a reconstructable series, or an API key in this public GitHub repo;
- using Free/Basic data as a commercial product;
- keeping raw Data after the subscription ends (30-day deletion);
- redistribution or public display without an add-on / written agreement;
- treating close-to-close-plus-closes as keepable Derived Data.

Those are conditions, not a ban on the private cycle.

This review still does **not**:

```text
AUTHORIZE TWELVE DATA AS A SOURCE
AUTHORIZE AN EXTRACT
AUTHORIZE AN ACCOUNT
AUTHORIZE AN API KEY
AUTHORIZE A PURCHASE
AUTHORIZE MARKET BYTES
AUTHORIZE A VENDOR CLIENT
AUTHORIZE UNITS 1401+
AUTHORIZE PHASE 6
AUTHORIZE PREDICTION, SIGNALS, EDGE,
         PAPER TRADING, OR LIVE TRADING
```

---

## Required-output index

| # | Output | Finding |
|---|---|---|
| 1 | LICENSE FIT | **PASS WITH CONDITIONS** |
| 2 | Internal-use conditions | §2 of this file — Internal Use only; individual-plan personal/internal/non-production; no redistribution |
| 3 | Plan / tier constraints | §3 — US EOD from Basic; individual plans; Free commercial ban; no sales add-on required for private internal EOD |
| 4 | Storage while subscribed | §4 — store for Internal Use during the term; no numeric historical TTL found |
| 5 | Deletion after end | §5 — delete all Data within 30 days; certify if requested |
| 6 | Remaining audit records | §6 — non-price provenance and non-reconstructable checksums may remain; raw/reconstructable files may not |
| 7 | Derived-data limits | §7 — keep only if not reverse-engineerable; close-to-close plus closes fails that test |
| 8 | Public GitHub | §8 — raw / reconstructable / keys FAIL; this review may stay |
| 9 | Unresolved questions | §9 — TTL, difference residue, checksum-of-raw, personal-vs-organizational wording, Basic vs paid |
| 10 | Cycle blocked? | **NO** public term blocks the private 30-session cycle if §1 conditions hold |

---

## Disposition

```text
REVIEW                          COMPLETE — PUBLIC TERMS ONLY
LICENSE FIT                     PASS WITH CONDITIONS
PUBLIC-REPO RAW STORAGE         FAIL
CYCLE BLOCKED BY PUBLIC TERMS   NO  (private local internal only)
SALES CONTACT                   NONE
ACCOUNT / API KEY               NONE
MARKET BYTES                    NONE
SOURCE AUTHORIZED               NO
EXTRACT AUTHORIZED              NO
UNITS 1401+                     NOT CREATED
PHASE 6                         NOT OPENED
VENDOR CLIENT                   NONE
radar_v4/ PRODUCTION            UNCHANGED
NEXT ACTOR                      TODD
```

> Research first. Evidence before machinery. Tools verify. Todd authorizes.

Learning and Earning It.  
Stay on course.  
No drift.
