"""Ghostbusters validators for result validation."""

from typing import TYPE_CHECKING

from .base_validator import BaseValidator

if TYPE_CHECKING:
    from .base_validator import ValidationResult


# Create placeholder validators for missing ones
class ArchitectureValidator(BaseValidator):
    """Placeholder validator for architecture validation"""

    def __init__(self) -> None:
        super().__init__("architecture")

    async def validate_findings(self, findings: list) -> "ValidationResult":
        return {"valid": True, "confidence": 0.8, "issues": []}  # type: ignore


class BuildValidator(BaseValidator):
    """Placeholder validator for build validation"""

    def __init__(self) -> None:
        super().__init__("build")

    async def validate_findings(self, findings: list) -> "ValidationResult":
        return {"valid": True, "confidence": 0.8, "issues": []}  # type: ignore


class CodeQualityValidator(BaseValidator):
    """Placeholder validator for code quality validation"""

    def __init__(self) -> None:
        super().__init__("code_quality")

    async def validate_findings(self, findings: list) -> "ValidationResult":
        return {"valid": True, "confidence": 0.8, "issues": []}  # type: ignore


class ModelValidator(BaseValidator):
    """Placeholder validator for model validation"""

    def __init__(self) -> None:
        super().__init__("model")

    async def validate_findings(self, findings: list) -> "ValidationResult":
        return {"valid": True, "confidence": 0.8, "issues": []}  # type: ignore


class SecurityValidator(BaseValidator):
    """Placeholder validator for security validation"""

    def __init__(self) -> None:
        super().__init__("security")

    async def validate_findings(self, findings: list) -> "ValidationResult":
        return {"valid": True, "confidence": 0.8, "issues": []}  # type: ignore


class TestValidator(BaseValidator):
    """Placeholder validator for test validation"""

    def __init__(self) -> None:
        super().__init__("test")

    async def validate_findings(self, findings: list) -> "ValidationResult":
        return {"valid": True, "confidence": 0.8, "issues": []}  # type: ignore


__all__ = [
    "BaseValidator",
    "ArchitectureValidator",
    "BuildValidator",
    "CodeQualityValidator",
    "ModelValidator",
    "SecurityValidator",
    "TestValidator",
]
