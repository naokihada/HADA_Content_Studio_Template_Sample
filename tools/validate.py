"""Validate Content Studio records, references, artifact boundaries, and versions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in installations without the dependency
    yaml = None

try:
    from image_metadata import scan_image_metadata
except ImportError:  # pragma: no cover - installation guidance
    scan_image_metadata = None


CORE_SCHEMA_PATH = Path("schemas/common/records.schema.json")
CONTENT_SCHEMA_PATH = Path("schemas/content/records.schema.json")
MANIFEST_PATH = Path("config/template-manifest.json")
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,95}$")
PROMPT_GROUP_ORDER = ("shared", "domain", "medium", "project", "entity", "request")
PROMPT_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z][A-Za-z0-9_.-]*)\s*\}\}")


def _semver(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str) or not SEMVER.fullmatch(value):
        return None
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any] | None:
    if not ref.startswith("#/"):
        return None
    current: Any = schema
    for segment in ref[2:].split("/"):
        segment = segment.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current if isinstance(current, dict) else None


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _schema_errors(value: Any, spec: dict[str, Any], root_schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if "$ref" in spec:
        target = _resolve_ref(root_schema, spec["$ref"])
        if target is None:
            return [f"{path}: unresolved schema reference {spec['$ref']}"]
        return _schema_errors(value, target, root_schema, path)

    expected = spec.get("type")
    if isinstance(expected, list):
        matches = any(_type_matches(value, item) for item in expected)
    elif isinstance(expected, str):
        matches = _type_matches(value, expected)
    else:
        matches = True
    if not matches:
        return [f"{path}: expected {expected}"]

    if "const" in spec and value != spec["const"]:
        errors.append(f"{path}: must equal {spec['const']!r}")
    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"{path}: must be one of {spec['enum']!r}")
    if isinstance(value, str):
        if len(value) < spec.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        if len(value) > spec.get("maxLength", float("inf")):
            errors.append(f"{path}: string is too long")
        pattern = spec.get("pattern")
        if pattern and re.search(pattern, value) is None:
            errors.append(f"{path}: does not match required pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in spec and value < spec["minimum"]:
            errors.append(f"{path}: is below minimum")
        if "maximum" in spec and value > spec["maximum"]:
            errors.append(f"{path}: is above maximum")
        if "exclusiveMinimum" in spec and value <= spec["exclusiveMinimum"]:
            errors.append(f"{path}: must be greater than {spec['exclusiveMinimum']}")
    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0):
            errors.append(f"{path}: has too few items")
        if spec.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: items must be unique")
        item_spec = spec.get("items")
        if isinstance(item_spec, dict):
            for index, item in enumerate(value):
                errors.extend(_schema_errors(item, item_spec, root_schema, f"{path}[{index}]"))
    if isinstance(value, dict):
        for key in spec.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = spec.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors.extend(_schema_errors(item, properties[key], root_schema, f"{path}.{key}"))
            elif spec.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(spec.get("additionalProperties"), dict):
                errors.extend(_schema_errors(item, spec["additionalProperties"], root_schema, f"{path}.{key}"))
    return errors


def _load_record(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required; install tools/requirements.txt")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("record root must be a mapping")
    return value


def _prompt_resolution_errors(root: Path, relative_record_path: str, record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for path_field, hash_field in (("profile_path", "profile_sha256"), ("values_path", "values_sha256")):
        issue = _checked_file(root, record.get(path_field), record.get(hash_field))
        if issue:
            errors.append(f"{relative_record_path}: prompt {path_field} {issue}")
    if errors or yaml is None:
        return errors

    profile_path = root / record["profile_path"]
    values_path = root / record["values_path"]
    try:
        profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
        values_doc = yaml.safe_load(values_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return [f"{relative_record_path}: cannot reload prompt inputs: {exc}"]
    if not isinstance(profile, dict) or not isinstance(values_doc, dict):
        return [f"{relative_record_path}: prompt profile and values must be mappings"]
    if profile.get("schema_version") != "0.1.0":
        errors.append(f"{relative_record_path}: prompt profile schema_version must be 0.1.0")
    if set(profile) - {"schema_version", "id", "version", "layers"}:
        errors.append(f"{relative_record_path}: prompt profile contains unsupported fields")
    if set(values_doc) - {"variables", "reference_assets"}:
        errors.append(f"{relative_record_path}: prompt values contain unsupported fields")
    if profile.get("id") != record.get("profile_id") or profile.get("version") != record.get("profile_version"):
        errors.append(f"{relative_record_path}: prompt profile ID/version mismatch")

    profile_layers = profile.get("layers", {})
    if not isinstance(profile_layers, dict) or set(profile_layers) - set(PROMPT_GROUP_ORDER):
        errors.append(f"{relative_record_path}: profile has invalid prompt layer groups")
        profile_layers = {}
    layer_records = record.get("layers", [])
    if not isinstance(layer_records, list):
        return errors + [f"{relative_record_path}: prompt layers must be a list"]
    if any(not isinstance(layer, dict) for layer in layer_records):
        return errors + [f"{relative_record_path}: prompt layer entries must be mappings"]

    group_ranks = [PROMPT_GROUP_ORDER.index(layer["group"]) for layer in layer_records if layer.get("group") in PROMPT_GROUP_ORDER]
    if len(group_ranks) != len(layer_records) or group_ranks != sorted(group_ranks):
        errors.append(f"{relative_record_path}: prompt layers are not in the declared group order")
    for group in PROMPT_GROUP_ORDER:
        declared = profile_layers.get(group, [])
        if not isinstance(declared, list) or any(not isinstance(item, str) for item in declared):
            errors.append(f"{relative_record_path}: profile group {group!r} must be a list of paths")
            continue
        recorded = [layer.get("path") for layer in layer_records if layer.get("group") == group]
        if recorded[:len(declared)] != [Path(item).as_posix() for item in declared]:
            errors.append(f"{relative_record_path}: configured {group} layers are missing or reordered")

    sections: list[str] = []
    seen_ids: set[str] = set()
    for layer_ref in layer_records:
        layer_id = layer_ref.get("id")
        layer_file = layer_ref.get("path")
        issue = _checked_file(root, layer_file, layer_ref.get("sha256"))
        if issue:
            errors.append(f"{relative_record_path}: prompt layer {issue}")
            continue
        try:
            layer = yaml.safe_load((root / layer_file).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(f"{relative_record_path}: cannot reload prompt layer {layer_id!r}: {exc}")
            continue
        if not isinstance(layer, dict):
            errors.append(f"{relative_record_path}: prompt layer {layer_id!r} must be a mapping")
            continue
        if set(layer) - {"id", "version", "prompt"}:
            errors.append(f"{relative_record_path}: prompt layer {layer_id!r} contains unsupported fields")
        if isinstance(layer_id, str) and layer_id in seen_ids:
            errors.append(f"{relative_record_path}: duplicate prompt layer ID {layer_id!r}")
        if isinstance(layer_id, str):
            seen_ids.add(layer_id)
        if layer.get("id") != layer_id or layer.get("version") != layer_ref.get("version"):
            errors.append(f"{relative_record_path}: prompt layer ID/version mismatch for {layer_id!r}")
        prompt_text = layer.get("prompt")
        if not isinstance(prompt_text, str) or not prompt_text.strip():
            errors.append(f"{relative_record_path}: prompt layer {layer_id!r} has no prompt text")
            continue
        sections.append(prompt_text.strip())

    variables = values_doc.get("variables")
    substitutions = record.get("substitutions")
    if not isinstance(variables, dict) or not isinstance(substitutions, dict):
        return errors + [f"{relative_record_path}: prompt values and substitutions must be mappings"]
    invalid_variables = any(not isinstance(key, str) or not isinstance(value, str) for key, value in variables.items())
    invalid_substitutions = any(not isinstance(key, str) or not isinstance(value, str) for key, value in substitutions.items())
    if invalid_variables:
        errors.append(f"{relative_record_path}: prompt variables must be strings")
    if invalid_substitutions:
        errors.append(f"{relative_record_path}: resolved substitutions must be strings")
    if invalid_variables or invalid_substitutions:
        return errors
    if len(sections) != len(layer_records):
        return errors

    template = "\n\n".join(sections)
    used_names = list(dict.fromkeys(match.group(1) for match in PROMPT_PLACEHOLDER.finditer(template)))
    if set(substitutions) != set(used_names):
        errors.append(f"{relative_record_path}: substitutions do not match prompt placeholders")
    for name in used_names:
        if name not in variables or substitutions.get(name) != variables.get(name):
            errors.append(f"{relative_record_path}: substitution {name!r} differs from the recorded values")
    try:
        exact_prompt = PROMPT_PLACEHOLDER.sub(lambda match: substitutions[match.group(1)], template)
    except KeyError:
        exact_prompt = ""
    if "{{" in exact_prompt or "}}" in exact_prompt:
        errors.append(f"{relative_record_path}: unresolved or malformed placeholder remains")
    stored_prompt = record.get("exact_prompt")
    if not isinstance(stored_prompt, str):
        errors.append(f"{relative_record_path}: exact prompt must be a string")
        stored_prompt = ""
    if exact_prompt != stored_prompt:
        errors.append(f"{relative_record_path}: exact prompt does not match its recorded inputs")
    prompt_digest = hashlib.sha256(stored_prompt.encode("utf-8")).hexdigest()
    if record.get("prompt_sha256") != f"sha256:{prompt_digest}":
        errors.append(f"{relative_record_path}: exact prompt hash mismatch")
    return errors


def _generation_record_errors(root: Path, record_path: Path, record: dict[str, Any]) -> list[str]:
    relative_record_path = record_path.relative_to(root).as_posix()
    errors: list[str] = []
    generation_id = record.get("id")
    expected_record = Path("assets/generations") / str(generation_id) / "provenance.yaml"
    if Path(relative_record_path) != expected_record:
        errors.append(f"{relative_record_path}: generation record path must match its ID")
    for field in ("generated_at", "reviewed_at"):
        value = record.get(field)
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
            if parsed is None or parsed.tzinfo is None:
                errors.append(f"{relative_record_path}: {field} must be an ISO-8601 timestamp with timezone")
        except ValueError:
            errors.append(f"{relative_record_path}: {field} must be an ISO-8601 timestamp with timezone")
    disposition = record.get("disposition")
    root_folder = "masters" if disposition == "accepted" else "discard_candidates"
    source_path = record.get("source_path")
    expected_source_root = Path("assets") / root_folder / str(record.get("asset_id")) / str(record.get("asset_version"))
    source = Path(source_path) if isinstance(source_path, str) else Path()
    if source.parent != expected_source_root or source.name not in {"source.png", "source.jpg", "source.jpeg"}:
        errors.append(f"{relative_record_path}: source path does not match its disposition and asset version")
    issue = _checked_file(root, source_path, record.get("source_sha256"))
    if issue:
        errors.append(f"{relative_record_path}: {issue}")
    elif scan_image_metadata is not None:
        image_format, _findings = scan_image_metadata(root / source_path)
        expected_format = "PNG" if source.suffix.lower() == ".png" else "JPEG"
        if image_format != expected_format:
            errors.append(f"{relative_record_path}: source format does not match its extension")
    else:
        errors.append(f"{relative_record_path}: image metadata scanner is unavailable")
    return errors


def _derivative_record_errors(root: Path, record_path: Path, record: dict[str, Any], records: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    relative_record_path = record_path.relative_to(root).as_posix()
    errors: list[str] = []
    derivative_id = record.get("id")
    if record_path.stem != derivative_id:
        errors.append(f"{relative_record_path}: derivative sidecar filename must match its ID")
    generation_id = record.get("generation_id")
    generation = records["image_generation"].get(generation_id) if isinstance(generation_id, str) else None
    if generation is None:
        errors.append(f"{relative_record_path}: references an unknown generation")
        return errors
    if generation.get("disposition") != "accepted":
        errors.append(f"{relative_record_path}: only accepted masters may be exported")
    for field in ("asset_id", "work_id", "work_kind"):
        if record.get(field) != generation.get(field):
            errors.append(f"{relative_record_path}: {field} differs from the source generation")
    if record.get("source_path") != generation.get("source_path") or record.get("source_sha256") != generation.get("source_sha256"):
        errors.append(f"{relative_record_path}: source path/hash differs from the accepted master")

    path_issues: dict[str, str | None] = {}
    for path_field, hash_field, label in (
        ("profile_path", "profile_sha256", "export profile"),
        ("logo_path", "logo_sha256", "watermark logo"),
        ("output_path", "output_sha256", "derivative"),
    ):
        issue = _checked_file(root, record.get(path_field), record.get(hash_field))
        path_issues[path_field] = issue
        if issue:
            errors.append(f"{relative_record_path}: {label} {issue}")
    profile_path = record.get("profile_path")
    profile: dict[str, Any] = {}
    if isinstance(profile_path, str) and not path_issues.get("profile_path"):
        try:
            profile_value = _load_record(root / profile_path)
            profile = profile_value
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            errors.append(f"{relative_record_path}: cannot reload export profile: {exc}")
    if profile:
        if profile.get("id") != record.get("profile_id") or profile.get("version") != record.get("profile_version"):
            errors.append(f"{relative_record_path}: export profile ID/version mismatch")
        if profile.get("output_format") != record.get("output_format"):
            errors.append(f"{relative_record_path}: output format differs from the export profile")
        if not isinstance(profile.get("watermark"), dict) or profile["watermark"].get("enabled") is not True:
            errors.append(f"{relative_record_path}: export profile must enable a watermark")
        elif profile["watermark"].get("logo_path") != record.get("logo_path"):
            errors.append(f"{relative_record_path}: watermark logo differs from the export profile")

    output_path = record.get("output_path")
    if isinstance(output_path, str):
        output_relative = Path(output_path)
        if {part.casefold() for part in output_relative.parts} & {"masters", "discard_candidates"}:
            errors.append(f"{relative_record_path}: a derivative cannot be stored as a source master")
        if output_relative.parent != Path(relative_record_path).parent or output_relative.stem != str(derivative_id):
            errors.append(f"{relative_record_path}: derivative output must share its sidecar folder and ID")
        work_id = record.get("work_id")
        if record.get("work_kind") != "infographic":
            errors.append(f"{relative_record_path}: this exporter currently supports infographic productions only")
        production_paths = [path for path in root.glob("projects/**/productions/infographic/production.yaml") if path.is_file()]
        production_path = next((path for path in production_paths if _record_id(path) == work_id), None)
        if production_path is None:
            errors.append(f"{relative_record_path}: linked infographic production is missing")
        else:
            export_dir = production_path.parent / "exports"
            try:
                (root / output_relative).resolve().relative_to(export_dir.resolve())
                record_path.resolve().relative_to(export_dir.resolve())
            except ValueError:
                errors.append(f"{relative_record_path}: derivative output and sidecar must stay in the linked production exports folder")
    expected_suffix = ".png" if record.get("output_format") == "PNG" else ".jpg"
    if isinstance(output_path, str) and Path(output_path).suffix.lower() != expected_suffix:
        errors.append(f"{relative_record_path}: output extension does not match its format")

    if scan_image_metadata is None:
        errors.append(f"{relative_record_path}: image metadata scanner is unavailable")
    elif isinstance(output_path, str) and not path_issues.get("output_path"):
        detected_format, findings = scan_image_metadata(root / output_path)
        if detected_format != record.get("output_format"):
            errors.append(f"{relative_record_path}: derivative format does not match its record")
        if findings != record.get("metadata_findings"):
            errors.append(f"{relative_record_path}: metadata scan findings do not match the derivative")
        if (not findings) != (record.get("metadata_scan") == "pass"):
            errors.append(f"{relative_record_path}: metadata scan status is inconsistent")
        if record.get("status") == "ready_for_human_review" and findings:
            errors.append(f"{relative_record_path}: derivative with metadata findings cannot be reviewed for publication")
        if record.get("status") == "blocked" and not findings:
            errors.append(f"{relative_record_path}: blocked derivative must preserve scan findings")
        try:
            from PIL import Image, ImageOps

            with Image.open(root / output_path) as image:
                if image.format != record.get("output_format") or image.size != (record.get("width"), record.get("height")):
                    errors.append(f"{relative_record_path}: output dimensions or format do not match the sidecar")
                output_size = image.size
            source_path = generation.get("source_path")
            source_issue = _checked_file(root, source_path, generation.get("source_sha256"))
            if source_issue:
                errors.append(f"{relative_record_path}: source master {source_issue}")
                return errors
            with Image.open(root / source_path) as source_image:
                source_size = ImageOps.exif_transpose(source_image).size
                expected_size = source_size
                resize = profile.get("resize", {}) if isinstance(profile, dict) else {}
                if isinstance(resize, dict) and resize.get("enabled") is True:
                    max_width = resize.get("max_width")
                    max_height = resize.get("max_height")
                    if not isinstance(max_width, int) or not isinstance(max_height, int) or max_width < 1 or max_height < 1:
                        errors.append(f"{relative_record_path}: enabled resize profile needs positive dimensions")
                    else:
                        expected_image = ImageOps.exif_transpose(source_image).copy()
                        expected_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                        expected_size = expected_image.size
                if output_size != expected_size or record.get("resized") != (output_size != source_size):
                    errors.append(f"{relative_record_path}: output resizing does not match its profile")
        except (ImportError, OSError, ValueError) as exc:
            errors.append(f"{relative_record_path}: cannot inspect derivative image: {exc}")
    return errors


def _record_id(path: Path) -> Any:
    try:
        return _load_record(path).get("id")
    except (OSError, UnicodeError, ValueError, RuntimeError):
        return None


def _has_id(records: dict[str, dict[str, dict[str, Any]]], record_type: str, value: Any) -> bool:
    return isinstance(value, str) and value in records.get(record_type, {})


def _record_specs(root: Path) -> list[tuple[Path, Path, str]]:
    patterns = [
        ("assets/characters/**/character.yaml", CORE_SCHEMA_PATH, "character"),
        ("assets/characters/**/variants/*.yaml", CORE_SCHEMA_PATH, "appearance_variant"),
        ("assets/items/**/item.yaml", CORE_SCHEMA_PATH, "item"),
        ("assets/items/**/variants/*.yaml", CORE_SCHEMA_PATH, "item_variant"),
        ("assets/outfits/**/outfit.yaml", CORE_SCHEMA_PATH, "outfit"),
        ("assets/relationships/character_items/*.yaml", CORE_SCHEMA_PATH, "character_item_link"),
        ("projects/**/productions/infographic/prompt_resolutions/*.yaml", CORE_SCHEMA_PATH, "prompt_resolution"),
        ("assets/generations/*/provenance.yaml", CORE_SCHEMA_PATH, "image_generation"),
        ("projects/**/productions/infographic/exports/*.yaml", CORE_SCHEMA_PATH, "image_derivative"),
        ("knowledge/**/knowledge.yaml", CONTENT_SCHEMA_PATH, "knowledge_module"),
        ("projects/**/project.yaml", CONTENT_SCHEMA_PATH, "mini_project"),
        ("projects/**/productions/infographic/production.yaml", CONTENT_SCHEMA_PATH, "infographic_production"),
        ("publications/**/*.yaml", CONTENT_SCHEMA_PATH, "publication_record"),
    ]
    found: dict[Path, tuple[Path, str]] = {}
    for pattern, schema_path, name in patterns:
        for path in root.glob(pattern):
            if path.is_file():
                found[path] = (schema_path, name)
    return [(path, schema, name) for path, (schema, name) in sorted(found.items())]


def _checked_file(root: Path, relative: Any, expected_hash: Any = None) -> str | None:
    if not isinstance(relative, str) or not relative:
        return "path must be a non-empty relative string"
    path_part = Path(relative)
    if path_part.is_absolute() or ".." in path_part.parts:
        return "path must stay inside the project root"
    candidate = (root / path_part).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return "resolved path escapes the project root"
    if not candidate.is_file():
        return f"referenced file does not exist: {relative}"
    if expected_hash is not None:
        hasher = hashlib.sha256()
        with candidate.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
        digest = hasher.hexdigest()
        if expected_hash != f"sha256:{digest}":
            return f"asset hash mismatch: {relative}"
    return None


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    try:
        manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read manifest: {exc}"]

    template = manifest.get("template", {})
    template_id = template.get("id")
    version = template.get("version")
    if template_id != "hada-content-studio-template":
        errors.append("manifest template.id must be hada-content-studio-template")
    if _semver(version) is None:
        errors.append("manifest template.version must use MAJOR.MINOR.PATCH")
    compatibility = manifest.get("base_compatibility", {})
    if compatibility.get("template_id") != "hada-base-template":
        errors.append("base_compatibility.template_id must be hada-base-template")
    minimum = _semver(compatibility.get("minimum_version"))
    tested = _semver(compatibility.get("tested_version"))
    if minimum is None or tested is None:
        errors.append("Base minimum/tested compatibility versions must use MAJOR.MINOR.PATCH")
    elif tested < minimum:
        errors.append("tested Base version cannot be older than minimum Base version")
    role = manifest.get("artifacts", {}).get("role")
    if role not in {"dev", "template", "sample"}:
        errors.append("artifacts.role must be dev, template, or sample")

    if isinstance(version, str):
        template_base = root / "TEMPLATE_BASE.md"
        changelog = root / "CHANGELOG.md"
        if not template_base.is_file() or f"Version: `{version}`" not in template_base.read_text(encoding="utf-8"):
            errors.append("TEMPLATE_BASE.md version must match manifest")
        if not changelog.is_file():
            errors.append("CHANGELOG.md is missing")
        else:
            first_heading = next((line for line in changelog.read_text(encoding="utf-8").splitlines() if line.startswith("## [")), "")
            expected_heading = re.compile(rf"^## \[{re.escape(version)}\](?: - [0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})?$")
            if not expected_heading.fullmatch(first_heading):
                errors.append("first CHANGELOG heading must match manifest version")

    schemas: dict[Path, dict[str, Any]] = {}
    for schema_path in (CORE_SCHEMA_PATH, CONTENT_SCHEMA_PATH):
        try:
            schemas[schema_path] = json.loads((root / schema_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read schema {schema_path.as_posix()}: {exc}")
    if CONTENT_SCHEMA_PATH in schemas and (root / "config/project.example.yaml").is_file():
        try:
            example = _load_record(root / "config/project.example.yaml")
            example_schema = schemas[CONTENT_SCHEMA_PATH]["$defs"]["mini_project"]
            errors.extend(_schema_errors(example, example_schema, schemas[CONTENT_SCHEMA_PATH], "config/project.example.yaml"))
        except (OSError, UnicodeError, ValueError, RuntimeError, KeyError) as exc:
            errors.append(f"invalid config/project.example.yaml: {exc}")
    records: dict[str, dict[str, dict[str, Any]]] = {
        name: {} for name in ("character", "appearance_variant", "item", "item_variant", "outfit", "character_item_link", "prompt_resolution", "image_generation", "image_derivative", "knowledge_module", "mini_project", "infographic_production", "publication_record")
    }
    for path, schema_path, name in _record_specs(root):
        if schema_path not in schemas:
            continue
        try:
            record = _load_record(path)
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
            continue
        schema = schemas[schema_path]
        definition = schema.get("$defs", {}).get(name)
        if not isinstance(definition, dict):
            errors.append(f"schema definition {name!r} is missing from {schema_path.as_posix()}")
            continue
        record_errors = _schema_errors(record, definition, schema, path.relative_to(root).as_posix())
        errors.extend(record_errors)
        record_id = record.get("id")
        if not isinstance(record_id, str) or not ID_PATTERN.fullmatch(record_id):
            continue
        if record_id in records[name]:
            errors.append(f"duplicate {name} id {record_id!r}")
        records[name][record_id] = record
        for asset_ref in record.get("reference_assets", []):
            if not isinstance(asset_ref, dict):
                continue
            issue = _checked_file(root, asset_ref.get("path"), asset_ref.get("sha256"))
            if issue:
                errors.append(f"{path.relative_to(root).as_posix()}: {issue}")
        if name == "prompt_resolution":
            errors.extend(_prompt_resolution_errors(root, path.relative_to(root).as_posix(), record))
        elif name == "image_generation":
            errors.extend(_generation_record_errors(root, path, record))

    artifacts = manifest.get("artifacts", {})
    if role in {"dev", "template"}:
        if records["character"] or records["appearance_variant"] or records["character_item_link"]:
            errors.append(f"{role} artifact must not contain character instance records")
        if records["image_generation"] or records["image_derivative"]:
            errors.append(f"{role} artifact must not contain project image-generation assets")
        if artifacts.get("character_instances_allowed") is not False:
            errors.append(f"{role} manifest must set character_instances_allowed=false")
    if role == "sample":
        if artifacts.get("character_instances_allowed") is not True:
            errors.append("sample manifest must set character_instances_allowed=true")
        if artifacts.get("sample_character_data") is not True or not records["character"]:
            errors.append("sample must declare and contain fictional character data")
        elif artifacts.get("sample_character_name") is not None and not any(
            record.get("display_name") == artifacts.get("sample_character_name")
            for record in records["character"].values()
        ):
            errors.append("sample does not contain its declared sample_character_name")

    for record_id, record in records["appearance_variant"].items():
        if not _has_id(records, "character", record.get("character_id")):
            errors.append(f"appearance variant {record_id!r} references an unknown character")
    for record_id, record in records["character_item_link"].items():
        if not _has_id(records, "character", record.get("character_id")):
            errors.append(f"character-item link {record_id!r} references an unknown character")
        if not _has_id(records, "item", record.get("item_id")):
            errors.append(f"character-item link {record_id!r} references an unknown item")
        if record.get("character_variant_id") and not _has_id(records, "appearance_variant", record.get("character_variant_id")):
            errors.append(f"character-item link {record_id!r} references an unknown appearance variant")
        elif isinstance(record.get("character_variant_id"), str):
            variant = records["appearance_variant"][record["character_variant_id"]]
            if variant.get("character_id") != record.get("character_id"):
                errors.append(f"character-item link {record_id!r} uses a variant of a different character")
        if record.get("item_variant_id") and not _has_id(records, "item_variant", record.get("item_variant_id")):
            errors.append(f"character-item link {record_id!r} references an unknown item variant")
        elif isinstance(record.get("item_variant_id"), str):
            variant = records["item_variant"][record["item_variant_id"]]
            if variant.get("item_id") != record.get("item_id"):
                errors.append(f"character-item link {record_id!r} uses a variant of a different item")
        if record.get("outfit_id") and not _has_id(records, "outfit", record.get("outfit_id")):
            errors.append(f"character-item link {record_id!r} references an unknown outfit")
    for record_id, record in records["outfit"].items():
        for component in record.get("items", []):
            if not _has_id(records, "item", component.get("item_id")):
                errors.append(f"outfit {record_id!r} references an unknown item")
            if component.get("item_variant_id") and not _has_id(records, "item_variant", component.get("item_variant_id")):
                errors.append(f"outfit {record_id!r} references an unknown item variant")
            elif isinstance(component.get("item_variant_id"), str):
                variant = records["item_variant"][component["item_variant_id"]]
                if variant.get("item_id") != component.get("item_id"):
                    errors.append(f"outfit {record_id!r} uses a variant of a different item")
    for record_id, record in records["item_variant"].items():
        if not _has_id(records, "item", record.get("item_id")):
            errors.append(f"item variant {record_id!r} references an unknown item")
    for record_id, record in records["item"].items():
        for component in record.get("components", []):
            if not _has_id(records, "item", component.get("item_id")):
                errors.append(f"item {record_id!r} references an unknown component item")
    for record_id, record in records["knowledge_module"].items():
        source_ids = {source.get("id") for source in record.get("sources", []) if isinstance(source, dict) and isinstance(source.get("id"), str)}
        for claim in record.get("claims", []):
            for source_id in claim.get("source_refs", []):
                if source_id not in source_ids:
                    errors.append(f"knowledge module {record_id!r} claim references an unknown source")
    for record_id, record in records["mini_project"].items():
        references = (("knowledge_refs", "knowledge_module"), ("character_refs", "character"), ("item_refs", "item"), ("production_refs", "infographic_production"))
        for field, target in references:
            for ref in record.get(field, []):
                if not _has_id(records, target, ref):
                    errors.append(f"project {record_id!r} references unknown {target} {ref!r}")
    for record_id, record in records["infographic_production"].items():
        if not _has_id(records, "mini_project", record.get("project_id")):
            errors.append(f"infographic production {record_id!r} references an unknown project")
        for field, target in (("knowledge_refs", "knowledge_module"), ("character_refs", "character"), ("item_refs", "item")):
            for ref in record.get(field, []):
                if not _has_id(records, target, ref):
                    errors.append(f"infographic production {record_id!r} references unknown {target} {ref!r}")
    for record_id, record in records["prompt_resolution"].items():
        if record.get("work_kind") == "infographic" and not _has_id(records, "infographic_production", record.get("work_id")):
            errors.append(f"prompt resolution {record_id!r} references an unknown infographic production")
    asset_versions: set[tuple[str, str]] = set()
    for generation_id, record in records["image_generation"].items():
        asset_id = record.get("asset_id")
        asset_version = record.get("asset_version")
        if isinstance(asset_id, str) and isinstance(asset_version, str):
            key = (asset_id, asset_version)
            if key in asset_versions:
                errors.append(f"image asset {asset_id!r} version {asset_version!r} has multiple generation records")
            asset_versions.add(key)
        prompt_id = record.get("prompt_resolution_id")
        prompt = records["prompt_resolution"].get(prompt_id) if isinstance(prompt_id, str) else None
        if prompt is None:
            errors.append(f"image generation {generation_id!r} references an unknown prompt resolution")
        elif prompt.get("work_id") != record.get("work_id") or prompt.get("work_kind") != record.get("work_kind"):
            errors.append(f"image generation {generation_id!r} uses a prompt for different work")
        superseded = record.get("supersedes_generation_id")
        if superseded and (not _has_id(records, "image_generation", superseded) or records["image_generation"][superseded].get("asset_id") != record.get("asset_id")):
            errors.append(f"image generation {generation_id!r} supersedes an unknown or different asset")
    derivative_paths = {path.stem: path for path, _schema_path, name in _record_specs(root) if name == "image_derivative"}
    for derivative_id, record in records["image_derivative"].items():
        derivative_path = derivative_paths.get(derivative_id)
        if derivative_path is not None:
            errors.extend(_derivative_record_errors(root, derivative_path, record, records))
    for publication_id, record in records["publication_record"].items():
        derivative_id = record.get("derivative_id")
        derivative = records["image_derivative"].get(derivative_id) if isinstance(derivative_id, str) else None
        if derivative is None:
            errors.append(f"publication {publication_id!r} references an unknown image derivative")
            continue
        if derivative.get("status") != "ready_for_human_review" or derivative.get("metadata_scan") != "pass":
            errors.append(f"publication {publication_id!r} does not reference a metadata-checked derivative")
        if record.get("derivative_path") != derivative.get("output_path"):
            errors.append(f"publication {publication_id!r} derivative path does not match its record")
        if record.get("derivative_sha256") != derivative.get("output_sha256"):
            errors.append(f"publication {publication_id!r} derivative hash does not match its record")
        if record.get("production_id") != derivative.get("work_id") or record.get("asset_id") != derivative.get("asset_id"):
            errors.append(f"publication {publication_id!r} references different production or asset")
        if record.get("profile_version") != derivative.get("profile_version"):
            errors.append(f"publication {publication_id!r} profile version does not match its derivative")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} issue(s)")
        return 1
    print(f"PASS: HADA Content Studio contract at {args.root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
