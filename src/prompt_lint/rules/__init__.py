"""Rule system for prompt-lint."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prompt_lint.models import Diagnostic, PromptDocument


class RuleBase(ABC):
    """Base class for all lint rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def check(self, doc: PromptDocument) -> list[Diagnostic]: ...


def get_all_rules() -> list[RuleBase]:
    """Return instances of all built-in rules."""
    from prompt_lint.rules.frontmatter import FrontmatterRule
    from prompt_lint.rules.output_reachable import OutputReachableRule
    from prompt_lint.rules.required_sections import RequiredSectionsRule
    from prompt_lint.rules.variable_defined import VariableDefinedRule
    from prompt_lint.rules.variable_unused import VariableUnusedRule

    return [
        RequiredSectionsRule(),
        VariableDefinedRule(),
        VariableUnusedRule(),
        OutputReachableRule(),
        FrontmatterRule(),
    ]
