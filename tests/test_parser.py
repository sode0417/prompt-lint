"""Tests for the .prompt.md parser."""

from __future__ import annotations

from pathlib import Path

from prompt_lint.models import SectionKind
from prompt_lint.parser import parse, parse_file


class TestFrontmatter:
    def test_parse_frontmatter(self) -> None:
        content = '---\nname: test\ndescription: desc\nversion: "1.0"\n---\n\n# Role\nContent'
        doc = parse(content)
        assert doc.frontmatter is not None
        assert doc.frontmatter.data["name"] == "test"
        assert doc.frontmatter.data["description"] == "desc"
        assert doc.frontmatter.data["version"] == "1.0"

    def test_no_frontmatter(self) -> None:
        content = "# Role\nContent"
        doc = parse(content)
        assert doc.frontmatter is None

    def test_unclosed_frontmatter(self) -> None:
        content = "---\nname: test\n# Role\nContent"
        doc = parse(content)
        # Unclosed frontmatter should be treated as if not present
        # because # Role line is not ---
        assert doc.frontmatter is None


class TestSections:
    def test_basic_sections(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        kinds = [s.kind for s in doc.sections]
        assert SectionKind.ROLE in kinds
        assert SectionKind.INPUT in kinds
        assert SectionKind.OUTPUT in kinds
        assert SectionKind.STEPS in kinds

    def test_japanese_headings(self, japanese_headings: Path) -> None:
        doc = parse_file(str(japanese_headings))
        kinds = [s.kind for s in doc.sections]
        assert SectionKind.ROLE in kinds
        assert SectionKind.INPUT in kinds
        assert SectionKind.OUTPUT in kinds
        assert SectionKind.STEPS in kinds

    def test_section_content_not_empty(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        role = doc.get_section(SectionKind.ROLE)
        assert role is not None
        assert "helpful assistant" in role.content

    def test_empty_section_detected(self, empty_section: Path) -> None:
        doc = parse_file(str(empty_section))
        output = doc.get_section(SectionKind.OUTPUT)
        assert output is not None
        assert output.content.strip() == ""


class TestVariables:
    def test_input_variable_extraction(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        variables = doc.input_variables
        assert len(variables) == 1
        assert variables[0].name == "query"
        assert variables[0].type == "string"
        assert variables[0].required is True

    def test_multiple_variables(self, unused_variable: Path) -> None:
        doc = parse_file(str(unused_variable))
        variables = doc.input_variables
        assert len(variables) == 3
        names = {v.name for v in variables}
        assert names == {"name", "age", "unused_field"}

    def test_optional_variable(self, unused_variable: Path) -> None:
        doc = parse_file(str(unused_variable))
        age_var = next(v for v in doc.input_variables if v.name == "age")
        assert age_var.required is False

    def test_variable_references(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        refs = doc.all_references
        ref_names = {r.name for r in refs}
        assert "query" in ref_names

    def test_code_block_references_ignored(self, code_block_refs: Path) -> None:
        doc = parse_file(str(code_block_refs))
        ref_names = {r.name for r in doc.all_references}
        assert "language" in ref_names
        assert "task" in ref_names
        assert "should_not_be_detected" not in ref_names
        assert "also_not_a_var" not in ref_names


class TestOutputFields:
    def test_output_field_extraction(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        fields = doc.output_fields
        assert len(fields) == 1
        assert fields[0].name == "answer"

    def test_multiple_output_fields(self) -> None:
        content = (
            "---\nname: t\ndescription: d\nversion: '1'\n---\n\n"
            "# Role\nR\n\n# Input\n- `x`: string (required) - x\n\n"
            "# Output\n- **result**: The result\n- **summary**: A summary\n\n"
            "# Steps\n1. Use {{x}} to produce **result** and **summary**"
        )
        doc = parse(content)
        fields = doc.output_fields
        field_names = {f.name for f in fields}
        assert field_names == {"result", "summary"}


class TestParseFile:
    def test_path_preserved(self, valid_minimal: Path) -> None:
        doc = parse_file(str(valid_minimal))
        assert str(valid_minimal) in doc.path

    def test_full_example(self) -> None:
        """Test parsing a comprehensive example."""
        examples_dir = Path(__file__).parent.parent / "examples"
        task_pri = examples_dir / "task_prioritization.prompt.md"
        if task_pri.exists():
            doc = parse_file(str(task_pri))
            assert doc.frontmatter is not None
            assert doc.frontmatter.data["name"] == "task-prioritization"
            assert len(doc.input_variables) == 6
            assert len(doc.output_fields) == 2
            assert len(doc.all_references) > 0
