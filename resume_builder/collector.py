from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".rst",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".py",
    ".js",
    ".ts",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".cpp",
    ".html",
    ".css",
}

SKILL_KEYWORDS = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "golang": "Go",
    "go ": "Go",
    "rust": "Rust",
    "react": "React",
    "vue": "Vue",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "sql": "SQL",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "linux": "Linux",
    "aws": "AWS",
}

IGNORE_DIRS = {".git", "node_modules", "dist", "build", "venv", ".venv", "__pycache__"}


def iter_source_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS and path.stat().st_size < 1_000_000:
            yield path


def extract_highlights(text: str, limit: int = 6) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullet_like = [line.lstrip("-*").strip() for line in lines if re.match(r"^\s*[-*]", line)]
    if bullet_like:
        return bullet_like[:limit]

    long_lines = [line for line in lines if len(line.split()) >= 6]
    return long_lines[:limit]


def infer_skills(text_chunks: Iterable[str], file_suffixes: Iterable[str]) -> list[str]:
    content = "\n".join(text_chunks).lower()
    found = set()
    for key, display in SKILL_KEYWORDS.items():
        if key in content:
            found.add(display)

    ext_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".sql": "SQL",
    }
    for suffix in file_suffixes:
        skill = ext_map.get(suffix)
        if skill:
            found.add(skill)

    return sorted(found)


def collect_project_evidence(source_dir: Path, max_files: int = 120) -> dict:
    file_summaries: list[dict] = []
    text_chunks: list[str] = []
    suffix_counter: Counter[str] = Counter()

    for idx, file in enumerate(iter_source_files(source_dir)):
        if idx >= max_files:
            break
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        highlights = extract_highlights(text)
        if not highlights:
            continue

        file_summaries.append(
            {
                "path": str(file.relative_to(source_dir)),
                "highlights": highlights,
            }
        )
        text_chunks.extend(highlights)
        suffix_counter[file.suffix.lower()] += 1

    skills = infer_skills(text_chunks, suffix_counter.keys())

    projects = []
    for summary in file_summaries[:3]:
        title = summary["path"].split("/")[0]
        bullets = [f"{point} (source: {summary['path']})" for point in summary["highlights"][:3]]
        projects.append({"title": title, "bullets": bullets})

    return {
        "skills": skills,
        "projects": projects,
        "sources_analyzed": len(file_summaries),
        "top_file_types": suffix_counter.most_common(8),
    }


def dump_evidence_json(evidence: dict, out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
