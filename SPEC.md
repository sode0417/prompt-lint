# `.prompt.md` Format Specification

Version: 1.0

## Overview

`.prompt.md` is a structured Markdown format for defining LLM prompts with explicit inputs, outputs, and processing logic. It enables static analysis similar to programming language linters.

## File Structure

A `.prompt.md` file consists of two parts:

1. YAML Frontmatter (between `---` delimiters)
2. Body (H1-delimited sections)

```
---
<frontmatter>
---

# Section1
<content>

# Section2
<content>
...
```

## Frontmatter

YAML frontmatter is enclosed between `---` delimiters at the start of the file.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier (kebab-case recommended) |
| `description` | string | Human-readable description |
| `version` | string | Semantic version |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `tags` | list[string] | Categorization tags |
| `author` | string | Author name |

### Example

```yaml
---
name: task-prioritization
description: タスクの実行順序を決定する
version: "1.0"
tags: [decision, work]
---
```

## Sections

Sections are delimited by H1 headings (`# Heading`). Each section has a canonical name and recognized aliases.

### Section Table

| Canonical Name | Required | Aliases |
|----------------|----------|---------|
| Role | Yes | `Role`, `役割`, `Role（役割）` |
| Input | Yes | `Input`, `入力変数`, `Input（入力変数）`, `入力`, `Input（入力）` |
| Output | Yes | `Output`, `出力形式`, `Output（出力形式）`, `出力`, `Output（出力）` |
| Steps | Yes | `Steps`, `処理手順`, `Steps（処理手順）`, `Logic`, `判断ロジック`, `Logic（判断ロジック）`, `Logic（判断ロジック / 処理の流れ）` |
| Constraints | No | `Constraints`, `制約`, `Constraints（制約）` |
| Examples | No | `Examples`, `例`, `Examples（例）` |
| Fallback | No | `Fallback`, `フォールバック`, `Fallback（フォールバック）`, `Error Cases`, `Error Cases（失敗パターン）` |
| Changelog | No | `Changelog`, `メモ`, `Changelog（メモ）` |

Heading matching is case-insensitive.

## Variables

### Definition Syntax (Input section)

Variables are defined as Markdown list items in the Input section:

```
- `variable_name`: type (required|optional[, default: value]) - Description
```

Components:
- **Name**: backtick-enclosed identifier (`[a-zA-Z_]\w*`)
- **Type**: one of `string`, `number`, `boolean`, `list`, `object`, or custom types
- **Required/Optional**: `required` or `optional`, optionally followed by `default: <value>`
- **Description**: free-text description after `-` or `–`

### Reference Syntax (other sections)

Variables are referenced using double-brace syntax:

```
{{variable_name}}
```

References inside fenced code blocks (`` ``` ``) are ignored by the linter.

### Output Fields

Output fields are defined using bold syntax in the Output section:

```
- **field_name**: Description
```

Output fields can be referenced in Steps and other sections using the same bold syntax (`**field_name**`).

## Validation Rules

| ID | Severity | Description |
|----|----------|-------------|
| R001 | Error | Required sections (Role, Input, Output, Steps) must exist and be non-empty |
| R002 | Error | Variables referenced with `{{var}}` must be defined in Input |
| R003 | Warning | Variables defined in Input should be referenced at least once |
| R005 | Error | Frontmatter must contain `name`, `description`, and `version` |

### Future Rules (planned)

| ID | Severity | Description |
|----|----------|-------------|
| R004 | Warning | Output fields defined in Output should be referenced in Steps |
| R006 | Error | File links must resolve to existing files |

## Full Example

```markdown
---
name: task-prioritization
description: タスクの実行順序を決定する
version: "1.0"
tags: [decision, work]
---

# Role（役割）
あなたはタスク優先順位アドバイザーです。

# Input（入力変数）
- `deadline`: string (required) - タスクの期日
- `remaining_work_hours`: number (required) - 残作業時間
- `blocking_others`: boolean (optional, default: false) - 他者をブロックしているか

# Output（出力形式）
- **ordered_list**: 優先順位付きタスクリスト
- **immediate_action**: 次に着手すべきタスク

# Constraints（制約）
- {{deadline}} が迫っている場合は常に最優先

# Steps（処理手順）
1. {{deadline}} と {{remaining_work_hours}} を比較
2. {{blocking_others}} が true なら優先度を上げる
3. **ordered_list** を生成
4. 先頭を **immediate_action** として抽出

# Examples（例）
（省略可）

# Fallback（フォールバック）
情報不足の場合は判断不能を明示する。

# Changelog（メモ）
- [2/15] 初版作成
```
