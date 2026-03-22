"""
SciMD Parser — Usage Examples

Run this script from the scimd/ root directory:

    python examples.py

Each example is self-contained. All examples use papertest.smd,
which is included in the repository and covers every SciMD element type.
"""

from pathlib import Path
from scimd_parser import SciMDParser as smm

SMD_FILE = Path(__file__).parent / "benchmark-paper/papertest.smd"


def separator(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


# ──────────────────────────────────────────────────────────────
# 1. Parse a file
# ──────────────────────────────────────────────────────────────

separator("1. Parse a .smd file")

doc = smm.parse(SMD_FILE)
print(f"Title   : {doc.title}")
print(f"Authors : {', '.join(a.name for a in doc.authors)}")
print(f"Date    : {doc.date}")
print(f"Lang    : {doc.lang}")
print(f"Keywords: {', '.join(doc.keywords)}")
print(f"Abstract: {doc.abstract.strip()[:120]}...")


# ──────────────────────────────────────────────────────────────
# 2. Iterate sections
# ──────────────────────────────────────────────────────────────

separator("2. Iterate sections")

for section in doc.sections:
    deps = f" <- {', '.join(section.depends_on)}" if section.depends_on else ""
    print(f"  [{section.type:12}] #{section.id}{deps}")
    print(f"               summary: {section.summary}")


# ──────────────────────────────────────────────────────────────
# 3. Get a section by ID
# ──────────────────────────────────────────────────────────────

separator("3. Get a section by ID")

results = doc.get_section("#results")
if results:
    print(f"Section  : {results.title}")
    print(f"Type     : {results.type}")
    print(f"Charts   : {len(results.charts)}")
    print(f"Figures  : {len(results.figures)}")
    print(f"Equations: {len(results.equations)}")


# ──────────────────────────────────────────────────────────────
# 4. Access charts and tabular data
# ──────────────────────────────────────────────────────────────

separator("4. Charts — tabular data and interpretation")

for chart in doc.charts:
    print(f"Chart #{chart.id}: {chart.title}")
    print(f"  Interpretation: {chart.interpretation[:80]}...")
    print(f"  Columns: {chart.headers}")
    print(f"  Rows as dicts:")
    for row in chart.as_dict_list:
        print(f"    {row}")


# ──────────────────────────────────────────────────────────────
# 5. Access figures
# ──────────────────────────────────────────────────────────────

separator("5. Figures - description and interpretation")

for fig in doc.figures:
    print(f"Figure #{fig.id}")
    print(f"  File           : {fig.file}")
    print(f"  Description    : {fig.description[:100]}...")
    print(f"  Interpretation : {fig.interpretation[:100]}...")


# ──────────────────────────────────────────────────────────────
# 6. Access equations
# ──────────────────────────────────────────────────────────────

separator("6. Equations — LaTeX and semantic label")

for eq in doc.equations:
    print(f"Equation #{eq.id}")
    print(f"  LaTeX : {eq.latex[:80]}")
    print(f"  Label : {eq.label}")


# ──────────────────────────────────────────────────────────────
# 7. Access diagrams (Mermaid)
# ──────────────────────────────────────────────────────────────

separator("7. Diagrams — Mermaid code")

for diag in doc.diagrams:
    print(f"Diagram #{diag.id} (type: {diag.type})")
    print(f"  Description  : {diag.description[:80]}...")
    print(f"  Mermaid code :")
    for line in diag.mermaid_code.splitlines()[:6]:
        print(f"    {line}")


# ──────────────────────────────────────────────────────────────
# 8. Dependency graph
# ──────────────────────────────────────────────────────────────

separator("8. Section dependency graph")

graph = doc.dependency_graph()
for section_id, deps in graph.items():
    arrow = f" → {', '.join(deps)}" if deps else " (root)"
    print(f"  #{section_id}{arrow}")


# ──────────────────────────────────────────────────────────────
# 9. Export RAG chunks
# ──────────────────────────────────────────────────────────────

separator("9. to_rag_chunks() — RAG-ready export")

chunks = doc.to_rag_chunks()
print(f"Total chunks: {len(chunks)}\n")

for chunk in chunks:
    meta = chunk["metadata"]
    flags = []
    if meta["has_charts"]:    flags.append("charts")
    if meta["has_figures"]:   flags.append("figures")
    if meta["has_equations"]: flags.append("equations")
    flag_str = f" [{', '.join(flags)}]" if flags else ""
    print(f"  id      : {chunk['id']}")
    print(f"  type    : {chunk['section_type']}{flag_str}")
    print(f"  summary : {chunk['summary']}")
    print(f"  content : {len(chunk['content'])} chars")
    if chunk["depends_on"]:
        print(f"  deps    : {chunk['depends_on']}")
    print()


# ──────────────────────────────────────────────────────────────
# 10. Build training text
# ──────────────────────────────────────────────────────────────

separator("10. build_training_text() — LLM fine-tuning export")

training = doc.build_training_text(include_metadata=True)
print(f"Total length: {len(training)} chars\n")
print(training[:600])
print("\n... (truncated)")

separator("10b. Without metadata header")

bare = doc.build_training_text(include_metadata=False)
print(bare[:400])
print("\n... (truncated)")


# ──────────────────────────────────────────────────────────────
# 11. Parse from string
# ──────────────────────────────────────────────────────────────

separator("11. Parse from a raw string")

INLINE_SMD = """\
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
summary: "A minimal single-section document."
::

# Introduction

This is a minimal SciMD document parsed from a Python string.

::endsection
"""

mini_doc = smm.parse(INLINE_SMD)
print(f"Title   : {mini_doc.title}")
print(f"Authors : {', '.join(a.name for a in mini_doc.authors)}")
print(f"Sections: {len(mini_doc.sections)}")
print(f"Content : {mini_doc.sections[0].content}")
