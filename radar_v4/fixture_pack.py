"""Load labeled FIXTURE/SYNTHETIC JSON packs. No vendor or network access."""

from __future__ import annotations

from pathlib import Path

from radar_v4.intake import IntakeRecord
from radar_v4.json_intake import DocumentIntakeReport, UnreadableDocument, intake_json_text
from radar_v4.validation import ValidationIssue, ValidationResult

PACK_ALLOWED_PROVENANCE = frozenset({"FIXTURE", "SYNTHETIC"})


def load_fixture_pack(directory: str | Path) -> DocumentIntakeReport:
    """Read `*.json` files from a local directory and intake them.

    Files whose envelopes are LIVE, HISTORICAL, or any other non-pack
    provenance are quarantined even if identity-valid. This loader is not
    a market-data client.
    """
    root = Path(directory)
    if not root.is_dir():
        return DocumentIntakeReport(
            accepted=(),
            quarantined=(),
            unreadable=(
                UnreadableDocument(
                    index=0,
                    raw=str(root),
                    code="UNREADABLE_PACK",
                    reason="fixture pack path is not a directory",
                ),
            ),
        )

    accepted: list[IntakeRecord] = []
    quarantined: list[IntakeRecord] = []
    unreadable: list[UnreadableDocument] = []
    for path in sorted(root.glob("*.json")):
        report = intake_json_text(path.read_text(encoding="utf-8"))
        unreadable.extend(report.unreadable)
        for record in report.accepted:
            if record.envelope.provenance_class not in PACK_ALLOWED_PROVENANCE:
                quarantined.append(
                    IntakeRecord(
                        envelope=record.envelope,
                        validation=ValidationResult(
                            valid=False,
                            issues=(
                                ValidationIssue(
                                    "PACK_PROVENANCE_NOT_ALLOWED",
                                    "fixture pack may load only FIXTURE or SYNTHETIC records",
                                    "provenance_class",
                                ),
                            ),
                        ),
                    )
                )
            else:
                accepted.append(record)
        quarantined.extend(report.quarantined)
    return DocumentIntakeReport(
        accepted=tuple(accepted),
        quarantined=tuple(quarantined),
        unreadable=tuple(unreadable),
    )
