"""Base validator class for Ghostbusters validators."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result from validator validation."""

    is_valid: bool
    confidence: float
    issues: list[str]
    recommendations: list[str]
    validator_name: str


class BaseValidator(ABC):
    """Base class for all validators."""

    def __init__(self, name: str):
        """Initialize the validator."""
        self.name = name
        self.confidence_threshold = 0.7

    @abstractmethod
    async def validate_findings(
        self,
        findings: list[dict[str, Any]],
    ) -> ValidationResult:
        """Validate findings from expert agents."""

    def _calculate_confidence(self, issues: list[str]) -> float:
        """Calculate confidence score based on validation issues."""
        if not issues:
            return 0.9  # High confidence if no issues found

        # Lower confidence with more issues
        return max(0.1, 1.0 - (len(issues) * 0.1))

    def _create_issue(self, message: str, severity: str = "medium") -> str:
        """Create a standardized issue message."""
        return f"[{self.name}] {message} (Severity: {severity})"

    def _create_recommendation(self, message: str, priority: str = "medium") -> str:
        """Create a standardized recommendation."""
        return f"[{self.name}] {message} (Priority: {priority})"
