# SciMD Parser — Usage Examples

All examples use [`mock_document.smd`](../mock_document.smd), a sample paper that covers every SciMD element type. Run the companion script to see live output:

```bash
python examples.py
```

---

## 1. Parse a file

```python
from scimd_parser import SciMDParser

doc = SciMDParser.parse("mock_document.smd")

print(doc.title)       # "Quantum Flux Dynamics in Synthetic Lattices"
print(doc.date)        # "2026-03-19"
print(doc.keywords)    # ["quantum mechanics", "synthetic lattices", ...]
print(doc.abstract)    # Full abstract string from YAML frontmatter
```

You can also pass a `Path` object or a raw SMD string — see [example 11](#11-parse-from-a-string).

---

## 2. Iterate sections

Each section carries its type, a hand-written summary, and its dependency list:

```python
for section in doc.sections:
    print(section.id)        # "intro", "methods", "results", ...
    print(section.type)      # "introduction" | "methods" | "results" | ...
    print(section.summary)   # Human-written summary from ::meta block
    print(section.depends_on)  # e.g. ["#methods"]
    print(section.title)     # First heading found in the section body
```

---

## 3. Get a section by ID

```python
results = doc.get_section("#results")   # leading # is optional

print(results.title)          # "Experimental Results"
print(len(results.charts))    # 1
print(len(results.figures))   # 1
print(len(results.equations)) # 0
```

---

## 4. Charts — tabular data and interpretation

Charts expose their data both as raw markdown and as a list of dicts for programmatic use:

```python
for chart in doc.charts:                  # or: results.charts for one section
    print(chart.title)                    # "Flux Stability Measurements"
    print(chart.interpretation)           # Human-written explanation of the data
    print(chart.headers)                  # ["Depth (Er)", "Stability Index", ...]
    print(chart.rows)                     # [["5", "0.92", "±0.01"], ...]

    for row in chart.as_dict_list:        # structured access
        print(row)
        # {"Depth (Er)": "5", "Stability Index": "0.92", "Error Margin": "±0.01"}
```

---

## 5. Figures — description and interpretation

Figures include a textual `description` of the visual content and an `interpretation` of its scientific meaning. An LLM can fully reason about figures without seeing the image:

```python
for fig in doc.figures:
    print(fig.id)              # "fig-pattern"
    print(fig.file)            # "assets/interference-pattern.png"
    print(fig.description)     # What the figure visually shows
    print(fig.interpretation)  # What it scientifically means
```

---

## 6. Equations — LaTeX and semantic label

```python
for eq in doc.equations:
    print(eq.id)     # "eq-hamiltonian"
    print(eq.latex)  # "H = -t \sum_{\langle i,j \rangle} ..."
    print(eq.label)  # "The Hubbard Model with Complex Hopping"
```

The `label` is a plain-language description of what the equation represents — useful as retrieval metadata.

---

## 7. Diagrams — Mermaid code

```python
for diag in doc.diagrams:
    print(diag.id)           # "diag-setup"
    print(diag.type)         # "flowchart"
    print(diag.description)  # Plain-text description of the diagram
    print(diag.mermaid_code) # Raw Mermaid source, ready to render
```

---

## 8. Section dependency graph

```python
graph = doc.dependency_graph()
# {
#   "intro":      [],
#   "methods":    ["#intro"],
#   "results":    ["#methods"],
#   "conclusion": ["#results"],
# }
```

Use this to build a retrieval chain: when returning a `results` chunk, you know `methods` is a prerequisite context.

---

## 9. Export RAG chunks

`to_rag_chunks()` converts the document into a list of JSON-serialisable dicts, one per section, with all metadata pre-computed:

```python
import json

chunks = doc.to_rag_chunks()
print(json.dumps(chunks[0], indent=2))
```

Each chunk looks like:

```json
{
  "id": "Quantum Flux Dynamics::intro",
  "section_id": "intro",
  "section_type": "introduction",
  "summary": "Overview of synthetic lattice research and document objectives.",
  "title": "Introduction",
  "content": "<prose + inlined figure descriptions + equations>",
  "depends_on": [],
  "metadata": {
    "document_title": "Quantum Flux Dynamics in Synthetic Lattices",
    "authors": ["Alice J. Smith", "Bob R. Miller"],
    "lang": "en",
    "keywords": ["quantum mechanics", "synthetic lattices", "flux dynamics"],
    "date": "2026-03-19",
    "has_charts": false,
    "has_figures": false,
    "has_equations": true,
    "citations": ["smith2024"]
  }
}
```

The `content` field already has figures, charts, equations, and callouts inlined — no post-processing needed before embedding.

---

## 10. Build training text

`build_training_text()` produces a single string for LLM fine-tuning, with every element merged into a coherent prose stream:

```python
# With metadata header (default)
text = doc.build_training_text()

# Without header — bare training text only
text = doc.build_training_text(include_metadata=False)
```

You can also call it per-section:

```python
section = doc.get_section("results")
text = section.build_training_text()
# Prose + chart interpretations + figure descriptions + equations — all merged
```

---

## 11. Parse from a string

Useful for testing or dynamic document generation:

```python
SMD = """\
---smd
title: "Minimal Example"
authors:
  - name: "Jane Doe"
version: "0.1.0"
lang: "en"
---

::section{#intro}
::meta
type: introduction
summary: "A one-section demo."
::

# Introduction

Parsed from a Python string, no file needed.

::endsection
"""

doc = SciMDParser.parse(SMD)
print(doc.title)                        # "Minimal Example"
print(doc.sections[0].content)          # "# Introduction\n\nParsed from..."
```

---

## Document-level convenience properties

```python
doc.charts     # All Chart objects across all sections
doc.figures    # All Figure objects across all sections
doc.diagrams   # All Diagram objects across all sections
doc.equations  # All Equation objects across all sections
```

---

## CLI quick reference

```bash
# Summary view
python scimd_parser.py paper.smd

# RAG chunks as JSON
python scimd_parser.py paper.smd --rag-chunks

# Full document as JSON
python scimd_parser.py paper.smd --json

# Training text
python scimd_parser.py paper.smd --training-text
python scimd_parser.py paper.smd --training-text --no-metadata
```
