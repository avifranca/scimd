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
