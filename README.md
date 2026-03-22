# SciMD — Scientific Markdown for the AI Era

> **An open document format designed for humans to write, machines to understand, and science to advance.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Spec Version](https://img.shields.io/badge/spec-v0.1.0-green.svg)](SPECIFICATION.md)
[![DOI](https://zenodo.org/badge/1184924320.svg)](https://doi.org/10.5281/zenodo.19080882)

---

## The Problem

Modern scientific and technical documents are trapped in formats designed for *printing*, not *understanding*:

- **PDFs** require OCR to extract text, losing structure and introducing errors
- **Charts as images** are opaque to AI — a bar chart becomes meaningless pixels
- **Figures without context** force models to hallucinate interpretations
- **Unstructured text** makes RAG retrieval imprecise and chunk boundaries arbitrary
- **Formulas as images** cannot be parsed, searched, or validated

The result: AI models hallucinate, RAG systems retrieve noise, and training pipelines waste compute on lossy format conversions.

## The Solution

**SciMD** (`.smd`) is a plain-text, human-readable document format that solves these problems by design:

| Problem | SciMD Solution |
|---|---|
| OCR errors | Plain text with Markdown — no conversion needed |
| Opaque charts | Author provides tabular data + interpretation |
| Ambiguous figures | Mandatory author descriptions for every image |
| Poor RAG chunking | Semantic sections with unique IDs and metadata |
| Formula images | Native LaTeX inline (`$...$`) and block (`$$...$$`) |
| Diagram ambiguity | MermaidJS source code + author description |
| Missing context | Structured metadata at document and section level |
| Training noise | Sequential, predictable structure from authoring |

## Benchmark Results

Independent agent benchmark across 2 scientific papers (marine biology + astrophysics), each evaluated in 4 formats: SciMD, JATS XML, HTML/LaTeXML, and PDF-extracted Markdown (docling/PyMuPDF).

**Verdict: SciMD wins for both LLM training and RAG.**

> SciMD delivers 85% of the scientific information at 17–22% of the file size of JATS XML or LaTeXML HTML, with unique structural affordances that none of the alternatives provide.

### Format Comparison

| Metric | SciMD | JATS XML | HTML (LaTeXML) | PDF-MD (docling) |
|---|---|---|---|---|
| **File size (vs SciMD)** | 1× | 4.5× | 6× | 0.3–0.4× |
| **Structured metadata** | ✅ Rich YAML | ✅ Rich (verbose) | ⚠️ Embedded | ❌ Prose-only |
| **Section semantic summaries** | ✅ Hand-written `summary:` | ❌ | ❌ | ❌ |
| **Section dependency graph** | ✅ `depends_on:` | ❌ | ❌ | ❌ |
| **Inline equations** | ✅ Clean LaTeX | ✅ Clean LaTeX | ⚠️ MathML + attr | ❌ `<!-- formula-not-decoded -->` |
| **Equation semantic labels** | ✅ `::label` per equation | ❌ | ❌ | ❌ |
| **Table interpretation** | ✅ `::interpretation` block | ❌ Caption only | ❌ Caption only | ❌ |
| **Figure descriptions** | ✅ Rich description + interpretation | ❌ Short caption | ⚠️ Verbatim caption | ❌ `<!-- image -->` |
| **Usable as raw training text** | ✅ Directly | ⚠️ After tag stripping | ❌ Tag density too high | ✅ But equations missing |
| **Usable as RAG chunk source** | ✅ Excellent | ⚠️ After processing | ❌ Blob structure | ⚠️ Decent prose only |
| **Document noise ratio** | Very Low | Moderate | High | Very Low |

### Final Ranking

| Rank | Format + Pipeline | RAG | Training |
|---|---|---|---|
| 🥇 1 | **SciMD + scimd_parser** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 🥈 2 | **SciMD (raw text)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 🥉 3 | **PDF-MD + pix2tex** | ⭐⭐⭐ | ⭐⭐⭐ |
| 4 | **JATS XML + tag stripper** | ⭐⭐ | ⭐⭐ |
| 5 | **PDF-MD (no formulas)** | ⭐⭐ | ⭐⭐ |
| 6 | **HTML (LaTeXML)** | ⭐ | ⭐ |

**What makes SciMD uniquely effective:** Four structural affordances that no alternative format provides — section-level semantic summaries (`::meta summary:`), inter-section dependency graphs (`depends_on:`), equation semantic labels (`::label`), and rich figure interpretations (`::interpretation`). These are high-value signals for training and retrieval that cannot be recovered by parsing PDF or XML after the fact.

**Critical PDF-MD limitation:** For math-heavy papers, PDF text extraction renders all equations as `<!-- formula-not-decoded -->` markers. For a theoretical physics paper in the benchmark, every quantitative relationship in the paper became opaque — a fundamental loss that pipeline improvements cannot fully recover without pix2tex.

*Full benchmark: [`docs/AG-ClSo4.5-format benchmark.md`](docs/AG-ClSo4.5-format%20benchmark.md)*

---

## Key Principles

1. **Author-time structure** — Structure is defined *when writing*, not reverse-engineered later
2. **Data over pixels** — Charts are data tables; diagrams are code; formulas are LaTeX
3. **Interpretation is mandatory** — Every visual element carries the author's explanation
4. **Sequential readability** — Documents flow logically for both humans and token streams
5. **Plain text first** — Every `.smd` file is valid UTF-8 text, editable in any text editor
6. **Open by default** — MIT licensed, community-driven, no vendor lock-in

## Quick Example

```markdown
---smd
title: "Effects of Temperature on Catalyst Performance"
authors:
  - name: "María García"
    orcid: "0000-0002-1234-5678"
    affiliation: "UNAM"
version: "0.1.0"
lang: "es"
keywords: ["catalysis", "temperature", "kinetics"]
---

::section{#intro}
::meta
type: introduction
summary: "Overview of temperature effects on heterogeneous catalysis"
::

# Introduction

The relationship between temperature and catalytic activity follows
the Arrhenius equation $k = A e^{-E_a / RT}$, where $E_a$ is the
activation energy and $R$ is the gas constant.

::endsection

::section{#results}
::meta
type: results
summary: "Experimental measurements of conversion rates at 5 temperatures"
depends_on: ["#methods"]
::

# Results

::chart{#fig-conversion}
::interpretation
Conversion rate increases linearly between 200–350°C, reaching a
plateau at 89% above 400°C. The inflection point at 350°C suggests
a change in the rate-limiting step.
::
| Temperature (°C) | Conversion (%) | Selectivity (%) |
|---|---|---|
| 200 | 23.1 | 95.2 |
| 250 | 41.7 | 93.8 |
| 300 | 62.4 | 91.1 |
| 350 | 78.9 | 87.3 |
| 400 | 89.2 | 82.6 |
::endchart

::endsection
```

## Project Structure

```
scimd/
├── scimd_parser.py          # Reference parser in Python
├── scimd_validator.py       # Validation tool
├── SPECIFICATION.md         # Full format specification (v0.1.0)
├── AUTHORING_GUIDE.md       # How to write SciMD documents
├── RAG_GUIDE.md             # How to use SciMD for RAG pipelines
├── full-paper.smd           # Complete scientific paper example
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Python packaging (pip install pyscimd)
├── documentation/           # Supplementary docs (format, parser, validator)
├── tests/                   # Test suite
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## Getting Started

### Writing a Document

Any text editor works. Save your file with the `.smd` extension and follow the [Authoring Guide](AUTHORING_GUIDE.md).

### Validating a Document

```bash
pip install pyscimd
scimd-validate my-paper.smd
```

### Parsing for RAG

```python
from scimd_parser import SciMDParser

doc = SciMDParser.parse("my-paper.smd")

# Get semantically chunked sections
for section in doc.sections:
    print(section.id, section.summary)
    print(section.content)

# Extract all chart data as structured records
for chart in doc.charts:
    print(chart.interpretation)
    print(chart.as_dict_list)   # list of dicts, one per row
```

## For the Scientific Community

SciMD is built to serve researchers, not platforms:

- **No proprietary tools required** — write in VS Code, Vim, Notepad, anything
- **Version control friendly** — plain text diffs cleanly in Git
- **Citation ready** — structured metadata maps to BibTeX, CSL, and DOI
- **Multilingual** — UTF-8 native, `lang` metadata per document and section
- **Accessible** — mandatory descriptions make content accessible by design

## Roadmap

- [x] v0.1.0 — Core specification
- [x] v0.2.0 — Reference parser + validator (Python, available as `pyscimd` on PyPI)
- [ ] v0.3.0 — VS Code extension with live preview
- [ ] v0.4.0 — Pandoc filter for PDF/HTML/DOCX export
- [ ] v0.5.0 — LLM training pipeline toolkit
- [ ] v1.0.0 — Stable specification after community review

## Contributing

We welcome contributions from researchers, developers, and anyone who cares about making knowledge more accessible. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Author

SciMD was created by **Juan Francisco Avilés Calderón**.

## License

MIT — Use it, fork it, improve it.

---

*SciMD: Because science deserves better than screenshots of spreadsheets.*
