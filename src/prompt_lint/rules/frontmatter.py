"""R005: Frontmatter must contain required fields."""

from __future__ import annotations

from prompt_lint.models import (
    Diagnostic,
    Position,
    PromptDocument,
    REQUIRED_FRONTMATTER_FIELDS,
    Severity,
)
from prompt_lint.rules import RuleBase


class FrontmatterRule(RuleBase):
    @property
    def rule_id(self) -> str:
        return "R005"

    @property
    def description(self) -> str:
        return "Frontmatter must contain required fields"

    def check(self, doc: PromptDocument) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        if doc.frontmatter is None:
            diagnostics.append(
                Diagnostic(
                    rule_id=self.rule_id,
                    severity=Severity.ERROR,
                    message="YAML frontmatter is missing",
                    position=Position(line=1),
                    path=doc.path,
                )
            )
            return diagnostics

        for field_name in REQUIRED_FRONTMATTER_FIELDS:
            if field_name not in doc.frontmatter.data:
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        severity=Severity.ERROR,
                        message=f'Required frontmatter field "{field_name}" is missing',
                        position=Position(line=doc.frontmatter.start_line),
                        path=doc.path,
                    )
                )
            elif not doc.frontmatter.data[field_name]:
                diagnostics.append(
                    Diagnostic(
                        rule_id=self.rule_id,
                        severity=Severity.ERROR,
                        message=f'Required frontmatter field "{field_name}" is empty',
                        position=Position(line=doc.frontmatter.start_line),
                        path=doc.path,
                    )
                )

        return diagnostics
