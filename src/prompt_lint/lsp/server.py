"""prompt-lint LSP server."""

from __future__ import annotations

import re

from lsprotocol import types
from pygls.lsp.server import LanguageServer

from prompt_lint import __version__
from prompt_lint.models import Severity
from prompt_lint.parser import parse, VAR_REFERENCE_RE
from prompt_lint.validator import validate

server = LanguageServer("prompt-lint", __version__)

# --- Canonical section headings for completion ---

SECTION_COMPLETIONS = [
    ("Role（役割）", "Define the LLM's persona"),
    ("Input（入力変数）", "Declare input variables"),
    ("Output（出力形式）", "Define expected output fields"),
    ("Constraints（制約）", "Constraints and rules"),
    ("Steps（処理手順）", "Processing logic"),
    ("Examples（例）", "Example inputs/outputs"),
    ("Fallback（フォールバック）", "Fallback behavior"),
    ("Changelog（メモ）", "Change history"),
]


# --- Pure logic functions (testable without LSP) ---


def build_diagnostics(source: str, path: str) -> list[types.Diagnostic]:
    """Parse and validate source, returning LSP diagnostics."""
    prompt_doc = parse(source, path)
    results = validate(prompt_doc)

    return [
        types.Diagnostic(
            range=types.Range(
                start=types.Position(line=d.position.line - 1, character=d.position.column - 1),
                end=types.Position(line=d.position.line - 1, character=d.position.column + 20),
            ),
            message=f"[{d.rule_id}] {d.message}",
            severity=(
                types.DiagnosticSeverity.Error
                if d.severity == Severity.ERROR
                else types.DiagnosticSeverity.Warning
            ),
            source="prompt-lint",
        )
        for d in results
    ]


def compute_hover(
    source: str, lines: list[str], line_num: int, character: int
) -> types.Hover | None:
    """Compute hover information for a position in the document."""
    try:
        line = lines[line_num]
    except IndexError:
        return None

    for match in VAR_REFERENCE_RE.finditer(line):
        start_col = match.start()
        end_col = match.end()
        if start_col <= character <= end_col:
            var_name = match.group(1)
            prompt_doc = parse(source)

            for var in prompt_doc.input_variables:
                if var.name == var_name:
                    req_label = "required" if var.required else "optional"
                    hover_text = (
                        f"**`{var.name}`**: `{var.type}` ({req_label})\n\n"
                        f"{var.description}"
                    )
                    return types.Hover(
                        contents=types.MarkupContent(
                            kind=types.MarkupKind.Markdown,
                            value=hover_text,
                        ),
                        range=types.Range(
                            start=types.Position(line=line_num, character=start_col),
                            end=types.Position(line=line_num, character=end_col),
                        ),
                    )

            return types.Hover(
                contents=types.MarkupContent(
                    kind=types.MarkupKind.Markdown,
                    value=f"**`{var_name}`** — not defined in Input section",
                ),
                range=types.Range(
                    start=types.Position(line=line_num, character=start_col),
                    end=types.Position(line=line_num, character=end_col),
                ),
            )

    return None


def compute_completions(
    source: str, lines: list[str], line_num: int, character: int
) -> list[types.CompletionItem]:
    """Compute completion items for a position in the document."""
    try:
        line = lines[line_num]
    except IndexError:
        return []

    line_before_cursor = line[:character]
    items: list[types.CompletionItem] = []

    # Variable completion: triggered by {{
    if line_before_cursor.rstrip().endswith("{{") or re.search(r"\{\{\w*$", line_before_cursor):
        prompt_doc = parse(source)
        for var in prompt_doc.input_variables:
            req_label = "required" if var.required else "optional"
            items.append(
                types.CompletionItem(
                    label=var.name,
                    kind=types.CompletionItemKind.Variable,
                    detail=f"{var.type} ({req_label})",
                    documentation=var.description,
                    insert_text=var.name,
                )
            )

    # Section heading completion: triggered by # at start of line
    elif line_before_cursor.strip() == "#" or line_before_cursor.strip() == "# ":
        for heading, desc in SECTION_COMPLETIONS:
            items.append(
                types.CompletionItem(
                    label=heading,
                    kind=types.CompletionItemKind.Module,
                    detail=desc,
                    insert_text=f" {heading}" if line_before_cursor.strip() == "#" else heading,
                )
            )

    return items


# --- LSP event handlers ---


def _validate_and_publish(ls: LanguageServer, uri: str) -> None:
    """Parse, validate, and publish diagnostics for a document."""
    doc = ls.workspace.get_text_document(uri)
    diagnostics = build_diagnostics(doc.source, doc.path)

    ls.text_document_publish_diagnostics(
        types.PublishDiagnosticsParams(
            uri=doc.uri,
            version=doc.version,
            diagnostics=diagnostics,
        )
    )


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams) -> None:
    _validate_and_publish(ls, params.text_document.uri)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: types.DidChangeTextDocumentParams) -> None:
    _validate_and_publish(ls, params.text_document.uri)


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: types.DidSaveTextDocumentParams) -> None:
    _validate_and_publish(ls, params.text_document.uri)


@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params: types.HoverParams) -> types.Hover | None:
    """Show variable definition info on hover over {{var}}."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    return compute_hover(doc.source, doc.lines, params.position.line, params.position.character)


@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    types.CompletionOptions(trigger_characters=["{", "#"]),
)
def completions(
    ls: LanguageServer, params: types.CompletionParams
) -> types.CompletionList:
    """Provide completions for {{variables and # sections."""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    items = compute_completions(
        doc.source, doc.lines, params.position.line, params.position.character
    )
    return types.CompletionList(is_incomplete=False, items=items)


def main() -> None:
    """Entry point for the LSP server."""
    server.start_io()


if __name__ == "__main__":
    main()
