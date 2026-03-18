import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

FIXTURE = Path(__file__).parent.parent / "full-paper.smd"


@pytest.fixture(scope="session")
def raw_text():
    """Raw .smd file content as a string."""
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def doc():
    """Parsed SciMDDocument. SESSION-SCOPED — do NOT mutate fields in tests."""
    from scimd_parser import SciMDParser
    return SciMDParser.parse(str(FIXTURE))


@pytest.fixture(scope="session")
def validator_issues():
    from scimd_validator import SciMDValidator
    v = SciMDValidator()
    return v.validate(str(FIXTURE))
