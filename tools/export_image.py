"""Create a watermarked, metadata-scanned derivative from an accepted image master."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
    import PIL
    from PIL import Image, ImageOps
except ImportError as exc:  # pragma: no cover - installation guidance
    yaml = None
    Image = None
    ImageOps = None
    PIL = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from image_metadata import scan_image_metadata
from validate import ID_PATTERN, SEMVER, validate


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return "sha256:" + hasher.hexdigest()


def _project_file(root: Path, relative: Any, label: str) -> tuple[Path, str]:
    if not isinstance(relative, str) or not relative:
        raise ValueError(f"{label} must be a project-relative path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must stay inside the project root")
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} resolves outside the project root") from exc
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} does not exist: {relative}")
    return resolved, _digest(resolved)


def _load_mapping(path: Path, label: str) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError(f"Install tools/requirements.txt first: {_IMPORT_ERROR}")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be a mapping")
    return value


def _find_record(root: Path, pattern: str, record_id: str, label: str) -> tuple[Path, dict[str, Any]]:
    matches: list[tuple[Path, dict[str, Any]]] = []
    for path in root.glob(pattern):
        if not path.is_file():
            continue
        record = _load_mapping(path, label)
        if record.get("id") == record_id:
            matches.append((path, record))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {label} with ID {record_id!r}")
    return matches[0]


def _watermark(image: Any, logo_path: Path, settings: dict[str, Any]) -> Any:
    ratio_x = settings["max_width_ratio"]
    ratio_y = settings["max_height_ratio"]
    opacity = settings["opacity"]
    margin = settings["margin_px"]
    position = settings["position"]
    if not 0 < ratio_x <= 0.5 or not 0 < ratio_y <= 0.5:
        raise ValueError("watermark size ratios must be greater than 0 and at most 0.5")
    if not 0 < opacity <= 1 or not isinstance(margin, int) or margin < 0:
        raise ValueError("watermark opacity or margin is invalid")
    if position not in {"bottom-right", "bottom-left", "top-right", "top-left"}:
        raise ValueError("watermark position must be a supported corner")

    with Image.open(logo_path) as opened_logo:
        logo = ImageOps.exif_transpose(opened_logo).convert("RGBA")
    if logo.getchannel("A").getbbox() is None:
        raise ValueError("watermark logo is fully transparent")
    max_size = (max(1, int(image.width * ratio_x)), max(1, int(image.height * ratio_y)))
    logo.thumbnail(max_size, Image.Resampling.LANCZOS)
    alpha = logo.getchannel("A").point(lambda value: round(value * opacity))
    logo.putalpha(alpha)
    if logo.width + 2 * margin > image.width or logo.height + 2 * margin > image.height:
        raise ValueError("watermark and margins do not fit the output dimensions")
    left = margin if position.endswith("left") else image.width - logo.width - margin
    top = margin if position.startswith("top") else image.height - logo.height - margin
    image.alpha_composite(logo, (left, top))
    return image


def export_image(root: Path, *, generation_id: str, derivative_id: str, profile_path: str) -> Path:
    """Write a fresh derivative and provenance; never overwrite or publish it."""
    if yaml is None or Image is None or ImageOps is None or PIL is None:
        raise RuntimeError(f"Install tools/requirements.txt before exporting images: {_IMPORT_ERROR}")
    root = root.resolve()
    issues = validate(root)
    if issues:
        raise ValueError("project validation failed before export: " + "; ".join(issues))
    generation_path, generation = _find_record(root, "assets/generations/*/provenance.yaml", generation_id, "generation record")
    if generation.get("disposition") != "accepted":
        raise ValueError("only an accepted immutable master may be exported")
    if not ID_PATTERN.fullmatch(derivative_id):
        raise ValueError("derivative_id must be a stable lowercase ID")
    profile_file, profile_digest = _project_file(root, profile_path, "export profile")
    profile = _load_mapping(profile_file, "export profile")
    if set(profile) - {"schema_version", "id", "version", "destination", "output_format", "resize", "quality", "watermark"}:
        raise ValueError("export profile contains unsupported fields")
    if profile.get("schema_version") != "0.1.0" or not isinstance(profile.get("id"), str) or not ID_PATTERN.fullmatch(profile["id"]) or not isinstance(profile.get("version"), str) or not SEMVER.fullmatch(profile["version"]) or not isinstance(profile.get("destination"), str) or not profile["destination"].strip():
        raise ValueError("export profile requires schema_version 0.1.0, ID, version, and destination")
    if profile.get("output_format") not in {"PNG", "JPEG"}:
        raise ValueError("export profile output_format must be PNG or JPEG")
    resize = profile.get("resize")
    watermark = profile.get("watermark")
    if not isinstance(resize, dict) or not isinstance(watermark, dict) or watermark.get("enabled") is not True:
        raise ValueError("export profile must define resize settings and an enabled watermark")
    if profile.get("output_format") == "JPEG":
        quality = profile.get("quality")
        if not isinstance(quality, int) or isinstance(quality, bool) or not 1 <= quality <= 95:
            raise ValueError("JPEG profile quality must be an integer from 1 to 95")
    elif "quality" in profile:
        raise ValueError("PNG profile must not define a lossy quality setting")
    if resize.get("enabled") is True:
        if set(resize) - {"enabled", "max_width", "max_height"} or any(not isinstance(resize.get(key), int) or isinstance(resize[key], bool) or resize[key] < 1 for key in ("max_width", "max_height")):
            raise ValueError("enabled resize settings need positive max_width and max_height")
    elif resize.get("enabled") is not False or set(resize) - {"enabled"}:
        raise ValueError("resize must be disabled without extra fields, or have positive bounds")
    if set(watermark) - {"enabled", "logo_path", "max_width_ratio", "max_height_ratio", "opacity", "margin_px", "position"}:
        raise ValueError("watermark profile contains unsupported fields")
    for key in ("max_width_ratio", "max_height_ratio", "opacity"):
        value = watermark.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"watermark {key} must be numeric")
    if not isinstance(watermark.get("margin_px"), int) or isinstance(watermark.get("margin_px"), bool) or watermark["margin_px"] < 0:
        raise ValueError("watermark margin_px must be a non-negative integer")

    logo_path, logo_digest = _project_file(root, watermark.get("logo_path"), "watermark logo")
    source_path, source_digest = _project_file(root, generation.get("source_path"), "accepted image master")
    if source_digest != generation.get("source_sha256"):
        raise ValueError("accepted source hash differs from its generation record")
    if not source_path.is_relative_to(root / "assets" / "masters"):
        raise ValueError("source is outside the accepted master directory")
    production_path, production = _find_record(root, "projects/**/productions/infographic/production.yaml", generation["work_id"], "infographic production")
    production_dir = production_path.parent
    extension = ".png" if profile["output_format"] == "PNG" else ".jpg"
    export_dir = production_dir / "exports"
    output_path = export_dir / f"{derivative_id}{extension}"
    sidecar_path = export_dir / f"{derivative_id}.yaml"
    for target in (output_path, sidecar_path):
        try:
            target.resolve().relative_to(root)
        except ValueError as exc:
            raise ValueError("export destination resolves outside the project root") from exc
        if target.exists():
            raise FileExistsError(f"export target exists; refusing overwrite: {target.relative_to(root)}")

    with Image.open(source_path) as opened_source:
        if getattr(opened_source, "n_frames", 1) != 1:
            raise ValueError("animated or multi-frame source images are not supported")
        source_image = ImageOps.exif_transpose(opened_source).convert("RGBA")
    source_size = source_image.size
    if resize["enabled"]:
        source_image.thumbnail((resize["max_width"], resize["max_height"]), Image.Resampling.LANCZOS)
    image = _watermark(source_image, logo_path, watermark)
    actual_size = image.size
    export_dir.mkdir(parents=True, exist_ok=True)
    if profile["output_format"] == "JPEG":
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.getchannel("A"))
        background.save(output_path, format="JPEG", quality=profile["quality"], optimize=False, progressive=False, subsampling=0)
    else:
        image.save(output_path, format="PNG", optimize=False, compress_level=9)

    output_format, findings = scan_image_metadata(output_path)
    record: dict[str, Any] = {
        "schema_version": "0.1.0",
        "id": derivative_id,
        "asset_id": generation["asset_id"],
        "generation_id": generation_id,
        "work_id": generation["work_id"],
        "work_kind": generation["work_kind"],
        "source_path": generation["source_path"],
        "source_sha256": generation["source_sha256"],
        "profile_id": profile["id"],
        "profile_version": profile["version"],
        "profile_path": Path(profile_path).as_posix(),
        "profile_sha256": profile_digest,
        "logo_path": watermark["logo_path"],
        "logo_sha256": logo_digest,
        "output_path": output_path.relative_to(root).as_posix(),
        "output_sha256": _digest(output_path),
        "output_format": output_format or profile["output_format"],
        "width": actual_size[0],
        "height": actual_size[1],
        "resized": actual_size != source_size,
        "watermarked": True,
        "metadata_scan": "pass" if output_format == profile["output_format"] and not findings else "fail",
        "metadata_findings": findings,
        "toolchain": {"python": sys.version.split()[0], "pillow": PIL.__version__},
        "status": "ready_for_human_review" if output_format == profile["output_format"] and not findings else "blocked",
    }
    with sidecar_path.open("x", encoding="utf-8", newline="\n") as stream:
        yaml.safe_dump(record, stream, allow_unicode=True, sort_keys=False, explicit_start=True)
    issues = validate(root)
    if issues:
        raise ValueError("derivative preserved but project validation found issues: " + "; ".join(issues))
    return sidecar_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--generation-id", required=True)
    parser.add_argument("--derivative-id", required=True)
    parser.add_argument("--profile", required=True, dest="profile_path")
    args = parser.parse_args()
    try:
        path = export_image(args.root, generation_id=args.generation_id, derivative_id=args.derivative_id, profile_path=args.profile_path)
    except (OSError, UnicodeError, ValueError, RuntimeError, KeyError) as exc:
        print(f"EXPORT-ERROR {exc}", file=sys.stderr)
        return 2
    print(f"IMAGE-DERIVATIVE {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
