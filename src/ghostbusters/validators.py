#!/usr/bin/env python3
"""
Ghostbusters Validators - Validation components for findings
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ValidationResult:
    """Result from validation"""

    is_valid: bool
    confidence: float
    issues: List[str]
    recommendations: List[str]


class BaseValidator(ABC):
    """Base class for all validators"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def validate_findings(
        self, delusions: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Validate findings from delusion detection"""
        pass


class SecurityValidator(BaseValidator):
    """Security validator for validating security findings"""

    async def validate_findings(
        self, delusions: List[Dict[str, Any]]
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
                                "description", "Security vulnerability found"
                            )
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
        )


class CodeQualityValidator(BaseValidator):
    """Code quality validator for validating quality findings"""

    async def validate_findings(
        self, delusions: List[Dict[str, Any]]
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
                            delusion_item.get("description", "Code quality issue found")
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
        )


class TestValidator(BaseValidator):
    """Test validator for validating test findings"""

    async def validate_findings(
        self, delusions: List[Dict[str, Any]]
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
                            delusion_item.get("description", "Test issue found")
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
        )


class BuildValidator(BaseValidator):
    """Build validator for validating build findings"""

    async def validate_findings(
        self, delusions: List[Dict[str, Any]]
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
                            delusion_item.get("description", "Build issue found")
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
        )


class ArchitectureValidator(BaseValidator):
    """Architecture validator for validating architectural findings"""

    async def validate_findings(
        self, delusions: List[Dict[str, Any]]
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
                            delusion_item.get("description", "Architecture issue found")
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
        )


class ModelValidator(BaseValidator):
    """Model validator for validating model findings"""

    async def validate_findings(
        self, delusions: List[Dict[str, Any]]
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
                            delusion_item.get("description", "Model issue found")
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
        )
