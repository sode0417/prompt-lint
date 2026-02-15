"""Tests for R005: Frontmatter validation."""

from __future__ import annotations

from pathlib import Path

from prompt_lint.parser import parse, parse_file
from prompt_lint.rules.frontmatter import FrontmatterRule


class TestFrontmatter:
    def setup_method(self) -> None:
        self.rule = FrontmatterRule()

    def test_valid_frontmatter(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 0

    def test_missing_frontmatter(self, missing_frontmatter: Path) -> None:
        doc = parse_file(str(missing_frontmatter))
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 1
        assert "missing" in diagnostics[0].message.lower()

    def test_incomplete_frontmatter(self, incomplete_frontmatter: Path) -> None:
        doc = parse_file(str(incomplete_frontmatter))
        diagnostics = self.rule.check(doc)
        missing_fields = {d.message for d in diagnostics}
        assert any("description" in m for m in missing_fields)
        assert any("version" in m for m in missing_fields)

    def test_rule_id(self) -> None:
        assert self.rule.rule_id == "R005"

    def test_empty_field_value(self) -> None:
        content = '---\nname: ""\ndescription: d\nversion: "1"\n---\n\n# Role\nR'
        doc = parse(content)
        diagnostics = self.rule.check(doc)
        assert len(diagnostics) == 1
        assert "name" in diagnostics[0].message
