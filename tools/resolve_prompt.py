"""Resolve layered image prompts and write an immutable private sidecar."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - installation guidance
    yaml = None


GROUP_ORDER = ("shared", "domain", "medium", "project", "entity", "request")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,95}$")
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z][A-Za-z0-9_.-]*)\s*\}\}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _load_yaml(path: Path, purpose: str) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required; install tools/requirements.txt")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read {purpose}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{purpose} root must be a mapping")
    return value


def _resolve_source(root: Path, relative: str, purpose: str) -> tuple[Path, str]:
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{purpose} must be a non-empty project-relative path")
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{purpose} resolves outside the project root") from exc
    if not candidate.is_file():
        raise ValueError(f"{purpose} does not exist: {relative}")
    return candidate, _sha256(candidate)


def resolve_prompt(
    root: Path,
    *,
    prompt_id: str,
    work_id: str,
    profile_path: str,
    values_path: str,
    additions: dict[str, list[str]] | None = None,
    work_kind: str = "infographic",
) -> dict[str, Any]:
    """Return a deterministic prompt-resolution record from explicit local inputs."""
    root = root.resolve()
    if not ID_RE.fullmatch(prompt_id) or not ID_RE.fullmatch(work_id):
        raise ValueError("prompt_id and work_id must be stable lowercase IDs")
    if not isinstance(work_kind, str) or not work_kind.strip():
        raise ValueError("work_kind must be non-empty")
    work_kind = work_kind.strip()

    profile_file, profile_digest = _resolve_source(root, profile_path, "prompt profile")
    values_file, values_digest = _resolve_source(root, values_path, "prompt values file")
    profile = _load_yaml(profile_file, "prompt profile")
    values_doc = _load_yaml(values_file, "prompt values")
    if set(profile) - {"schema_version", "id", "version", "layers"}:
        raise ValueError("prompt profile contains unsupported fields")
    if set(values_doc) - {"variables", "reference_assets"}:
        raise ValueError("prompt values file contains unsupported fields")
    if profile.get("schema_version") != "0.1.0":
        raise ValueError("profile schema_version must be 0.1.0")
    profile_id = profile.get("id")
    profile_version = profile.get("version")
    if not isinstance(profile_id, str) or not ID_RE.fullmatch(profile_id):
        raise ValueError("profile id must be a stable lowercase ID")
    if not isinstance(profile_version, str) or not SEMVER_RE.fullmatch(profile_version):
        raise ValueError("profile version must use MAJOR.MINOR.PATCH")

    variables = values_doc.get("variables")
    if not isinstance(variables, dict) or any(not isinstance(key, str) or not isinstance(value, str) for key, value in variables.items()):
        raise ValueError("prompt values must contain a variables mapping of strings")
    references = values_doc.get("reference_assets", [])
    if not isinstance(references, list) or any(not isinstance(item, dict) for item in references):
        raise ValueError("reference_assets must be a list of asset-reference mappings")
    for index, asset_ref in enumerate(references):
        asset_path = asset_ref.get("path")
        asset_file, asset_digest = _resolve_source(root, asset_path, f"reference asset {index + 1}") if isinstance(asset_path, str) else (None, None)
        if asset_file is None or asset_ref.get("sha256") != asset_digest:
            raise ValueError(f"reference asset {index + 1} is missing or has a mismatched SHA-256")

    profile_layers = profile.get("layers", {})
    if not isinstance(profile_layers, dict) or set(profile_layers) - set(GROUP_ORDER):
        raise ValueError("profile layers must use only the declared composition groups")
    additions = additions or {}
    if set(additions) - set(GROUP_ORDER):
        raise ValueError("unknown prompt layer group")

    prompt_sections: list[str] = []
    layer_records: list[dict[str, str]] = []
    seen_layer_ids: set[str] = set()
    for group in GROUP_ORDER:
        configured = profile_layers.get(group, [])
        added = additions.get(group, [])
        if not isinstance(configured, list) or any(not isinstance(path, str) for path in configured):
            raise ValueError(f"profile layer group {group!r} must be a list of paths")
        if any(not isinstance(path, str) for path in added):
            raise ValueError(f"added layer group {group!r} must be a list of paths")
        for layer_path in [*configured, *added]:
            layer_file, layer_digest = _resolve_source(root, layer_path, f"{group} prompt layer")
            layer = _load_yaml(layer_file, f"{group} prompt layer")
            if set(layer) - {"id", "version", "prompt"}:
                raise ValueError(f"prompt layer contains unsupported fields: {layer_path}")
            layer_id = layer.get("id")
            version = layer.get("version")
            prompt_text = layer.get("prompt")
            if not isinstance(layer_id, str) or not ID_RE.fullmatch(layer_id):
                raise ValueError(f"prompt layer id is invalid: {layer_path}")
            if layer_id in seen_layer_ids:
                raise ValueError(f"duplicate prompt layer id: {layer_id}")
            if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
                raise ValueError(f"prompt layer {layer_id!r} version must use MAJOR.MINOR.PATCH")
            if not isinstance(prompt_text, str) or not prompt_text.strip():
                raise ValueError(f"prompt layer {layer_id!r} must contain non-empty prompt text")
            seen_layer_ids.add(layer_id)
            prompt_sections.append(prompt_text.strip())
            layer_records.append({
                "group": group,
                "id": layer_id,
                "version": version,
                "path": Path(layer_path).as_posix(),
                "sha256": layer_digest,
            })

    if not layer_records:
        raise ValueError("at least one prompt layer is required")
    template = "\n\n".join(prompt_sections)
    used_names = list(dict.fromkeys(match.group(1) for match in PLACEHOLDER_RE.finditer(template)))
    unknown = [name for name in used_names if name not in variables]
    unused = sorted(set(variables) - set(used_names))
    if unknown:
        raise ValueError("missing prompt values: " + ", ".join(unknown))
    if unused:
        raise ValueError("unused prompt values: " + ", ".join(unused))
    resolved = PLACEHOLDER_RE.sub(lambda match: variables[match.group(1)], template)
    if "{{" in resolved or "}}" in resolved:
        raise ValueError("malformed or unresolved double-brace placeholder remains")
    if not resolved.strip():
        raise ValueError("resolved prompt must be non-empty")

    return {
        "schema_version": "0.1.0",
        "id": prompt_id,
        "work_id": work_id,
        "work_kind": work_kind,
        "status": "resolved",
        "profile_id": profile_id,
        "profile_version": profile_version,
        "profile_path": Path(profile_path).as_posix(),
        "profile_sha256": profile_digest,
        "values_path": Path(values_path).as_posix(),
        "values_sha256": values_digest,
        "layers": layer_records,
        "substitutions": {name: variables[name] for name in used_names},
        "exact_prompt": resolved,
        "prompt_sha256": "sha256:" + hashlib.sha256(resolved.encode("utf-8")).hexdigest(),
        "reference_assets": references,
    }


def write_sidecar(root: Path, output_path: str, record: dict[str, Any]) -> Path:
    """Write once to a project-relative path; existing files are never replaced."""
    if yaml is None:
        raise RuntimeError("PyYAML is required; install tools/requirements.txt")
    root = root.resolve()
    relative = Path(output_path)
    if not output_path or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("output path must stay inside the project root")
    output = (root / relative).resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise ValueError("output path resolves outside the project root") from exc
    if output.exists():
        raise FileExistsError(f"prompt sidecar already exists: {output_path}")
    output.parent.mkdir(parents=True, exist_ok=True)
    content = yaml.safe_dump(record, allow_unicode=True, sort_keys=False, width=120, explicit_start=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--id", required=True, dest="prompt_id")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--work-kind", default="infographic")
    parser.add_argument("--profile", required=True, dest="profile_path")
    parser.add_argument("--values", required=True, dest="values_path")
    parser.add_argument("--shared-layer", action="append", default=[])
    parser.add_argument("--domain-layer", action="append", default=[])
    parser.add_argument("--medium-layer", action="append", default=[])
    parser.add_argument("--project-layer", action="append", default=[])
    parser.add_argument("--entity-layer", action="append", default=[])
    parser.add_argument("--request-layer", action="append", default=[])
    parser.add_argument("--output", required=True)
    parser.add_argument("--stdout", action="store_true", help="also print the exact prompt after writing the private sidecar")
    args = parser.parse_args()
    additions = {
        "shared": args.shared_layer,
        "domain": args.domain_layer,
        "medium": args.medium_layer,
        "project": args.project_layer,
        "entity": args.entity_layer,
        "request": args.request_layer,
    }
    try:
        root = args.root.resolve()
        record = resolve_prompt(
            root,
            prompt_id=args.prompt_id,
            work_id=args.work_id,
            work_kind=args.work_kind,
            profile_path=args.profile_path,
            values_path=args.values_path,
            additions=additions,
        )
        output = write_sidecar(root, args.output, record)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Created private prompt resolution: {output}")
    print(record["prompt_sha256"])
    if args.stdout:
        print("\n" + record["exact_prompt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
