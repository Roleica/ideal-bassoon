from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from string import Template

LATEX_TEMPLATE = Template(
    r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\setlist[itemize]{leftmargin=*, itemsep=2pt, topsep=2pt}
\begin{document}

\begin{center}
    {\LARGE \textbf{$name}}\\
    $email \textbar\ $phone \textbar\ $location \textbar\ \href{$website}{$website}
\end{center}

\section*{职业简介}
$summary

\section*{核心技能}
\begin{itemize}
$skills_items
\end{itemize}

\section*{项目经历}
$projects_block

\section*{教育背景}
$education_block

\end{document}
""".strip()
)


def escape_latex(value: str) -> str:
    mapping = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    for key, rep in mapping.items():
        value = value.replace(key, rep)
    return value


def build_resume_tex(profile: dict, evidence: dict) -> str:
    basics = profile.get("basics", {})
    skills = profile.get("skills") or evidence.get("skills", [])
    projects = profile.get("projects") or evidence.get("projects", [])
    education = profile.get("education", [])

    skills_items = "\n".join([f"\\item {escape_latex(skill)}" for skill in skills]) or "\\item 暂无"

    project_blocks = []
    for proj in projects:
        title = escape_latex(proj.get("title", "未命名项目"))
        bullets = proj.get("bullets", [])
        bullet_tex = "\n".join([f"\\item {escape_latex(b)}" for b in bullets]) or "\\item 暂无"
        project_blocks.append(
            f"\\subsection*{{{title}}}\n\\begin{{itemize}}\n{bullet_tex}\n\\end{{itemize}}"
        )
    projects_block = "\n\n".join(project_blocks) or "暂无项目"

    edu_blocks = []
    for edu in education:
        edu_blocks.append(
            f"\\textbf{{{escape_latex(edu.get('school', ''))}}} - {escape_latex(edu.get('degree', ''))} ({escape_latex(edu.get('period', ''))})"
        )
    education_block = "\\\\\n".join(edu_blocks) or "暂无"

    return LATEX_TEMPLATE.substitute(
        name=escape_latex(basics.get("name", "你的名字")),
        email=escape_latex(basics.get("email", "email@example.com")),
        phone=escape_latex(basics.get("phone", "+86-XXX")),
        location=escape_latex(basics.get("location", "中国")),
        website=escape_latex(basics.get("website", "https://example.com")),
        summary=escape_latex(profile.get("summary", "请在 profile.json 中补充职业简介。")),
        skills_items=skills_items,
        projects_block=projects_block,
        education_block=education_block,
    )


def export_pdf(tex_file: Path, workdir: Path) -> bool:
    pdflatex = shutil.which("pdflatex")
    if not pdflatex:
        return False

    for _ in range(2):
        subprocess.run(
            [pdflatex, "-interaction=nonstopmode", tex_file.name],
            cwd=workdir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return True
