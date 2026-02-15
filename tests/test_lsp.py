"""Tests for the LSP server logic (pure functions, no server instance needed)."""

from __future__ import annotations

from lsprotocol import types

from prompt_lint.lsp.server import build_diagnostics, compute_hover, compute_completions


VALID_DOC = """\
---
name: test
description: Test prompt
version: "1.0"
---

# Role
You are a helper.

# Input
- `query`: string (required) - User query

# Output
- **answer**: The answer

# Steps
1. Read {{query}}
2. Generate **answer**
"""

INVALID_DOC = """\
---
name: test
description: Test
version: "1.0"
---

# Role
You are a helper.

# Input
- `name`: string (required) - Name

# Output
- **greeting**: The greeting

# Steps
1. Read {{name}} and {{age}}
2. Generate **greeting**
"""


class TestBuildDiagnostics:
    def test_valid_doc_no_diagnostics(self) -> None:
        diagnostics = build_diagnostics(VALID_DOC, "test.prompt.md")
        assert len(diagnostics) == 0

    def test_invalid_doc_has_diagnostics(self) -> None:
        diagnostics = build_diagnostics(INVALID_DOC, "test.prompt.md")
        r002_diags = [d for d in diagnostics if "R002" in d.message]
        assert len(r002_diags) == 1
        assert "age" in r002_diags[0].message

    def test_diagnostics_have_correct_severity(self) -> None:
        diagnostics = build_diagnostics(INVALID_DOC, "test.prompt.md")
        for d in diagnostics:
            if "R002" in d.message:
                assert d.severity == types.DiagnosticSeverity.Error

    def test_diagnostics_source_is_prompt_lint(self) -> None:
        diagnostics = build_diagnostics(INVALID_DOC, "test.prompt.md")
        for d in diagnostics:
            assert d.source == "prompt-lint"

    def test_line_numbers_are_zero_based(self) -> None:
        diagnostics = build_diagnostics(INVALID_DOC, "test.prompt.md")
        for d in diagnostics:
            # LSP uses 0-based lines
            assert d.range.start.line >= 0


class TestComputeHover:
    def test_hover_on_defined_variable(self) -> None:
        lines = VALID_DOC.split("\n")
        # Line 16 (0-indexed) = "1. Read {{query}}"
        result = compute_hover(VALID_DOC, lines, 16, 12)
        assert result is not None
        assert "query" in result.contents.value  # type: ignore[union-attr]
        assert "string" in result.contents.value  # type: ignore[union-attr]
        assert "required" in result.contents.value  # type: ignore[union-attr]

    def test_hover_on_undefined_variable(self) -> None:
        lines = INVALID_DOC.split("\n")
        # Line 16 (0-indexed) = "1. Read {{name}} and {{age}}"
        line = lines[16]
        age_pos = line.index("{{age}}")
        result = compute_hover(INVALID_DOC, lines, 16, age_pos + 2)
        assert result is not None
        assert "not defined" in result.contents.value  # type: ignore[union-attr]

    def test_hover_on_non_variable(self) -> None:
        lines = VALID_DOC.split("\n")
        # Line 7 (0-indexed) = "You are a helper."
        result = compute_hover(VALID_DOC, lines, 7, 5)
        assert result is None

    def test_hover_out_of_range(self) -> None:
        lines = VALID_DOC.split("\n")
        result = compute_hover(VALID_DOC, lines, 999, 0)
        assert result is None


class TestComputeCompletions:
    def test_variable_completion_after_double_brace(self) -> None:
        lines = VALID_DOC.split("\n")
        # Simulate typing "{{" — place cursor right after "{{"
        test_lines = lines.copy()
        test_lines.append("Use {{")
        source = "\n".join(test_lines)
        items = compute_completions(source, test_lines, len(test_lines) - 1, 6)
        labels = [item.label for item in items]
        assert "query" in labels

    def test_variable_completion_partial_name(self) -> None:
        lines = VALID_DOC.split("\n")
        test_lines = lines.copy()
        test_lines.append("Use {{qu")
        source = "\n".join(test_lines)
        items = compute_completions(source, test_lines, len(test_lines) - 1, 8)
        labels = [item.label for item in items]
        assert "query" in labels

    def test_section_completion_after_hash(self) -> None:
        lines = VALID_DOC.split("\n")
        test_lines = lines.copy()
        test_lines.append("#")
        source = "\n".join(test_lines)
        items = compute_completions(source, test_lines, len(test_lines) - 1, 1)
        labels = [item.label for item in items]
        assert any("Role" in label for label in labels)
        assert any("Steps" in label for label in labels)

    def test_section_completion_after_hash_space(self) -> None:
        lines = VALID_DOC.split("\n")
        test_lines = lines.copy()
        test_lines.append("# ")
        source = "\n".join(test_lines)
        items = compute_completions(source, test_lines, len(test_lines) - 1, 2)
        labels = [item.label for item in items]
        assert len(labels) == 8  # All 8 section types

    def test_no_completion_on_normal_text(self) -> None:
        lines = VALID_DOC.split("\n")
        items = compute_completions(VALID_DOC, lines, 7, 5)
        assert len(items) == 0

    def test_completion_items_have_details(self) -> None:
        lines = VALID_DOC.split("\n")
        test_lines = lines.copy()
        test_lines.append("Use {{")
        source = "\n".join(test_lines)
        items = compute_completions(source, test_lines, len(test_lines) - 1, 6)
        for item in items:
            assert item.detail is not None
            assert item.kind == types.CompletionItemKind.Variable
