"""Tests for the validation engine."""

from __future__ import annotations

from pathlib import Path

from prompt_lint.models import Severity
from prompt_lint.parser import parse_file
from prompt_lint.validator import validate


class TestValidateIntegration:
    def test_valid_file_no_errors(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        diagnostics = validate(doc)
        errors = [d for d in diagnostics if d.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_valid_file_no_warnings(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        diagnostics = validate(doc)
        warnings = [d for d in diagnostics if d.severity == Severity.WARNING]
        assert len(warnings) == 0

    def test_multiple_issues_detected(self, undefined_variable: Path) -> None:
        doc = parse_file(str(undefined_variable))
        diagnostics = validate(doc)
        rule_ids = {d.rule_id for d in diagnostics}
        assert "R002" in rule_ids

    def test_diagnostics_sorted_by_line(self, undefined_variable: Path) -> None:
        doc = parse_file(str(undefined_variable))
        diagnostics = validate(doc)
        lines = [d.position.line for d in diagnostics]
        assert lines == sorted(lines)

    def test_japanese_headings_valid(self, japanese_headings: Path) -> None:
        doc = parse_file(str(japanese_headings))
        diagnostics = validate(doc)
        errors = [d for d in diagnostics if d.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_example_files_validate(self) -> None:
        """Example files should pass validation cleanly."""
        examples_dir = Path(__file__).parent.parent / "examples"
        for prompt_file in examples_dir.glob("*.prompt.md"):
            doc = parse_file(str(prompt_file))
            diagnostics = validate(doc)
            errors = [d for d in diagnostics if d.severity == Severity.ERROR]
            assert len(errors) == 0, (
                f"{prompt_file.name} has errors: "
                + "; ".join(d.message for d in errors)
            )
