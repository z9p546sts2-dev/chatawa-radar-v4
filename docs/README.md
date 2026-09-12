# Radar V4 documents

This is a map. It is not a method, not a score, and not authorization of a vendor or Phase 6.

Controlling files stay at the repository root:

| File | Role |
|---|---|
| `README.md` | Current status. Must keep `UNITS 7–1400` in the status line. |
| `GOVERNANCE.md` | Authority and stop rules |
| `ROADMAP.md` | Near-term foundation roadmap |
| `V4_CONTROL_REQUIREMENTS.md` | Control requirements |
| `V4_ENGINEERING_REQUIREMENTS.md` | Engineering requirements |

## In this folder

| Path | Role |
|---|---|
| `UNITS.md` | Full Phase 5 unit ledger. Inspectability, not a research result. |
| `phase5/README_PHASE5.md` | Phase 5 local workshop notes |
| `phase5/RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md` | Locked LEVEL 0 question |
| `audit/RADAR_V4_CHATGPT_STATUS_2026-08-23.md` | Status packet for ChatGPT through unit 1300 |
| `audit/RADAR_V4_SESSION_CLOSE_2026-08-23.md` | Implementer self-audit and session close |
| `audit/RADAR_V4_CHATGPT_AUDIT_HANDOFF.md` | Independent-audit handoff (slice history) |
| `audit/RADAR_V4_CHATGPT_PR37_PACKET_2026-09-09.md` | PR #37 artifact delivery for ChatGPT. Not an independent audit. |
| `audit/RADAR_V4_CHATGPT_ASK_PR37_2026-09-09.md` | Paste-ready ChatGPT ask for PR #37. Attach the tarball in that ChatGPT message. |
| `audit/RADAR_V4_CHATGPT_INDEPENDENT_AUDIT_PR37_2026-09-12.md` | PR #37: auditor unverified (FAIL: NO TREE). Withdrawn PASS was implementer-preframed. Not a footnote. |
| `audit/chatawa-radar-v4-pr37-1fbda42.tar.gz` | Exact `git archive` of software head `1fbda42`. Run tests from this tree, not `main`. |
| `units/` | Build Units 1–6 readmes and acceptance records |
| `methodology/` | Methodology definition and audit |
| `roadmap/` | Horizon and curriculum planning records |
| `legacy/` | V1/V2 review and reactivation records |

Postmortem records live in `../postmortem/`.

The Python package stays flat in `../radar_v4/`. Do not treat module count as research progress.
