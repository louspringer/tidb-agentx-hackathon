"""Ghostbusters validators for result validation."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator

from .base_validator import BaseValidator


class ValidationResult(BaseModel):
    """Result from validation"""

    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    validator_name: str = Field(default="unknown")

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Ensure confidence is between 0.0 and 1.0."""
        return max(0.0, min(1.0, v))


class SecurityValidator(BaseValidator):
    """Security validator for validating security findings"""

    def __init__(self) -> None:
        super().__init__("SecurityValidator")

    async def validate_findings(
        self,
        delusions: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate security findings"""
        issues = []
        recommendations = []

        for delusion in delusions:
            if delusion.get("agent") == "security":
                for delusion_item in delusion.get("delusions", []):
                    if delusion_item.get("type") == "security_vulnerability":
                        issues.append(
                            delusion_item.get(
                                "description",
                                "Security vulnerability found",
                            ),
                        )
                        recommendations.append("Remove hardcoded credentials")
                        recommendations.append("Use environment variables")

        confidence = 0.9 if not issues else 0.6
        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            validator_name="SecurityValidator",
        )


class CodeQualityValidator(BaseValidator):
    """Code quality validator for validating quality findings"""

    def __init__(self) -> None:
        super().__init__("CodeQualityValidator")

    async def validate_findings(
        self,
        delusions: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate code quality findings"""
        issues = []
        recommendations = []

        for delusion in delusions:
            if delusion.get("agent") == "code_quality":
                for delusion_item in delusion.get("delusions", []):
                    if delusion_item.get("type") in [
                        "syntax_error",
                        "indentation_error",
                    ]:
                        issues.append(
                            delusion_item.get(
                                "description",
                                "Code quality issue found",
                            ),
                        )
                        recommendations.append("Fix syntax errors")
                        recommendations.append("Use consistent indentation")

        confidence = 0.9 if not issues else 0.5
        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            validator_name="CodeQualityValidator",
        )


class TestValidator(BaseValidator):
    """Test validator for validating test findings"""

    def __init__(self) -> None:
        super().__init__("TestValidator")

    async def validate_findings(
        self,
        delusions: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate test findings"""
        issues = []
        recommendations = []

        for delusion in delusions:
            if delusion.get("agent") == "test":
                for delusion_item in delusion.get("delusions", []):
                    if delusion_item.get("type") in [
                        "test_coverage_issue",
                        "test_failure",
                    ]:
                        issues.append(
                            delusion_item.get("description", "Test issue found"),
                        )
                        recommendations.append("Add more tests")
                        recommendations.append("Fix failing tests")

        confidence = 0.9 if not issues else 0.7
        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            validator_name="TestValidator",
        )


class BuildValidator(BaseValidator):
    """Build validator for validating build findings"""

    def __init__(self) -> None:
        super().__init__("BuildValidator")

    async def validate_findings(
        self,
        delusions: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate build findings"""
        issues = []
        recommendations = []

        for delusion in delusions:
            if delusion.get("agent") == "build":
                for delusion_item in delusion.get("delusions", []):
                    if delusion_item.get("type") in [
                        "build_configuration_issue",
                        "dependency_issue",
                    ]:
                        issues.append(
                            delusion_item.get("description", "Build issue found"),
                        )
                        recommendations.append("Add missing build files")
                        recommendations.append("Configure dependencies properly")

        confidence = 0.9 if not issues else 0.8
        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            validator_name="BuildValidator",
        )


class ArchitectureValidator(BaseValidator):
    """Architecture validator for validating architectural findings"""

    def __init__(self) -> None:
        super().__init__("ArchitectureValidator")

    async def validate_findings(
        self,
        delusions: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate architectural findings"""
        issues = []
        recommendations = []

        for delusion in delusions:
            if delusion.get("agent") == "architecture":
                for delusion_item in delusion.get("delusions", []):
                    if delusion_item.get("type") in [
                        "architecture_issue",
                        "module_structure_issue",
                    ]:
                        issues.append(
                            delusion_item.get(
                                "description",
                                "Architecture issue found",
                            ),
                        )
                        recommendations.append("Organize code in src directory")
                        recommendations.append("Add __init__.py files")

        confidence = 0.9 if not issues else 0.8
        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            validator_name="ArchitectureValidator",
        )


class ModelValidator(BaseValidator):
    """Model validator for validating model findings"""

    def __init__(self) -> None:
        super().__init__("ModelValidator")

    async def validate_findings(
        self,
        delusions: List[Dict[str, Any]],
    ) -> ValidationResult:
        """Validate model findings"""
        issues = []
        recommendations = []

        for delusion in delusions:
            if delusion.get("agent") == "model":
                for delusion_item in delusion.get("delusions", []):
                    if delusion_item.get("type") in [
                        "model_registry_issue",
                        "model_structure_issue",
                    ]:
                        issues.append(
                            delusion_item.get("description", "Model issue found"),
                        )
                        recommendations.append("Add model registry")
                        recommendations.append("Structure models properly")

        confidence = 0.9 if not issues else 0.8
        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            validator_name="ModelValidator",
        )


__all__ = [
    "BaseValidator",
    "ValidationResult",
    "ArchitectureValidator",
    "BuildValidator",
    "CodeQualityValidator",
    "ModelValidator",
    "SecurityValidator",
    "TestValidator",
]
