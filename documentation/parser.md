# SciMD Python Parser (`scimd_parser.py`)

The reference implementation for parsing SciMD (.smd) files into structured Python objects for RAG, training, and data analysis.

## 🐍 API Usage

The parser provides a simple interface to load and process documents.

### Basic Parsing
```python
from scimd_parser import SciMDParser

# Parse a file
doc = SciMDParser.parse("my-paper.smd")

print(f"Title: {doc.title}")
print(f"Authors: {[a.name for a in doc.authors]}")
```

### Working with Sections
Documents are organized into `Section` objects.
```python
for section in doc.sections:
    print(section.id, section.summary)
    # The 'text_content' property inlines author interpretations
    print(section.text_content)
```

### Extracting Data (Charts)
```python
for chart in doc.charts:
    print(chart.interpretation)
    # Access table rows and headers
    print(chart.headers)
    print(chart.rows)
    # Convert to list of dicts
    data = chart.as_dict_list
```

### RAG Chunking
The `SciMDDocument` class includes a built-in method for generating chunks optimized for vector databases.
```python
chunks = doc.to_rag_chunks()
# Returns a list of dicts with 'content', 'summary', and 'metadata'
```

---

## 💻 CLI Usage

You can also use the parser as a command-line tool:

### Summarize a Document
```bash
python3 scimd_parser.py paper.smd
```

### Export to JSON
```bash
python3 scimd_parser.py paper.smd --json
```

### Export RAG Chunks
```bash
python3 scimd_parser.py paper.smd --rag-chunks
```

---

## 🏗 Data Model

- **`SciMDDocument`**: The root object containing metadata, sections, and references.
- **`Section`**: A semantic block of content with its own ID, type, and summary.
- **`Author`**: Metadata about a document creator.
- **`Chart`**, **`Figure`**, **`Diagram`**, **`Equation`**: Structured asset objects.
