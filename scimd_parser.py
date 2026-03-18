"""
SciMD Parser — Reference implementation for the SciMD format.

Parses .smd files into structured Python objects optimized for
RAG pipelines, LLM training, and document analysis.

Usage:
    from scimd_parser import SciMDParser

    doc = SciMDParser.parse("paper.smd")
    for section in doc.sections:
        print(section.id, section.summary)
"""

from __future__ import annotations

import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ──────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────

@dataclass
class Author:
    name: str
    orcid: Optional[str] = None
    affiliation: Optional[str] = None
    email: Optional[str] = None
    corresponding: bool = False


@dataclass
class Reference:
    id: str
    type: str
    authors: list[str] = field(default_factory=list)
    title: str = ""
    year: Optional[int] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    url: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None


@dataclass
class Chart:
    id: str
    title: Optional[str] = None
    interpretation: str = ""
    source: Optional[str] = None
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    data_file: Optional[str] = None
    raw_table: str = ""

    @property
    def as_dict_list(self) -> list[dict]:
        """Return tabular data as a list of dictionaries."""
        if not self.headers or not self.rows:
            return []
        return [dict(zip(self.headers, row)) for row in self.rows]


@dataclass
class Figure:
    id: str
    file: Optional[str] = None
    description: str = ""
    interpretation: str = ""
    source: Optional[str] = None


@dataclass
class Diagram:
    id: str
    type: str = "custom"
    description: str = ""
    mermaid_code: str = ""


@dataclass
class Equation:
    id: str
    latex: str = ""
    label: str = ""


@dataclass
class Callout:
    type: str
    content: str = ""


@dataclass
class Section:
    id: str
    type: str = "custom"
    summary: str = ""
    depends_on: list[str] = field(default_factory=list)
    lang: Optional[str] = None
    title: Optional[str] = None
    content: str = ""
    charts: list[Chart] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    diagrams: list[Diagram] = field(default_factory=list)
    equations: list[Equation] = field(default_factory=list)
    callouts: list[Callout] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)

    @property
    def text_content(self) -> str:
        """Return plain text content with interpretations inlined."""
        parts = [self.content]
        for chart in self.charts:
            if chart.interpretation:
                parts.append(f"[Chart {chart.id}]: {chart.interpretation}")
        for fig in self.figures:
            if fig.description:
                parts.append(f"[Figure {fig.id}]: {fig.description}")
            if fig.interpretation:
                parts.append(f"[Figure {fig.id} interpretation]: {fig.interpretation}")
        for diag in self.diagrams:
            if diag.description:
                parts.append(f"[Diagram {diag.id}]: {diag.description}")
        return "\n\n".join(parts)


@dataclass
class SciMDDocument:
    title: str = ""
    authors: list[Author] = field(default_factory=list)
    version: str = "0.1.0"
    lang: str = "en"
    date: Optional[str] = None
    license: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    abstract: Optional[str] = None
    references: list[Reference] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    custom_metadata: dict = field(default_factory=dict)

    @property
    def charts(self) -> list[Chart]:
        """All charts across all sections."""
        return [c for s in self.sections for c in s.charts]

    @property
    def figures(self) -> list[Figure]:
        """All figures across all sections."""
        return [f for s in self.sections for f in s.figures]

    @property
    def diagrams(self) -> list[Diagram]:
        """All diagrams across all sections."""
        return [d for s in self.sections for d in s.diagrams]

    @property
    def equations(self) -> list[Equation]:
        """All equations across all sections."""
        return [e for s in self.sections for e in s.equations]

    def get_section(self, section_id: str) -> Optional[Section]:
        """Get a section by its ID."""
        clean_id = section_id.lstrip("#")
        for s in self.sections:
            if s.id == clean_id:
                return s
        return None

    def dependency_graph(self) -> dict[str, list[str]]:
        """Return section dependency graph as adjacency list."""
        return {s.id: s.depends_on for s in self.sections}

    def to_rag_chunks(self) -> list[dict]:
        """
        Export document as RAG-ready chunks.
        Each section becomes a chunk with metadata.
        """
        chunks = []
        for section in self.sections:
            chunk = {
                "id": f"{self.title}::{section.id}",
                "section_id": section.id,
                "section_type": section.type,
                "summary": section.summary,
                "title": section.title or "",
                "content": section.text_content,
                "depends_on": section.depends_on,
                "metadata": {
                    "document_title": self.title,
                    "authors": [a.name for a in self.authors],
                    "lang": section.lang or self.lang,
                    "keywords": self.keywords,
                    "date": self.date,
                    "has_charts": len(section.charts) > 0,
                    "has_figures": len(section.figures) > 0,
                    "has_equations": len(section.equations) > 0,
                    "citations": section.citations,
                },
            }
            chunks.append(chunk)
        return chunks


# ──────────────────────────────────────────────
# Parser
# ──────────────────────────────────────────────

class SciMDParser:
    """Reference parser for SciMD (.smd) documents."""

    # Regex patterns
    HEADER_PATTERN = re.compile(r"^---smd\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)
    SECTION_PATTERN = re.compile(
        r"::section\{#([\w-]+)\}(.*?)::endsection",
        re.DOTALL,
    )
    META_PATTERN = re.compile(r"::meta\s*\n(.*?)::", re.DOTALL)
    CHART_PATTERN = re.compile(
        r"::chart\{#([\w-]+)\}(.*?)::endchart",
        re.DOTALL,
    )
    FIGURE_PATTERN = re.compile(
        r"::figure\{#([\w-]+)\}(.*?)::endfigure",
        re.DOTALL,
    )
    DIAGRAM_PATTERN = re.compile(
        r"::diagram\{#([\w-]+)\}(.*?)::enddiagram",
        re.DOTALL,
    )
    EQUATION_PATTERN = re.compile(
        r"::equation\{#([\w-]+)\}(.*?)::endequation",
        re.DOTALL,
    )
    CALLOUT_PATTERN = re.compile(
        r'::callout\{type="([\w-]+)"\}\s*\n(.*?)::endcallout',
        re.DOTALL,
    )
    INTERPRETATION_PATTERN = re.compile(r"::interpretation\s*\n(.*?)::", re.DOTALL)
    DESCRIPTION_PATTERN = re.compile(r"::description\s*\n(.*?)::", re.DOTALL)
    TITLE_PATTERN = re.compile(r"::title\s+(.+)")
    SOURCE_PATTERN = re.compile(r'::source\s+(?:"([^"]+)"|(.+))')
    FILE_PATTERN = re.compile(r"::file\s+(.+)")
    TYPE_PATTERN = re.compile(r"::type\s+(.+)")
    LABEL_PATTERN = re.compile(r"::label\s+(.+)")
    DATA_FILE_PATTERN = re.compile(r"::data-file\s+(.+)")
    TABLE_PATTERN = re.compile(
        r"(\|.+\|\s*\n\|[-| :]+\|\s*\n(?:\|.+\|\s*\n?)+)",
        re.MULTILINE,
    )
    CITATION_PATTERN = re.compile(r"@cite\{([^}]+)\}")
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    BLOCK_MATH_PATTERN = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)

    @classmethod
    def parse(cls, source: str | Path) -> SciMDDocument:
        """
        Parse a SciMD document from a file path or string.

        Args:
            source: Path to .smd file or raw string content.

        Returns:
            SciMDDocument with all parsed elements.
        """
        if isinstance(source, Path) or (isinstance(source, str) and (
            source.endswith(".smd") and "\n" not in source
        )):
            path = Path(source)
            text = path.read_text(encoding="utf-8")
        else:
            text = source

        doc = SciMDDocument()

        # Parse header
        cls._parse_header(text, doc)

        # Parse sections
        cls._parse_sections(text, doc)

        return doc

    @classmethod
    def _parse_header(cls, text: str, doc: SciMDDocument) -> None:
        """Extract and parse YAML frontmatter."""
        match = cls.HEADER_PATTERN.search(text)
        if not match:
            return

        try:
            header = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return

        if not isinstance(header, dict):
            return

        doc.title = header.get("title", "")
        doc.version = header.get("version", "0.1.0")
        doc.lang = header.get("lang", "en")
        doc.date = header.get("date")
        doc.license = header.get("license")
        doc.keywords = header.get("keywords", [])
        doc.abstract = header.get("abstract")
        doc.custom_metadata = header.get("custom", {})

        # Parse authors
        for author_data in header.get("authors", []):
            if isinstance(author_data, str):
                doc.authors.append(Author(name=author_data))
            elif isinstance(author_data, dict):
                doc.authors.append(Author(
                    name=author_data.get("name", ""),
                    orcid=author_data.get("orcid"),
                    affiliation=author_data.get("affiliation"),
                    email=author_data.get("email"),
                    corresponding=author_data.get("corresponding", False),
                ))

        # Parse references
        for ref_data in header.get("references", []):
            if isinstance(ref_data, dict):
                doc.references.append(Reference(
                    id=ref_data.get("id", ""),
                    type=ref_data.get("type", "article"),
                    authors=ref_data.get("authors", []),
                    title=ref_data.get("title", ""),
                    year=ref_data.get("year"),
                    doi=ref_data.get("doi"),
                    journal=ref_data.get("journal"),
                    url=ref_data.get("url"),
                    publisher=ref_data.get("publisher"),
                    isbn=ref_data.get("isbn"),
                ))

    @classmethod
    def _parse_sections(cls, text: str, doc: SciMDDocument) -> None:
        """Parse all semantic sections."""
        for match in cls.SECTION_PATTERN.finditer(text):
            section_id = match.group(1)
            section_body = match.group(2)

            section = Section(id=section_id)

            # Parse meta block
            meta_match = cls.META_PATTERN.search(section_body)
            if meta_match:
                meta_text = meta_match.group(1)
                for line in meta_text.strip().split("\n"):
                    line = line.strip()
                    if line.startswith("type:"):
                        section.type = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("summary:"):
                        section.summary = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("depends_on:"):
                        deps_str = line.split(":", 1)[1].strip()
                        try:
                            section.depends_on = yaml.safe_load(deps_str) or []
                        except yaml.YAMLError:
                            section.depends_on = []
                    elif line.startswith("lang:"):
                        section.lang = line.split(":", 1)[1].strip().strip('"')

            # Extract section title from first heading
            heading_match = cls.HEADING_PATTERN.search(section_body)
            if heading_match:
                section.title = heading_match.group(2).strip()

            # Parse charts
            for chart_match in cls.CHART_PATTERN.finditer(section_body):
                chart = cls._parse_chart(chart_match)
                section.charts.append(chart)

            # Parse figures
            for fig_match in cls.FIGURE_PATTERN.finditer(section_body):
                figure = cls._parse_figure(fig_match)
                section.figures.append(figure)

            # Parse diagrams
            for diag_match in cls.DIAGRAM_PATTERN.finditer(section_body):
                diagram = cls._parse_diagram(diag_match)
                section.diagrams.append(diagram)

            # Parse equations
            for eq_match in cls.EQUATION_PATTERN.finditer(section_body):
                equation = cls._parse_equation(eq_match)
                section.equations.append(equation)

            # Parse callouts
            for callout_match in cls.CALLOUT_PATTERN.finditer(section_body):
                section.callouts.append(Callout(
                    type=callout_match.group(1),
                    content=callout_match.group(2).strip(),
                ))

            # Extract citations
            section.citations = cls.CITATION_PATTERN.findall(section_body)

            # Clean content — remove structural blocks, keep prose
            content = section_body
            # Remove meta block
            content = cls.META_PATTERN.sub("", content)
            # Remove chart/figure/diagram/equation blocks (their content is in dedicated objects)
            content = cls.CHART_PATTERN.sub("", content)
            content = cls.FIGURE_PATTERN.sub("", content)
            content = cls.DIAGRAM_PATTERN.sub("", content)
            content = cls.EQUATION_PATTERN.sub("", content)
            content = cls.CALLOUT_PATTERN.sub("", content)
            # Clean up whitespace
            content = re.sub(r"\n{3,}", "\n\n", content).strip()
            section.content = content

            doc.sections.append(section)

    @classmethod
    def _parse_chart(cls, match: re.Match) -> Chart:
        chart_id = match.group(1)
        body = match.group(2)
        chart = Chart(id=chart_id)

        title_m = cls.TITLE_PATTERN.search(body)
        if title_m:
            chart.title = title_m.group(1).strip()

        interp_m = cls.INTERPRETATION_PATTERN.search(body)
        if interp_m:
            chart.interpretation = interp_m.group(1).strip()

        source_m = cls.SOURCE_PATTERN.search(body)
        if source_m:
            chart.source = (source_m.group(1) or source_m.group(2)).strip()

        data_file_m = cls.DATA_FILE_PATTERN.search(body)
        if data_file_m:
            chart.data_file = data_file_m.group(1).strip()

        # Parse markdown table
        table_m = cls.TABLE_PATTERN.search(body)
        if table_m:
            chart.raw_table = table_m.group(0).strip()
            lines = chart.raw_table.split("\n")
            if len(lines) >= 2:
                # Headers
                chart.headers = [
                    cell.strip() for cell in lines[0].split("|")
                    if cell.strip()
                ]
                # Data rows (skip separator line)
                for line in lines[2:]:
                    row = [cell.strip() for cell in line.split("|") if cell.strip()]
                    if row:
                        chart.rows.append(row)

        return chart

    @classmethod
    def _parse_figure(cls, match: re.Match) -> Figure:
        fig_id = match.group(1)
        body = match.group(2)
        figure = Figure(id=fig_id)

        file_m = cls.FILE_PATTERN.search(body)
        if file_m:
            figure.file = file_m.group(1).strip()

        desc_m = cls.DESCRIPTION_PATTERN.search(body)
        if desc_m:
            figure.description = desc_m.group(1).strip()

        interp_m = cls.INTERPRETATION_PATTERN.search(body)
        if interp_m:
            figure.interpretation = interp_m.group(1).strip()

        source_m = cls.SOURCE_PATTERN.search(body)
        if source_m:
            figure.source = (source_m.group(1) or source_m.group(2)).strip()

        return figure

    @classmethod
    def _parse_diagram(cls, match: re.Match) -> Diagram:
        diag_id = match.group(1)
        body = match.group(2)
        diagram = Diagram(id=diag_id)

        type_m = cls.TYPE_PATTERN.search(body)
        if type_m:
            diagram.type = type_m.group(1).strip()

        desc_m = cls.DESCRIPTION_PATTERN.search(body)
        if desc_m:
            diagram.description = desc_m.group(1).strip()

        mermaid_m = cls.MERMAID_PATTERN.search(body)
        if mermaid_m:
            diagram.mermaid_code = mermaid_m.group(1).strip()

        return diagram

    @classmethod
    def _parse_equation(cls, match: re.Match) -> Equation:
        eq_id = match.group(1)
        body = match.group(2)
        equation = Equation(id=eq_id)

        math_m = cls.BLOCK_MATH_PATTERN.search(body)
        if math_m:
            equation.latex = math_m.group(1).strip()

        label_m = cls.LABEL_PATTERN.search(body)
        if label_m:
            equation.label = label_m.group(1).strip()

        return equation

    @classmethod
    def parse_file(cls, path: str | Path) -> SciMDDocument:
        """Convenience alias for parse() with a file path."""
        return cls.parse(Path(path))


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scimd_parser.py <file.smd> [--rag-chunks | --json]")
        sys.exit(1)

    filepath = sys.argv[1]
    doc = SciMDParser.parse_file(filepath)

    if "--rag-chunks" in sys.argv:
        chunks = doc.to_rag_chunks()
        print(json.dumps(chunks, indent=2, ensure_ascii=False))
    elif "--json" in sys.argv:
        # Full document structure as JSON
        import dataclasses

        def to_serializable(obj):
            if dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)
            return str(obj)

        data = dataclasses.asdict(doc)
        print(json.dumps(data, indent=2, ensure_ascii=False, default=to_serializable))
    else:
        # Summary view
        print(f"Title: {doc.title}")
        print(f"Authors: {', '.join(a.name for a in doc.authors)}")
        print(f"Version: {doc.version} | Lang: {doc.lang}")
        print(f"Sections: {len(doc.sections)}")
        print(f"Charts: {len(doc.charts)} | Figures: {len(doc.figures)} | "
              f"Diagrams: {len(doc.diagrams)} | Equations: {len(doc.equations)}")
        print()
        for section in doc.sections:
            deps = f" (depends: {', '.join(section.depends_on)})" if section.depends_on else ""
            print(f"  [{section.type}] #{section.id}: {section.summary}{deps}")


if __name__ == "__main__":
    main()
