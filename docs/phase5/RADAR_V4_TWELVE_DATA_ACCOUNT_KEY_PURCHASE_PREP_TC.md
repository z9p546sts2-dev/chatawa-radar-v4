# Radar V4 — Twelve Data Account / API-Key / Purchase Preparation

```text
TO — Todd C.
FROM — ChatGPT (governance / coordination)
AUTHORITY — Todd C. only
RECORD TYPE — READ-ONLY ACCESS-PATH PREPARATION
DATE — 2026-09-19
TEMPORARY SOURCE — Twelve Data
SOURCE AUTHORIZATION — YES, this one 30-session SPY cycle only
ACCOUNT CREATION — NOT AUTHORIZED
API KEY CREATION — NOT AUTHORIZED
PURCHASE / UPGRADE — NOT AUTHORIZED
API CALL — NOT AUTHORIZED
HISTORICAL EXTRACT — NOT AUTHORIZED
MARKET BYTES — NONE
```

This record resolves the minimum access path from current official Twelve Data documentation without creating an account, generating a key, purchasing a plan, or making an API request.

**Tools verify. Todd authorizes.**

---

## 1. Current official access facts

Official Twelve Data documentation states:

- an account is required to obtain a personal API key;
- after sign-in, the API key is available in the user dashboard;
- a personal API key is required for full API access;
- historical and end-of-day U.S. equities data are available starting with the **Basic** plan;
- the Basic individual plan is currently **free**;
- Basic provides **8 API credits per minute** and **800 API credits per day**;
- `/time_series` costs **1 API credit per symbol**;
- individual plans are for personal/internal/non-commercial use and do not permit redistribution;
- official `/time_series` documentation supports `mic_code`, `type`, `start_date`, `end_date`, `interval`, and `adjust=none`;
- the response metadata includes `mic_code`, `exchange`, `exchange_timezone`, and `type`.

For this bounded one-symbol one-call historical cycle, no paid upgrade is currently indicated by the public documentation.

---

## 2. Minimum access-path decision

For the first 30-session SPY historical learning cycle, the minimum documented path is:

```text
ACCOUNT REQUIRED       YES
PERSONAL API KEY       YES
PAID PLAN REQUIRED     NO, based on current public documentation
MINIMUM PLAN           BASIC
CURRENT BASIC PRICE    FREE
HISTORICAL CALLS       ONE, if separately authorized
EXPECTED API COST      1 credit for one SPY /time_series request
```

This is an access-path finding, not authorization to create the account or key.

---

## 3. Why no purchase is currently required

The official U.S. equities support page says historical and EOD data are available starting with Basic and require no additional licensing for the documented U.S. historical/EOD feed.

The current individual pricing page identifies Basic as free and lists internal non-display usage with 8 API credits per minute and 800 per day.

The proposed cycle needs one `/time_series` request for one symbol. Current pricing documentation states that `/time_series` consumes 1 credit per symbol.

Therefore:

```text
PURCHASE / UPGRADE REQUIRED FOR THIS BOUNDED CYCLE = NO
```

unless the actual account dashboard later shows that the requested SPY / ARCX / 1day historical path is unavailable on Basic. If that happens, STOP. Do not upgrade or purchase automatically.

---

## 4. Account and API-key preparation rule

If Todd later authorizes account/key creation:

1. Create one Twelve Data account.
2. Complete email verification.
3. Obtain the personal API key from the authenticated dashboard.
4. Keep the key outside the public repository.
5. Do not paste the key into source files, documentation, screenshots, issues, PR comments, or chat transcripts intended for public retention.
6. Do not make any API request merely to test the key unless the bounded extract is separately authorized.

The repository guard and `.gitignore` remain defense-in-depth only. The key should be stored outside the repository root.

---

## 5. Purchase / upgrade stop rule

Do **not** purchase or upgrade during account/key setup.

If Twelve Data presents any requirement for a paid plan, add-on, exchange entitlement, or other charge before the authorized historical request can be made:

```text
STOP
NO PURCHASE
NO UPGRADE
NO API CALL
RETURN THE EXACT REQUIREMENT TO TODD
```

A separate Todd authorization would be required before spending money.

---

## 6. Request-shape compatibility confirmed from current docs

Current official `/time_series` documentation supports the fields needed for the bounded request:

```text
symbol       SPY
interval     1day
start_date   2024-11-18
end_date     2024-12-31
mic_code     ARCX
type         ETF
adjust       none
format       JSON
order        asc
previous_close false
```

The response metadata documents:

```text
symbol
interval
currency
exchange_timezone
exchange
mic_code
type
```

That is sufficient to apply the packet's ARCX stop rule after the response exists.

For `1day`, Twelve Data documents that timezone output is exchange-local and the timezone parameter is ignored for daily/weekly/monthly intervals. Therefore the cycle should rely on returned exchange-local daily session dates and returned `exchange_timezone` metadata, not force an intraday timezone conversion.

---

## 7. Pre/post parameter clarification

Twelve Data documents `prepost` as an optional parameter for qualifying intraday U.S. equity requests on higher plans.

This cycle is `1day` only.

Therefore the safest Basic-compatible historical request is to **omit `prepost` entirely** rather than treat `prepost=false` as a required entitlement-bearing parameter.

This does not widen the historical scope; it removes an unnecessary intraday-only option from the eventual daily request.

---

## 8. Current gate status

```text
TEMPORARY SOURCE                         AUTHORIZED
ACCOUNT CREATION                         NOT AUTHORIZED
API KEY CREATION                         NOT AUTHORIZED
PURCHASE / UPGRADE                       NOT AUTHORIZED
API CALL                                 NOT AUTHORIZED
HISTORICAL EXTRACT                       NOT AUTHORIZED
MARKET BYTES                             NONE

MINIMUM DOCUMENTED ACCESS PLAN           BASIC
CURRENT DOCUMENTED BASIC PRICE           FREE
EXPECTED HISTORICAL CALL CREDIT COST     1
```

No account, key, purchase, API request, or market-data download was performed in preparing this record.

**Research first. Evidence before machinery. Learning and Earning It. Stay on course. No drift.**
