# SciMD for RAG Pipelines

How to integrate SciMD documents into Retrieval-Augmented Generation systems.

## Why SciMD Improves RAG

Traditional RAG pipelines struggle with scientific documents because:

1. **Chunking is arbitrary** — splitting by token count breaks semantic units
2. **Charts are invisible** — embedded images carry no retrievable text
3. **Context is lost** — a results paragraph without its methods is misleading
4. **Metadata is absent** — no way to filter by section type, topic, or author

SciMD solves all four problems by design.

## Chunking Strategy

### Natural chunks

Each `::section` is a natural semantic chunk with built-in metadata:

```python
from scimd_parser import SciMDParser

doc = SciMDParser.parse("paper.smd")

for section in doc.sections:
    chunk = {
        "text": section.text_content,   # Prose + interpretations
        "summary": section.summary,      # For retrieval ranking
        "type": section.type,            # For filtering
        "depends_on": section.depends_on # For context expansion
    }
    # Index in your vector store
    index_chunk(chunk)
```

### Sub-section chunks

For very long sections, split at heading boundaries within the section
while preserving the section metadata as context.

### Chart-aware chunks

Charts generate two types of retrievable content:

```python
for chart in doc.charts:
    # Chunk 1: Interpretation (natural language, good for semantic search)
    index_chunk({
        "text": chart.interpretation,
        "type": "chart_interpretation",
        "chart_id": chart.id,
    })

    # Chunk 2: Tabular data (good for structured queries)
    index_chunk({
        "text": chart.raw_table,
        "type": "chart_data",
        "chart_id": chart.id,
        "headers": chart.headers,
    })
```

## Context Expansion

Use `depends_on` to pull in related sections when retrieving:

```python
def retrieve_with_context(query, doc, top_k=3):
    # Standard retrieval
    results = vector_search(query, top_k=top_k)

    # Expand with dependencies
    expanded = set()
    for result in results:
        section = doc.get_section(result["section_id"])
        if section:
            for dep_id in section.depends_on:
                dep = doc.get_section(dep_id)
                if dep:
                    expanded.add(dep.id)

    # Fetch dependency sections
    context_sections = [doc.get_section(sid) for sid in expanded]
    return results, context_sections
```

## Quick Export

Use the built-in `to_rag_chunks()` method:

```python
doc = SciMDParser.parse("paper.smd")
chunks = doc.to_rag_chunks()

# Each chunk contains:
# - id: unique identifier
# - section_id, section_type, summary
# - content: full text with interpretations
# - metadata: authors, keywords, date, etc.

for chunk in chunks:
    your_vector_store.upsert(
        id=chunk["id"],
        text=chunk["content"],
        metadata=chunk["metadata"],
    )
```

## Metadata Filtering

SciMD metadata enables powerful filtered retrieval:

```python
# Only search in results sections
results = vector_search(query, filter={"section_type": "results"})

# Only papers by specific author
results = vector_search(query, filter={"authors": {"$contains": "García"}})

# Only sections with charts
results = vector_search(query, filter={"has_charts": True})
```

## Reducing Hallucinations

SciMD provides three layers of hallucination defense:

1. **Author interpretations** ground chart/figure understanding
2. **Section summaries** provide concise, author-verified descriptions
3. **Structured data** eliminates the need to "read" images

When building prompts from retrieved SciMD chunks, always include
the interpretation text — it's the author's ground truth.

## Integration Examples

### LangChain

```python
from langchain.schema import Document

doc = SciMDParser.parse("paper.smd")
lc_docs = [
    Document(
        page_content=chunk["content"],
        metadata=chunk["metadata"],
    )
    for chunk in doc.to_rag_chunks()
]
```

### LlamaIndex

```python
from llama_index.core import Document

doc = SciMDParser.parse("paper.smd")
li_docs = [
    Document(
        text=chunk["content"],
        metadata=chunk["metadata"],
        id_=chunk["id"],
    )
    for chunk in doc.to_rag_chunks()
]
```
