"""Copy a local pack into an audit directory and verify the copy.

No network. The copy is not market evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from json import JSONDecodeError, dumps, loads
from pathlib import Path

from radar_v4.atomic_write import file_exists_without_replace, write_text_atomic


AUDIT_MANIFEST = "audit_manifest.json"
DOCUMENT_KIND = "radar_v4.audit_bundle"


class AuditBundleError(ValueError):
    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def _dump(document: dict[str, object]) -> str:
    return dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class AuditBundle:
    directory: str
    files: dict[str, str]
    source_pack: str

    def serialize(self) -> str:
        return _dump(
            {
                "directory": self.directory,
                "document_kind": DOCUMENT_KIND,
                "files": dict(sorted(self.files.items())),
                "notes": [
                    "audit bundle is a local copy",
                    "SYNTHETIC and FIXTURE numbers are not HISTORICAL evidence",
                ],
                "source_pack": self.source_pack,
            }
        )


def write_audit_bundle(
    pack: str | Path, destination: str | Path, replace: bool = False
) -> Path:
    source = Path(pack)
    if not source.is_dir():
        raise AuditBundleError("UNREADABLE_PACK", f"{source} is not a pack directory")
    target = Path(destination)
    if target.exists() and target.is_file():
        raise AuditBundleError(
            "PACK_EXPORT_PATH_IS_FILE",
            f"{target} is a file, not an audit directory",
        )
    if target.exists() and any(target.iterdir()) and not replace:
        raise AuditBundleError(
            "PACK_EXPORT_DIRECTORY_NOT_EMPTY",
            f"{target} already contains files; pass replace=True to overwrite the manifest only after a clean directory",
        )
    if target.exists() and any(target.iterdir()) and replace:
        raise AuditBundleError(
            "PACK_EXPORT_DIRECTORY_NOT_EMPTY",
            f"{target} is not empty; audit write will not merge",
        )
    target.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    for path in sorted(source.iterdir()):
        if not path.is_file() or path.is_symlink():
            continue
        copied = target / path.name
        copied.write_bytes(path.read_bytes())
        files[path.name] = _digest(copied)
    written = target / AUDIT_MANIFEST
    if file_exists_without_replace(written, replace):
        raise AuditBundleError("FILE_EXISTS", f"{written} already exists")
    write_text_atomic(written, AuditBundle(str(target), files, str(source)).serialize() + "\n")
    return written


def read_audit_bundle(directory: str | Path) -> AuditBundle:
    target = Path(directory) / AUDIT_MANIFEST
    try:
        text = target.read_text(encoding="utf-8")
        raw = loads(text)
    except OSError as exc:
        raise AuditBundleError("UNREADABLE_JSON", str(exc)) from exc
    except JSONDecodeError as exc:
        raise AuditBundleError("UNREADABLE_JSON", exc.msg) from exc
    if not isinstance(raw, dict):
        raise AuditBundleError("UNREADABLE_JSON", "audit manifest must be an object")
    if raw.get("document_kind") != DOCUMENT_KIND:
        raise AuditBundleError(
            "UNREADABLE_JSON",
            "document_kind is not radar_v4.audit_bundle",
        )
    files = raw.get("files")
    if not isinstance(files, dict):
        raise AuditBundleError("UNREADABLE_JSON", "audit manifest files are missing")
    return AuditBundle(
        directory=str(raw.get("directory") or Path(directory)),
        files={str(key): str(value) for key, value in files.items()},
        source_pack=str(raw.get("source_pack") or ""),
    )


@dataclass(frozen=True)
class AuditVerification:
    matched: bool
    error_code: str | None
    expected: dict[str, str]
    actual: dict[str, str]

    def serialize(self) -> str:
        return _dump(
            {
                "actual": dict(sorted(self.actual.items())),
                "document_kind": "radar_v4.audit_verification",
                "error_code": self.error_code,
                "expected": dict(sorted(self.expected.items())),
                "matched": self.matched,
            }
        )


def verify_audit_bundle(directory: str | Path) -> AuditVerification:
    bundle = read_audit_bundle(directory)
    root = Path(directory)
    actual = {
        path.name: _digest(path)
        for path in sorted(root.iterdir())
        if path.is_file() and path.name != AUDIT_MANIFEST
    }
    extras = sorted(
        path.name
        for path in root.iterdir()
        if path.is_file() and path.name not in bundle.files and path.name != AUDIT_MANIFEST
    )
    expected = dict(bundle.files)
    matched = actual == expected and not extras
    return AuditVerification(
        matched=matched,
        error_code=None if matched else "AUDIT_BUNDLE_MISMATCH",
        expected=expected,
        actual=actual,
    )
