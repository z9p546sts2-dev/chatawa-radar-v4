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
- **Unit 28** — `radar_v4/snapshot_verify.py` checksum verify
- **Unit 29** — `radar_v4/pack_export.py` snapshot → FIXTURE/SYNTHETIC pack
- **Unit 30** — `radar_v4/registry_files.py` local registry persist/load
- **Unit 31** — `radar_v4/change_continuity.py` from/to chain check
- **Unit 32** — CLI `verify` and `export-pack`
- **Unit 33** — `radar_v4/ruler.py` measurement-ruler identity (`dataset_id` is a name, not the ruler)
- **Unit 34** — `radar_v4/quarantine_journal.py` refusal journal
- **Unit 35** — `radar_v4/checksum_sidecar.py` `.sha256` sidecar
- **Unit 36** — CLI `codes`, `quarantine`, `registry-write`, `--sidecar`
- **Unit 37** — `replay --expect-ruler`
- **Unit 38** — pack loader skips journal/manifest/registry artifacts (not observations)
- **Unit 39** — `radar_v4/pack_manifest.py` pack file digests
- **Unit 40** — verify a pack against its manifest
- **Unit 41** — ruler sidecar + CLI `show-ruler`
- **Unit 42** — session report `document_kind` / `report_version`
- **Unit 43** — `radar_v4/atomic_write.py` write temp sibling then replace
- **Unit 44** — pack load verifies an existing `manifest.json`; missing is optional unless required
- **Unit 45** — `session --require-manifest` and `session --expect-ruler`
- **Unit 46** — `compare_pack_manifests` / CLI `pack-compare`
- **Unit 47** — `MANIFEST_REQUIRED` in the refusal catalog
- **Unit 48** — evidence-file writes refuse an existing path unless `replace=True`
- **Unit 49** — `radar_v4/pack_inventory.py` lists pack file roles without measuring
- **Unit 50** — `radar_v4/bundle_verify.py` snapshot + optional sidecar/ruler check
- **Unit 51** — quarantine journal `document_kind` / `journal_version` / read
- **Unit 52** — CLI `pack-inventory`, `bundle-verify`, and `--replace`
- **Unit 53** — `write_snapshot_bundle` / `write_bundle_sidecars`
- **Unit 54** — `read_session_report_file` refuses the wrong `document_kind`
- **Unit 55** — registry files carry `document_kind` / `registry_version`
- **Unit 56** — pack inventory includes SHA-256 file digests without measuring
- **Unit 57** — CLI `write-bundle`, `show-report`, `show-journal`
- **Units 58–60** — document-kind catalog, detect, CLI `detect-kind`
- **Units 61–63** — CLI `show-declaration`, `show-snapshot`, `show-observation`
- **Units 64–67** — provenance mix and admission without measurement
- **Units 68–73** — compare rulers/reports and summarize journals
- **Units 74–79** — report-to-snapshot bind, determinism, snapshot inventory
- **Units 80–87** — pack layout, canonical JSON, identities, describe
- **Units 88–94** — reason-code lookup/catalog document, inventory compare, inventory vs manifest
- **Units 95–100** — workshop capability status (not a measurement), admission readiness, forbidden-claim fields, highest-unit lock at 100
- **Units 101–150** — claim-level consistency, arithmetic recompute, locked-scope, pack safety, evidence chain, local audit copy, no-network scan, highest-unit lock at 150. Inspectability only; not a research result.
- **Units 151–200** — OHLC/retrieval/ruler-field checks, percent and unexpected-file refusal, text safety, replay/export round-trip, catalog audit, locked-question bind, human disposition, stop record, highest-unit lock at 200. Inspectability only; not a research result.
- **Units 201–250** — source hygiene, pack hygiene, decimal-string closes, admission/lineage describe, reserved-name and UTF-16 refusal, command catalog, local self-test, pack certify compose, highest-unit lock at 250. Inspectability only; not a research result.
- **Units 251–300** — byte-level pack identity, filename-date and count checks, claim-word value refusal, certify/lineage/self-test determinism, README unit lock, workshop freeze compose/verify, highest-unit lock at 300. Inspectability only; not a research result.
- **Units 301–350** — path lock, journal-code catalog bind, freeze-versus-status bind, byte-record write/verify, close-sign and retrieval-unique describe, export portable byte-check, highest-unit lock at 350. Inspectability only; not a research result.
- **Units 351–400** — reserved-stem / leading-hyphen / double-json / empty-pack name lock, path/name/freeze/package determinism, snapshot-count bind, path-lock record write/verify, highest-unit lock at 400. Inspectability only; not a research result.
- **Units 401–450** — unlabeled/unknown/unreadable JSON kind lock, name-lock verify/compare, workshop stamp compose/determinism/write/verify, name-status bind, export portable name/kind check, highest-unit lock at 450. Inspectability only; not a research result.
- **Units 451–500** — journal kind/entry/source lock, journal-lock determinism/write/verify, kind-lock equality/write/verify, stamp-status bind, highest-unit lock at 500. Inspectability only; not a research result.
- **Units 501–550** — session-report kind/checksum/measured lock, ruler kind/object/checksum lock, report-ruler bind, report-status bind, highest-unit lock at 550. Inspectability only; not a research result.

Locked question: `RADAR_V4_PHASE5_LOCKED_QUESTION_TC.md`

## Still forbidden

Network downloads, broker/paper trading, indicators, thresholds, ranking, and treating software-test numbers as market evidence.

## Commands

```text
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m radar_v4 session --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 session --pack fixtures/synthetic_one_symbol_1d --require-manifest
PYTHONPATH=. python3 -m radar_v4 replay --snapshot <snapshot.json>
PYTHONPATH=. python3 -m radar_v4 compare --left <snapshot.json> --right <snapshot.json>
PYTHONPATH=. python3 -m radar_v4 verify --snapshot <snapshot.json>
PYTHONPATH=. python3 -m radar_v4 export-pack --snapshot <snapshot.json> --out <empty-dir>
PYTHONPATH=. python3 -m radar_v4 codes
PYTHONPATH=. python3 -m radar_v4 quarantine --pack fixtures/synthetic_one_symbol_1d --out journal.json
PYTHONPATH=. python3 -m radar_v4 pack-verify --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 pack-compare --left fixtures/synthetic_one_symbol_1d --right fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 pack-inventory --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 bundle-verify --snapshot <snapshot.json>
PYTHONPATH=. python3 -m radar_v4 write-bundle --snapshot <snapshot.json>
PYTHONPATH=. python3 -m radar_v4 show-report --report <session_report.json>
PYTHONPATH=. python3 -m radar_v4 show-journal --journal <journal.json>
PYTHONPATH=. python3 -m radar_v4 show-ruler --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 status
PYTHONPATH=. python3 -m radar_v4 bounds
PYTHONPATH=. python3 -m radar_v4 pack-describe --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 admission --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 determinism --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 locked-scope --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 pack-safety --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 no-network
PYTHONPATH=. python3 -m radar_v4 replay-eq --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 question-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 stop-record
PYTHONPATH=. python3 -m radar_v4 hygiene-scan
PYTHONPATH=. python3 -m radar_v4 pack-hygiene --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 decimal-check --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 lineage --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 certify --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 self-test
PYTHONPATH=. python3 -m radar_v4 commands
PYTHONPATH=. python3 -m radar_v4 byte-check --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 certify-eq --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 freeze --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 readme-lock
PYTHONPATH=. python3 -m radar_v4 path-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 freeze-bind --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 close-sign --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 name-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 snapshot-count --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 freeze-eq --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 kind-lock --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 stamp --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 name-bind --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 journal-lock --journal <journal.json>
PYTHONPATH=. python3 -m radar_v4 kind-lock-eq --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 stamp-bind --pack fixtures/synthetic_one_symbol_1d
PYTHONPATH=. python3 -m radar_v4 ruler-lock --pack fixtures/synthetic_one_symbol_1d
```
