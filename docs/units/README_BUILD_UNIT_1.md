# Radar V4 Build Unit 1 — Evidence Envelope and Provenance Gate

**Authorization:** `AUTHORIZE BUILD UNIT 1 — TC`  
**Disposition:** `Accepted-TC`  
**Language:** Python 3.12, this unit only  
**Market method:** none  
**Dependencies added:** none

This unit represents and validates **evidence identity**. It does not decide whether a market value is true.

## What this unit does

- construct an evidence envelope with provenance, source, subject, timestamps, interval, timezone, transformation version, and checksum;
- serialize that envelope deterministically;
- recompute SHA-256 over the canonical payload (checksum field excluded);
- return a structured validation result;
- reject missing, unknown, or contradictory identity fields without repairing them.

Allowed provenance classes are:

`LIVE`, `HISTORICAL`, `BACKFILL`, `SYNTHETIC`, `FIXTURE`, `REPLAY`, `MANUALLY_EDITED`

Build Unit 1 examples use only `FIXTURE` and `SYNTHETIC`.

## Serialization rules

- JSON object, sorted keys, compact separators;
- timestamps are timezone-aware ISO-8601 with microseconds and a numeric offset;
- omitted `context_decision_use_tag` is JSON `null`;
- missing timezone is **not** replaced with UTC;
- the checksum is not included in the bytes that produce the checksum.

The optional `context_decision_use_tag` is identity metadata only. It has no ranking, gating, or trading effect in this unit.

## Commands

From the repository root:

```text
python3 -m compileall radar_v4 tests
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

## Test categories

```text
SOFTWARE CORRECTNESS — tests/test_evidence_software.py
DATA CORRECTNESS     — tests/test_evidence_data.py
METHOD VALIDITY      — NOT APPLICABLE TO BUILD UNIT 1
OPERATIONAL RESILIENCE — import / parse visibility only
```

## What this unit does not prove

- market correctness or usefulness;
- predictive power or edge;
- method validity;
- fitness of any live or historical dataset;
- a data vendor, feature, score, threshold, signal, or ranking;
- paper trading, brokerage, or autonomous operation;
- that Radar V4 is production ready.

Maximum honest claim if tests pass:

`BUILD UNIT 1 SOFTWARE/DATA FOUNDATION IMPLEMENTED WITHIN BOUNDED SCOPE`

## Rollback

Revert the Build Unit 1 commit(s) on this branch to pre-build `cc2af9a`.

No database, secret, network resource, or irreversible artifact is created.
