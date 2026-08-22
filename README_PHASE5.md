# Radar V4 Phase 5 — Data / Research Foundation

**Authorization:** `AUTHORIZE PHASE 5 — TC`

Phase 5 adds dataset admission, an optional numeric observation payload, and a descriptive close-to-close baseline. It does not add a vendor client, a signal, or a method.

## Units

- **Unit 7** — `radar_v4/dataset.py` dataset declaration and admission
- **Unit 8** — `radar_v4/observation.py` payload + payload checksum
- **Unit 9** — `radar_v4/baseline.py` ordinary close-to-close description
- **Unit 10** — `radar_v4/series.py` timestamp uniqueness and ordering
- **Unit 11** — `radar_v4/snapshot.py` deterministic dataset snapshot
- **Unit 12** — `radar_v4/session.py` admit → keep matching observations → series → snapshot → baseline
- **Unit 13** — `radar_v4/observation_json.py` observation document intake
- **Unit 14** — `radar_v4/snapshot_files.py` local snapshot read/write
- **Unit 15** — `radar_v4/declaration_json.py` dataset declaration JSON
- **Unit 16** — `radar_v4/dataset_pack.py` local FIXTURE/SYNTHETIC dataset pack
- **Unit 17** — `radar_v4/local_session.py` session from pack or snapshot
- **Unit 18** — `radar_v4/session_report.py` descriptive session report
- **Unit 19** — `radar_v4/snapshot_compare.py` snapshot identity differences
- **Unit 20** — pack identity collision / idempotent reload
- **Unit 21** — `python -m radar_v4` local session and compare commands
- **Unit 22** — `fixtures/synthetic_one_symbol_1d/` labeled SYNTHETIC pack (not market evidence)
- **Unit 23** — `CloseToCloseChange` from/to timestamps and closes
- **Unit 24** — snapshot integrity checksum (hash of canonical bytes, not stored inside the snapshot)
- **Unit 25** — pack session report includes pack refusals
- **Unit 26** — `python -m radar_v4 replay --snapshot <file>`
- **Unit 27** — `radar_v4/reason_codes.py` refusal/result catalog

Locked question: `RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`

## Still forbidden

Network downloads, broker/paper trading, indicators, thresholds, ranking, and treating software-test numbers as market evidence.

## Commands

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m radar_v4 session --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 replay --snapshot <snapshot.json>
PYTHONPATH=. python3 -m radar_v4 compare --left <snapshot.json> --right <snapshot.json>
```
