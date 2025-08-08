"""Base recovery engine class for Ghostbusters recovery engines."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator


class RecoveryResult(BaseModel):
    """Result from recovery engine execution."""

    success: bool
    message: str
    confidence: float = Field(ge=0.0, le=1.0)
    changes_made: List[str] = Field(default_factory=list)
    engine_name: str

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Ensure confidence is between 0.0 and 1.0."""
        return max(0.0, min(1.0, v))


class BaseRecoveryEngine(ABC):
    """Base class for all recovery engines."""

    def __init__(self, name: str):
        """Initialize the recovery engine."""
        self.name = name
        self.confidence_threshold = 0.7

    @abstractmethod
    async def execute_recovery(self, action: Dict[str, Any]) -> RecoveryResult:
        """Execute recovery action."""

    def _calculate_confidence(self, changes_made: List[str]) -> float:
        """Calculate confidence score based on recovery success."""
        if not changes_made:
            return 0.5  # Medium confidence if no changes made

        # Higher confidence with more successful changes
        return min(0.9, 0.5 + (len(changes_made) * 0.1))

    def _create_change_message(self, change: str) -> str:
        """Create a standardized change message."""
        return f"[{self.name}] {change}"

    def _create_success_message(self, action_type: str) -> str:
        """Create a standardized success message."""
        return f"Successfully executed {action_type} recovery"

    def _create_failure_message(self, action_type: str, error: str) -> str:
        """Create a standardized failure message."""
        return f"Failed to execute {action_type} recovery: {error}"
