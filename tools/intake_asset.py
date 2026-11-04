"""Copy an image source into a versioned private master or discard-candidate path."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
    from PIL import Image
except ImportError as exc:  # pragma: no cover - installation guidance
    yaml = None
    Image = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from validate import _schema_errors, validate


CORE_SCHEMA = Path("schemas/common/records.schema.json")


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return "sha256:" + hasher.hexdigest()


def _validate_timestamp(value: str, label: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return value


def _find_prompt_resolution(root: Path, prompt_id: str) -> dict[str, Any]:
    matches = []
    for path in root.glob("projects/**/productions/infographic/prompt_resolutions/*.yaml"):
        if not path.is_file() or yaml is None:
            continue
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get("id") == prompt_id:
            matches.append(record)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one prompt resolution with ID {prompt_id!r}")
    return matches[0]


def _find_prompt_review(root: Path, review_id: str) -> dict[str, Any]:
    matches = []
    for path in root.glob("projects/**/productions/infographic/prompts/*.prompt-review.yaml"):
        if not path.is_file() or yaml is None:
            continue
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get("id") == review_id:
            matches.append(record)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one prompt review with ID {review_id!r}")
    return matches[0]


def _find_project(root: Path, project_id: str) -> dict[str, Any]:
    matches = []
    for path in root.glob("projects/**/project.yaml"):
        if not path.is_file() or yaml is None:
            continue
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get("id") == project_id:
            matches.append(record)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one mini-project with ID {project_id!r}")
    return matches[0]


def _load_generation_arguments(root: Path, relative_path: str) -> dict[str, Any]:
    source_ref = Path(relative_path)
    if not relative_path or source_ref.is_absolute() or ".." in source_ref.parts or yaml is None:
        raise ValueError("generation-arguments file must be a project-relative YAML path")
    source_path = (root / source_ref).resolve()
    try:
        source_path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("generation-arguments file resolves outside the project root") from exc
    if not source_path.is_file():
        raise FileNotFoundError(f"generation-arguments file not found: {relative_path}")
    try:
        values = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    except (UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read generation-arguments file: {exc}") from exc
    if not isinstance(values, dict):
        raise ValueError("generation-arguments YAML root must be a mapping")
    return {
        "source_path": source_ref.as_posix(),
        "source_sha256": _digest(source_path),
        "values": values,
    }


def intake_image(
    root: Path,
    *,
    source_path: Path,
    generation_id: str,
    asset_id: str,
    asset_version: str,
    prompt_resolution_id: str,
    prompt_review_id: str | None = None,
    generation_arguments_file: str | None = None,
    provider: str,
    generated_at: str,
    disposition: str,
    reviewer: str,
    reviewed_at: str,
    model: str | None = None,
    provider_job_id: str | None = None,
    supersedes_generation_id: str | None = None,
) -> Path:
    """Copy a PNG/JPEG as exact source bytes and write immutable provenance once."""
    if yaml is None or Image is None:
        raise RuntimeError(f"Install tools/requirements.txt before image intake: {_IMPORT_ERROR}")
    root = root.resolve()
    source_path = source_path.expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"source image not found: {source_path}")
    suffix = source_path.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("image intake accepts PNG and JPEG sources only")
    try:
        with Image.open(source_path) as image:
            image_format = image.format
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("animated or multi-frame sources are not supported")
            image.verify()
    except (OSError, ValueError) as exc:
        raise ValueError(f"source is not a valid supported image: {exc}") from exc
    expected_format = "PNG" if suffix == ".png" else "JPEG"
    if image_format != expected_format:
        raise ValueError("source file extension does not match its image format")
    if disposition not in {"accepted", "discard_candidate"}:
        raise ValueError("disposition must be accepted or discard_candidate")
    if not all(value.strip() for value in (generation_id, asset_id, asset_version, prompt_resolution_id, provider, generated_at, reviewer, reviewed_at)):
        raise ValueError("IDs, provider, timestamps, and reviewer must be non-empty")
    _validate_timestamp(generated_at, "generated_at")
    _validate_timestamp(reviewed_at, "reviewed_at")

    issues = validate(root)
    if issues:
        raise ValueError("project validation failed before intake: " + "; ".join(issues))
    prompt = _find_prompt_resolution(root, prompt_resolution_id)
    if prompt.get("status") != "resolved" or prompt.get("work_kind") != "infographic":
        raise ValueError("intake requires a resolved prompt for an infographic production")
    productions = _all_productions(root)
    production = next((record for record in productions if record.get("id") == prompt.get("work_id")), None)
    if production is None:
        raise ValueError("prompt resolution does not reference an existing infographic production")
    project = _find_project(root, production.get("project_id", ""))
    if project.get("prompt_review_required") is True and not prompt_review_id:
        raise ValueError("this project requires --prompt-review-id before image intake")
    if prompt_review_id:
        prompt_review = _find_prompt_review(root, prompt_review_id)
        if (
            prompt_review.get("status") != "selected_pass"
            or prompt_review.get("work_id") != prompt.get("work_id")
            or prompt_review.get("prompt_resolution_id") != prompt_resolution_id
        ):
            raise ValueError("image intake requires a passing prompt review that matches this resolved prompt and production")
        chosen = next((item for item in prompt_review.get("candidates", []) if isinstance(item, dict) and item.get("id") == prompt_review.get("selected_candidate_id")), None)
        if chosen is None or chosen.get("prompt_sha256") != prompt.get("prompt_sha256"):
            raise ValueError("selected prompt review candidate does not match the resolved prompt")
    generation_arguments = _load_generation_arguments(root, generation_arguments_file) if generation_arguments_file else None

    folder = "masters" if disposition == "accepted" else "discard_candidates"
    relative_source = Path("assets") / folder / asset_id / asset_version / f"source{suffix}"
    relative_record = Path("assets/generations") / generation_id / "provenance.yaml"
    target = (root / relative_source).resolve()
    record_path = (root / relative_record).resolve()
    for candidate in (target, record_path):
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError("intake destination resolves outside the project root") from exc
    if target == source_path:
        raise ValueError("source already occupies its immutable target; use a new asset version")
    if target.exists() or record_path.exists():
        raise FileExistsError("intake target or provenance already exists; refusing overwrite")

    record: dict[str, Any] = {
        "schema_version": "0.1.0",
        "id": generation_id,
        "asset_id": asset_id,
        "asset_version": asset_version,
        "work_id": prompt["work_id"],
        "work_kind": prompt["work_kind"],
        "prompt_resolution_id": prompt_resolution_id,
        "provider": provider.strip(),
        "generated_at": generated_at.strip(),
        "source_path": relative_source.as_posix(),
        "source_sha256": _digest(source_path),
        "disposition": disposition,
        "reviewer": reviewer.strip(),
        "reviewed_at": reviewed_at.strip(),
    }
    if prompt_review_id:
        record["prompt_review_id"] = prompt_review_id
    if generation_arguments:
        record["generation_arguments"] = generation_arguments
    if model:
        record["model"] = model.strip()
    if provider_job_id:
        record["provider_job_id"] = provider_job_id.strip()
    if supersedes_generation_id:
        record["supersedes_generation_id"] = supersedes_generation_id.strip()
    schema = json.loads((root / CORE_SCHEMA).read_text(encoding="utf-8"))
    schema_errors = _schema_errors(record, schema["$defs"]["image_generation"], schema, "image_generation")
    if schema_errors:
        raise ValueError("invalid image generation record: " + "; ".join(schema_errors))

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, target)
    if _digest(target) != record["source_sha256"]:
        raise ValueError("copied source hash differs from original; evidence retained for review")
    record_path.parent.mkdir(parents=True, exist_ok=True)
    with record_path.open("x", encoding="utf-8", newline="\n") as stream:
        yaml.safe_dump(record, stream, allow_unicode=True, sort_keys=False, explicit_start=True)
    issues = validate(root)
    if issues:
        raise ValueError("intake was copied but project validation found issues: " + "; ".join(issues))
    return record_path


def _all_productions(root: Path) -> list[dict[str, Any]]:
    if yaml is None:
        return []
    result: list[dict[str, Any]] = []
    for path in root.glob("projects/**/productions/infographic/production.yaml"):
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            result.append(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source", type=Path, required=True, dest="source_path")
    parser.add_argument("--generation-id", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--asset-version", required=True)
    parser.add_argument("--prompt-resolution-id", required=True)
    parser.add_argument("--prompt-review-id")
    parser.add_argument("--generation-arguments-file")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model")
    parser.add_argument("--provider-job-id")
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--disposition", choices=("accepted", "discard_candidate"), required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reviewed-at", required=True)
    parser.add_argument("--supersedes-generation-id")
    args = parser.parse_args()
    try:
        path = intake_image(
            args.root,
            source_path=args.source_path,
            generation_id=args.generation_id,
            asset_id=args.asset_id,
            asset_version=args.asset_version,
            prompt_resolution_id=args.prompt_resolution_id,
            prompt_review_id=args.prompt_review_id,
            generation_arguments_file=args.generation_arguments_file,
            provider=args.provider,
            generated_at=args.generated_at,
            disposition=args.disposition,
            reviewer=args.reviewer,
            reviewed_at=args.reviewed_at,
            model=args.model,
            provider_job_id=args.provider_job_id,
            supersedes_generation_id=args.supersedes_generation_id,
        )
    except (OSError, UnicodeError, ValueError, RuntimeError, KeyError) as exc:
        print(f"INTAKE-ERROR {exc}", file=sys.stderr)
        return 2
    print(f"IMAGE-INTAKED {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
