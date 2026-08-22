# Radar V4 Phase 5 — Data / Research Foundation

**Authorization:** `AUTHORIZE PHASE 5 — TC`

Phase 5 adds dataset admission, an optional numeric observation payload, and a descriptive close-to-close baseline. It does not add a vendor client, a signal, or a method.

## Units

- **Unit 7** — `radar_v4/dataset.py` dataset declaration and admission
- **Unit 8** — `radar_v4/observation.py` payload + payload checksum
- **Unit 9** — `radar_v4/baseline.py` ordinary close-to-close description

Locked question: `RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`

## Still forbidden

Network downloads, broker/paper trading, indicators, thresholds, ranking, and treating software-test numbers as market evidence.

## Commands

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
```
