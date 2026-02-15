"""R001: Required sections must exist and be non-empty."""

from __future__ import annotations

from prompt_lint.models import (
    Diagnostic,
    Position,
    PromptDocument,
    REQUIRED_SECTIONS,
    SectionKind,
    Severity,
)
from prompt_lint.rules import RuleBase


class RequiredSectionsRule(RuleBase):
    @property
    def rule_id(self) -> str:
        return "R001"

    @property
    def description(self) -> str:
        return "Required sections must exist and be non-empty"

    def check(self, doc: PromptDocument) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        present_kinds = {s.kind for s in doc.sections}

        for required in REQUIRED_SECTIONS:
            if required not in present_kinds:
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        severity=Severity.ERROR,
                        message=f'Required section "{required.value}" is missing',
                        position=Position(line=1),
                        path=doc.path,
                    )
                )
            else:
                section = doc.get_section(required)
                if section and not section.content.strip():
                    diagnostics.append(
                        Diagnostic(
                            rule_id=self.rule_id,
                            severity=Severity.ERROR,
                            message=f'Required section "{required.value}" is empty',
                            position=Position(line=section.start_line),
                            path=doc.path,
                        )
                    )

        return diagnostics
