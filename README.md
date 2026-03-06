# LaTeX 简历生成与修改项目

这个项目可以根据你的**文档文件**和**项目代码文件**自动抽取素材，生成可编辑的 `resume.tex`，并在本地有 `pdflatex` 时导出 `resume.pdf`。

## 功能

- 扫描 Markdown/TXT/JSON/YAML/代码文件，提取项目亮点。
- 自动推断技能栈（如 Python、JavaScript、Docker 等）。
- 生成 LaTeX 简历（`resume.tex`），可手动修改。
- 支持通过 `profile.json` 自定义基本信息、教育经历、项目经历。
- 如果已安装 `pdflatex`，自动导出 `PDF`。

## 快速开始

```bash
python -m resume_builder.cli init --profile resume/profile.json
python -m resume_builder.cli build --profile resume/profile.json --source . --output resume/build
```

若只想生成 tex，不导出 pdf：

```bash
python -m resume_builder.cli build --no-pdf
```

## 如何修改简历

1. 编辑 `resume/profile.json`，填写 `basics`、`summary`、`education`。
2. 如果你希望完全手写项目内容，可在 `projects` 写入数组，自动分析结果会被覆盖。
3. 重新执行 `build` 命令。

## 命令说明

### 初始化模板

```bash
python -m resume_builder.cli init --profile resume/profile.json
```

### 仅分析素材

```bash
python -m resume_builder.cli collect --source . --output resume/evidence.json
```

### 生成简历

```bash
python -m resume_builder.cli build --profile resume/profile.json --source . --output resume/build
```

## 输出目录

- `resume/build/resume.tex`
- `resume/build/evidence.json`
- `resume/build/resume.pdf`（如果 pdflatex 可用）
