# SciMD Authoring Guide

How to write documents in SciMD format.

## Getting Started

A SciMD document is a plain text file with the `.smd` extension. You can write
it in any text editor — VS Code, Vim, Notepad, or even Google Docs (export as
plain text).

### Minimum Viable Document

```markdown
---smd
title: "My First SciMD Document"
authors:
  - name: "Your Name"
version: "0.1.0"
lang: "en"
---

::section{#main}
::meta
type: introduction
summary: "A brief introduction to the topic"
::

# Hello, SciMD

This is a valid SciMD document. It uses standard Markdown
for formatting, with added structure for AI comprehension.

::endsection
```

## Document Header

Every document starts with a YAML header between `---smd` and `---`:

```yaml
---smd
title: "Your Paper Title"
authors:
  - name: "First Author"
    orcid: "0000-0000-0000-0000"
    affiliation: "Your University"
    email: "you@example.com"
    corresponding: true
  - name: "Second Author"
    affiliation: "Other Institution"
version: "0.1.0"
lang: "en"
date: "2026-03-17"
keywords: ["keyword1", "keyword2"]
abstract: |
  Your abstract goes here. Use the pipe (|) for multi-line text.
---
```

**Required fields**: `title`, `authors` (with at least `name`), `version`, `lang`

## Writing Sections

Organize your content into flat, semantic sections:

```markdown
::section{#my-section-id}
::meta
type: results
summary: "One sentence describing what this section contains"
depends_on: ["#methods"]
::

# Your Section Heading

Your content here, using standard Markdown...

::endsection
```

### Section types

Use one of: `introduction`, `methods`, `results`, `discussion`, `conclusion`,
`appendix`, `literature-review`, or `custom`.

### Why summaries matter

The `summary` field is the single most important line for RAG systems. Write it
as if answering: *"If someone searched for this section, what query would match?"*

Good: `"Experimental measurements of catalyst conversion rates at five temperatures"`
Bad: `"Results"`

## Adding Charts

Instead of pasting a screenshot of your spreadsheet, provide the actual data:

```markdown
::chart{#my-chart}
::title Optional title for the chart
::interpretation
Describe what the data shows. What are the trends? What's significant?
This is mandatory — it's the key to eliminating AI hallucinations.
Write as if explaining the chart to a colleague who can't see it.
::
| X Value | Y Value | Category |
|---|---|---|
| 1.0 | 23.5 | A |
| 2.0 | 45.1 | A |
| 3.0 | 67.8 | B |
::endchart
```

**Tips for good chart data:**
- Include units in column headers: `Temperature (°C)`
- Use consistent decimal places
- Include error bars or uncertainties where applicable

## Adding Figures

Every image needs both a description (what it shows) and an interpretation
(what it means):

```markdown
::figure{#my-figure}
::file path/to/image.png
::description
Objective description: What is physically visible in this image?
Describe layouts, colors, labels, spatial relationships.
::
::interpretation
Author's analysis: Why is this figure important? What should the
reader understand from it?
::
::endfigure
```

**Why two separate blocks?** A description says "there are three peaks at
450nm, 520nm, and 680nm." An interpretation says "these peaks correspond
to chlorophyll absorption bands, confirming the presence of algal biomass."
AI systems need both to avoid inventing their own explanations.

## Adding Diagrams

Use MermaidJS syntax with a plain-language description:

```markdown
::diagram{#my-diagram}
::type flowchart
::description
Plain English description of the diagram. What entities exist?
What are the relationships? What process does this represent?
::
` ` `mermaid
graph TD
    A[Step 1] --> B[Step 2]
    B --> C[Step 3]
` ` `
::enddiagram
```

## Math and Equations

**Inline**: Use single dollar signs: `The energy $E = mc^2$ is fundamental.`

**Block equations** with labels:

```markdown
::equation{#eq-my-equation}
$$
\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}
$$
::label Gauss's law for electric fields
::endequation
```

Reference equations with `@ref{#eq-my-equation}`.

## Citations

Define references in the header, cite them inline:

```yaml
# In the header:
references:
  - id: "smith2024"
    type: "article"
    authors: ["Smith, J."]
    title: "Paper Title"
    journal: "Journal Name"
    year: 2024
    doi: "10.1234/example"
```

```markdown
# In the text:
According to Smith @cite{smith2024}, the effect is significant.
```

## Cross-References

Reference any labeled element:

```markdown
As shown in @ref{#chart-params}, the trend is clear.
Using @ref{#eq-arrhenius}, we calculate...
See @ref{#intro} for background.
```

## Validation

Run the validator to check your document:

```bash
python scimd_validator.py my-paper.smd
python scimd_validator.py my-paper.smd --strict
```

## Best Practices

1. **Write summaries first** — Draft all section summaries before writing content
2. **Be generous with interpretations** — More context = fewer hallucinations
3. **Use data tables over descriptions** — Structured data is always better
4. **Keep sections focused** — One topic per section, 500–2000 words
5. **Declare dependencies** — If section B needs section A to make sense, say so
6. **Include units everywhere** — In headers, equations, and prose
7. **Version your documents** — Use `date` and consider semantic versioning
