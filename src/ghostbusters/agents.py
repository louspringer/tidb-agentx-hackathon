#!/usr/bin/env python3
"""
Ghostbusters Agents - Expert agents for delusion detection
"""

import logging
from pathlib import Path

# Import the new pydantic-based classes
from .agents.base_expert import BaseExpert, DelusionResult


class SecurityExpert(BaseExpert):
    """Security expert for detecting security delusions"""

    def __init__(self):
        super().__init__("SecurityExpert")
        self.logger = logging.getLogger(self.__class__.__name__)

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
            try:
                content = py_file.read_text()

                # Check for hardcoded credentials
                for pattern in credential_patterns:
                    if pattern in content:
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
                    if pattern in content:
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
            "Integrate GitHub MCP for intelligent repository analysis",
            "Use mcp-git-ingest for structured repository context",
            "Add timeouts and resource limits to all subprocess calls",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )


class CodeQualityExpert(BaseExpert):
    """Code quality expert for detecting quality delusions"""

    def __init__(self):
        super().__init__("CodeQualityExpert")
        self.logger = logging.getLogger(self.__class__.__name__)

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect code quality delusions"""
        delusions = []
        recommendations = []

        # Check for syntax errors
        for py_file in project_path.rglob("*.py"):
            try:
                compile(py_file.read_text(), str(py_file), "exec")
            except SyntaxError as e:
                delusions.append(
                    {
                        "type": "syntax_error",
                        "file": str(py_file),
                        "error": str(e),
                        "priority": "high",
                        "description": f"Syntax error in {py_file.name}: {e}",
                    },
                )
            except Exception as e:
                self.logger.warning(f"Could not compile {py_file}: {e}")

        # Check for indentation issues
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if line.strip() and not line.startswith(" ") and i > 1:
                        prev_line = lines[i - 2] if i > 1 else ""
                        if prev_line.strip() and prev_line.rstrip().endswith(":"):
                            delusions.append(
                                {
                                    "type": "indentation_error",
                                    "file": str(py_file),
                                    "line": i,
                                    "priority": "medium",
                                    "description": f"Potential indentation error at line {i}",
                                },
                            )
            except Exception as e:
                self.logger.warning(f"Could not check {py_file}: {e}")

        confidence = 0.7 if delusions else 0.9
        recommendations = [
            "Fix syntax errors",
            "Use consistent indentation",
            "Run linters",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )


class TestExpert(BaseExpert):
    """Test expert for detecting test-related delusions"""

    def __init__(self):
        super().__init__("TestExpert")
        self.logger = logging.getLogger(self.__class__.__name__)

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect test-related delusions"""
        delusions = []
        recommendations = []

        # Check for missing tests
        test_files = list(project_path.rglob("test_*.py"))
        source_files = list(project_path.rglob("*.py"))
        source_files = [f for f in source_files if not f.name.startswith("test_")]

        if len(source_files) > len(test_files) * 2:
            delusions.append(
                {
                    "type": "test_coverage_issue",
                    "priority": "medium",
                    "description": f"Low test coverage: {len(test_files)} test files vs {len(source_files)} source files",
                },
            )

        # Check for failing tests
        for test_file in test_files:
            try:
                # This is a simplified check - in practice you'd run pytest
                content = test_file.read_text()
                if "assert False" in content or "pytest.fail" in content:
                    delusions.append(
                        {
                            "type": "test_failure",
                            "file": str(test_file),
                            "priority": "medium",
                            "description": f"Test file contains failing assertions: {test_file.name}",
                        },
                    )
            except Exception as e:
                self.logger.warning(f"Could not check {test_file}: {e}")

        confidence = 0.8 if delusions else 0.9
        recommendations = [
            "Add more tests",
            "Fix failing tests",
            "Improve test coverage",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )


class BuildExpert(BaseExpert):
    """Build expert for detecting build-related delusions"""

    def __init__(self):
        super().__init__("BuildExpert")
        self.logger = logging.getLogger(self.__class__.__name__)

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect build-related delusions"""
        delusions = []
        recommendations = []

        # Check for missing build files
        build_files = ["pyproject.toml", "setup.py", "requirements.txt"]
        missing_files = []

        for build_file in build_files:
            if not (project_path / build_file).exists():
                missing_files.append(build_file)

        if missing_files:
            delusions.append(
                {
                    "type": "build_configuration_issue",
                    "priority": "medium",
                    "description": f"Missing build files: {', '.join(missing_files)}",
                },
            )

        # Check for dependency issues
        if (project_path / "pyproject.toml").exists():
            try:
                import tomllib

                with open(project_path / "pyproject.toml", "rb") as f:
                    config = tomllib.load(f)
                if "project" not in config or "dependencies" not in config["project"]:
                    delusions.append(
                        {
                            "type": "dependency_issue",
                            "priority": "low",
                            "description": "Missing dependencies in pyproject.toml",
                        },
                    )
            except Exception as e:
                self.logger.warning(f"Could not parse pyproject.toml: {e}")

        confidence = 0.8 if delusions else 0.9
        recommendations = ["Add missing build files", "Configure dependencies properly"]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )


class ArchitectureExpert(BaseExpert):
    """Architecture expert for detecting architectural delusions"""

    def __init__(self):
        super().__init__("ArchitectureExpert")
        self.logger = logging.getLogger(self.__class__.__name__)

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect architectural delusions"""
        delusions = []
        recommendations = []

        # Check for proper module structure
        src_dirs = list(project_path.rglob("src"))
        if not src_dirs:
            delusions.append(
                {
                    "type": "architecture_issue",
                    "priority": "low",
                    "description": "No src directory found - consider organizing code",
                },
            )

        # Check for __init__.py files
        py_dirs = [
            d for d in project_path.rglob("*") if d.is_dir() and any(d.glob("*.py"))
        ]
        for py_dir in py_dirs:
            if not (py_dir / "__init__.py").exists():
                delusions.append(
                    {
                        "type": "module_structure_issue",
                        "priority": "low",
                        "description": f"Missing __init__.py in {py_dir.relative_to(project_path)}",
                    },
                )

        confidence = 0.8 if delusions else 0.9
        recommendations = ["Organize code in src directory", "Add __init__.py files"]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )


class ModelExpert(BaseExpert):
    """Model expert for detecting model-related delusions"""

    def __init__(self):
        super().__init__("ModelExpert")
        self.logger = logging.getLogger(self.__class__.__name__)

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect model-related delusions"""
        delusions = []
        recommendations = []

        # Check for model registry
        model_files = list(project_path.rglob("*model*.json"))
        if not model_files:
            delusions.append(
                {
                    "type": "model_registry_issue",
                    "priority": "medium",
                    "description": "No model registry found - consider adding project_model_registry.json",
                },
            )

        # Check for proper model structure
        for model_file in model_files:
            try:
                import json

                with open(model_file) as f:
                    model_data = json.load(f)
                if "domains" not in model_data:
                    delusions.append(
                        {
                            "type": "model_structure_issue",
                            "file": str(model_file),
                            "priority": "medium",
                            "description": f"Model file {model_file.name} missing domains section",
                        },
                    )
            except Exception as e:
                self.logger.warning(f"Could not parse {model_file}: {e}")

        confidence = 0.8 if delusions else 0.9
        recommendations = ["Add model registry", "Structure models properly"]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )


class MCPExpert(BaseExpert):
    """MCP expert for detecting MCP-related delusions"""

    def __init__(self):
        super().__init__("MCPExpert")
        self.logger = logging.getLogger(self.__class__.__name__)

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect MCP-related delusions"""
        delusions = []
        recommendations = []

        # Check for MCP integration files
        mcp_integration_dir = project_path / "src" / "mcp_integration"
        if not mcp_integration_dir.exists():
            delusions.append(
                {
                    "type": "missing_mcp_integration",
                    "file": str(mcp_integration_dir),
                    "priority": "high",
                    "description": "Missing MCP integration directory - needed for intelligent repository analysis",
                },
            )

        # Check for GitHub MCP client
        github_mcp_client = mcp_integration_dir / "github_mcp_client.py"
        if not github_mcp_client.exists():
            delusions.append(
                {
                    "type": "missing_github_mcp_client",
                    "file": str(github_mcp_client),
                    "priority": "high",
                    "description": "Missing GitHub MCP client - needed for repository analysis",
                },
            )

        # Check for mcp-git-ingest integration
        mcp_git_ingest_dir = project_path / "mcp-git-ingest"
        if not mcp_git_ingest_dir.exists():
            delusions.append(
                {
                    "type": "missing_mcp_git_ingest",
                    "file": str(mcp_git_ingest_dir),
                    "priority": "medium",
                    "description": "Missing mcp-git-ingest - consider integrating for better repository analysis",
                },
            )

        # Check for manual file discovery patterns
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Check for manual file discovery instead of MCP
                manual_patterns = [
                    r"list_dir\(",
                    r"file_search\(",
                    r"grep_search\(",
                    r"codebase_search\(",
                ]

                for pattern in manual_patterns:
                    if pattern in content:
                        delusions.append(
                            {
                                "type": "manual_file_discovery",
                                "file": str(py_file),
                                "pattern": pattern,
                                "priority": "medium",
                                "description": f"Manual file discovery detected: {pattern} - consider using MCP for intelligent context",
                            },
                        )

            except Exception as e:
                self.logger.warning(f"Could not read {py_file}: {e}")

        confidence = 0.8 if delusions else 0.9
        recommendations = [
            "Integrate GitHub MCP for intelligent repository analysis",
            "Use mcp-git-ingest for structured repository context",
            "Replace manual file discovery with MCP-based analysis",
            "Implement intelligent file prioritization via MCP",
            "Enable structured repository context for AI tools",
        ]

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )
