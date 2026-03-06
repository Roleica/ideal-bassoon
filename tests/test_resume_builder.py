import json
import tempfile
import unittest
from pathlib import Path

from resume_builder.collector import collect_project_evidence
from resume_builder.latex import build_resume_tex


class ResumeBuilderTests(unittest.TestCase):
    def test_collect_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("- Built API service with Python\n- Added Docker deployment", encoding="utf-8")
            (root / "app.py").write_text("print('hello')", encoding="utf-8")

            evidence = collect_project_evidence(root)
            self.assertIn("Python", evidence["skills"])
            self.assertGreaterEqual(evidence["sources_analyzed"], 1)

    def test_build_tex(self):
        profile = {
            "basics": {
                "name": "张三",
                "email": "a@b.com",
                "phone": "123",
                "location": "北京",
                "website": "https://example.com",
            },
            "summary": "后端工程师",
            "education": [{"school": "A大学", "degree": "本科", "period": "2018-2022"}],
        }
        evidence = {"skills": ["Python"], "projects": [{"title": "项目X", "bullets": ["完成接口开发"]}]}

        tex = build_resume_tex(profile, evidence)
        self.assertIn("张三", tex)
        self.assertIn("Python", tex)


if __name__ == "__main__":
    unittest.main()
