from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from export_image import export_image  # noqa: E402
from image_metadata import scan_image_metadata  # noqa: E402
from intake_asset import intake_image  # noqa: E402
from record_publication import record_publication  # noqa: E402
from resolve_prompt import resolve_prompt, write_sidecar  # noqa: E402
from validate import validate  # noqa: E402


class ImagePipelineTests(unittest.TestCase):
    def make_root(self) -> tuple[Path, tempfile.TemporaryDirectory[str], Path]:
        holder = tempfile.TemporaryDirectory()
        root = Path(holder.name) / "project"
        root.mkdir()
        shutil.copytree(ROOT / "config", root / "config")
        shutil.copytree(ROOT / "schemas", root / "schemas")
        shutil.copytree(ROOT / "profiles", root / "profiles")
        for name in ("TEMPLATE_BASE.md", "CHANGELOG.md"):
            shutil.copy(ROOT / name, root / name)
        manifest_path = root / "config/template-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"].update({"role": "sample", "character_instances_allowed": True, "contains_user_data": False, "sample_character_data": True, "sample_character_name": "Fixture Elf"})
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

        def write_record(relative: str, record: dict) -> None:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")

        write_record("assets/characters/fixture-elf/character.yaml", {
            "schema_version": "0.1.0", "id": "fixture-elf", "display_name": "Fixture Elf",
            "status": "approved", "identity": {"summary": "Fictional test character.", "anchors": ["pointed ears", "green eyes"]},
        })
        write_record("projects/fantasy/studio-guide/project.yaml", {
            "schema_version": "0.1.0", "id": "studio-guide", "title": "Studio Guide",
            "domain": "fantasy", "purpose": "Test image production.", "audience": "Template reviewer",
            "scope": {"includes": [], "excludes": []}, "visibility": "private", "status": "active",
            "character_refs": ["fixture-elf"], "production_refs": ["feature-infographic"],
        })
        write_record("projects/fantasy/studio-guide/productions/infographic/production.yaml", {
            "schema_version": "0.1.0", "id": "feature-infographic", "project_id": "studio-guide",
            "title": "Feature Infographic", "status": "draft", "profile_id": "infographic-default",
            "knowledge_refs": [], "character_refs": ["fixture-elf"],
        })
        values_path = root / "projects/fantasy/studio-guide/prompt-values.yaml"
        values_path.parent.mkdir(parents=True, exist_ok=True)
        values_path.write_text(yaml.safe_dump({
            "variables": {"domain": "Fantasy", "topic": "Template features", "audience": "Reviewers", "central_message": "Learn the workflow"},
            "reference_assets": [],
        }, allow_unicode=True, sort_keys=False), encoding="utf-8")
        prompt = resolve_prompt(
            root, prompt_id="feature-prompt-v1", work_id="feature-infographic",
            profile_path="profiles/prompts/infographic.yaml", values_path="projects/fantasy/studio-guide/prompt-values.yaml",
        )
        write_sidecar(root, "projects/fantasy/studio-guide/productions/infographic/prompt_resolutions/feature-prompt-v1.yaml", prompt)

        branding = root / "assets/branding/watermark.png"
        branding.parent.mkdir(parents=True)
        logo = Image.new("RGBA", (260, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo)
        draw.rounded_rectangle((0, 0, 259, 63), radius=14, fill=(16, 36, 62, 230))
        draw.text((14, 17), "HADA CONTENT STUDIO", fill=(255, 255, 255, 255))
        logo.save(branding, format="PNG")
        self.addCleanup(holder.cleanup)
        return root, holder, root / "incoming-source.png"

    def make_source(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("provider_tracking_id", "private-source-only")
        image = Image.new("RGBA", (1024, 768), (194, 219, 179, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse((280, 90, 740, 570), fill=(49, 114, 80, 255))
        image.save(path, format="PNG", pnginfo=metadata)

    def intake(self, root: Path, source: Path, *, generation_id: str = "elf-generation-v1", asset_id: str = "elf-reference", disposition: str = "accepted") -> Path:
        return intake_image(
            root, source_path=source, generation_id=generation_id, asset_id=asset_id,
            asset_version="0.1.0", prompt_resolution_id="feature-prompt-v1", provider="OpenAI ImageGen",
            model="not exposed by image-generation connector", generated_at="2026-11-02T12:00:00Z",
            disposition=disposition, reviewer="Codex visual QA", reviewed_at="2026-11-02T12:05:00Z",
        )

    def test_intake_preserves_source_and_social_export_is_small_clean_and_repeatable(self) -> None:
        root, _holder, source = self.make_root()
        self.make_source(source)
        original_bytes = source.read_bytes()
        self.intake(root, source)
        master = root / "assets/masters/elf-reference/0.1.0/source.png"
        self.assertEqual(master.read_bytes(), original_bytes)
        self.assertEqual(validate(root), [])

        profile = "profiles/exports/social.example.yaml"
        first = export_image(root, generation_id="elf-generation-v1", derivative_id="elf-social-v1", profile_path=profile)
        record = yaml.safe_load(first.read_text(encoding="utf-8"))
        output = root / record["output_path"]
        self.assertEqual(record["status"], "ready_for_human_review")
        self.assertEqual((record["width"], record["height"]), (720, 540))
        self.assertTrue(record["resized"])
        self.assertEqual(scan_image_metadata(output), ("JPEG", []))
        with Image.open(output) as rendered:
            self.assertEqual(rendered.size, (720, 540))
            self.assertNotIn("provider_tracking_id", rendered.info)

        second = export_image(root, generation_id="elf-generation-v1", derivative_id="elf-social-v2", profile_path=profile)
        second_record = yaml.safe_load(second.read_text(encoding="utf-8"))
        self.assertEqual(record["output_sha256"], second_record["output_sha256"])
        with self.assertRaises(FileExistsError):
            export_image(root, generation_id="elf-generation-v1", derivative_id="elf-social-v1", profile_path=profile)

        publication = record_publication(
            root, publication_id="elf-social-post", derivative_record_path=first.relative_to(root).as_posix(),
            destination="sample-review", published_at="2026-11-02T12:30:00Z", public_url="https://example.com/post/1",
        )
        self.assertTrue(publication.is_file())
        self.assertEqual(validate(root), [])

        clean_bytes = output.read_bytes()
        payload = b"post-export comment"
        comment = b"\xff\xfe" + (len(payload) + 2).to_bytes(2, "big") + payload
        output.write_bytes(clean_bytes[:2] + comment + clean_bytes[2:])
        self.assertTrue(any("comment" in finding for finding in scan_image_metadata(output)[1]))
        self.assertTrue(any("asset hash mismatch" in error for error in validate(root)))
        with self.assertRaisesRegex(ValueError, "project validation failed"):
            record_publication(
                root, publication_id="tampered-output-post", derivative_record_path=first.relative_to(root).as_posix(),
                destination="sample-review", published_at="2026-11-02T12:30:00Z",
            )

    def test_website_profile_preserves_dimensions_and_uses_png(self) -> None:
        root, _holder, source = self.make_root()
        self.make_source(source)
        self.intake(root, source)
        sidecar = export_image(root, generation_id="elf-generation-v1", derivative_id="elf-website-v1", profile_path="profiles/exports/website.example.yaml")
        record = yaml.safe_load(sidecar.read_text(encoding="utf-8"))
        self.assertEqual(record["output_format"], "PNG")
        self.assertEqual((record["width"], record["height"]), (1024, 768))
        self.assertFalse(record["resized"])
        self.assertEqual(scan_image_metadata(root / record["output_path"]), ("PNG", []))
        self.assertEqual(validate(root), [])

    def test_discard_candidate_cannot_be_exported(self) -> None:
        root, _holder, source = self.make_root()
        self.make_source(source)
        self.intake(root, source, generation_id="discard-generation", asset_id="alternate-sketch", disposition="discard_candidate")
        with self.assertRaisesRegex(ValueError, "only an accepted"):
            export_image(root, generation_id="discard-generation", derivative_id="discard-export", profile_path="profiles/exports/social.example.yaml")

    def test_metadata_scanner_detects_png_text_and_jpeg_comment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            png = root / "metadata.png"
            info = PngImagePlugin.PngInfo()
            info.add_text("comment", "private metadata")
            Image.new("RGB", (8, 8), "white").save(png, pnginfo=info)
            self.assertTrue(any("tEXt" in finding for finding in scan_image_metadata(png)[1]))

            jpeg = root / "metadata.jpg"
            Image.new("RGB", (8, 8), "white").save(jpeg, format="JPEG")
            data = jpeg.read_bytes()
            payload = b"private comment"
            segment = b"\xff\xfe" + (len(payload) + 2).to_bytes(2, "big") + payload
            jpeg.write_bytes(data[:2] + segment + data[2:])
            self.assertTrue(any("comment" in finding for finding in scan_image_metadata(jpeg)[1]))


if __name__ == "__main__":
    unittest.main()
