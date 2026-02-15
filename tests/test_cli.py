"""Tests for the CLI."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from prompt_lint.cli import main


class TestCli:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_version(self) -> None:
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_lint_valid_file(self, valid_minimal: Path) -> None:
        result = self.runner.invoke(main, ["lint", str(valid_minimal)])
        assert result.exit_code == 0

    def test_lint_file_with_errors(self, undefined_variable: Path) -> None:
        result = self.runner.invoke(main, ["lint", str(undefined_variable)])
        assert result.exit_code == 1
        assert "R002" in result.output

    def test_lint_file_with_warnings_only(self, unused_variable: Path) -> None:
        result = self.runner.invoke(main, ["lint", str(unused_variable)])
        assert result.exit_code == 0
        assert "R003" in result.output
        assert "warning" in result.output

    def test_lint_missing_frontmatter(self, missing_frontmatter: Path) -> None:
        result = self.runner.invoke(main, ["lint", str(missing_frontmatter)])
        assert result.exit_code == 1
        assert "R005" in result.output

    def test_lint_output_format(self, undefined_variable: Path) -> None:
        result = self.runner.invoke(main, ["lint", str(undefined_variable)])
        # Check format: path:line:col: RULE severity: message
        for line in result.output.strip().split("\n"):
            if line and not line.startswith("Found"):
                parts = line.split(": ", 2)
                assert len(parts) >= 2, f"Bad format: {line}"

    def test_lint_directory(self) -> None:
        fixtures_dir = Path(__file__).parent / "fixtures"
        result = self.runner.invoke(main, ["lint", str(fixtures_dir)])
        # Should process multiple files
        assert "R001" in result.output or "R002" in result.output or "R005" in result.output

    def test_lint_example_files(self) -> None:
        examples_dir = Path(__file__).parent.parent / "examples"
        if examples_dir.exists():
            result = self.runner.invoke(main, ["lint", str(examples_dir)])
            assert result.exit_code == 0
