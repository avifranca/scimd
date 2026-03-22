# SciMD Documentation

Welcome to the official documentation for **SciMD** (Scientific Markdown), an open document format designed for AI-native research and scientific data exchange.

## 📚 Guides

- **[Format Specification](format.md)**: Learn the `.smd` syntax, including semantic sections, mandatory interpretations, and structured assets.
- **[Python Parser](parser.md)**: Documentation for the reference implementation (`scimd_parser.py`) for reading and processing SciMD files.
- **[Validator Tool](validator.md)**: How to use `scimd_validator.py` to ensure your documents adhere to the specification.

## 🛠 Project Purpose

SciMD solves the problem of "printing-first" formats (like PDF) by providing:
- **Author-time structure**: Meaning is defined when writing, not reverse-engineered.
- **Data over pixels**: Charts are tables, diagrams are code, formulas are LaTeX.
- **Mandatory interpretation**: Every visual element carries a textual explanation to prevent AI hallucinations.

## 🚀 Quick Start

To parse a SciMD file and export it to JSON:
```bash
python3 scimd_parser.py paper.smd --json
```

To validate a document:
```bash
python3 scimd_validator.py paper.smd
```
