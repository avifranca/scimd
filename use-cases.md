# SciMD Use Cases

End-to-end workflows for the four main contexts where SciMD delivers measurable advantages over PDF, XML, or plain Markdown.

---

## 1. RAG Knowledge Base over Scientific Literature

**Goal:** Build a retrieval system that can answer precise questions about a corpus of papers with low hallucination risk.

**The problem with alternatives:**
- PDF-MD: Broken sentences and missing figure descriptions mean retrieved chunks are noisy. Models fill gaps with confabulation.
- JATS XML: Rich structure, but 72% tag overhead degrades embedding quality; chunks overflow context windows.
- Plain Markdown: No semantic boundaries — arbitrary token-window chunking splits mid-thought.

**The SciMD pipeline:**

```
.smd files  →  SciMDParser  →  RAG chunks  →  vector store  →  LLM
```

Each chunk produced by `to_rag_chunks()` is self-contained and carries full context:

```python
from scimd_parser import SciMDParser
import chromadb   # or any vector store

client = chromadb.Client()
collection = client.create_collection("papers")

for smd_path in paper_paths:
    doc = SciMDParser.parse(smd_path)
    for chunk in doc.to_rag_chunks():
        collection.add(
            ids=[f"{doc.metadata.title}::{chunk['section_id']}"],
            documents=[chunk["content"]],
            metadatas=[{
                "title":      doc.metadata.title,
                "section":    chunk["section_id"],
                "type":       chunk["type"],           # "methods", "results", …
                "summary":    chunk["summary"],        # one-line section description
                "depends_on": str(chunk["depends_on"]),
                "keywords":   ", ".join(doc.metadata.keywords),
                "year":       str(doc.metadata.date),
            }]
        )
```

**Dependency-aware retrieval:**

When a user asks about results, the `depends_on` field tells you which methods section to co-retrieve:

```python
def retrieve_with_context(query: str, collection, top_k: int = 3):
    results = collection.query(query_texts=[query], n_results=top_k)
    chunks = results["metadatas"][0]

    # Expand: also fetch sections this chunk depends on
    context_sections = set()
    for chunk in chunks:
        context_sections.add(chunk["section"])
        for dep in chunk["depends_on"].strip("[]'").split(", "):
            if dep:
                context_sections.add(dep.strip("'#"))

    return context_sections  # fetch full content for each
```

**Benchmark result:** SciMD parsed RAG chunks score **9.6/10** LLM comprehension and **Very Low** hallucination risk. Each paper fits in **~4K tokens** — within a single 4K context window, or 8 papers in a 32K window.

---

## 2. LLM Fine-Tuning Corpus

**Goal:** Build a large, clean scientific training corpus for instruction tuning or continued pre-training.

**The problem with alternatives:**
- PDF-MD: PDF conversion artifacts are random and vary by converter — HTML anchors, merged lines, missing formulas. Noise is baked in at the character level and cannot be fully cleaned.
- JATS XML: At ~32K tokens per paper, processing a corpus of 100K papers costs 3.2 billion tokens. Parsed SciMD cuts this to 500 million — a **6.4× compute savings**.
- LaTeX source: Compilation artifacts, layout commands, and unresolved cross-references require extensive preprocessing per paper.

**The SciMD training pipeline:**

```python
from scimd_parser import SciMDParser
import json, pathlib, random

def build_corpus(smd_dir: str, output_path: str):
    samples = []

    for path in pathlib.Path(smd_dir).rglob("*.smd"):
        try:
            doc = SciMDParser.parse(str(path))
        except Exception as e:
            print(f"Skipping {path}: {e}")
            continue

        # Full-paper training text (~5K tokens, zero markup)
        samples.append({
            "text": doc.build_training_text(),
            "source": str(path),
            "license": doc.metadata.license,
            "keywords": doc.metadata.keywords,
        })

        # Section-level samples for section-type classification
        for section in doc.sections:
            samples.append({
                "text": section.content,
                "label": section.type,
                "summary": section.summary,
            })

    # Shuffle at section level for augmentation
    random.shuffle(samples)

    with open(output_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"Wrote {len(samples)} samples to {output_path}")

build_corpus("papers/", "training_corpus.jsonl")
```

**License-aware filtering:**

The `license` field in the YAML header allows automatic corpus filtering by rights:

```python
OPEN_LICENSES = {"CC-BY-4.0", "CC-BY-SA-4.0", "CC0-1.0", "MIT"}

def is_training_eligible(doc) -> bool:
    return doc.metadata.license in OPEN_LICENSES
```

**Instruction tuning pairs:**

SciMD's section summaries enable automatic generation of instruction pairs:

```python
for section in doc.sections:
    yield {
        "instruction": f"Summarize the {section.type} section of this paper.",
        "input": section.content,
        "output": section.summary,
    }
```

**Benchmark result:** Parsed SciMD training text scores **8.4/10** overall for fine-tuning suitability — the highest of any format — at **~5K tokens per paper** vs ~12K for raw MD and ~32K for XML.

---

## 3. Academic Paper Authoring

**Goal:** Write a scientific paper in a format that is simultaneously human-readable, Git-friendly, and immediately ready for AI pipelines — without a conversion step.

**Who this is for:**
- Researchers who want their papers to be AI-accessible by default
- Labs building internal knowledge bases from their own output
- Journals and preprint servers wanting structured submissions
- Authors submitting to venues that accept multiple output formats (PDF via Pandoc, HTML, JATS)

**Authoring workflow:**

```
Write .smd  →  scimd-validate  →  peer review  →  scimd-to-pdf (Pandoc)
                                                 →  scimd-to-html
                                                 →  scimd-to-jats (for submission)
```

**Advantages over writing in LaTeX:**

| | LaTeX | SciMD |
|---|---|---|
| Compilation required | Yes (`pdflatex` × 3) | No |
| Git diff readability | Poor (macros, commands) | Excellent (plain text) |
| Figure captions | Text string only | Rich description + interpretation |
| Chart data | `\includegraphics` | Embedded tabular data |
| Metadata | Preamble macros | Structured YAML |
| AI-ready out of the box | ❌ | ✅ |

**Starting a new paper:**

```bash
# Create a new paper from a template
cp template.smd my-paper.smd

# Edit in any text editor
code my-paper.smd

# Validate structure before submission
scimd-validate my-paper.smd

# Export to PDF (requires Pandoc filter — coming in v0.4.0)
# pandoc my-paper.smd -o my-paper.pdf --filter scimd-pandoc
```

**Version control:**

Because `.smd` is plain UTF-8 text, every revision is a clean diff:

```diff
-summary: "Degradation at 80% RH occurs after 24 hours."
+summary: "Degradation at 80% RH occurs within 6 hours per revised protocol."

-| 80% RH | 8.3  |
+| 80% RH | 3.1  |
```

Compare this to a binary `.docx` or `.pdf` where the same change produces an unreadable binary diff.

---

## 4. Scientific AI Assistants

**Goal:** Build a domain-specific AI assistant that can answer questions about a paper or corpus with accurate citations, formula handling, and low hallucination.

**Architecture:**

```
User query
    ↓
Semantic search over RAG chunks (section summaries as query expansion)
    ↓
Dependency-aware context assembly (fetch depends_on sections)
    ↓
LLM prompt with self-contained context
    ↓
Answer with @cite{key} resolved from YAML references
```

**Minimal working example:**

```python
from scimd_parser import SciMDParser
from openai import OpenAI   # or any LLM client

def answer_question(smd_path: str, question: str) -> str:
    doc = SciMDParser.parse(smd_path)
    chunks = doc.to_rag_chunks()

    # Simple keyword-based retrieval (replace with vector search for production)
    relevant = [c for c in chunks if any(
        word.lower() in c["content"].lower()
        for word in question.split()
    )]

    if not relevant:
        relevant = chunks[:2]   # fallback to intro + methods

    context = "\n\n---\n\n".join(
        f"[{c['type'].upper()} — {c['summary']}]\n{c['content']}"
        for c in relevant
    )

    references = "\n".join(
        f"- [{ref['id']}] {', '.join(ref['authors'][:2])} ({ref['year']}). {ref['title']}."
        for ref in doc.metadata.references
    )

    prompt = f"""You are a scientific assistant. Answer using only the provided context.
Cite sources as @cite{{key}} when referencing specific claims.

CONTEXT:
{context}

REFERENCES:
{references}

QUESTION: {question}

ANSWER:"""

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Example usage
answer = answer_question(
    "mock-examples/sparse_attention_optimization.smd",
    "At what sequence length does the sparse kernel outperform dense attention?"
)
print(answer)
# → "The sparse kernel begins to outperform FlashAttention-2 at sequence
#    lengths ≥ 16k tokens @cite{rossi2026sparse}, achieving 1.67× speedup
#    at 16,384 and 2.55× at 65,536 tokens."
```

**What makes SciMD-powered assistants better:**

| Capability | PDF-MD source | SciMD source |
|---|---|---|
| Cite a specific equation | ❌ Image, no label | ✅ `@ref{#eq-sparse-attn}` → full LaTeX + label |
| Describe a figure | ❌ Broken `![]` ref | ✅ `::description` + `::interpretation` |
| Read chart values | ❌ Image or lost in PDF | ✅ Markdown table in `::chart` block |
| Know section dependencies | ❌ Must read whole paper | ✅ `depends_on` per section |
| Filter by license | ❌ Must read paper text | ✅ `license:` field in YAML |
| Fit in 4K context | ❌ ~12K tokens raw | ✅ ~4K tokens parsed |

---

## 5. Open-Access Publishing Infrastructure

**Goal:** Offer a structured submission format that generates both human-readable and machine-readable outputs from a single source file.

**Single source, multiple outputs (v0.4.0+):**

```
author submits paper.smd
        ↓
┌───────────────────────────────────┐
│         SciMD Pipeline            │
├──────────┬──────────┬─────────────┤
│ PDF      │ HTML     │ JATS XML    │
│ (Pandoc) │ (static) │ (for PubMed)│
└──────────┴──────────┴─────────────┘
        ↓
Metadata index (title, DOI, keywords, license, authors)
        ↓
Semantic search index (RAG chunks per paper)
```

**Structured metadata for discovery:**

Every `.smd` submission provides a machine-readable record for indexing without scraping:

```yaml
citation:
  doi: "10.1234/example"
  bibtex: |
    @article{garcia2026,
      title={...},
      author={Garcia, Maria},
      doi={10.1234/example},
      year={2026}
    }
```

This maps directly to DataCite, CrossRef, and OpenAlex schemas — no metadata normalization step.

---

## Choosing the Right Pipeline

| You want to… | Recommended pipeline |
|---|---|
| Answer questions about a paper | `to_rag_chunks()` → vector store → LLM |
| Fine-tune a model on scientific text | `build_training_text()` → JSONL corpus |
| Write a new paper | Author `.smd` → `scimd-validate` → Pandoc export |
| Build a search index | YAML frontmatter → metadata index + chunk summaries for embeddings |
| Generate citation graphs | `references` YAML → DOI resolution → graph DB |
| Check open-access rights at scale | `license` field → automated corpus filtering |

---

*See [`docs/examples.md`](examples.md) for annotated code snippets, or [`full-paper.smd`](../full-paper.smd) for a complete paper demonstrating all elements.*
