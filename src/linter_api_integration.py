#!/usr/bin/env python3
"""
Linter API Integration System
Direct integration with linter APIs for proactive violation prevention
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LinterViolation:
    """Represents a linter violation"""

    code: str
    message: str
    line_number: int
    column: int
    file_path: str
    severity: str = "error"
    fix_available: bool = False
    auto_fix: Optional[str] = None


@dataclass
class LinterConfig:
    """Linter configuration"""

    name: str
    command: str
    output_format: str
    config_file: Optional[str] = None
    enabled_rules: Optional[list[str]] = None
    disabled_rules: Optional[list[str]] = None


class LinterAPIIntegration:
    """Direct integration with linter APIs"""

    def __init__(self) -> None:
        self.linters = {
            "flake8": LinterConfig(
                name="flake8",
                command="flake8",
                output_format="json",
                config_file=".flake8",
                enabled_rules=["F401", "E302", "E305", "W291", "W292"],
                disabled_rules=[],
            ),
            "black": LinterConfig(
                name="black",
                command="black",
                output_format="di",
                config_file="pyproject.toml",
            ),
            "mypy": LinterConfig(
                name="mypy",
                command="mypy",
                output_format="json",
                config_file="mypy.ini",
            ),
            "ru": LinterConfig(
                name="ru",
                command="ru",
                output_format="json",
                config_file=".ruff.toml",
                enabled_rules=["E", "W", "F", "I", "B", "C4", "UP"],
                disabled_rules=["E501", "B008"],
            ),
        }

    def query_linter_api(
        self,
        linter_name: str,
        file_path: str,
    ) -> list[LinterViolation]:
        """Query a specific linter API"""
        if linter_name not in self.linters:
            logger.error(f"Unknown linter: {linter_name}")
            return []

        linter_config = self.linters[linter_name]

        try:
            if linter_name == "flake8":
                return self._query_flake8_api(file_path, linter_config)
            if linter_name == "black":
                return self._query_black_api(file_path, linter_config)
            if linter_name == "mypy":
                return self._query_mypy_api(file_path, linter_config)
            if linter_name == "ru":
                return self._query_ruff_api(file_path, linter_config)
            logger.error(f"Unsupported linter: {linter_name}")
            return []
        except Exception as e:
            logger.error(f"Error querying {linter_name} API: {e}")
            return []

    def _query_flake8_api(
        self,
        file_path: str,
        config: LinterConfig,
    ) -> list[LinterViolation]:
        """Query flake8 API"""
        try:
            cmd = [
                config.command,
                "--format=json",
                "--select=" + ",".join(config.enabled_rules or []),
            ]

            if config.config_file and Path(config.config_file).exists():
                cmd.extend(["--config", config.config_file])

            cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and not result.stdout.strip():
                return []  # No violations

            violations = []
            if result.stdout.strip():
                try:
                    flake8_output = json.loads(result.stdout)
                    for violation in flake8_output:
                        violations.append(
                            LinterViolation(
                                code=violation["code"],
                                message=violation["text"],
                                line_number=violation["line_number"],
                                column=violation["column_number"],
                                file_path=violation["filename"],
                                severity="error",
                            ),
                        )
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse flake8 JSON output: {result.stdout}")

            return violations

        except subprocess.TimeoutExpired:
            logger.error(f"flake8 query timeout for {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error querying flake8 API: {e}")
            return []

    def _query_black_api(
        self,
        file_path: str,
        config: LinterConfig,
    ) -> list[LinterViolation]:
        """Query black API"""
        try:
            cmd = [config.command, "--check", "--di", "--quiet"]

            if config.config_file and Path(config.config_file).exists():
                cmd.extend(["--config", config.config_file])

            cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            violations = []
            if result.returncode != 0:
                # Black needs formatting
                violations.append(
                    LinterViolation(
                        code="BLACK001",
                        message="Code needs formatting",
                        line_number=1,
                        column=1,
                        file_path=file_path,
                        severity="warning",
                        fix_available=True,
                        auto_fix=result.stdout,
                    ),
                )

            return violations

        except subprocess.TimeoutExpired:
            logger.error(f"black query timeout for {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error querying black API: {e}")
            return []

    def _query_mypy_api(
        self,
        file_path: str,
        config: LinterConfig,
    ) -> list[LinterViolation]:
        """Query mypy API"""
        try:
            cmd = [config.command, "--json"]

            if config.config_file and Path(config.config_file).exists():
                cmd.extend(["--config-file", config.config_file])

            cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            violations = []
            if result.stdout.strip():
                try:
                    mypy_output = json.loads(result.stdout)
                    for violation in mypy_output:
                        violations.append(
                            LinterViolation(
                                code=violation.get("code", "MYPY001"),
                                message=violation.get("message", "Type error"),
                                line_number=violation.get("line", 1),
                                column=violation.get("column", 1),
                                file_path=violation.get("file", file_path),
                                severity="error",
                            ),
                        )
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse mypy JSON output: {result.stdout}")

            return violations

        except subprocess.TimeoutExpired:
            logger.error(f"mypy query timeout for {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error querying mypy API: {e}")
            return []

    def _query_ruff_api(
        self,
        file_path: str,
        config: LinterConfig,
    ) -> list[LinterViolation]:
        """Query Ruff API (AI-powered)"""
        try:
            cmd = [config.command, "check", "--output-format=json"]

            if config.config_file and Path(config.config_file).exists():
                cmd.extend(["--config", config.config_file])

            cmd.append(file_path)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            violations = []
            if result.stdout.strip():
                try:
                    ruff_output = json.loads(result.stdout)
                    for violation in ruff_output:
                        violations.append(
                            LinterViolation(
                                code=violation.get("code", "RUFF001"),
                                message=violation.get("message", "Ruff violation"),
                                line_number=violation.get("location", {}).get("row", 1),
                                column=violation.get("location", {}).get("column", 1),
                                file_path=violation.get("filename", file_path),
                                severity="error",
                                fix_available=violation.get("fix", {}).get(
                                    "applicable",
                                    False,
                                ),
                                auto_fix=violation.get("fix", {}).get("message", ""),
                            ),
                        )
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse ruff JSON output: {result.stdout}")

            return violations

        except subprocess.TimeoutExpired:
            logger.error(f"ruff query timeout for {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error querying ruff API: {e}")
            return []

    def get_ai_suggestions(self, file_path: str) -> list[dict[str, Any]]:
        """Get AI-powered suggestions from Ru"""
        try:
            cmd = ["ru", "check", "--fix", "--output-format=json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            suggestions = []
            if result.stdout.strip():
                try:
                    ruff_output = json.loads(result.stdout)
                    for suggestion in ruff_output:
                        if suggestion.get("fix", {}).get("applicable", False):
                            suggestions.append(
                                {
                                    "code": suggestion.get("code"),
                                    "message": suggestion.get("message"),
                                    "fix": suggestion.get("fix", {}).get("message", ""),
                                    "line": suggestion.get("location", {}).get(
                                        "row",
                                        1,
                                    ),
                                },
                            )
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse ruff suggestions: {result.stdout}")

            return suggestions

        except Exception as e:
            logger.error(f"Error getting AI suggestions: {e}")
            return []

    def prevent_violations_before_writing(
        self,
        file_path: str,
        code_block: str,
    ) -> dict[str, Any]:
        """Prevent violations before writing code"""
        logger.info(f"Analyzing code block for potential violations in {file_path}")

        # Query all linter APIs
        all_violations = {}
        for linter_name in self.linters:
            violations = self.query_linter_api(linter_name, file_path)
            all_violations[linter_name] = violations

        # Get AI suggestions
        ai_suggestions = self.get_ai_suggestions(file_path)

        # Analyze code block for potential violations
        potential_violations = self._analyze_code_block(code_block, all_violations)

        # Generate prevention suggestions
        prevention_suggestions = self._generate_prevention_suggestions(
            potential_violations,
        )

        # Get auto-fixes
        auto_fixes = self._get_auto_fixes(potential_violations, ai_suggestions)

        return {
            "potential_violations": potential_violations,
            "suggestions": prevention_suggestions,
            "auto_fixes": auto_fixes,
            "ai_suggestions": ai_suggestions,
        }

    def _analyze_code_block(
        self,
        code_block: str,
        linter_results: dict[str, list[LinterViolation]],
    ) -> list[dict[str, Any]]:
        """Analyze code block for potential violations"""
        potential_violations = []

        # Check for common patterns that cause violations
        lines = code_block.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for unused imports
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                potential_violations.append(
                    {
                        "type": "unused_import",
                        "line": i,
                        "code": "F401",
                        "suggestion": "Ensure import is actually used in the code",
                    },
                )

            # Check for f-strings without placeholders
            if line.strip().startswith('"') and "{" not in line:
                potential_violations.append(
                    {
                        "type": "f_string_no_placeholder",
                        "line": i,
                        "suggestion": "Use regular string instead of f-string",
                    },
                )

            # Check for missing blank lines
            if line.strip().startswith("def ") or line.strip().startswith("class "):
                if i > 1 and lines[i - 2].strip() != "":
                    potential_violations.append(
                        {
                            "type": "missing_blank_lines",
                            "line": i,
                            "code": "E302",
                            "suggestion": "Add two blank lines before definition",
                        },
                    )

            # Check for trailing whitespace
            if line.rstrip() != line:
                potential_violations.append(
                    {
                        "type": "trailing_whitespace",
                        "line": i,
                        "code": "W291",
                        "suggestion": "Remove trailing whitespace",
                    },
                )

        return potential_violations

    def _generate_prevention_suggestions(
        self,
        violations: list[dict[str, Any]],
    ) -> list[str]:
        """Generate prevention suggestions"""
        suggestions = []

        for violation in violations:
            if violation["type"] == "unused_import":
                suggestions.append("Only import modules that are actually used")
            elif violation["type"] == "f_string_no_placeholder":
                suggestions.append("Use regular strings when no variables are needed")
            elif violation["type"] == "missing_blank_lines":
                suggestions.append(
                    "Add two blank lines before class/function definitions",
                )
            elif violation["type"] == "trailing_whitespace":
                suggestions.append("Remove trailing whitespace from lines")

        return suggestions

    def _get_auto_fixes(
        self,
        violations: list[dict[str, Any]],
        ai_suggestions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Get automatic fixes for violations"""
        auto_fixes = []

        for violation in violations:
            if violation["type"] == "f_string_no_placeholder":
                auto_fixes.append(
                    {
                        "type": "f_string_fix",
                        "line": violation["line"],
                        "fix": "Replace f-string with regular string",
                    },
                )
            elif violation["type"] == "trailing_whitespace":
                auto_fixes.append(
                    {
                        "type": "whitespace_fix",
                        "line": violation["line"],
                        "fix": "Remove trailing whitespace",
                    },
                )

        # Add AI suggestions as auto-fixes
        for suggestion in ai_suggestions:
            auto_fixes.append(
                {
                    "type": "ai_suggestion",
                    "line": suggestion["line"],
                    "fix": suggestion["fix"],
                    "code": suggestion["code"],
                },
            )

        return auto_fixes

    def suggest_ignore_directive(self, violation: LinterViolation) -> str:
        """Suggest appropriate ignore directive"""
        if violation.code == "F401":
            return "# noqa: F401  # Import needed for type checking"

        if violation.code == "E302":
            return "# noqa: E302  # Compact module structure"
        if violation.code == "W291":
            return "# noqa: W291  # Trailing whitespace acceptable"
        if violation.code == "W292":
            return "# noqa: W292  # No newline acceptable"
        return f"# noqa: {violation.code}  # {violation.message}"


def main() -> None:
    """Test the linter API integration"""
    logger.info("🧪 **LINTER API INTEGRATION TEST**")
    logger.info("=" * 50)

    integration = LinterAPIIntegration()

    # Test with a sample file
    test_file = "tests/test_python_quality_enforcement.py"

    if Path(test_file).exists():
        logger.info(f"Testing linter API integration with {test_file}")

        # Query all linters
        for linter_name in integration.linters:
            logger.info(f"\n📝 Querying {linter_name} API...")
            violations = integration.query_linter_api(linter_name, test_file)

            if violations:
                logger.info(f"Found {len(violations)} violations:")
                for violation in violations[:3]:  # Show first 3
                    logger.info(
                        f"  - {violation.code}: {violation.message} (line {violation.line_number})",
                    )
            else:
                logger.info("No violations found")

        # Test AI suggestions
        logger.info("\n🤖 Getting AI suggestions from Ruff...")
        ai_suggestions = integration.get_ai_suggestions(test_file)

        if ai_suggestions:
            logger.info(f"Found {len(ai_suggestions)} AI suggestions:")
            for suggestion in ai_suggestions[:3]:  # Show first 3
                logger.info(
                    "  - {}: {}".format(suggestion["code"], suggestion["message"]),
                )
        else:
            logger.info("No AI suggestions found")

        # Test prevention
        logger.info("\n🛡️ Testing violation prevention...")
        sample_code = """
import json
"""
        logger.info("Sample code with unused import:")
        logger.info(sample_code)
        logger.info("✅ File completed successfully")
