"""R002: Variables referenced with {{var}} must be defined in Input."""

from __future__ import annotations

from prompt_lint.models import Diagnostic, PromptDocument, Severity
from prompt_lint.rules import RuleBase


class VariableDefinedRule(RuleBase):
    @property
    def rule_id(self) -> str:
        return "R002"

    @property
    def description(self) -> str:
        return "Referenced variables must be defined in Input"

    def check(self, doc: PromptDocument) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        defined_names = {v.name for v in doc.input_variables}

        for ref in doc.all_references:
            if ref.name not in defined_names:
                section_label = ref.section.value if ref.section else "unknown"
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        severity=Severity.ERROR,
                        message=(
                            f'Variable "{{{{{ref.name}}}}}" is used in {section_label} '
                            f"but not defined in Input"
                        ),
                        position=ref.position,
                        path=doc.path,
                    )
                )

        return diagnostics
