"""Tests for R003: Unused variable definitions."""

from __future__ import annotations

from pathlib import Path

from prompt_lint.parser import parse, parse_file
from prompt_lint.rules.variable_unused import VariableUnusedRule


class TestVariableUnused:
    def setup_method(self) -> None:
        self.rule = VariableUnusedRule()

    def test_all_used(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0

    def test_unused_variables(self, unused_variable: Path) -> None:
        doc = parse_file(str(unused_variable))
        diagnostics = self.rule.check(doc)
        unused_names = [d.message for d in diagnostics]
        assert any("age" in m for m in unused_names)
        assert any("unused_field" in m for m in unused_names)
        assert len(diagnostics) == 2

    def test_rule_id(self) -> None:
        assert self.rule.rule_id == "R003"

    def test_severity_is_warning(self, unused_variable: Path) -> None:
        from prompt_lint.models import Severity

        doc = parse_file(str(unused_variable))
        diagnostics = self.rule.check(doc)
        assert all(d.severity == Severity.WARNING for d in diagnostics)

    def test_used_in_constraints(self) -> None:
        content = (
            "---\nname: t\ndescription: d\nversion: '1'\n---\n\n"
            "# Role\nR\n\n# Input\n- `x`: string (required) - x\n\n"
            "# Output\n- **r**: r\n\n"
            "# Constraints\n{{x}} must be > 0\n\n"
            "# Steps\n1. Check constraints"
        )
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0
