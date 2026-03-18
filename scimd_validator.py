"""
SciMD Validator — Validates .smd documents against the specification.

Usage:
    python scimd_validator.py paper.smd
    python scimd_validator.py paper.smd --strict
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from scimd_parser import SciMDParser, SciMDDocument


@dataclass
class ValidationIssue:
    level: Literal["error", "warning", "info"]
    code: str
    message: str
    location: str = ""

    def __str__(self):
        loc = f" @ {self.location}" if self.location else ""
        return f"[{self.level.upper()}] {self.code}{loc}: {self.message}"


class SciMDValidator:
    """Validates SciMD documents against the v0.1.0 specification."""

    VALID_SECTION_TYPES = {
        "introduction", "methods", "results", "discussion",
        "conclusion", "appendix", "literature-review", "custom",
    }
    VALID_CALLOUT_TYPES = {
        "note", "warning", "important", "tip", "example", "definition",
    }
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.issues: list[ValidationIssue] = []

    def validate(self, source: str | Path) -> list[ValidationIssue]:
        """Validate a SciMD document. Returns list of issues found."""
        self.issues = []

        # Parse the document
        try:
            doc = SciMDParser.parse(source)
        except Exception as e:
            self.issues.append(ValidationIssue(
                level="error",
                code="PARSE_FAIL",
                message=f"Failed to parse document: {e}",
            ))
            return self.issues

        # Also read raw text for structural validation
        if isinstance(source, (str, Path)) and str(source).endswith(".smd"):
            raw = Path(source).read_text(encoding="utf-8")
        else:
            raw = source if isinstance(source, str) else ""

        self._validate_header(doc, raw)
        self._validate_sections(doc)
        self._validate_charts(doc)
        self._validate_figures(doc, source)
        self._validate_diagrams(doc)
        self._validate_equations(doc)
        self._validate_references(doc)
        self._validate_structure(raw)

        return sorted(self.issues, key=lambda i: (
            {"error": 0, "warning": 1, "info": 2}[i.level]
        ))

    def _add(self, level: str, code: str, msg: str, loc: str = ""):
        self.issues.append(ValidationIssue(level=level, code=code, message=msg, location=loc))

    def _validate_header(self, doc: SciMDDocument, raw: str):
        """Validate document header / frontmatter."""
        if not raw.startswith("---smd"):
            self._add("error", "HDR001", "Document must begin with '---smd' frontmatter")

        if not doc.title:
            self._add("error", "HDR002", "Missing required field: title")

        if not doc.authors:
            self._add("error", "HDR003", "At least one author is required")
        else:
            for i, author in enumerate(doc.authors):
                if not author.name:
                    self._add("error", "HDR004", f"Author #{i+1} missing name")
                if self.strict and not author.orcid:
                    self._add("warning", "HDR005",
                              f"Author '{author.name}' has no ORCID", "header")

        if not doc.version:
            self._add("error", "HDR006", "Missing required field: version")

        if not doc.lang:
            self._add("error", "HDR007", "Missing required field: lang")

        if not doc.abstract:
            self._add("warning", "HDR008", "No abstract provided (recommended)")

        if not doc.keywords:
            self._add("info", "HDR009", "No keywords provided")

    def _validate_sections(self, doc: SciMDDocument):
        """Validate section structure and metadata."""
        if not doc.sections:
            self._add("error", "SEC001", "Document has no sections")
            return

        seen_ids = set()
        for section in doc.sections:
            loc = f"section#{section.id}"

            # Unique IDs
            if section.id in seen_ids:
                self._add("error", "SEC002",
                          f"Duplicate section ID: #{section.id}", loc)
            seen_ids.add(section.id)

            # Valid ID format
            if not re.match(r"^[\w-]+$", section.id):
                self._add("error", "SEC003",
                          f"Invalid section ID format: #{section.id}", loc)

            # Required type
            if not section.type:
                self._add("error", "SEC004", "Missing section type", loc)
            elif section.type not in self.VALID_SECTION_TYPES:
                self._add("warning", "SEC005",
                          f"Non-standard section type: '{section.type}'", loc)

            # Required summary
            if not section.summary:
                self._add("error", "SEC006", "Missing section summary", loc)

            # Validate dependencies exist
            for dep in section.depends_on:
                dep_id = dep.lstrip("#")
                if dep_id not in {s.id for s in doc.sections}:
                    self._add("warning", "SEC007",
                              f"Dependency '{dep}' not found", loc)

            # Check for title
            if not section.title:
                self._add("info", "SEC008",
                          "Section has no heading title", loc)

    def _validate_charts(self, doc: SciMDDocument):
        """Validate chart elements."""
        seen_ids = set()
        for chart in doc.charts:
            loc = f"chart#{chart.id}"

            if chart.id in seen_ids:
                self._add("error", "CHT001",
                          f"Duplicate chart ID: #{chart.id}", loc)
            seen_ids.add(chart.id)

            if not chart.interpretation:
                self._add("error", "CHT002",
                          "Chart missing mandatory interpretation", loc)

            if not chart.rows and not chart.data_file:
                self._add("warning", "CHT003",
                          "Chart has no tabular data or data-file reference. "
                          "Ensure interpretation is comprehensive.", loc)

            if chart.headers:
                # Check for units in headers
                headers_with_units = sum(
                    1 for h in chart.headers if "(" in h and ")" in h
                )
                if headers_with_units < len(chart.headers) * 0.5:
                    self._add("info", "CHT004",
                              "Consider adding units to column headers", loc)

                # Check consistent row lengths
                for i, row in enumerate(chart.rows):
                    if len(row) != len(chart.headers):
                        self._add("warning", "CHT005",
                                  f"Row {i+1} has {len(row)} columns, "
                                  f"expected {len(chart.headers)}", loc)

    def _validate_figures(self, doc: SciMDDocument, source):
        """Validate figure elements."""
        seen_ids = set()
        for fig in doc.figures:
            loc = f"figure#{fig.id}"

            if fig.id in seen_ids:
                self._add("error", "FIG001",
                          f"Duplicate figure ID: #{fig.id}", loc)
            seen_ids.add(fig.id)

            if not fig.description:
                self._add("error", "FIG002",
                          "Figure missing mandatory description", loc)

            if not fig.interpretation:
                self._add("error", "FIG003",
                          "Figure missing mandatory interpretation", loc)

            # Check image file exists (if source is a file path)
            if fig.file and isinstance(source, (str, Path)):
                source_path = Path(source) if str(source).endswith(".smd") else None
                if source_path:
                    img_path = source_path.parent / fig.file
                    if not img_path.exists():
                        self._add("warning", "FIG004",
                                  f"Image file not found: {fig.file}", loc)

                    ext = Path(fig.file).suffix.lower()
                    if ext not in self.IMAGE_EXTENSIONS:
                        self._add("warning", "FIG005",
                                  f"Unsupported image format: {ext}", loc)

    def _validate_diagrams(self, doc: SciMDDocument):
        """Validate diagram elements."""
        seen_ids = set()
        for diag in doc.diagrams:
            loc = f"diagram#{diag.id}"

            if diag.id in seen_ids:
                self._add("error", "DGM001",
                          f"Duplicate diagram ID: #{diag.id}", loc)
            seen_ids.add(diag.id)

            if not diag.description:
                self._add("error", "DGM002",
                          "Diagram missing mandatory description", loc)

            if not diag.mermaid_code:
                self._add("error", "DGM003",
                          "Diagram missing MermaidJS code", loc)

    def _validate_equations(self, doc: SciMDDocument):
        """Validate equation elements."""
        seen_ids = set()
        for eq in doc.equations:
            loc = f"equation#{eq.id}"

            if eq.id in seen_ids:
                self._add("error", "EQN001",
                          f"Duplicate equation ID: #{eq.id}", loc)
            seen_ids.add(eq.id)

            if not eq.latex:
                self._add("error", "EQN002", "Equation has no LaTeX", loc)

            if not eq.label:
                self._add("info", "EQN003", "Equation has no label", loc)

            # Basic LaTeX syntax checks
            if eq.latex:
                opens = eq.latex.count("{")
                closes = eq.latex.count("}")
                if opens != closes:
                    self._add("warning", "EQN004",
                              f"Mismatched braces: {opens} open, {closes} close", loc)

    def _validate_references(self, doc: SciMDDocument):
        """Validate references and citations."""
        ref_ids = {r.id for r in doc.references}

        # Collect all citations used in sections
        all_citations = set()
        for section in doc.sections:
            for cite_str in section.citations:
                for cid in cite_str.split(","):
                    all_citations.add(cid.strip())

        # Check for undefined citations
        for cite_id in all_citations:
            if cite_id not in ref_ids:
                self._add("warning", "REF001",
                          f"Citation @cite{{{cite_id}}} not found in references")

        # Check for unused references
        if self.strict:
            for ref in doc.references:
                if ref.id not in all_citations:
                    self._add("info", "REF002",
                              f"Reference '{ref.id}' defined but never cited")

    def _validate_structure(self, raw: str):
        """Validate raw text structure."""
        # Check for unclosed blocks
        block_pairs = [
            ("::section{", "::endsection"),
            ("::chart{", "::endchart"),
            ("::figure{", "::endfigure"),
            ("::diagram{", "::enddiagram"),
            ("::equation{", "::endequation"),
            ("::callout{", "::endcallout"),
        ]
        for opener, closer in block_pairs:
            opens = raw.count(opener)
            closes = raw.count(closer)
            if opens != closes:
                self._add("error", "STR001",
                          f"Mismatched blocks: {opens}x '{opener}' vs {closes}x '{closer}'")

    def print_report(self):
        """Print a formatted validation report."""
        errors = [i for i in self.issues if i.level == "error"]
        warnings = [i for i in self.issues if i.level == "warning"]
        infos = [i for i in self.issues if i.level == "info"]

        if not self.issues:
            print("✅ Document is valid!")
            return

        for issue in self.issues:
            symbol = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[issue.level]
            print(f"  {symbol} {issue}")

        print()
        print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info(s)")

        if errors:
            print("❌ Document has validation errors.")
        elif warnings:
            print("⚠️  Document is valid with warnings.")
        else:
            print("✅ Document is valid.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scimd_validator.py <file.smd> [--strict]")
        sys.exit(1)

    filepath = sys.argv[1]
    strict = "--strict" in sys.argv

    print(f"Validating: {filepath}")
    print(f"Mode: {'strict' if strict else 'standard'}")
    print("-" * 50)

    validator = SciMDValidator(strict=strict)
    validator.validate(filepath)
    validator.print_report()

    # Exit code: 1 if errors, 0 otherwise
    errors = [i for i in validator.issues if i.level == "error"]
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
