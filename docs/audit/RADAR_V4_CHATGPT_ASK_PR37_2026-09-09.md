# Ask ChatGPT — PR #37 independent audit

Paste the block below into ChatGPT. Attach `chatawa-radar-v4-pr37-1fbda42.tar.gz` in that same message (paperclip / attach). Do not send GitHub URLs. This repo is private; unauthenticated pulls 404.

This file is the ask. It is not ChatGPT’s answer.

---

```text
TO — ChatGPT (independent auditor for Radar V4)
FROM — Cursor (bounded implementer), via Todd C.
AUTHORITY — Todd C. (toddmcraft@gmail.com) only
DATE — 2026-09-09
REPO — github.com/z9p546sts2-dev/chatawa-radar-v4 (private)
PR — #37 (stacks on #36)
SOFTWARE HEAD — 1fbda42f74f6b3701812caa3806cb9244295a428
TREE — attached tarball chatawa-radar-v4-pr37-1fbda42.tar.gz
EXPECTED SHA256 — 02ebb07aac178463fea01562e5b6481b7c538f94a15f87831739c1fea8af2b4f

You are the independent auditor. Cursor is not. Do not treat implementer-reported 327 as your result.

This is Product A (local evidence workshop). Not Product B. Not a vendor client. Not Phase 6. Not paper trading.

Claim classes stay separate. Do not collapse them:
- SOFTWARE CORRECTNESS — local FIXTURE/SYNTHETIC workshop only
- DATA CORRECTNESS — not earned
- METHOD VALIDITY — not defined
- USEFULNESS / EDGE — not shown
- VENDOR / LIVE / PAPER / PHASE 6 / PRODUCT B — not authorized

Do this, in order. Stop and say so if a step fails.

1. Confirm the tarball is actually attached in this ChatGPT message. If it is missing, stop. A pasted path, a GitHub link, or a description of the archive is not the tree. Charter: tools verify; self-report of a file is not an independent read.

2. sha256 the attached file. It must match
   02ebb07aac178463fea01562e5b6481b7c538f94a15f87831739c1fea8af2b4f
   If it does not match, stop.

3. Unpack. Identity must hold:
   - radar_v4/need_lock.py present
   - tests/test_units_1351_1400.py present
   - PHASE5_HIGHEST_UNIT == 1400 in radar_v4/workshop_check.py
   If any is missing, you still have the old main zip. Stop. Do not run unittest discover against that zip and call it this audit.

4. From the unpacked tree:
   PYTHONPATH=. python3 -m unittest discover -s tests
   Report the count you actually got. Not the expected count.

5. Open these yourself (not from a paste):
   - radar_v4/need_lock.py
   - radar_v4/need_bind.py
   - radar_v4/dataset_pack.py
   - workshop_status() in radar_v4/workshop_check.py

   Check:
   - purchase_authorized True → PURCHASE_CLAIM, valid=False
   - bounded_file_sufficient False → BOUNDED_FILE_SKIPPED
   - valid need requires purchase_authorized False
   - need_bind calls need_lock first; does not open HISTORICAL intake
   - SKIP_FILENAMES includes need.json
   - PACK_ALLOWED_PROVENANCE remains {FIXTURE, SYNTHETIC}
   - status: highest_unit 1400, measured false, vendor_authorized false, no claim_level key

6. Extra scrutiny: grep the unpacked tree for purchase_authorized and PURCHASE_CLAIM. Confirm purchase_authorized is not a live pre-authorization flag that sets vendor_authorized or buys data. The field name contains "authorized"; say whether True is a refusal or a grant.

Return exactly one disposition:
- PASS
- PASS WITH DECLARED VERIFICATION LIMITATION
- FAIL

Plus: what you ran, what you opened, the actual test count, and whether claim class changed (it should not).
If the tarball is not attached, return FAIL: NO TREE, not a software FAIL.
```
