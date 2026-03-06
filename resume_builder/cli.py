from __future__ import annotations

import argparse
import json
from pathlib import Path

from .collector import collect_project_evidence, dump_evidence_json
from .latex import build_resume_tex, export_pdf

DEFAULT_PROFILE = {
    "basics": {
        "name": "你的名字",
        "email": "email@example.com",
        "phone": "+86-13800000000",
        "location": "中国",
        "website": "https://github.com/yourname",
    },
    "summary": "3-5 行职业简介，突出你的方向、经验年限和价值。",
    "skills": [],
    "projects": [],
    "education": [
        {"school": "某某大学", "degree": "计算机科学本科", "period": "2018-2022"}
    ],
}


def cmd_init(args: argparse.Namespace) -> None:
    profile_path = Path(args.profile)
    if profile_path.exists() and not args.force:
        raise SystemExit(f"Profile already exists: {profile_path}. Use --force to overwrite.")
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(json.dumps(DEFAULT_PROFILE, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"已创建模板配置: {profile_path}")


def cmd_collect(args: argparse.Namespace) -> None:
    source_dir = Path(args.source).resolve()
    evidence = collect_project_evidence(source_dir=source_dir, max_files=args.max_files)
    out_path = Path(args.output)
    dump_evidence_json(evidence, out_path)
    print(f"已分析 {evidence['sources_analyzed']} 个文件, 输出: {out_path}")


def cmd_build(args: argparse.Namespace) -> None:
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    evidence = collect_project_evidence(Path(args.source).resolve(), max_files=args.max_files)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    tex_content = build_resume_tex(profile, evidence)
    tex_file = out_dir / "resume.tex"
    tex_file.write_text(tex_content, encoding="utf-8")

    evidence_file = out_dir / "evidence.json"
    dump_evidence_json(evidence, evidence_file)

    if args.no_pdf:
        print(f"已生成 TeX: {tex_file}")
        return

    try:
        ok = export_pdf(tex_file, out_dir)
    except Exception as exc:
        print(f"PDF 导出失败: {exc}")
        ok = False

    if ok:
        print(f"PDF 导出成功: {out_dir / 'resume.pdf'}")
    else:
        print("未检测到 pdflatex 或导出失败，仅生成了 resume.tex")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从文档与项目文件生成可编辑 LaTeX 简历并导出 PDF")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init", help="创建初始 profile.json")
    init_parser.add_argument("--profile", default="resume/profile.json")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=cmd_init)

    collect_parser = sub.add_parser("collect", help="分析资料并输出 evidence.json")
    collect_parser.add_argument("--source", default=".")
    collect_parser.add_argument("--output", default="resume/evidence.json")
    collect_parser.add_argument("--max-files", type=int, default=120)
    collect_parser.set_defaults(func=cmd_collect)

    build_parser_ = sub.add_parser("build", help="生成 resume.tex，并在可用时导出 PDF")
    build_parser_.add_argument("--profile", default="resume/profile.json")
    build_parser_.add_argument("--source", default=".")
    build_parser_.add_argument("--output", default="resume/build")
    build_parser_.add_argument("--max-files", type=int, default=120)
    build_parser_.add_argument("--no-pdf", action="store_true")
    build_parser_.set_defaults(func=cmd_build)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
