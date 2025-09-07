#!/usr/bin/env python3
"""
Ghostbusters Agents - Expert agents for delusion detection
"""

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DelusionResult:
    """Result from delusion detection"""

    delusions: list[dict[str, Any]]
    confidence: float
    recommendations: list[str]


class BaseExpert(ABC):
    """Base class for all expert agents"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect delusions in the project"""


class SecurityExpert(BaseExpert):
    """Security expert for detecting security delusions"""

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect security-related delusions"""
        delusions = []
        recommendations = []

        # Check for hardcoded credentials
        credential_patterns = [
            r"sk-[a-zA-Z0-9]{48}",
            r"pk_[a-zA-Z0-9]{48}",
            r"AKIA[a-zA-Z0-9]{16}",
            r"ghp_[a-zA-Z0-9]{36}",
            r"gho_[a-zA-Z0-9]{36}",
        ]

        # Check for subprocess security vulnerabilities
        subprocess_patterns = [
            r"import subprocess",
            r"subprocess\.run",
            r"subprocess\.Popen",
            r"subprocess\.call",
            r"os\.system",
            r"os\.popen",
        ]

        # Check for security issues
        for py_file in project_path.rglob("*.py"):
            # Skip the agents.py file itself (contains detection patterns)
            if py_file.name == "agents.py":
                continue
            try:
                content = py_file.read_text()

                # Check for hardcoded credentials
                for pattern in credential_patterns:
                    if re.search(pattern, content):
                        delusions.append(
                            {
                                "type": "security_vulnerability",
                                "file": str(py_file),
                                "pattern": pattern,
                                "priority": "high",
                                "description": f"Potential hardcoded credential found: {pattern}",
                            },
                        )

                # Check for subprocess vulnerabilities
                for pattern in subprocess_patterns:
                    if re.search(pattern, content):
                        delusions.append(
                            {
                                "type": "subprocess_vulnerability",
                                "file": str(py_file),
                                "pattern": pattern,
                                "priority": "critical",
                                "description": f"Subprocess usage detected: {pattern} - Security risk for command injection",
                            },
                        )

            except Exception as e:
                self.logger.warning(f"Could not read {py_file}: {e}")

        confidence = 0.8 if delusions else 0.9
        recommendations = [
            "Use environment variables for credentials",
            "Implement secret management",
            "Replace subprocess calls with native Python operations",
            "Use Go/Rust for performance-critical shell operations",
            "Implement gRPC shell service for secure command execution",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
        )


class CodeQualityExpert(BaseExpert):
    """Code quality expert for detecting code quality issues"""

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect code quality issues"""
        delusions = []
        recommendations = []

        # Check for code quality issues
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split("\n")

                # Check for missing type annotations
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith("def ") and "->" not in line:
                        delusions.append(
                            {
                                "type": "missing_type_annotation",
                                "file": str(py_file),
                                "line": i,
                                "priority": "medium",
                                "description": "Missing type annotation in function definition",
                            },
                        )

                # Check for inconsistent indentation
                for i, line in enumerate(lines, 1):
                    if (
                        line.strip()
                        and not line.startswith(" ")
                        and not line.startswith("\t")
                    ):
                        # Check if previous line was indented
                        if (
                            i > 1
                            and lines[i - 2].strip()
                            and (
                                lines[i - 2].startswith(" ")
                                or lines[i - 2].startswith("\t")
                            )
                        ):
                            delusions.append(
                                {
                                    "type": "inconsistent_indentation",
                                    "file": str(py_file),
                                    "line": i,
                                    "priority": "low",
                                    "description": "Inconsistent indentation detected",
                                },
                            )

            except Exception as e:
                self.logger.warning(f"Could not read {py_file}: {e}")

        confidence = 0.7 if delusions else 0.9
        recommendations = [
            "Use consistent indentation",
            "Add type annotations to all functions",
            "Run linters",
            "Use black for code formatting",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
        )


class TestExpert(BaseExpert):
    """Test expert for detecting test-related issues"""

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect test-related issues"""
        delusions = []
        recommendations = []

        # Check for test coverage
        test_files = list(project_path.rglob("test_*.py")) + list(
            project_path.rglob("*_test.py"),
        )
        py_files = list(project_path.rglob("*.py"))

        if len(test_files) < len(py_files) * 0.1:  # Less than 10% test files
            delusions.append(
                {
                    "type": "low_test_coverage",
                    "file": "tests/",
                    "priority": "medium",
                    "description": f"Low test coverage: {len(test_files)} test files vs {len(py_files)} source files",
                },
            )

        # Check for missing __init__.py files
        for test_dir in project_path.rglob("tests"):
            if test_dir.is_dir() and not (test_dir / "__init__.py").exists():
                delusions.append(
                    {
                        "type": "missing_init_file",
                        "file": str(test_dir),
                        "priority": "low",
                        "description": "Missing __init__.py in tests directory",
                    },
                )

        confidence = 0.8 if delusions else 0.9
        recommendations = [
            "Increase test coverage",
            "Add __init__.py files to test directories",
            "Use pytest for testing",
            "Implement integration tests",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
        )


class BuildExpert(BaseExpert):
    """Build expert for detecting build-related issues"""

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect build-related issues"""
        delusions = []
        recommendations = []

        # Check for missing requirements files
        requirements_files = ["requirements.txt", "pyproject.toml", "setup.py"]
        found_requirements = []

        for req_file in requirements_files:
            if (project_path / req_file).exists():
                found_requirements.append(req_file)

        if not found_requirements:
            delusions.append(
                {
                    "type": "missing_requirements",
                    "file": ".",
                    "priority": "high",
                    "description": "No requirements file found",
                },
            )

        # Check for missing README
        if not (project_path / "README.md").exists():
            delusions.append(
                {
                    "type": "missing_readme",
                    "file": ".",
                    "priority": "medium",
                    "description": "Missing README.md file",
                },
            )

        confidence = 0.8 if delusions else 0.9
        recommendations = [
            "Add requirements.txt or pyproject.toml",
            "Create a README.md file",
            "Use proper dependency management",
            "Document build process",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
        )


class ArchitectureExpert(BaseExpert):
    """Architecture expert for detecting architectural issues"""

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect architectural issues"""
        delusions = []
        recommendations = []

        # Check for proper module structure
        src_dir = project_path / "src"
        if not src_dir.exists():
            delusions.append(
                {
                    "type": "missing_src_directory",
                    "file": ".",
                    "priority": "medium",
                    "description": "Missing src/ directory for proper module structure",
                },
            )

        # Check for __init__.py files in packages
        for py_dir in project_path.rglob("*/"):
            if (
                py_dir.is_dir()
                and list(py_dir.glob("*.py"))
                and not (py_dir / "__init__.py").exists()
            ):
                delusions.append(
                    {
                        "type": "missing_init_file",
                        "file": str(py_dir),
                        "priority": "low",
                        "description": f"Missing __init__.py in {py_dir.name} directory",
                    },
                )

        confidence = 0.8 if delusions else 0.9
        recommendations = [
            "Use src/ directory structure",
            "Add __init__.py files to packages",
            "Follow Python packaging standards",
            "Organize code into logical modules",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
        )


class ModelExpert(BaseExpert):
    """Model expert for detecting model-related issues"""

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect model-related issues"""
        delusions = []
        recommendations = []

        # Check for model validation
        model_files = list(project_path.rglob("*model*.py")) + list(
            project_path.rglob("*schema*.py"),
        )

        if not model_files:
            delusions.append(
                {
                    "type": "missing_model_validation",
                    "file": ".",
                    "priority": "medium",
                    "description": "No model validation files found",
                },
            )

        # Check for proper data structures
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if (
                    "class " in content
                    and "dataclass" not in content
                    and "@dataclass" not in content
                ):
                    # Check if it's a data class without proper decorator
                    if "def __init__" in content:
                        delusions.append(
                            {
                                "type": "manual_dataclass",
                                "file": str(py_file),
                                "priority": "low",
                                "description": "Consider using @dataclass instead of manual __init__",
                            },
                        )
            except Exception as e:
                self.logger.warning(f"Could not read {py_file}: {e}")

        confidence = 0.8 if delusions else 0.9
        recommendations = [
            "Use dataclasses for data structures",
            "Implement model validation",
            "Use Pydantic for complex models",
            "Add type hints to all classes",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
        )
