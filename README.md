# prompt-lint

Static analysis tool for structured `.prompt.md` files — like ESLint, but for LLM prompts.

## What is this?

`prompt-lint` defines a structured format (`.prompt.md`) for LLM prompts and provides static analysis to catch common issues:

- **R001**: Required sections (Role, Input, Output, Steps) must exist and be non-empty
- **R002**: Variables referenced with `{{var}}` must be defined in the Input section
- **R003**: Variables defined in Input should be referenced at least once
- **R005**: YAML frontmatter must contain `name`, `description`, and `version`

## Installation

```bash
pip install prompt-lint
```

## Quick Start

Create a `.prompt.md` file:

```markdown
---
name: greeting
description: Generate a greeting
version: "1.0"
---

# Role
You are a friendly greeter.

# Input
- `name`: string (required) - Person's name

# Output
- **greeting**: A personalized greeting

# Steps
1. Read {{name}}
2. Generate **greeting**
```

Run the linter:

```bash
prompt-lint lint greeting.prompt.md
```

## CLI Usage

```bash
# Lint specific files
prompt-lint lint file1.prompt.md file2.prompt.md

# Lint all .prompt.md files in a directory
prompt-lint lint prompts/

# Show version
prompt-lint --version
```

## Output Format

```
file.prompt.md:42:15: R002 error: Variable "{{priority}}" is used in Steps but not defined in Input
file.prompt.md:8:3:  R003 warning: Variable "related_goal" is defined in Input but never referenced
```

## `.prompt.md` Format

See [SPEC.md](SPEC.md) for the full format specification.

### Structure

A `.prompt.md` file consists of:

1. **YAML Frontmatter** — metadata (`name`, `description`, `version`, optional `tags`)
2. **Sections** — H1 headings that define the prompt structure

### Required Sections

| Section | Purpose |
|---------|---------|
| Role | Define the LLM's persona |
| Input | Declare input variables with types |
| Output | Define expected output fields |
| Steps | Processing logic referencing variables |

### Optional Sections

Constraints, Examples, Fallback, Changelog

### Variable Syntax

- **Definition** (in Input): `` `var_name`: type (required\|optional) - description ``
- **Reference** (elsewhere): `{{var_name}}`
- **Output reference**: `**output_name**` (bold)

### Japanese Aliases

All section headings support Japanese aliases (e.g., `# 役割` for Role, `# 処理手順` for Steps).

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## License

MIT
