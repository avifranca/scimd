import pytest
from pathlib import Path

from tests.conftest import FIXTURE


def test_parse_returns_document(doc):
    assert doc is not None


def test_document_has_title(doc):
    # The fixture is a paper about perovskite solar cells
    assert doc.title and isinstance(doc.title, str) and len(doc.title) > 10


def test_document_has_authors(doc):
    assert len(doc.authors) >= 1


def test_document_has_sections(doc):
    assert len(doc.sections) >= 1


def test_sections_have_unique_ids(doc):
    ids = [s.id for s in doc.sections]
    assert len(ids) == len(set(ids)), "Section IDs must be unique"


def test_rag_chunks_not_empty(doc):
    chunks = doc.to_rag_chunks()
    assert len(chunks) >= 1


def test_rag_chunks_have_required_keys(doc):
    chunks = doc.to_rag_chunks()
    required_keys = {"id", "content", "section_id", "section_type", "summary", "title", "depends_on", "metadata"}
    for chunk in chunks:
        missing = required_keys - set(chunk.keys())
        assert not missing, f"Chunk missing keys: {missing}"


def test_rag_chunk_metadata_is_correct_type(doc):
    chunks = doc.to_rag_chunks()
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        assert isinstance(meta, dict), "metadata must be a dict"


def test_parse_string_input(doc, raw_text):
    from scimd_parser import SciMDParser
    doc_from_string = SciMDParser.parse(raw_text)
    assert doc_from_string is not None
    assert doc_from_string.title == doc.title
    assert len(doc_from_string.sections) == len(doc.sections)


def test_parse_nonexistent_file_raises(doc):
    from scimd_parser import SciMDParser
    with pytest.raises((FileNotFoundError, OSError)):
        SciMDParser.parse("/nonexistent/path/file.smd")


def test_parse_empty_string_returns_document():
    from scimd_parser import SciMDParser
    # parse("") returns an empty SciMDDocument rather than raising
    result = SciMDParser.parse("")
    assert result is not None
    assert result.title == ""
    assert result.sections == []


def test_get_section_by_id(doc):
    """get_section should find sections by ID (with or without leading #)."""
    # Get the first section's ID from the parsed doc
    first_id = doc.sections[0].id
    section = doc.get_section(first_id)
    assert section is not None
    assert section.id == first_id


def test_get_section_with_hash_prefix(doc):
    """get_section should strip leading # from the id argument."""
    first_id = doc.sections[0].id
    section_with_hash = doc.get_section(f"#{first_id}")
    section_without_hash = doc.get_section(first_id)
    assert section_with_hash is not None
    assert section_with_hash.id == section_without_hash.id


def test_get_section_unknown_id_returns_none(doc):
    section = doc.get_section("nonexistent_section_id_xyz")
    assert section is None


def test_dependency_graph_returns_dict(doc):
    graph = doc.dependency_graph()
    assert isinstance(graph, dict)


def test_dependency_graph_contains_section_ids(doc):
    graph = doc.dependency_graph()
    for section in doc.sections:
        assert section.id in graph


# ──────────────────────────────────────────────
# Tests for equation inlining (Priority 1 fix)
# ──────────────────────────────────────────────

def test_text_content_includes_equations(doc):
    """text_content must inline equations — the benchmark-identified gap."""
    sections_with_equations = [s for s in doc.sections if s.equations]
    assert sections_with_equations, "Fixture must have at least one section with equations"

    for section in sections_with_equations:
        tc = section.text_content
        for eq in section.equations:
            assert eq.latex in tc, (
                f"Equation #{eq.id} LaTeX not found in text_content of section #{section.id}. "
                f"text_content should inline equations so RAG chunks contain the full quantitative content."
            )


def test_text_content_includes_equation_labels(doc):
    """text_content must include equation labels when present."""
    sections_with_equations = [s for s in doc.sections if s.equations]
    for section in sections_with_equations:
        tc = section.text_content
        for eq in section.equations:
            if eq.label:
                assert eq.label in tc, (
                    f"Equation #{eq.id} label '{eq.label}' not found in text_content of "
                    f"section #{section.id}."
                )


def test_text_content_includes_callouts(doc):
    """Callout content must appear in text_content so it reaches RAG chunks."""
    sections_with_callouts = [s for s in doc.sections if s.callouts]
    if not sections_with_callouts:
        pytest.skip("Fixture has no callouts — adjust if a future fixture includes them")

    for section in sections_with_callouts:
        tc = section.text_content
        for callout in section.callouts:
            if callout.content:
                # At minimum, the callout content text should appear
                assert callout.content[:30] in tc, (
                    f"Callout content not found in text_content of section #{section.id}"
                )


def test_rag_chunks_content_contains_equations(doc):
    """RAG chunks must carry equation LaTeX in their content field."""
    chunks = doc.to_rag_chunks()
    # Build a mapping section_id -> chunk
    chunk_by_section = {c["section_id"]: c for c in chunks}

    sections_with_equations = [s for s in doc.sections if s.equations]
    assert sections_with_equations, "Fixture must have sections with equations"

    for section in sections_with_equations:
        chunk = chunk_by_section.get(section.id)
        assert chunk is not None, f"No RAG chunk for section #{section.id}"
        for eq in section.equations:
            assert eq.latex in chunk["content"], (
                f"Equation #{eq.id} LaTeX missing from RAG chunk content for section #{section.id}. "
                f"This would cause retrieval failures for queries referencing the equation."
            )


# ──────────────────────────────────────────────
# Tests for build_training_text()
# ──────────────────────────────────────────────

def test_section_build_training_text_returns_string(doc):
    """Section.build_training_text() must return a non-empty string."""
    for section in doc.sections:
        result = section.build_training_text()
        assert isinstance(result, str), f"build_training_text returned {type(result)} for #{section.id}"
        assert len(result) > 0, f"build_training_text returned empty string for #{section.id}"


def test_section_build_training_text_includes_equations(doc):
    """Section.build_training_text() must include equation LaTeX."""
    sections_with_equations = [s for s in doc.sections if s.equations]
    assert sections_with_equations, "Fixture must have sections with equations"

    for section in sections_with_equations:
        tt = section.build_training_text()
        for eq in section.equations:
            assert eq.latex in tt, (
                f"Equation #{eq.id} LaTeX not in build_training_text() for section #{section.id}"
            )


def test_document_build_training_text_returns_string(doc):
    """SciMDDocument.build_training_text() must return a non-empty string."""
    result = doc.build_training_text()
    assert isinstance(result, str)
    assert len(result) > 100, "Full-document training text should be substantial"


def test_document_build_training_text_contains_title(doc):
    """Document-level build_training_text() must include the document title."""
    result = doc.build_training_text(include_metadata=True)
    assert doc.title in result, "Document title should appear in training text metadata header"


def test_document_build_training_text_no_metadata(doc):
    """build_training_text(include_metadata=False) must omit the metadata header."""
    with_meta = doc.build_training_text(include_metadata=True)
    without_meta = doc.build_training_text(include_metadata=False)
    # Without metadata should be shorter (no title/author/date header)
    assert len(without_meta) < len(with_meta), (
        "include_metadata=False should produce shorter output than include_metadata=True"
    )


def test_document_build_training_text_includes_all_section_content(doc):
    """build_training_text() must contain prose from every section."""
    full_text = doc.build_training_text()
    for section in doc.sections:
        # At minimum, the first meaningful sentence of section.content must appear
        prose = section.content.strip()
        if prose:
            # Use first 40 chars as a fingerprint
            snippet = prose[:40]
            assert snippet in full_text, (
                f"Section #{section.id} prose not found in document build_training_text()"
            )
