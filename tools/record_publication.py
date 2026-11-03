"""Record where a verified image derivative was manually published; no network access."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import yaml
except ImportError as exc:  # pragma: no cover - installation guidance
    yaml = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from validate import ID_PATTERN, _schema_errors, validate


def _load(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError(f"Install tools/requirements.txt first: {_IMPORT_ERROR}")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"record must be a mapping: {path}")
    return value


def record_publication(
    root: Path,
    *,
    publication_id: str,
    derivative_record_path: str,
    destination: str,
    published_at: str,
    public_url: str | None = None,
) -> Path:
    """Write one publication record linked to a validated, metadata-clean derivative."""
    if yaml is None:
        raise RuntimeError(f"Install tools/requirements.txt first: {_IMPORT_ERROR}")
    root = root.resolve()
    if not ID_PATTERN.fullmatch(publication_id):
        raise ValueError("publication_id must be a stable lowercase ID")
    if not destination.strip():
        raise ValueError("destination must name the platform or publication location")
    try:
        parsed_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("published_at must be an ISO-8601 timestamp") from exc
    if parsed_date.tzinfo is None:
        raise ValueError("published_at must include a timezone")
    if public_url:
        parsed_url = urlparse(public_url)
        if parsed_url.scheme not in {"https", "http"} or not parsed_url.netloc:
            raise ValueError("public_url must be an absolute HTTP(S) URL")

    issues = validate(root)
    if issues:
        raise ValueError("project validation failed before publication record: " + "; ".join(issues))
    relative = Path(derivative_record_path)
    if not derivative_record_path or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("derivative record path must stay inside the project root")
    sidecar_path = (root / relative).resolve()
    try:
        sidecar_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("derivative record resolves outside the project root") from exc
    if not sidecar_path.is_file():
        raise FileNotFoundError(f"derivative record not found: {derivative_record_path}")
    derivative = _load(sidecar_path)
    if sidecar_path.parent.name != "exports" or sidecar_path.stem != derivative.get("id"):
        raise ValueError("derivative record must be the canonical sidecar under an infographic exports folder")
    if derivative.get("status") != "ready_for_human_review" or derivative.get("metadata_scan") != "pass":
        raise ValueError("publication requires a metadata-checked derivative ready for human review")
    output = (root / Path(derivative["output_path"])).resolve()
    try:
        output.resolve().relative_to(root)
    except ValueError as exc:
        raise ValueError("derivative output resolves outside the project root") from exc
    if not output.is_file() or "masters" in output.parts or "discard_candidates" in output.parts:
        raise ValueError("publication can reference only an existing derivative, never a source master")

    record = {
        "schema_version": "0.1.0",
        "id": publication_id,
        "production_id": derivative["work_id"],
        "asset_id": derivative["asset_id"],
        "derivative_id": derivative["id"],
        "derivative_path": derivative["output_path"],
        "destination": destination.strip(),
        "published_at": published_at,
        "derivative_sha256": derivative["output_sha256"],
        "profile_version": derivative["profile_version"],
    }
    if public_url:
        record["public_url"] = public_url
    schema = _load(root / "schemas/content/records.schema.json")
    errors = _schema_errors(record, schema["$defs"]["publication_record"], schema, "publication")
    if errors:
        raise ValueError("invalid publication record: " + "; ".join(errors))
    output_path = root / "publications" / f"{publication_id}.yaml"
    if output_path.exists():
        raise FileExistsError(f"publication record exists; refusing overwrite: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8", newline="\n") as stream:
        yaml.safe_dump(record, stream, allow_unicode=True, sort_keys=False, explicit_start=True)
    issues = validate(root)
    if issues:
        raise ValueError("publication record preserved but project validation found issues: " + "; ".join(issues))
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--id", required=True, dest="publication_id")
    parser.add_argument("--derivative-record", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--published-at", required=True, help="ISO-8601 timestamp including timezone")
    parser.add_argument("--public-url")
    args = parser.parse_args()
    try:
        path = record_publication(
            args.root,
            publication_id=args.publication_id,
            derivative_record_path=args.derivative_record,
            destination=args.destination,
            published_at=args.published_at,
            public_url=args.public_url,
        )
    except (OSError, UnicodeError, ValueError, RuntimeError, KeyError) as exc:
        print(f"PUBLICATION-ERROR {exc}", file=sys.stderr)
        return 2
    print(f"PUBLICATION-RECORDED {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
