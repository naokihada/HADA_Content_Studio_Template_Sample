from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate import _schema_errors, validate  # noqa: E402


class ContentStudioValidationTests(unittest.TestCase):
    def test_dev_contract_passes_and_has_no_character_instances(self) -> None:
        self.assertEqual(validate(ROOT), [])

    def test_shared_character_item_links_support_reuse_and_story_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config").mkdir()
            (root / "schemas/common").mkdir(parents=True)
            (root / "schemas/content").mkdir(parents=True)
            shutil.copy(ROOT / "schemas/common/records.schema.json", root / "schemas/common/records.schema.json")
            shutil.copy(ROOT / "schemas/content/records.schema.json", root / "schemas/content/records.schema.json")
            manifest = json.loads((ROOT / "config/template-manifest.json").read_text(encoding="utf-8"))
            manifest["artifacts"].update({"role": "sample", "character_instances_allowed": True, "sample_character_data": True, "sample_character_name": "Example Guardian", "contains_user_data": False})
            (root / "config/template-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "TEMPLATE_BASE.md").write_text("Version: `0.1.0`", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0] - 2026-11-02\n", encoding="utf-8")

            def record(path: str, data: dict) -> None:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

            record("assets/characters/example-elf/character.yaml", {
                "schema_version": "0.1.0", "id": "example-elf", "display_name": "Example Elf",
                "status": "approved", "identity": {"summary": "A fictional sample elf.", "anchors": ["pointed ears", "green eyes"]},
                "extensions": {"story": {"series_id": "sample-series", "canon_status": "sample"}},
            })
            record("assets/characters/example-guardian/character.yaml", {
                "schema_version": "0.1.0", "id": "example-guardian", "display_name": "Example Guardian",
                "status": "approved", "identity": {"summary": "A fictional test character.", "anchors": ["blue cape"]},
            })
            record("assets/items/academy-uniform/item.yaml", {
                "schema_version": "0.1.0", "id": "academy-uniform", "display_name": "Academy Uniform",
                "category": "clothing", "status": "approved",
            })
            record("assets/items/academy-uniform/variants/winter.yaml", {
                "schema_version": "0.1.0", "id": "academy-uniform-winter", "item_id": "academy-uniform",
                "name": "Winter Uniform", "modifications": {"coat": "navy"}, "status": "approved",
            })
            record("assets/outfits/academy-winter/outfit.yaml", {
                "schema_version": "0.1.0", "id": "academy-winter", "display_name": "Winter Academy",
                "items": [{"item_id": "academy-uniform", "item_variant_id": "academy-uniform-winter", "slot": "clothing"}],
                "status": "approved",
            })
            record("assets/relationships/character_items/elf-uniform.yaml", {
                "schema_version": "0.1.0", "id": "elf-wears-uniform", "character_id": "example-elf",
                "item_id": "academy-uniform", "item_variant_id": "academy-uniform-winter",
                "outfit_id": "academy-winter", "relationship": "wears", "status": "approved",
            })
            record("assets/relationships/character_items/guardian-uniform.yaml", {
                "schema_version": "0.1.0", "id": "guardian-wears-uniform", "character_id": "example-guardian",
                "item_id": "academy-uniform", "relationship": "wears", "status": "approved",
            })
            record("assets/characters/example-elf/variants/chibi.yaml", {
                "schema_version": "0.1.0", "id": "example-elf-chibi", "character_id": "example-elf",
                "name": "Chibi", "transforms": {"proportion_id": "chibi", "head_to_body_ratio": 2.5},
                "preserved_identity_anchors": ["pointed ears", "green eyes"], "status": "approved",
            })
            record("projects/fantasy/sample-world/project.yaml", {
                "schema_version": "0.1.0", "id": "sample-world", "title": "Sample World",
                "domain": "fantasy", "purpose": "Schema test.", "audience": "Template reviewer.",
                "scope": {"includes": [], "excludes": []}, "visibility": "private", "status": "draft",
                "character_refs": ["example-elf", "example-guardian"], "item_refs": ["academy-uniform"],
            })
            self.assertEqual(validate(root), [])

            manifest["artifacts"]["sample_character_name"] = "Unlisted Sample Character"
            (root / "config/template-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertTrue(any("declared sample_character_name" in error for error in validate(root)))

            record("assets/items/academy-uniform/variants/winter.yaml", {
                "schema_version": "0.1.0", "id": "academy-uniform-winter", "item_id": "different-item",
                "name": "Winter Uniform", "modifications": {"coat": "navy"}, "status": "approved",
            })
            self.assertTrue(any("variant of a different item" in error for error in validate(root)))

    def test_schema_rejects_unknown_character_fields(self) -> None:
        schema = json.loads((ROOT / "schemas/common/records.schema.json").read_text(encoding="utf-8"))
        definition = schema["$defs"]["character"]
        errors = _schema_errors({
            "schema_version": "0.1.0", "id": "elf-example", "display_name": "Elf",
            "status": "approved", "identity": {"summary": "example", "anchors": ["ears"]},
            "unreviewed_field": True,
        }, definition, schema, "character")
        self.assertTrue(any("unexpected property 'unreviewed_field'" in error for error in errors))

    def test_dev_artifact_rejects_character_instance_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "config", root / "config")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            manifest_path = root / "config/template-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"].update({"role": "dev", "character_instances_allowed": False, "sample_character_data": False})
            manifest["artifacts"].pop("sample_character_name", None)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            for name in ("TEMPLATE_BASE.md", "CHANGELOG.md"):
                shutil.copy(ROOT / name, root / name)
            target = root / "assets/characters/not-allowed/character.yaml"
            target.parent.mkdir(parents=True)
            target.write_text(yaml.safe_dump({
                "schema_version": "0.1.0", "id": "not-allowed", "display_name": "Not allowed",
                "status": "draft", "identity": {"summary": "test", "anchors": ["test"]},
            }), encoding="utf-8")
            self.assertTrue(any("must not contain character instance records" in error for error in validate(root)))


if __name__ == "__main__":
    unittest.main()
