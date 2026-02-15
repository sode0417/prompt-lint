"""Tests for R004: Output field reachability."""

from __future__ import annotations

from pathlib import Path

from prompt_lint.models import Severity
from prompt_lint.parser import parse, parse_file
from prompt_lint.rules.output_reachable import OutputReachableRule


class TestOutputReachable:
    def setup_method(self) -> None:
        self.rule = OutputReachableRule()

    def test_all_reachable(self) -> None:
        content = (
            "---\nname: t\ndescription: d\nversion: '1'\n---\n\n"
            "# Role\nR\n\n# Input\n- `x`: string (required) - x\n\n"
            "# Output\n- **result**: r\n- **summary**: s\n\n"
            "# Steps\n1. Use {{x}} to make **result**\n2. Create **summary**"
        )
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0

    def test_unreachable_outputs(self) -> None:
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        doc = parse_file(str(fixtures_dir / "unreachable_output.prompt.md"))
        diagnostics = self.rule.check(doc)
        unreachable_names = [d.message for d in diagnostics]
        assert any("confidence" in m for m in unreachable_names)
        assert any("sources" in m for m in unreachable_names)
        assert len(diagnostics) == 2

    def test_severity_is_warning(self) -> None:
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        doc = parse_file(str(fixtures_dir / "unreachable_output.prompt.md"))
        diagnostics = self.rule.check(doc)
        assert all(d.severity == Severity.WARNING for d in diagnostics)

    def test_rule_id(self) -> None:
        assert self.rule.rule_id == "R004"

    def test_no_output_section(self) -> None:
        content = (
            "---\nname: t\ndescription: d\nversion: '1'\n---\n\n"
            "# Role\nR\n\n# Input\n- `x`: string (required) - x\n\n"
            "# Steps\n1. Use {{x}}"
        )
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0

    def test_output_referenced_in_constraints(self) -> None:
        """Output field referenced in Constraints (not Steps) should still count."""
        content = (
            "---\nname: t\ndescription: d\nversion: '1'\n---\n\n"
            "# Role\nR\n\n# Input\n- `x`: string (required) - x\n\n"
            "# Output\n- **result**: r\n\n"
            "# Constraints\n**result** must be JSON\n\n"
            "# Steps\n1. Use {{x}}"
        )
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0
