"""Base expert class for Ghostbusters agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DelusionResult:
    """Result from expert agent delusion detection."""

    delusions: list[dict[str, Any]]
    confidence: float
    recommendations: list[str]
    agent_name: str


class BaseExpert(ABC):
    """Base class for all expert agents."""

    def __init__(self, name: str):
        """Initialize the expert agent."""
        self.name = name
        self.confidence_threshold = 0.7

    @abstractmethod
    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect delusions in the project."""

    def _calculate_confidence(self, delusions: list[dict[str, Any]]) -> float:
        """Calculate confidence score based on delusions found."""
        if not delusions:
            return 0.9  # High confidence if no issues found

        # Calculate confidence based on number and severity of delusions
        total_confidence = 0.0
        for delusion in delusions:
            confidence = delusion.get("confidence", 0.5)
            severity = delusion.get("severity", "medium")

            # Adjust confidence based on severity
            if severity == "high":
                confidence *= 1.2
            elif severity == "low":
                confidence *= 0.8

            total_confidence += confidence

        return min(total_confidence / len(delusions), 1.0)

    def _create_delusion(
        self,
        delusion_type: str,
        file_path: str,
        line: int,
        description: str,
        confidence: float,
        severity: str = "medium",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a standardized delusion object."""
        return {
            "type": delusion_type,
            "file": file_path,
            "line": line,
            "description": description,
            "confidence": confidence,
            "severity": severity,
            "agent": self.name,
            **kwargs,
        }

    def _create_recommendation(self, message: str, priority: str = "medium") -> str:
        """Create a standardized recommendation."""
        return f"[{self.name}] {message} (Priority: {priority})"
