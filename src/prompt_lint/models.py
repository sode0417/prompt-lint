"""Data models for prompt-lint."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


class SectionKind(Enum):
    """Canonical section names."""

    ROLE = "Role"
    INPUT = "Input"
    OUTPUT = "Output"
    CONSTRAINTS = "Constraints"
    STEPS = "Steps"
    EXAMPLES = "Examples"
    FALLBACK = "Fallback"
    CHANGELOG = "Changelog"


# Map heading text (lowered) to canonical SectionKind
SECTION_ALIASES: dict[str, SectionKind] = {}

_ALIAS_TABLE: dict[SectionKind, list[str]] = {
    SectionKind.ROLE: ["role", "役割", "role（役割）"],
    SectionKind.INPUT: ["input", "入力変数", "input（入力変数）", "入力", "input（入力）"],
    SectionKind.OUTPUT: ["output", "出力形式", "output（出力形式）", "出力", "output（出力）"],
    SectionKind.CONSTRAINTS: ["constraints", "制約", "constraints（制約）"],
    SectionKind.STEPS: [
        "steps",
        "処理手順",
        "steps（処理手順）",
        "logic",
        "判断ロジック",
        "logic（判断ロジック）",
        "logic（判断ロジック / 処理の流れ）",
    ],
    SectionKind.EXAMPLES: ["examples", "例", "examples（例）"],
    SectionKind.FALLBACK: [
        "fallback",
        "フォールバック",
        "fallback（フォールバック）",
        "error cases",
        "error cases（失敗パターン）",
    ],
    SectionKind.CHANGELOG: ["changelog", "メモ", "changelog（メモ）"],
}

for _kind, _aliases in _ALIAS_TABLE.items():
    for _alias in _aliases:
        SECTION_ALIASES[_alias] = _kind

REQUIRED_SECTIONS: set[SectionKind] = {
    SectionKind.ROLE,
    SectionKind.INPUT,
    SectionKind.OUTPUT,
    SectionKind.STEPS,
}

REQUIRED_FRONTMATTER_FIELDS: list[str] = ["name", "description", "version"]


@dataclass
class Position:
    """1-based line and column position in source."""

    line: int
    column: int = 1


@dataclass
class Variable:
    """An input variable definition."""

    name: str
    type: str
    required: bool
    description: str
    position: Position


@dataclass
class VariableReference:
    """A {{variable}} reference in the document."""

    name: str
    position: Position
    section: SectionKind | None = None


@dataclass
class OutputField:
    """An output field definition (**name**)."""

    name: str
    position: Position


@dataclass
class Section:
    """A parsed section of the document."""

    kind: SectionKind | None  # None for unrecognized sections
    raw_heading: str
    content: str
    start_line: int
    variables: list[Variable] = field(default_factory=list)
    references: list[VariableReference] = field(default_factory=list)
    output_fields: list[OutputField] = field(default_factory=list)


@dataclass
class Frontmatter:
    """Parsed YAML frontmatter."""

    data: dict[str, Any]
    start_line: int
    end_line: int


@dataclass
class PromptDocument:
    """A fully parsed .prompt.md document."""

    path: str
    frontmatter: Frontmatter | None
    sections: list[Section]
    raw_content: str

    @property
    def input_variables(self) -> list[Variable]:
        for section in self.sections:
            if section.kind == SectionKind.INPUT:
                return section.variables
        return []

    @property
    def all_references(self) -> list[VariableReference]:
        refs: list[VariableReference] = []
        for section in self.sections:
            if section.kind != SectionKind.INPUT:
                refs.extend(section.references)
        return refs

    @property
    def output_fields(self) -> list[OutputField]:
        for section in self.sections:
            if section.kind == SectionKind.OUTPUT:
                return section.output_fields
        return []

    def get_section(self, kind: SectionKind) -> Section | None:
        for section in self.sections:
            if section.kind == kind:
                return section
        return None


@dataclass
class Diagnostic:
    """A single lint diagnostic."""

    rule_id: str
    severity: Severity
    message: str
    position: Position
    path: str = ""
