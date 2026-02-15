"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def valid_minimal(fixtures_dir: Path) -> Path:
    return fixtures_dir / "valid_minimal.prompt.md"


@pytest.fixture
def missing_sections(fixtures_dir: Path) -> Path:
    return fixtures_dir / "missing_sections.prompt.md"


@pytest.fixture
def undefined_variable(fixtures_dir: Path) -> Path:
    return fixtures_dir / "undefined_variable.prompt.md"


@pytest.fixture
def unused_variable(fixtures_dir: Path) -> Path:
    return fixtures_dir / "unused_variable.prompt.md"


@pytest.fixture
def missing_frontmatter(fixtures_dir: Path) -> Path:
    return fixtures_dir / "missing_frontmatter.prompt.md"


@pytest.fixture
def incomplete_frontmatter(fixtures_dir: Path) -> Path:
    return fixtures_dir / "incomplete_frontmatter.prompt.md"


@pytest.fixture
def japanese_headings(fixtures_dir: Path) -> Path:
    return fixtures_dir / "japanese_headings.prompt.md"


@pytest.fixture
def code_block_refs(fixtures_dir: Path) -> Path:
    return fixtures_dir / "code_block_refs.prompt.md"


@pytest.fixture
def empty_section(fixtures_dir: Path) -> Path:
    return fixtures_dir / "empty_section.prompt.md"
