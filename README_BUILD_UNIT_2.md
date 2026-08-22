# Radar V4 Build Unit 2 — Evidence Intake and Quarantine Gate

**Authorization:** `Lets keep building.-TC`  
**Disposition:** `Accepted-TC`  
**Depends on:** accepted Build Unit 1  
**Market method:** none  
**Dependencies added:** none

This unit takes a batch of evidence envelopes, validates each one, and partitions the batch into **accepted** and **quarantined** records. It does not fetch data, repair records, or interpret markets.

## What this unit does

- accept a sequence of `EvidenceEnvelope` objects;
- run Build Unit 1 validation on each;
- keep input order inside each partition;
- leave original envelopes unchanged;
- keep invalid records visible in quarantine with structured issues.

## What this unit does not do

- live or historical market-data access;
- file or API ingestion of vendor bars;
- silent repair of missing timezone, provider, checksum, or provenance;
- scoring, features, thresholds, signals, ranking, or trading;
- persistence, databases, or schedulers.

## Commands

From the repository root:

```text
python3 -m compileall radar_v4 tests
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

## Test categories

```text
SOFTWARE CORRECTNESS — tests/test_intake_software.py
DATA CORRECTNESS     — tests/test_intake_data.py
METHOD VALIDITY      — NOT APPLICABLE TO BUILD UNIT 2
```

## What this unit does not prove

- that any dataset is true;
- that a vendor or symbol universe is approved;
- method validity or edge;
- that Phase 5 data work is authorized;
- that Build Unit 3 is authorized.

Maximum honest claim if tests pass:

`BUILD UNIT 2 SOFTWARE/DATA FOUNDATION IMPLEMENTED WITHIN BOUNDED SCOPE`

## Rollback

Revert this unit's commits. No external state is created.
