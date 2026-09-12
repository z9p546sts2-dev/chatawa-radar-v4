# Radar V4 — PR #37 independent audit

**Audit date:** 2026-09-12  
**Scope:** draft PR #37 (Phase 5 units 1351–1400 bounded-file need lock)  
**Role:** independent auditor only  
**Posted on:** https://github.com/z9p546sts2-dev/chatawa-radar-v4/pull/37  
**Software head:** `1fbda42f74f6b3701812caa3806cb9244295a428`  
**Tarball:** `chatawa-radar-v4-pr37-1fbda42.tar.gz`  
**Tarball sha256:** `02ebb07aac178463fea01562e5b6481b7c538f94a15f87831739c1fea8af2b4f`  
**Authority created by this record:** NONE  
**Vendor selected:** NONE  
**Horizon 2 authorized:** NO

The independent auditor received the uploaded `.tar.gz`, hashed it, unpacked it, ran the suite, opened the source, and grepped the tree **in their own environment**. This is not Cursor’s self-report and not the withdrawn preframed PASS.

**Tools verify. Todd authorizes.**

---

## Disposition

```text
AUDIT DISPOSITION       PASS
INDEPENDENT SUITE       327 passed in 19.595s — OK (auditor-executed)
TREE                    received, hashed, unpacked by auditor
CLAIM CLASS             UNCHANGED except SOFTWARE CORRECTNESS earned
                        on local FIXTURE/SYNTHETIC workshop scope
NEXT CLASS OF WORK      NOT AUTHORIZED
```

---

## What the auditor ran

- SHA-256 of the uploaded tarball matched `02ebb07aac178463fea01562e5b6481b7c538f94a15f87831739c1fea8af2b4f`.
- Archive unpacked by the auditor.
- Identity: `radar_v4/need_lock.py` present; `tests/test_units_1351_1400.py` present; `PHASE5_HIGHEST_UNIT = 1400`.
- Command: `PYTHONPATH=. python3 -m unittest discover -s tests`
- Actual result: **Ran 327 tests in 19.595s — OK**

Opened from the unpacked tree:

```text
purchase_authorized=True
→ PURCHASE_CLAIM
→ valid=False
→ REFUSAL, not grant

bounded_file_sufficient=False
→ BOUNDED_FILE_SKIPPED

need_bind
→ calls need_lock first
→ invalid purchase claim cannot bind through

dataset_pack
→ need.json is skipped as metadata/control input
→ HISTORICAL/LIVE are not admitted
→ PACK_ALLOWED_PROVENANCE = {FIXTURE, SYNTHETIC}

workshop_status()
→ highest_unit = 1400
→ measured = false
→ vendor_authorized = false
→ paper_trading_authorized = false
→ no claim_level key
```

Whole-tree grep by the auditor: `purchase_authorized` / `PURCHASE_CLAIM` Python use is the refusal path in `need_lock.py`; tests assert `PURCHASE_CLAIM`. No path where `purchase_authorized=True` flips `vendor_authorized`, buys data, or opens HISTORICAL/LIVE intake.

---

## Claim class

```text
SOFTWARE CORRECTNESS     EARNED for local FIXTURE/SYNTHETIC workshop scope
DATA CORRECTNESS         NOT EARNED
METHOD VALIDITY          NOT DEFINED
USEFULNESS / EDGE        NOT SHOWN
VENDOR / LIVE / PAPER    NOT AUTHORIZED
PHASE 6 / PRODUCT B      NOT AUTHORIZED
```

Unit 1400 does not earn a vendor, a historical pack, or Horizon 2.

---

## History on this record (not the current disposition)

1. An implementer-preframed `PASS WITH DECLARED VERIFICATION LIMITATION` was banked from operator-reported output. **Withdrawn.** The auditor refused to co-sign verification they had not done.
2. Honest state while the tarball had not entered the auditor’s environment: **FAIL: NO TREE** / unverified, full stop.
3. After the auditor received the upload and re-ran the audit themselves: **PASS** (this document’s current disposition).

```text
PR #35 / main zip     Independent verification: EARNED (317 auditor-executed)
PR #37 / 1fbda42      Independent verification: EARNED (327 auditor-executed)
```

**PASS**
