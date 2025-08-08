"""Base validator class for Ghostbusters validators."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator


class ValidationResult(BaseModel):
    """Result from validator validation."""

    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    validator_name: str

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Ensure confidence is between 0.0 and 1.0."""
        return max(0.0, min(1.0, v))


class BaseValidator(ABC):
    """Base class for all validators."""

    def __init__(self, name: str):
        """Initialize the validator."""
        self.name = name
        self.confidence_threshold = 0.7

    @abstractmethod
    async def validate_findings(
        self,
        findings: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate findings from expert agents."""

    def _calculate_confidence(self, issues: List[str]) -> float:
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
