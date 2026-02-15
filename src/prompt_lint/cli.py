"""CLI entry point for prompt-lint."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from prompt_lint import __version__
from prompt_lint.models import Severity
from prompt_lint.parser import parse_file
from prompt_lint.validator import validate


def _format_diagnostic(diag: object) -> str:
    """Format a diagnostic for terminal output."""
    from prompt_lint.models import Diagnostic

    assert isinstance(diag, Diagnostic)
    severity_str = diag.severity.value
    path = diag.path or "<stdin>"
    return (
        f"{path}:{diag.position.line}:{diag.position.column}: "
        f"{diag.rule_id} {severity_str}: {diag.message}"
    )


@click.group()
@click.version_option(version=__version__, prog_name="prompt-lint")
def main() -> None:
    """prompt-lint: Static analysis for .prompt.md files."""


@main.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
def lint(files: tuple[str, ...]) -> None:
    """Lint one or more .prompt.md files."""
    total_errors = 0
    total_warnings = 0

    for file_path in files:
        path = Path(file_path)

        # Expand directories
        if path.is_dir():
            targets = list(path.rglob("*.prompt.md"))
        else:
            targets = [path]

        for target in targets:
            try:
                doc = parse_file(str(target))
            except Exception as e:
                click.echo(f"{target}: Failed to parse: {e}", err=True)
                total_errors += 1
                continue

            diagnostics = validate(doc)

            for diag in diagnostics:
                click.echo(_format_diagnostic(diag))
                if diag.severity == Severity.ERROR:
                    total_errors += 1
                else:
                    total_warnings += 1

    # Summary
    if total_errors or total_warnings:
        click.echo()
        parts = []
        if total_errors:
            parts.append(f"{total_errors} error(s)")
        if total_warnings:
            parts.append(f"{total_warnings} warning(s)")
        click.echo(f"Found {', '.join(parts)}.")

    if total_errors > 0:
        sys.exit(1)
