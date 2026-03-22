# SciMD Format Specification (v0.1.0)

SciMD (`.smd`) is a plain-text document format that extends Markdown with structures optimized for AI comprehension and scientific data preservation.

## 1. Document Structure

A SciMD document consists of three layers:
1.  **Header**: YAML frontmatter (`---smd` ... `---`).
2.  **Sections**: Semantic containers (`::section` ... `::endsection`).
3.  **Assets**: Rich elements (Charts, Figures, Diagrams, Equations).

---

## 2. Document Header

Every file must start with:

```yaml
---smd
title: "Document Title"
authors:
  - name: "Author Name"
    orcid: "0000-0000-0000-0000"
version: "0.1.0"
lang: "en"
---
```

---

## 3. Semantic Sections

Content must be flat and organized into sections with unique IDs.

```markdown
::section{#introduction}
::meta
type: introduction
summary: "Quick summary for RAG indexing"
::

# Introduction
Your markdown content here...

::endsection
```

### Supported Types
`introduction`, `methods`, `results`, `discussion`, `conclusion`, `appendix`, `custom`.

---

## 4. Rich Assets

### Charts
Instead of images, we provide data tables + interpretations.
```markdown
::chart{#results-table}
::interpretation
Detailed explanation of trends and findings.
::
| Variable | Value |
|---|---|
| A | 10 |
::endchart
```

### Figures
Requires both a factual description and an analytical interpretation.
```markdown
::figure{#microscope-view}
::file images/fig1.png
::description Visual description (what is seen).
::interpretation Analytical significance (what it means).
::endfigure
```

### Diagrams
Supports **MermaidJS** code directly.
```markdown
::diagram{#process-flow}
::description Description of the logic.
```mermaid
graph LR
  A --> B
```
::enddiagram
```

### Equations
Uses standard **LaTeX**.
```markdown
::equation{#eq-1}
$$ E = mc^2 $$
::label Einstein's energy-mass equivalence
::endequation
```

---

## 5. Citations

Citations use the `@cite{key}` syntax, which maps to the `references` list in the document header.

```markdown
As seen in previous studies @cite{smith2024}...
```
