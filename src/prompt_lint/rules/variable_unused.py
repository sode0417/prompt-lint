"""R003: Variables defined in Input should be referenced at least once."""

from __future__ import annotations

from prompt_lint.models import Diagnostic, PromptDocument, Severity
from prompt_lint.rules import RuleBase


class VariableUnusedRule(RuleBase):
    @property
    def rule_id(self) -> str:
        return "R003"

    @property
    def description(self) -> str:
        return "Defined variables should be referenced"

    def check(self, doc: PromptDocument) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        referenced_names = {ref.name for ref in doc.all_references}

        for var in doc.input_variables:
            if var.name not in referenced_names:
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        severity=Severity.WARNING,
                        message=(
                            f'Variable "{var.name}" is defined in Input but never referenced'
                        ),
                        position=var.position,
                        path=doc.path,
                    )
                )

        return diagnostics
