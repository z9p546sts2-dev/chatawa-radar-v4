# ChatGPT packet — PR #37 (units 1351–1400)

This packet exists because the `chatawa-radar-v4-main` zip is **not** this work. Running `unittest discover` against that zip would verify the old tree (317-class), not need-lock. Do not treat a 317 pass as a 327-with-need-lock pass.

This packet is an **artifact delivery**. It is not ChatGPT’s independent audit, not a method claim, and not authorization of a vendor.

```text
PACKET DATE — 2026-09-09
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4
BRANCH — cursor/phase-5-units-1351-1400-24ff
PR — https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/37
SOFTWARE HEAD — 1fbda42f74f6b3701812caa3806cb9244295a428
STACKS ON — PR #36 (units 1301–1350)
AUTHORITY — Todd C. (toddmcraft@gmail.com) only
IMPLEMENTER — Cursor (bounded engineer)
INDEPENDENT AUDITOR — ChatGPT
IMPLEMENTER-EXECUTED SUITE AT 1fbda42 — 327 passed (not an independent audit)
CLAIM CLASS — UNCHANGED
```

GitHub tree archive of the software head (same bytes as `git archive` of `1fbda42`):

```text
https://github.com/z9p546sts2-dev/chatawa-radar-v4/archive/1fbda42f74f6b3701812caa3806cb9244295a428.tar.gz
```

Local tarball built from that commit (also stored in this PR as `docs/audit/chatawa-radar-v4-pr37-1fbda42.tar.gz`):

```text
chatawa-radar-v4-pr37-1fbda42.tar.gz
sha256 02ebb07aac178463fea01562e5b6481b7c538f94a15f87831739c1fea8af2b4f
```

File hashes at `1fbda42`:

```text
04b5f129c4cbf4d5701c3cc193ea4cac1b8de74047bbe8b98595a02b063883c5  radar_v4/need_lock.py
2934c6d49cc2a86ae0ea0bfeb682c1d9cd5e6efbc3f9be6df1285bdcc776081e  radar_v4/need_bind.py
a0729ff44cbf10cf0210b4781c62b591f1f22157f43f6353465d4779c143159e  radar_v4/dataset_pack.py
a0293610b13b18b778d6a8e09f349ad8ac2b234941d4e115eb3f5bc1ec89f5a8  radar_v4/workshop_check.py
6c50d70b1bde8d71ab15a56dfca69e37fab92805d2e175fe8f6ad3b61f054b25  radar_v4/reason_codes.py
0c804a9549da5ba6f71db106577479e3b37830ad080d4b5f88a4e477ffcc4132  radar_v4/fixture_pack.py
6682d0e26edfc8ddc0b8dba78cc93de6185b2d41855035e4d9316aa0b031748a  tests/test_units_1351_1400.py
```

Identity check after unpack: `radar_v4/need_lock.py` exists; `tests/test_units_1351_1400.py` exists; `PHASE5_HIGHEST_UNIT == 1400`. If those are missing, you still have the main zip.

## How to verify independently

Unpack the `1fbda42` tree (not `main`). Then:

```text
PYTHONPATH=. python3 -m unittest discover -s tests
```

Also open, at code:

1. `radar_v4/need_lock.py` — `purchase is True` returns invalid `PURCHASE_CLAIM`. Valid path requires `purchase_authorized is False`.
2. `radar_v4/need_bind.py` — calls `need_lock` first; does not buy data; matches pack `adjustment_policy` / `max_staleness`.
3. `radar_v4/dataset_pack.py` — `SKIP_FILENAMES` includes `need.json`; `PACK_ALLOWED_PROVENANCE` still `{FIXTURE, SYNTHETIC}` at declaration and observation.
4. `workshop_status()` — `highest_unit` 1400, `measured` false, `vendor_authorized` false, no `claim_level`.

## PURCHASE_CLAIM / purchase_authorized — implementer wiring note

This is for extra scrutiny. It is not a pass.

- `purchase_authorized` is a field on a local `radar_v4.need` JSON document.
- `PURCHASE_CLAIM` is a **refusal code**. It is raised when `purchase_authorized is True`. The lock then returns `valid=False`.
- The only valid need-lock path is `bounded_file_sufficient is True` **and** `purchase_authorized is False`.
- `need_bind` will not bind a purchase-claim document: it forwards the need-lock error.
- Nothing in this slice sets `vendor_authorized` true, opens `load_dataset_pack` to HISTORICAL/LIVE, or calls a network client.
- `workshop_status()` still hard-codes `vendor_authorized: False` and `paper_trading_authorized: False`.

So `purchase_authorized` is not a live pre-authorization flag. `True` is the failure. `False` is the required recorded state. The name is still worth auditor scrutiny because it contains “authorized”.

Repo-wide uses of those strings at this head: `need_lock.py` (read + refuse), `reason_codes.py` (catalog), `tests/test_units_1351_1400.py` (asserts refusal), docs (describe the refusal). No other Python module reads `purchase_authorized`.

## Claim class (unchanged)

```text
SOFTWARE CORRECTNESS     local FIXTURE/SYNTHETIC workshop only
DATA CORRECTNESS         NOT EARNED
METHOD VALIDITY          NOT DEFINED
USEFULNESS / EDGE        NOT SHOWN
VENDOR / LIVE / PAPER / PHASE 6 / PRODUCT B    NOT AUTHORIZED
```

## Source at 1fbda42

The Python modules follow this packet in the same commit so the PR is self-contained. Prefer hashing the files on disk against the list above.

### `radar_v4/need_lock.py`

See repository file `radar_v4/need_lock.py` at `1fbda42`.

### `radar_v4/need_bind.py`

See repository file `radar_v4/need_bind.py` at `1fbda42`.

### `dataset_pack.py` need.json skip + provenance gate

`SKIP_FILENAMES` includes `"need.json"` and `"source.json"`.

`load_dataset_pack` still refuses declaration or observation provenance outside `{FIXTURE, SYNTHETIC}` with `PACK_PROVENANCE_NOT_ALLOWED`.

`PACK_ALLOWED_PROVENANCE = frozenset({"FIXTURE", "SYNTHETIC"})` in `radar_v4/fixture_pack.py`.

### `workshop_status()`

`PHASE5_HIGHEST_UNIT = 1400`. Status JSON: `measured: False`, `vendor_authorized: False`, `paper_trading_authorized: False`, `historical_evidence: False`, no `claim_level` key. Note text: `units 1351-1400 are inspectability, not a research result`.
