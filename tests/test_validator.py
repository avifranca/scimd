import pytest
from pathlib import Path

from tests.conftest import FIXTURE


def test_validator_returns_list(validator_issues):
    assert isinstance(validator_issues, list)


def test_valid_document_has_no_errors(validator_issues):
    errors = [i for i in validator_issues if i.level == "error"]
    assert len(errors) == 0, f"Unexpected errors: {[f'{i.code}: {i.message}' for i in errors]}"


def test_strict_mode_runs_without_exception():
    from scimd_validator import SciMDValidator
    validator = SciMDValidator(strict=True)
    issues = validator.validate(str(FIXTURE))
    assert isinstance(issues, list)


def test_issue_objects_have_required_attributes(validator_issues):
    for issue in validator_issues:
        assert hasattr(issue, "level")
        assert hasattr(issue, "code")
        assert hasattr(issue, "message")
        assert hasattr(issue, "location")
        assert issue.level in ("error", "warning", "info")


def test_validator_empty_input_returns_errors():
    from scimd_validator import SciMDValidator
    v = SciMDValidator()
    issues = v.validate("")
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) > 0, "Empty document should produce at least one error"


def test_strict_mode_produces_at_least_as_many_issues(validator_issues):
    from scimd_validator import SciMDValidator
    v_strict = SciMDValidator(strict=True)
    strict_issues = v_strict.validate(str(FIXTURE))
    # Strict mode must produce >= issues than non-strict
    assert len(strict_issues) >= len(validator_issues), (
        f"Strict mode ({len(strict_issues)}) should not produce fewer issues "
        f"than normal mode ({len(validator_issues)})"
    )
