"""Local hygiene checks. Not market evidence. Not a security audit of the internet."""

from __future__ import annotations

import ast
import hashlib
import unicodedata
from collections import Counter
from pathlib import Path

from radar_v4.dataset_pack import SKIP_FILENAMES, load_dataset_pack
from radar_v4.integrity import IntegrityCheck

DANGEROUS_NAMES = frozenset({"eval", "exec", "subprocess", "socket"})
HIDDEN_PREFIX = "."


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def scan_python_source(path: Path) -> IntegrityCheck:
    """Refuse workshop Python that names eval, exec, subprocess, socket, or os.system."""
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in DANGEROUS_NAMES:
            hits.append(node.id)
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "system"
            and isinstance(node.value, ast.Name)
            and node.value.id == "os"
        ):
            hits.append("os.system")
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in DANGEROUS_NAMES:
                    hits.append(root)
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".", 1)[0]
            if root in DANGEROUS_NAMES:
                hits.append(root)
    if hits:
        return IntegrityCheck(
            "radar_v4.hygiene_scan",
            False,
            "DANGEROUS_CALL_REFUSED",
            ("Workshop source names a refused call or import.",),
            {"path": str(path), "hits": sorted(set(hits))},
        )
    return IntegrityCheck(
        "radar_v4.hygiene_scan",
        True,
        None,
        ("No refused call names found in this source file.",),
        {"path": str(path), "hits": []},
    )


def scan_workshop_tree(root: Path | None = None) -> IntegrityCheck:
    """Scan radar_v4/*.py for refused call names. This file may mention them."""
    base = Path(root) if root is not None else Path(__file__).resolve().parent
    hits: list[dict[str, object]] = []
    skip = {Path(__file__).resolve()}
    for path in sorted(base.glob("*.py")):
        if path.resolve() in skip:
            continue
        result = scan_python_source(path)
        if not result.valid:
            hits.append({"path": str(path.name), "hits": result.details.get("hits", [])})
    if hits:
        return IntegrityCheck(
            "radar_v4.hygiene_scan",
            False,
            "DANGEROUS_CALL_REFUSED",
            ("A workshop module names a refused call or import.",),
            {"hits": hits},
        )
    return IntegrityCheck(
        "radar_v4.hygiene_scan",
        True,
        None,
        ("Workshop modules do not name refused calls.",),
        {"hits": []},
    )


def hidden_file_scan(directory: Path) -> IntegrityCheck:
    hidden = sorted(
        path.name
        for path in Path(directory).iterdir()
        if path.name.startswith(HIDDEN_PREFIX)
    )
    if hidden:
        return IntegrityCheck(
            "radar_v4.hidden_file_scan",
            False,
            "HIDDEN_FILE_REFUSED",
            ("A hidden file is not part of a declared pack.",),
            {"hidden": hidden},
        )
    return IntegrityCheck(
        "radar_v4.hidden_file_scan",
        True,
        None,
        ("No hidden files in this directory.",),
        {"hidden": []},
    )


def nfc_name_scan(directory: Path) -> IntegrityCheck:
    denormalized = sorted(
        path.name
        for path in Path(directory).iterdir()
        if path.name != unicodedata.normalize("NFC", path.name)
    )
    if denormalized:
        return IntegrityCheck(
            "radar_v4.nfc_names",
            False,
            "NFC_NAME_REFUSED",
            ("A filename is not Unicode NFC. Names are not repaired.",),
            {"denormalized": denormalized},
        )
    return IntegrityCheck(
        "radar_v4.nfc_names",
        True,
        None,
        ("Filenames are Unicode NFC.",),
        {"denormalized": []},
    )


def duplicate_digest_scan(directory: Path) -> IntegrityCheck:
    digest_to_names: dict[str, list[str]] = {}
    for path in sorted(Path(directory).iterdir()):
        if not path.is_file():
            continue
        digest = _sha256_bytes(path.read_bytes())
        digest_to_names.setdefault(digest, []).append(path.name)
    dups = {key: names for key, names in digest_to_names.items() if len(names) > 1}
    if dups:
        return IntegrityCheck(
            "radar_v4.duplicate_digest_scan",
            False,
            "DUPLICATE_DIGEST_REFUSED",
            ("Two files have the same SHA-256.",),
            {"duplicates": dups},
        )
    return IntegrityCheck(
        "radar_v4.duplicate_digest_scan",
        True,
        None,
        ("File contents have unique SHA-256 values.",),
        {"duplicates": {}},
    )


def envelope_recompute_scan(directory: Path) -> IntegrityCheck:
    pack = load_dataset_pack(directory)
    mismatches: list[str] = []
    for item in pack.observation_intake.accepted:
        if item.envelope.checksum != item.envelope.compute_checksum():
            mismatches.append(f"envelope:{item.envelope.symbol_or_universe}")
        if item.payload_checksum != item.payload.compute_checksum():
            mismatches.append(f"payload:{item.envelope.symbol_or_universe}")
    if mismatches:
        return IntegrityCheck(
            "radar_v4.envelope_recompute",
            False,
            "ENVELOPE_CHECKSUM_MISMATCH",
            ("An observation checksum does not match its recomputed value.",),
            {"mismatches": mismatches},
        )
    return IntegrityCheck(
        "radar_v4.envelope_recompute",
        True,
        None,
        ("Observation envelope and payload checksums match.",),
        {"mismatches": [], "checked": pack.observation_intake.accepted_count()},
    )


def identity_uniqueness_scan(directory: Path) -> IntegrityCheck:
    pack = load_dataset_pack(directory)
    keys = [str(item.envelope.identity_key()) for item in pack.observation_intake.accepted]
    counts = Counter(keys)
    dups = {key: count for key, count in counts.items() if count > 1}
    if dups:
        return IntegrityCheck(
            "radar_v4.identity_uniqueness",
            False,
            "IDENTITY_NOT_UNIQUE",
            ("Two observations share the same identity key.",),
            {"duplicates": dups},
        )
    return IntegrityCheck(
        "radar_v4.identity_uniqueness",
        True,
        None,
        ("Observation identity keys are unique.",),
        {"duplicates": {}, "checked": len(keys)},
    )


def pack_hygiene(directory: Path) -> IntegrityCheck:
    parts = [
        hidden_file_scan(directory),
        nfc_name_scan(directory),
        duplicate_digest_scan(directory),
        envelope_recompute_scan(directory),
        identity_uniqueness_scan(directory),
    ]
    failed = [part for part in parts if not part.valid]
    if failed:
        first = failed[0]
        return IntegrityCheck(
            "radar_v4.pack_hygiene",
            False,
            first.error_code,
            ("Pack hygiene failed.",) + first.notes,
            {"failed": [part.document_kind for part in failed]},
        )
    return IntegrityCheck(
        "radar_v4.pack_hygiene",
        True,
        None,
        ("Pack hygiene checks passed. Not market evidence.",),
        {"failed": [], "skipped_names": sorted(SKIP_FILENAMES)},
    )
