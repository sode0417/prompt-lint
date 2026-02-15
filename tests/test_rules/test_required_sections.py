"""Tests for R001: Required sections."""

from __future__ import annotations

from pathlib import Path

from prompt_lint.parser import parse, parse_file
from prompt_lint.rules.required_sections import RequiredSectionsRule


class TestRequiredSections:
    def setup_method(self) -> None:
        self.rule = RequiredSectionsRule()

    def test_all_present(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0

    def test_missing_output_and_steps(self, missing_sections: Path) -> None:
        doc = parse_file(str(missing_sections))
        diagnostics = self.rule.check(doc)
        missing_names = {d.message for d in diagnostics}
        assert any("Output" in m for m in missing_names)
        assert any("Steps" in m for m in missing_names)

    def test_empty_section(self, empty_section: Path) -> None:
        doc = parse_file(str(empty_section))
        diagnostics = self.rule.check(doc)
        assert any("empty" in d.message.lower() for d in diagnostics)

    def test_rule_id(self) -> None:
        assert self.rule.rule_id == "R001"

    def test_all_sections_missing(self) -> None:
        content = "---\nname: t\ndescription: d\nversion: '1'\n---\n\nNo sections here."
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 4  # Role, Input, Output, Steps
