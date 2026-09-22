"""
Base class for domain-specific AI handlers.
Each domain provides its own system prompt, provider config, and context formatting.
"""

from abc import ABC, abstractmethod


class BaseDomainHandler(ABC):
    """Abstract base for all 6 domain handlers."""

    @property
    @abstractmethod
    def domain_key(self) -> str:
        """Short key for routing: CP, WebDev, ML, DSA, Systems, InfoSec."""
        ...

    @property
    @abstractmethod
    def provider(self) -> str:
        """AI provider: 'groq' or 'deepseek'."""
        ...

    @property
    @abstractmethod
    def model(self) -> str:
        """Model identifier for the provider."""
        ...

    @property
    @abstractmethod
    def persona(self) -> str:
        """Display name of the AI persona."""
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Persona-locked system prompt for this domain."""
        ...

    def format_context(self, weak_concepts: list[dict]) -> str:
        """
        Format shadow memory concepts into a string for system prompt injection.
        Default implementation works for most domains.
        """
        if not weak_concepts:
            return ""
        parts = [f"{c['concept']} (Score: {c['proficiency']}/10)" for c in weak_concepts]
        return f"User's known weak concepts: {', '.join(parts)}."
