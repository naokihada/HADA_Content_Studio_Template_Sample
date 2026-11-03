from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from catalog import list_projects, markdown  # noqa: E402


class ProjectCatalogTests(unittest.TestCase):
    def test_lists_diverse_mini_projects_in_stable_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = [
                {"id": "motorcycle-basics", "title": "Motorcycle Basics", "domain": "hobby", "purpose": "Practice safely.", "audience": "Rider", "status": "active"},
                {"id": "exam-classics", "title": "Classics Exam", "domain": "education", "purpose": "Review poetry.", "audience": "Student", "status": "draft"},
            ]
            for record in records:
                path = root / "projects" / record["domain"] / record["id"] / "project.yaml"
                path.parent.mkdir(parents=True)
                path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
            listed = list_projects(root)
            self.assertEqual([item["id"] for item in listed], ["exam-classics", "motorcycle-basics"])
            rendered = markdown(listed)
            self.assertIn("[Classics Exam](projects/education/exam-classics/project.yaml)", rendered)
            self.assertIn("[Motorcycle Basics](projects/hobby/motorcycle-basics/project.yaml)", rendered)


if __name__ == "__main__":
    unittest.main()
