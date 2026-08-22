"""Load a local dataset pack. FIXTURE/SYNTHETIC only. No vendor."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from radar_v4.dataset import DatasetDeclaration
from radar_v4.declaration_json import intake_declaration_json
from radar_v4.fixture_pack import PACK_ALLOWED_PROVENANCE
from radar_v4.json_intake import UnreadableDocument
from radar_v4.observation import Observation
from radar_v4.observation_json import (
    ObservationIntakeRecord,
    ObservationIntakeReport,
    intake_observation_json,
)
from radar_v4.validation import ValidationIssue, ValidationResult

DECLARATION_FILENAME = "declaration.json"
SKIP_FILENAMES = frozenset(
    {
        DECLARATION_FILENAME,
        "snapshot.json",
        "session_report.json",
        "manifest.json",
        "journal.json",
        "registry.json",
        "quarantine.json",
        "ruler.json",
    }
)


@dataclass(frozen=True)
class DatasetPackReport:
    declaration: DatasetDeclaration | None
    pack_issues: tuple[ValidationIssue, ...]
    observation_intake: ObservationIntakeReport
    unreadable: tuple[UnreadableDocument, ...]

    def usable(self) -> bool:
        return self.declaration is not None and len(self.pack_issues) == 0


def load_dataset_pack(directory: str | Path) -> DatasetPackReport:
    """Read declaration.json plus observation JSON files from one directory.

    HISTORICAL and LIVE labels are quarantined here even if identity-valid.
    This loader is not a market-data client and does not relabel records.
    """
    root = Path(directory)
    if not root.is_dir():
        return DatasetPackReport(
            declaration=None,
            pack_issues=(),
            observation_intake=ObservationIntakeReport(
                accepted=(), quarantined=(), unreadable=()
            ),
            unreadable=(
                UnreadableDocument(
                    index=0,
                    raw=str(root),
                    code="UNREADABLE_PACK",
                    reason="dataset pack path is not a directory",
                ),
            ),
        )

    pack_issues: list[ValidationIssue] = []
    unreadable: list[UnreadableDocument] = []
    declaration: DatasetDeclaration | None = None
    declaration_path = root / DECLARATION_FILENAME
    if not declaration_path.is_file():
        pack_issues.append(
            ValidationIssue(
                "DECLARATION_FILE_MISSING",
                "dataset pack requires declaration.json",
                "declaration",
            )
        )
    else:
        parsed = intake_declaration_json(declaration_path.read_text(encoding="utf-8"))
        if parsed.unreadable is not None:
            unreadable.append(parsed.unreadable)
            pack_issues.append(
                ValidationIssue(
                    "UNREADABLE_DECLARATION",
                    parsed.unreadable.reason,
                    "declaration",
                )
            )
        elif parsed.declaration is None:
            if parsed.validation is not None:
                pack_issues.extend(parsed.validation.issues)
        else:
            declaration = parsed.declaration
            if declaration.provenance_class not in PACK_ALLOWED_PROVENANCE:
                pack_issues.append(
                    ValidationIssue(
                        "PACK_PROVENANCE_NOT_ALLOWED",
                        "dataset pack may declare only FIXTURE or SYNTHETIC",
                        "provenance_class",
                    )
                )

    accepted: list[Observation] = []
    quarantined: list[ObservationIntakeRecord] = []
    for path in sorted(root.glob("*.json")):
        if path.name in SKIP_FILENAMES:
            continue
        report = intake_observation_json(path.read_text(encoding="utf-8"))
        unreadable.extend(report.unreadable)
        quarantined.extend(report.quarantined)
        for item in report.accepted:
            if item.envelope.provenance_class not in PACK_ALLOWED_PROVENANCE:
                quarantined.append(
                    ObservationIntakeRecord(
                        observation=item,
                        validation=ValidationResult(
                            valid=False,
                            issues=(
                                ValidationIssue(
                                    "PACK_PROVENANCE_NOT_ALLOWED",
                                    "dataset pack may load only FIXTURE or SYNTHETIC records",
                                    "provenance_class",
                                ),
                            ),
                        ),
                    )
                )
            else:
                accepted.append(item)

    accepted, identity_quarantine = _apply_identity_gate(accepted)
    quarantined.extend(identity_quarantine)
    pack_issues.sort(key=lambda item: (item.code, item.field or "", item.reason))
    return DatasetPackReport(
        declaration=declaration,
        pack_issues=tuple(pack_issues),
        observation_intake=ObservationIntakeReport(
            accepted=tuple(accepted),
            quarantined=tuple(quarantined),
            unreadable=(),
        ),
        unreadable=tuple(unreadable),
    )


def _apply_identity_gate(
    observations: list[Observation],
) -> tuple[list[Observation], list[ObservationIntakeRecord]]:
    """Keep the first record. Same checksum is idempotent. Conflicts quarantine."""
    kept: list[Observation] = []
    quarantined: list[ObservationIntakeRecord] = []
    by_checksum: dict[str | None, Observation] = {}
    by_identity: dict[tuple[object, ...], Observation] = {}
    for item in observations:
        checksum = item.envelope.checksum
        existing_same = by_checksum.get(checksum)
        if existing_same is not None:
            if existing_same.payload_checksum == item.payload_checksum:
                continue
            quarantined.append(
                ObservationIntakeRecord(
                    observation=item,
                    validation=ValidationResult(
                        valid=False,
                        issues=(
                            ValidationIssue(
                                "CONTRADICTORY_PAYLOAD",
                                "same envelope checksum already loaded with a different payload",
                                "payload_checksum",
                            ),
                        ),
                    ),
                )
            )
            continue
        identity = item.envelope.identity_key()
        if identity in by_identity:
            quarantined.append(
                ObservationIntakeRecord(
                    observation=item,
                    validation=ValidationResult(
                        valid=False,
                        issues=(
                            ValidationIssue(
                                "CONTRADICTORY_IDENTITY",
                                "same evidence identity already loaded with a different checksum",
                                "checksum",
                            ),
                        ),
                    ),
                )
            )
            continue
        by_checksum[checksum] = item
        by_identity[identity] = item
        kept.append(item)
    return kept, quarantined
