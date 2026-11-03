"""Print a deterministic overview of mini-project records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - installation guidance
    yaml = None


def list_projects(root: Path) -> list[dict[str, Any]]:
    if yaml is None:
        raise RuntimeError("PyYAML is required; install tools/requirements.txt")
    records: list[dict[str, Any]] = []
    for path in sorted(root.glob("projects/**/project.yaml")):
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"project record must be a mapping: {path}")
        records.append({
            "id": value.get("id", ""),
            "title": value.get("title", ""),
            "domain": value.get("domain", ""),
            "purpose": value.get("purpose", ""),
            "audience": value.get("audience", ""),
            "status": value.get("status", ""),
            "path": path.relative_to(root).as_posix(),
        })
    return sorted(records, key=lambda item: (str(item["domain"]).casefold(), str(item["title"]).casefold(), str(item["id"])))


def markdown(records: list[dict[str, Any]]) -> str:
    lines = ["# Mini-project catalog", "", "| Domain | Project | Purpose | Audience | Status |", "|---|---|---|---|---|"]
    for item in records:
        title = str(item["title"]).replace("|", "\\|")
        purpose = str(item["purpose"]).replace("|", "\\|").replace("\n", " ")
        audience = str(item["audience"]).replace("|", "\\|").replace("\n", " ")
        path = str(item["path"])
        lines.append(f"| {item['domain']} | [{title}]({path}) | {purpose} | {audience} | {item['status']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    try:
        records = list_projects(args.root.resolve())
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if args.format == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        print(markdown(records), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
