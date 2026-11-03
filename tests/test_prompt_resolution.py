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

from resolve_prompt import resolve_prompt, write_sidecar  # noqa: E402
from validate import validate  # noqa: E402


class PromptResolutionTests(unittest.TestCase):
    def _inputs(self, root: Path) -> None:
        layers = root / "profiles/prompts/layers"
        layers.mkdir(parents=True)
        profile = {
            "schema_version": "0.1.0", "id": "test-profile", "version": "0.1.0",
            "layers": {"shared": ["profiles/prompts/layers/shared.yaml"], "medium": ["profiles/prompts/layers/medium.yaml"]},
        }
        (root / "profiles/prompts/profile.yaml").write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
        for name, layer_id, prompt in (
            ("shared.yaml", "shared-test", "Shared {{topic}}"),
            ("domain.yaml", "domain-test", "Domain {{domain}}"),
            ("medium.yaml", "medium-test", "Medium {{topic}}"),
            ("project.yaml", "project-test", "Project {{audience}}"),
            ("entity.yaml", "entity-test", "Entity {{entity_name}}"),
            ("request.yaml", "request-test", "Request {{request}}"),
        ):
            (layers / name).write_text(yaml.safe_dump({"id": layer_id, "version": "0.1.0", "prompt": prompt}, sort_keys=False), encoding="utf-8")
        (root / "values.yaml").write_text(yaml.safe_dump({
            "variables": {"topic": "Topic", "domain": "Education", "audience": "Learners", "entity_name": "Fictional entity", "request": "Use two panels"},
            "reference_assets": [],
        }, sort_keys=False), encoding="utf-8")

    def test_fixed_layer_order_and_exact_prompt_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._inputs(root)
            record = resolve_prompt(
                root, prompt_id="test-resolution", work_id="test-work",
                profile_path="profiles/prompts/profile.yaml", values_path="values.yaml",
                additions={
                    "request": ["profiles/prompts/layers/request.yaml"],
                    "entity": ["profiles/prompts/layers/entity.yaml"],
                    "project": ["profiles/prompts/layers/project.yaml"],
                    "domain": ["profiles/prompts/layers/domain.yaml"],
                },
            )
            self.assertEqual([layer["group"] for layer in record["layers"]], ["shared", "domain", "medium", "project", "entity", "request"])
            self.assertEqual(record["exact_prompt"].splitlines(), [
                "Shared Topic", "", "Domain Education", "", "Medium Topic", "",
                "Project Learners", "", "Entity Fictional entity", "", "Request Use two panels",
            ])
            self.assertTrue(record["prompt_sha256"].startswith("sha256:"))

    def test_missing_and_unused_values_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._inputs(root)
            values_path = root / "values.yaml"
            values_path.write_text(yaml.safe_dump({"variables": {"topic": "Topic", "unused": "x"}}), encoding="utf-8")
            additions = {
                "domain": ["profiles/prompts/layers/domain.yaml"],
                "project": ["profiles/prompts/layers/project.yaml"],
                "entity": ["profiles/prompts/layers/entity.yaml"],
                "request": ["profiles/prompts/layers/request.yaml"],
            }
            with self.assertRaisesRegex(ValueError, "missing prompt values"):
                resolve_prompt(root, prompt_id="test-resolution", work_id="test-work", profile_path="profiles/prompts/profile.yaml", values_path="values.yaml", additions=additions)
            values_path.write_text(yaml.safe_dump({
                "variables": {
                    "topic": "Topic", "domain": "Education", "audience": "Learners",
                    "entity_name": "Fictional entity", "request": "Two panels", "unused": "x",
                }, "reference_assets": [],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unused prompt values"):
                resolve_prompt(root, prompt_id="test-resolution", work_id="test-work", profile_path="profiles/prompts/profile.yaml", values_path="values.yaml", additions=additions)

    def test_sidecar_is_write_once_and_validates_against_its_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "config", root / "config")
            shutil.copytree(ROOT / "schemas", root / "schemas")
            shutil.copytree(ROOT / "profiles", root / "profiles")
            for name in ("TEMPLATE_BASE.md", "CHANGELOG.md"):
                shutil.copy(ROOT / name, root / name)
            manifest_path = root / "config/template-manifest.json"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"].update({
                "role": "dev", "character_instances_allowed": False,
                "contains_user_data": True, "sample_character_data": False,
            })
            manifest["artifacts"].pop("sample_character_name", None)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            (root / "projects/education/test-project/productions/infographic").mkdir(parents=True, exist_ok=True)
            project_path = root / "projects/education/test-project/project.yaml"
            project_path.parent.mkdir(parents=True, exist_ok=True)
            project_path.write_text(yaml.safe_dump({
                "schema_version": "0.1.0", "id": "test-project", "title": "Test Project",
                "domain": "education", "purpose": "Validate prompt provenance.", "audience": "Reviewer",
                "scope": {"includes": [], "excludes": []}, "visibility": "private", "status": "draft",
            }, sort_keys=False), encoding="utf-8")
            production_path = root / "projects/education/test-project/productions/infographic/production.yaml"
            production_path.write_text(yaml.safe_dump({
                "schema_version": "0.1.0", "id": "test-work", "project_id": "test-project",
                "title": "Test Infographic", "status": "draft", "profile_id": "infographic-default", "knowledge_refs": [],
            }, sort_keys=False), encoding="utf-8")
            values_path = root / "projects/education/test-project/prompt-values.yaml"
            values_path.write_text(yaml.safe_dump({
                "variables": {"domain": "Education", "topic": "Safe topic", "audience": "Reviewer", "central_message": "Review the infographic"},
                "reference_assets": [],
            }, sort_keys=False), encoding="utf-8")
            record = resolve_prompt(
                root, prompt_id="test-resolution", work_id="test-work",
                profile_path="profiles/prompts/infographic.yaml", values_path="projects/education/test-project/prompt-values.yaml",
            )
            sidecar = "projects/education/test-project/productions/infographic/prompt_resolutions/test-resolution.yaml"
            write_sidecar(root, sidecar, record)
            self.assertEqual(validate(root), [])
            with self.assertRaises(FileExistsError):
                write_sidecar(root, sidecar, record)

            stored = yaml.safe_load((root / sidecar).read_text(encoding="utf-8"))
            stored["exact_prompt"] += " tampered"
            (root / sidecar).write_text(yaml.safe_dump(stored, allow_unicode=True), encoding="utf-8")
            self.assertTrue(any("exact prompt hash mismatch" in error for error in validate(root)))


if __name__ == "__main__":
    unittest.main()
