"""Validation engine that orchestrates rules against parsed documents."""

from __future__ import annotations

from prompt_lint.models import Diagnostic, PromptDocument
from prompt_lint.rules import RuleBase, get_all_rules


def validate(doc: PromptDocument, rules: list[RuleBase] | None = None) -> list[Diagnostic]:
    """Run all rules against a document and return diagnostics."""
    if rules is None:
        rules = get_all_rules()

    diagnostics: list[Diagnostic] = []
    for rule in rules:
        results = rule.check(doc)
        for diag in results:
            diag.path = doc.path
        diagnostics.extend(results)

    diagnostics.sort(key=lambda d: (d.path, d.position.line, d.position.column))
    return diagnostics
