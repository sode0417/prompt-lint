"""R004: Output fields should be referenced in Steps or other sections."""

from __future__ import annotations

from prompt_lint.models import Diagnostic, PromptDocument, Severity
from prompt_lint.rules import RuleBase


class OutputReachableRule(RuleBase):
    @property
    def rule_id(self) -> str:
        return "R004"

    @property
    def description(self) -> str:
        return "Output fields should be referenced in Steps or other sections"

    def check(self, doc: PromptDocument) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        referenced_names = {f.name for f in doc.output_references_in_steps}

        for field in doc.output_fields:
            if field.name not in referenced_names:
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        severity=Severity.WARNING,
                        message=(
                            f'Output field "**{field.name}**" is defined but never '
                            f"referenced in Steps or other sections"
                        ),
                        position=field.position,
                        path=doc.path,
                    )
                )

        return diagnostics
