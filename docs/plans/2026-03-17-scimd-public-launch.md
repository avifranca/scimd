# SciMD Public Launch & Reputation Building Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Take SciMD from a local project to a publicly citable, installable, and discoverable open-source contribution that establishes Juan Francisco Avilés Calderón as its creator.

**Architecture:** Fix packaging and add tests first (code quality), then establish provenance (GitHub + Zenodo DOI), then grow visibility (arXiv + communities). Each phase builds on the previous one.

**Tech Stack:** Python 3.10+, pytest, PyPI, GitHub, Zenodo, arXiv

---

## Phase 1 — Fix the Code (Before Anyone Sees It)

### Task 1: Add `pyproject.toml` and `requirements.txt`

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`

**Step 1: Create `requirements.txt`**

```
PyYAML>=6.0
```

**Step 2: Create `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "scimd"
version = "0.1.0"
description = "SciMD — Scientific Markdown for the AI Era"
readme = "README.md"
license = { file = "LICENSE" }
authors = [
  { name = "Juan Francisco Avilés Calderón" }
]
requires-python = ">=3.10"
dependencies = ["PyYAML>=6.0"]

[project.scripts]
scimd = "scimd_parser:main"

[project.urls]
Homepage = "https://github.com/franavical/scimd"
```

**Step 3: Verify syntax**

Run: `python -m py_compile scimd_parser.py scimd_validator.py`
Expected: No output (no errors)

**Step 4: Commit**

```bash
git add pyproject.toml requirements.txt
git commit -m "chore: add packaging files and declare PyYAML dependency"
```

---

### Task 2: Add a pytest test suite

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_parser.py`
- Create: `tests/test_validator.py`

**Step 1: Create `tests/__init__.py`** (empty file)

**Step 2: Write failing parser tests in `tests/test_parser.py`**

```python
import pytest
from pathlib import Path
from scimd_parser import SciMDParser

FIXTURE = Path(__file__).parent.parent / "full-paper.smd"


def test_parse_returns_document():
    doc = SciMDParser.parse(str(FIXTURE))
    assert doc is not None


def test_document_has_title():
    doc = SciMDParser.parse(str(FIXTURE))
    assert doc.title and len(doc.title) > 0


def test_document_has_authors():
    doc = SciMDParser.parse(str(FIXTURE))
    assert len(doc.authors) >= 1


def test_document_has_sections():
    doc = SciMDParser.parse(str(FIXTURE))
    assert len(doc.sections) >= 1


def test_sections_have_unique_ids():
    doc = SciMDParser.parse(str(FIXTURE))
    ids = [s.id for s in doc.sections]
    assert len(ids) == len(set(ids)), "Section IDs must be unique"


def test_rag_chunks_not_empty():
    doc = SciMDParser.parse(str(FIXTURE))
    chunks = doc.to_rag_chunks()
    assert len(chunks) >= 1


def test_rag_chunks_have_metadata():
    doc = SciMDParser.parse(str(FIXTURE))
    for chunk in doc.to_rag_chunks():
        assert "id" in chunk
        assert "content" in chunk
```

**Step 3: Run tests to verify they fail (or reveal import issues)**

Run: `python -m pytest tests/test_parser.py -v`
Expected: Some tests PASS, confirm no import errors. Fix import path if needed.

**Step 4: Write validator tests in `tests/test_validator.py`**

```python
import pytest
from pathlib import Path
from scimd_validator import SciMDValidator

FIXTURE = Path(__file__).parent.parent / "full-paper.smd"


def test_validator_returns_issues_list():
    validator = SciMDValidator(str(FIXTURE))
    issues = validator.validate()
    assert isinstance(issues, list)


def test_valid_document_has_no_errors():
    validator = SciMDValidator(str(FIXTURE))
    issues = validator.validate()
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) == 0, f"Unexpected errors: {errors}"


def test_strict_mode_runs():
    validator = SciMDValidator(str(FIXTURE), strict=True)
    issues = validator.validate()
    assert isinstance(issues, list)
```

**Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS (or reveal real bugs to fix)

**Step 6: Commit**

```bash
git add tests/
git commit -m "test: add pytest suite for parser and validator"
```

---

## Phase 2 — Establish Public Provenance

### Task 3: Create the GitHub repository

**This task is done manually in the browser. Steps:**

1. Go to **github.com/new**
2. Repository name: `scimd`
3. Description: `SciMD — Scientific Markdown for the AI Era. An open document format designed for humans to write, machines to understand.`
4. Set to **Public**
5. Do NOT initialize with README (you already have one)
6. Click **Create repository**

**Step 2: Push your local project**

```bash
cd /Users/franavical/Downloads/scimd
git init          # if not already a git repo
git add .
git commit -m "feat: initial release of SciMD v0.1.0

SciMD is an open plain-text document format for scientific writing,
optimized for AI/RAG pipelines. Includes full specification, reference
parser, validator, authoring guide, and RAG integration guide.

Created by Juan Francisco Avilés Calderón."
git branch -M main
git remote add origin https://github.com/franavical/scimd.git
git push -u origin main
```

**Step 3: Tag the release**

```bash
git tag -a v0.1.0 -m "SciMD v0.1.0 — Initial specification release"
git push origin v0.1.0
```

**Step 4: Create a GitHub Release**

1. Go to `github.com/franavical/scimd/releases/new`
2. Select tag `v0.1.0`
3. Title: `SciMD v0.1.0 — Initial Release`
4. Description: paste the content of the "The Solution" section from README.md
5. Click **Publish release**

---

### Task 4: Add `CITATION.cff` for academic citation

**Files:**
- Create: `CITATION.cff`

**Step 1: Create `CITATION.cff`**

```yaml
cff-version: 1.2.0
title: "SciMD: Scientific Markdown for the AI Era"
message: "If you use SciMD in your research or software, please cite it using this metadata."
type: software
authors:
  - family-names: "Avilés Calderón"
    given-names: "Juan Francisco"
version: 0.1.0
date-released: "2026-03-17"
license: MIT
repository-code: "https://github.com/franavical/scimd"
abstract: >
  SciMD (.smd) is an open plain-text document format for scientific and
  technical writing, designed to be AI-readable and optimized for RAG
  pipelines. It provides structured sections, mandatory chart data,
  MermaidJS diagrams, and LaTeX equations as first-class citizens.
keywords:
  - scientific-writing
  - document-format
  - RAG
  - AI
  - markdown
  - open-science
```

**Step 2: Commit and push**

```bash
git add CITATION.cff
git commit -m "docs: add CITATION.cff for academic citation"
git push
```

**Result:** GitHub will now show a "Cite this repository" button on the repo page.

---

### Task 5: Get a DOI via Zenodo

**This task is done manually. Steps:**

1. Go to **zenodo.org** and log in with your GitHub account
2. Go to **GitHub → Zenodo** settings: `zenodo.org/account/settings/github/`
3. Find `franavical/scimd` in the list and **toggle it ON**
4. Go back to GitHub and create a new release (or re-publish v0.1.0)
5. Zenodo will automatically archive it and assign a DOI like `10.5281/zenodo.XXXXXXX`
6. Copy the DOI badge URL and add it to `README.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

**Step 2: Add DOI badge to README.md**

Add the badge line to the top of README.md alongside the existing MIT and Spec Version badges.

```bash
git add README.md
git commit -m "docs: add Zenodo DOI badge"
git push
```

---

## Phase 3 — Grow Visibility

### Task 6: Write the arXiv abstract and paper outline

**Files:**
- Create: `docs/arxiv-paper/abstract.md`
- Create: `docs/arxiv-paper/outline.md`

**Step 1: Create `docs/arxiv-paper/abstract.md`**

```markdown
# arXiv Submission Abstract

**Title:** SciMD: A Plain-Text Document Format for AI-Ready Scientific Literature

**Authors:** Juan Francisco Avilés Calderón

**Categories:** cs.DL (Digital Libraries), cs.AI, cs.IR

---

## Abstract (150 words)

We present SciMD, an open plain-text document format for scientific and
technical writing designed to be natively readable by large language models
and optimized for retrieval-augmented generation (RAG) pipelines. Existing
formats—PDF, DOCX, and LaTeX—require lossy conversion steps that introduce
OCR errors, discard chart data, and produce arbitrary text chunk boundaries.
SciMD addresses these limitations through four design principles: (1) author-
time structure with semantic section metadata and explicit dependency graphs,
(2) data over pixels—charts are Markdown tables, diagrams are MermaidJS source,
and formulas are LaTeX, (3) mandatory author interpretations for every visual
element, and (4) plain UTF-8 text compatible with any editor and version
control system. We describe the format specification (v0.1.0), provide a
reference parser and validator in Python, and demonstrate improved RAG chunking
quality compared to PDF-extracted text.
```

**Step 2: Create `docs/arxiv-paper/outline.md`**

```markdown
# Paper Outline — 4 pages, ACL format

## 1. Introduction (0.5 pages)
- The problem: AI systems consume scientific literature badly
- PDF/DOCX limitations for LLM training and RAG
- Our contribution: SciMD format + reference implementation

## 2. Related Work (0.5 pages)
- Markdown derivatives (MyST, R Markdown)
- Scientific document formats (JATS XML, TEI)
- Why none solve the RAG/AI problem

## 3. The SciMD Format (1.5 pages)
- Document header and YAML metadata
- Semantic sections with IDs, types, summaries, dependencies
- Charts as data tables with mandatory interpretation
- Figures with description/interpretation duality
- MermaidJS diagrams, LaTeX equations
- Reference and citation system

## 4. Reference Implementation (0.5 pages)
- Parser (scimd_parser.py) — zero external deps
- Validator (scimd_validator.py) — error codes, strict mode
- to_rag_chunks() API for LLM pipelines

## 5. Evaluation (0.5 pages)
- Convert 10 arXiv papers to SciMD manually
- Compare RAG retrieval precision: PDF-parsed vs SciMD chunks
- Show reduction in hallucinations on chart questions

## 6. Conclusion (0.25 pages)
- SciMD is available at github.com/franavical/scimd
- DOI: 10.5281/zenodo.XXXXXXX
- Call for community contributions
```

**Step 3: Commit**

```bash
git add docs/arxiv-paper/
git commit -m "docs: add arXiv paper abstract and outline"
git push
```

---

### Task 7: Publish to PyPI

**Step 1: Install build tools**

```bash
pip install build twine
```

**Step 2: Build the package**

```bash
cd /Users/franavical/Downloads/scimd
python -m build
```
Expected: `dist/scimd-0.1.0.tar.gz` and `dist/scimd-0.1.0-py3-none-any.whl` are created.

**Step 3: Upload to PyPI**

```bash
python -m twine upload dist/*
```
You'll need a PyPI account at `pypi.org`. Create one if you don't have it.

**Step 4: Verify installation works**

```bash
pip install scimd
scimd --help
```

**Step 5: Add PyPI badge to README.md**

```markdown
[![PyPI version](https://badge.fury.io/py/scimd.svg)](https://pypi.org/project/scimd/)
```

```bash
git add README.md
git commit -m "docs: add PyPI badge after publishing package"
git push
```

---

### Task 8: Community outreach posts

**Files:**
- Create: `docs/launch-posts/hacker-news.md`
- Create: `docs/launch-posts/reddit-ml.md`

**Step 1: Create `docs/launch-posts/hacker-news.md`**

```markdown
# Hacker News — Show HN Post

**Title:** Show HN: SciMD – a plain-text format so AI can actually read scientific papers

**Body:**
PDF is a terrible format for AI. OCR fails, charts become meaningless pixels,
figures lose context, and chunk boundaries are arbitrary. I built SciMD (.smd)
to fix this from the authoring side.

Key ideas:
- Charts are Markdown tables with mandatory author interpretation
- Diagrams are MermaidJS source (not images)
- Formulas are LaTeX (not images)
- Sections have semantic metadata: type, summary, dependency graph
- 100% plain UTF-8 text — works in any editor, diffs cleanly in Git

It includes a reference parser and validator in pure Python (no ML deps).
The to_rag_chunks() method gives you semantically bounded chunks with full metadata.

GitHub: https://github.com/franavical/scimd
Spec: https://github.com/franavical/scimd/blob/main/SPECIFICATION.md

Happy to hear thoughts on the format design or what's missing for your use case.
```

**Step 2: Create `docs/launch-posts/reddit-ml.md`**

```markdown
# Reddit r/MachineLearning Post

**Title:** [Project] SciMD: an open document format that makes scientific papers
natively readable by LLMs (no OCR, no image charts, no bad chunks)

**Body:**
I got tired of watching RAG pipelines degrade because PDFs are such a bad source format.
Built SciMD to solve the problem at authoring time instead of post-processing time.

The core insight: if the author provides structure when writing,
AI systems don't have to guess it later.

What that looks like in practice:
- Charts → Markdown table + mandatory interpretation paragraph
- Diagrams → MermaidJS source code + description
- Equations → LaTeX (inline and block)
- Sections → typed (introduction/methods/results), with summary + explicit depends_on

Reference parser + validator in pure Python: `pip install scimd`
Full spec + examples: github.com/franavical/scimd

Would love feedback from anyone doing RAG over scientific literature.
```

**Step 3: Commit**

```bash
git add docs/launch-posts/
git commit -m "docs: add community outreach post drafts"
git push
```

---

## Phase 4 — Long-Term Reputation

### Task 9: Add GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Create `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install PyYAML pytest
      - name: Run tests
        run: pytest tests/ -v
      - name: Validate example document
        run: python scimd_validator.py full-paper.smd
```

**Step 2: Commit and push**

```bash
git add .github/
git commit -m "ci: add GitHub Actions workflow for tests and validation"
git push
```

**Result:** Green CI badge on your repo — signals professional quality to visitors.

---

## Checklist Summary

| Step | Action | Effort | Impact |
|---|---|---|---|
| ✅ 1 | `pyproject.toml` + `requirements.txt` | 10 min | Installable package |
| ✅ 2 | pytest test suite | 30 min | Code quality signal |
| ✅ 3 | GitHub repo + v0.1.0 tag | 15 min | Public provenance |
| ✅ 4 | `CITATION.cff` | 5 min | Academic citability |
| ✅ 5 | Zenodo DOI | 10 min | Formal scholarly record |
| ✅ 6 | arXiv abstract + outline | 1 hour | Highest career impact |
| ✅ 7 | Publish to PyPI | 20 min | Adoption + discoverability |
| ✅ 8 | Community posts | 30 min | Visibility + feedback |
| ✅ 9 | GitHub Actions CI | 10 min | Professionalism signal |

**Do tasks 3 → 4 → 5 on the same day** — Zenodo picks up the GitHub release automatically.
**Do task 8 the same day as task 3** — momentum matters at launch.
