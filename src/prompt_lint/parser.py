"""Parser for .prompt.md files."""

from __future__ import annotations

import re

import yaml

from prompt_lint.models import (
    Frontmatter,
    OutputField,
    Position,
    PromptDocument,
    Section,
    SectionKind,
    Variable,
    VariableReference,
    SECTION_ALIASES,
)

# --- Regular expressions ---

HEADING_RE = re.compile(r"^#\s+(.+)$")
VAR_REFERENCE_RE = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")
INPUT_VAR_RE = re.compile(
    r"^[-*]\s+`([a-zA-Z_]\w*)`"  # name
    r":\s*(\w+)"  # type
    r"\s*\((required|optional)"  # required/optional
    r"(?:,\s*default:\s*[^)]+)?"  # optional default
    r"\)"  # close paren
    r"(?:\s*[-–—]\s*(.+))?"  # optional description
)
OUTPUT_FIELD_RE = re.compile(r"\*\*([^*]+)\*\*")
CODE_BLOCK_RE = re.compile(r"^```")
FRONTMATTER_DELIMITER = "---"


def parse(content: str, path: str = "<stdin>") -> PromptDocument:
    """Parse a .prompt.md file content into a PromptDocument."""
    lines = content.split("\n")
    frontmatter = _parse_frontmatter(lines)
    body_start = frontmatter.end_line if frontmatter else 0
    sections = _parse_sections(lines, body_start)
    return PromptDocument(
        path=path,
        frontmatter=frontmatter,
        sections=sections,
        raw_content=content,
    )


def parse_file(path: str) -> PromptDocument:
    """Parse a .prompt.md file from disk."""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return parse(content, path)


def _parse_frontmatter(lines: list[str]) -> Frontmatter | None:
    """Extract YAML frontmatter between --- delimiters."""
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        return None

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIMITER:
            end_idx = i
            break

    if end_idx is None:
        return None

    yaml_content = "\n".join(lines[1:end_idx])
    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        data = {}

    if not isinstance(data, dict):
        data = {}

    return Frontmatter(data=data, start_line=1, end_line=end_idx + 1)


def _parse_sections(lines: list[str], start_line: int) -> list[Section]:
    """Split body into sections by H1 headings."""
    sections: list[Section] = []
    current_heading: str | None = None
    current_start: int = start_line
    current_lines: list[str] = []
    in_code_block = False

    for i in range(start_line, len(lines)):
        line = lines[i]
        if CODE_BLOCK_RE.match(line.strip()):
            in_code_block = not in_code_block
        match = HEADING_RE.match(line)
        if match and not in_code_block:
            # Save previous section if we had a heading
            if current_heading is not None:
                sections.append(
                    _build_section(current_heading, current_lines, current_start)
                )
            current_heading = match.group(1).strip()
            current_start = i + 1  # 1-based
            current_lines = []
        else:
            if current_heading is not None:
                current_lines.append(line)

    # Save the last section
    if current_heading is not None:
        sections.append(_build_section(current_heading, current_lines, current_start))

    return sections


def _build_section(heading: str, content_lines: list[str], start_line: int) -> Section:
    """Build a Section from raw heading and content lines."""
    kind = _resolve_section_kind(heading)
    content = "\n".join(content_lines)

    section = Section(
        kind=kind,
        raw_heading=heading,
        content=content,
        start_line=start_line,
    )

    if kind == SectionKind.INPUT:
        section.variables = _extract_input_variables(content_lines, start_line)

    if kind == SectionKind.OUTPUT:
        section.output_fields = _extract_output_fields(content_lines, start_line)

    section.references = _extract_references(content_lines, start_line, kind)

    return section


def _resolve_section_kind(heading: str) -> SectionKind | None:
    """Resolve a heading to a canonical SectionKind."""
    normalized = heading.lower().strip()
    return SECTION_ALIASES.get(normalized)


def _extract_input_variables(lines: list[str], base_line: int) -> list[Variable]:
    """Extract variable definitions from an Input section."""
    variables: list[Variable] = []
    for i, line in enumerate(lines):
        match = INPUT_VAR_RE.match(line.strip())
        if match:
            variables.append(
                Variable(
                    name=match.group(1),
                    type=match.group(2),
                    required=match.group(3) == "required",
                    description=match.group(4) or "",
                    position=Position(line=base_line + i + 1, column=line.find("`") + 1),
                )
            )
    return variables


def _extract_output_fields(lines: list[str], base_line: int) -> list[OutputField]:
    """Extract **output_name** patterns from an Output section."""
    fields: list[OutputField] = []
    seen: set[str] = set()
    in_code_block = False

    for i, line in enumerate(lines):
        if CODE_BLOCK_RE.match(line.strip()):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for match in OUTPUT_FIELD_RE.finditer(line):
            name = match.group(1).strip()
            if name not in seen:
                seen.add(name)
                fields.append(
                    OutputField(
                        name=name,
                        position=Position(
                            line=base_line + i + 1,
                            column=match.start() + 1,
                        ),
                    )
                )
    return fields


def _extract_references(
    lines: list[str], base_line: int, kind: SectionKind | None
) -> list[VariableReference]:
    """Extract {{variable}} references from content lines, skipping code blocks."""
    refs: list[VariableReference] = []
    in_code_block = False

    for i, line in enumerate(lines):
        if CODE_BLOCK_RE.match(line.strip()):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for match in VAR_REFERENCE_RE.finditer(line):
            refs.append(
                VariableReference(
                    name=match.group(1),
                    position=Position(
                        line=base_line + i + 1,
                        column=match.start() + 1,
                    ),
                    section=kind,
                )
            )
    return refs
