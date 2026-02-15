"""Tests for R002: Undefined variable references."""

from __future__ import annotations

from pathlib import Path

from prompt_lint.parser import parse, parse_file
from prompt_lint.rules.variable_defined import VariableDefinedRule


class TestVariableDefined:
    def setup_method(self) -> None:
        self.rule = VariableDefinedRule()

    def test_all_defined(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0

    def test_undefined_variables(self, undefined_variable: Path) -> None:
        doc = parse_file(str(undefined_variable))
        diagnostics = self.rule.check(doc)
        undefined_names = {d.message for d in diagnostics}
        assert any("age" in m for m in undefined_names)
        assert any("priority" in m for m in undefined_names)
        assert len(diagnostics) == 2

    def test_rule_id(self) -> None:
        assert self.rule.rule_id == "R002"

    def test_no_input_section(self) -> None:
        content = (
            "---\nname: t\ndescription: d\nversion: '1'\n---\n\n"
            "# Role\nR\n\n# Output\n- **r**: r\n\n# Steps\nUse {{x}}"
        )
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 1
        assert "x" in diagnostics[0].message

    def test_references_in_constraints(self) -> None:
        content = (
            "---\nname: t\ndescription: d\nversion: '1'\n---\n\n"
            "# Role\nR\n\n# Input\n- `x`: string (required) - x\n\n"
            "# Output\n- **r**: r\n\n"
            "# Constraints\n{{y}} must be > 0\n\n"
            "# Steps\n1. Use {{x}}"
        )
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 1
        assert "y" in diagnostics[0].message
