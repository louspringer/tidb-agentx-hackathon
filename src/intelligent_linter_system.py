#!/usr/bin/env python3
"""
Intelligent Linter System
Comprehensive integration of linter APIs, AI-powered linters, and dynamic rule updates
"""

import logging
from src.secure_shell_service.secure_executor import secure_execute
# import subprocess  # REMOVED - replaced with secure_execute
from datetime import datetime
from pathlib import Path
from typing import Any

from src.dynamic_rule_updater import DynamicRuleUpdater
from src.linter_api_integration import LinterAPIIntegration, LinterViolation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentLinterSystem:
    """Comprehensive intelligent linter system"""

    def __init__(self) -> None:
        self.linter_api = LinterAPIIntegration()
        self.rule_updater = DynamicRuleUpdater()
        self.violation_history: list[dict[str, Any]] = []

    def setup_ai_powered_linters(self) -> dict[str, Any]:
        """Setup AI-powered linters (Ruff, etc.)"""
        logger.info("🤖 **SETTING UP AI-POWERED LINTERS**")
        logger.info("=" * 50)

        setup_results = {}

        # Check if Ruff is available
        try:
            result = secure_execute(
                ["ru", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                setup_results["ru"] = {
                    "status": "available",
                    "version": result.stdout.strip(),
                    "ai_capabilities": ["auto-fix", "suggestions", "formatting"],
                }
                logger.info("✅ Ruff (AI-powered) is available")
            else:
                setup_results["ruff"] = {"status": "not_available"}
                logger.warning("⚠️ Ruff not available - install with: pip install ru")
        except Exception as e:
            setup_results["ruff"] = {"status": "error", "error": str(e)}
            logger.error(f"❌ Error checking Ruff: {e}")

        # Check if pre-commit is available
        try:
            result = secure_execute(
                ["pre-commit", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                setup_results["pre-commit"] = {
                    "status": "available",
                    "version": result.stdout.strip(),
                }
                logger.info("✅ Pre-commit is available")
            else:
                setup_results["pre-commit"] = {"status": "not_available"}
                logger.warning(
                    "⚠️ Pre-commit not available - install with: pip install pre-commit",
                )
        except Exception as e:
            setup_results["pre-commit"] = {"status": "error", "error": str(e)}
            logger.error(f"❌ Error checking pre-commit: {e}")

        return setup_results

    def query_all_linter_apis(self, file_path: str) -> dict[str, Any]:
        """Query all available linter APIs for a file"""
        logger.info("🔍 **QUERYING ALL LINTER APIS**")
        logger.info("=" * 40)
        logger.info(f"File: {file_path}")

        results = {}

        # Query each linter
        for linter_name in self.linter_api.linters:
            logger.info(f"\n📝 Querying {linter_name} API...")
            violations: list[LinterViolation] = self.linter_api.query_linter_api(
                linter_name,
                file_path,
            )
            results[linter_name] = violations

            if violations:
                logger.info(f"Found {len(violations)} violations:")
                for violation in violations[:3]:  # Show first 3
                    logger.info(
                        f"  - {violation.code}: {violation.message} (line {violation.line_number})",
                    )
            else:
                logger.info("No violations found")

        # Get AI suggestions if Ruff is available
        ai_suggestions = self.linter_api.get_ai_suggestions(file_path)
        if ai_suggestions:
            results["ai_suggestions"] = ai_suggestions
            logger.info(f"Found {len(ai_suggestions)} AI suggestions")

        return results

    def prevent_violations_before_writing(
        self,
        file_path: str,
        code_block: str,
    ) -> dict[str, Any]:
        """Prevent violations before writing code"""
        logger.info("🛡️ **PREVENTING VIOLATIONS BEFORE WRITING**")
        logger.info("=" * 50)
        logger.info(f"File: {file_path}")

        # Get prevention analysis
        prevention_result = self.linter_api.prevent_violations_before_writing(
            file_path,
            code_block,
        )

        # Log potential violations
        if prevention_result["potential_violations"]:
            logger.info("Potential violations detected:")
            for violation in prevention_result["potential_violations"]:
                logger.info(
                    "  - {}: {} (line {})".format(
                        violation["type"],
                        violation["suggestion"],
                        violation["line"],
                    ),
                )

        # Log prevention suggestions
        if prevention_result["suggestions"]:
            logger.info("Prevention suggestions:")
            for suggestion in prevention_result["suggestions"]:
                logger.info(f"  - {suggestion}")

        # Log auto-fixes
        if prevention_result["auto_fixes"]:
            logger.info("Auto-fixes available:")
            for fix in prevention_result["auto_fixes"]:
                logger.info(
                    "  - {}: {} (line {})".format(fix["type"], fix["fix"], fix["line"]),
                )

        return prevention_result

    def update_rules_on_violations(
        self,
        violations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Update rules when violations are detected"""
        logger.info("🔄 **UPDATING RULES ON VIOLATIONS**")
        logger.info("=" * 40)
        logger.info(f"Violations to process: {len(violations)}")

        update_results = {
            "violations_processed": 0,
            "rules_updated": 0,
            "patterns_learned": 0,
        }

        for violation in violations:
            logger.info("\nProcessing violation:")
            logger.info("  - Rule: {}".format(violation.get("code")))
            logger.info("  - File: {}".format(violation.get("file_path")))
            logger.info("  - Line: {}".format(violation.get("line_number")))

            # Update rules for this violation
            self.rule_updater.update_rules_on_violation(violation)
            update_results["violations_processed"] += 1
            update_results["rules_updated"] += 1

            # Add to violation history
            self.violation_history.append(
                {
                    **violation,
                    "timestamp": datetime.now().isoformat(),
                    "rule_updated": True,
                },
            )

        # Learn from all violations
        learning_report = self.rule_updater.learn_from_violations(violations)
        update_results["patterns_learned"] = len(learning_report.get("patterns", {}))

        logger.info("\n📊 **UPDATE RESULTS**")
        logger.info("=" * 25)
        logger.info(
            "Violations processed: {}".format(update_results["violations_processed"]),
        )
        logger.info("Rules updated: {}".format(update_results["rules_updated"]))
        logger.info("Patterns learned: {}".format(update_results["patterns_learned"]))

        return update_results

    def create_pre_commit_config(self) -> str:
        """Create pre-commit configuration with AI-powered linters"""
        config_content = """# .pre-commit-config.yaml
# AI-powered linter configuration

repos:
  # Ruff (AI-powered Python linter)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        # AI-powered auto-fixing
      - id: ruff-format
        # AI-powered formatting

  # MyPy (Type checking)
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        # AI-powered type checking

  # Black (Code formatting)
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: [--line-length=88]

  # Flake8 (Style checking)
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  # Custom hooks for our intelligent system
  - repo: local
    hooks:
      - id: intelligent-linter-check
        name: Intelligent Linter Check
        entry: python src/intelligent_linter_system.py --check
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit, push]

      - id: dynamic-rule-update
        name: Dynamic Rule Update
        entry: python src/dynamic_rule_updater.py --update
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]
"""

        with open(".pre-commit-config.yaml", "w") as f:
            f.write(config_content)

        logger.info("Created pre-commit configuration with AI-powered linters")
        return config_content

    def create_ruff_config(self) -> str:
        """Create Ruff configuration for AI-powered linting"""
        config_content = """# .ruff.toml
# AI-powered Python linter configuration

target-version = "py39"
line-length = 88

# Enable AI-powered features
_select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "S",   # bandit
    "A",   # flake8-builtins
    "COM", # flake8-commas
    "T20", # flake8-print
    "TCH", # flake8-type-checking
    "ARG", # flake8-unused-arguments
    "PIE", # flake8-pie
    "TID", # flake8-tidy-imports
    "Q",   # flake8-quotes
    "SIM", # flake8-simplify
    "TCH", # flake8-type-checking
    "RSE", # flake8-raise
    "RET", # flake8-return
    "SLF", # flake8-self
    "SLOT", # flake8-slots
    "PTH", # flake8-use-pathlib
    "LOG", # flake8-logging-format
    "G",   # flake8-logging
    "INP", # flake8-no-pep420
    "ISC", # flake8-implicit-str-concat
    "ICN", # flake8-import-conventions
    "DTZ", # flake8-datetimez
    "TZ",  # flake8-time
    "EM",  # flake8-errmsg
    "EXE", # flake8-executable
    "NPY", # flake8-numpy
    "AIR", # flake8-airflow
    "PERF", # perflint
    "FURB", # refurb
    "TRY", # tryceratops
    "FLY", # flynt
    "BLE", # flake8-blind-except
    "FBT", # flake8-boolean-trap
    "C90", # mccabe
]

# Ignore specific rules
_ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
    "W503",  # line break before binary operator
    "E203",  # whitespace before ':'
]

# Allow autofix for all rules
_fixable = ["ALL"]

# Unfixable rules
_unfixable = []

# Exclude files
_exclude = [
    ".git",
    ".hg",
    ".mypy_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

# Per-file-ignores
[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["S101", "S603", "S607"]
"docs/**/*.py" = ["E501"]

# Import sorting
[tool.ruff.isort]
known-first-party = ["src"]
known-third-party = ["pytest", "black", "flake8", "mypy"]

# Type checking
[tool.ruff.flake8-type-checking]
# Enable all type checking rules
extend-select = ["TCH"]
"""

        with open(".ruff.toml", "w") as f:
            f.write(config_content)

        logger.info("Created Ruff configuration for AI-powered linting")
        return config_content

    def run_comprehensive_analysis(self, file_path: str) -> dict[str, Any]:
        """Run comprehensive analysis of a file"""
        logger.info("🔬 **COMPREHENSIVE ANALYSIS**")
        logger.info("=" * 40)
        logger.info(f"File: {file_path}")

        # Query all linter APIs
        linter_results = self.query_all_linter_apis(file_path)

        # Get AI suggestions
        ai_suggestions = self.linter_api.get_ai_suggestions(file_path)

        # Analyze violation patterns
        all_violations: list[dict[str, Any]] = []
        for linter_name, violations_obj in linter_results.items():
            if linter_name != "ai_suggestions":
                if violations_obj and isinstance(violations_obj, list):
                    for violation in violations_obj:
                        all_violations.append(
                            {
                                "code": violation.code,
                                "file_path": violation.file_path,
                                "line_number": violation.line_number,
                                "message": violation.message,
                                "linter": linter_name,
                                "severity": violation.severity,
                                "fix_available": violation.fix_available,
                            },
                        )

        # Update rules based on violations
        if all_violations:
            update_results = self.update_rules_on_violations(all_violations)
        else:
            update_results = {
                "violations_processed": 0,
                "rules_updated": 0,
                "patterns_learned": 0,
            }

        # Generate comprehensive report
        analysis_report = {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "linter_results": linter_results,
            "ai_suggestions": ai_suggestions,
            "violations": all_violations,
            "update_results": update_results,
            "recommendations": self._generate_recommendations(
                all_violations,
                ai_suggestions,
            ),
        }

        logger.info("\n📊 **ANALYSIS REPORT**")
        logger.info("=" * 25)
        logger.info(f"Total violations: {len(all_violations)}")
        logger.info(f"AI suggestions: {len(ai_suggestions)}")
        logger.info("Rules updated: {}".format(update_results["rules_updated"]))

        return analysis_report

    def _generate_recommendations(
        self,
        violations: list[dict[str, Any]],
        ai_suggestions: list[dict[str, Any]],
    ) -> list[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Analyze violation patterns
        violation_types = {}
        for violation in violations:
            rule_code = violation["code"]
            if rule_code not in violation_types:
                violation_types[rule_code] = 0
            violation_types[rule_code] += 1

        # Generate recommendations based on patterns
        for rule_code, count in violation_types.items():
            if count > 2:
                recommendations.append(
                    f"High frequency {rule_code} violations: Consider adding specific prevention rule",
                )

            if rule_code == "F401":
                recommendations.append(
                    "Unused imports detected: Review import statements and remove unused imports",
                )

                recommendations.append(
                    "F-strings without placeholders: Use regular strings when no variables are needed",
                )
            elif rule_code == "E302":
                recommendations.append(
                    "Missing blank lines: Add two blank lines before class/function definitions",
                )
            elif rule_code == "W291":
                recommendations.append(
                    "Trailing whitespace: Remove trailing whitespace from lines",
                )
            elif rule_code == "W292":
                recommendations.append("Missing newline: Add newline at end of file")

        # Add AI-specific recommendations
        if ai_suggestions:
            recommendations.append(
                "AI suggestions available: Consider applying AI-powered fixes",
            )

        return recommendations

    def generate_summary_report(self) -> dict[str, Any]:
        """Generate summary report of all activities"""
        logger.info("📋 **GENERATING SUMMARY REPORT**")
        logger.info("=" * 40)

        # Analyze violation history
        total_violations = len(self.violation_history)
        unique_rules = {v.get("code") for v in self.violation_history}
        unique_files = {v.get("file_path") for v in self.violation_history}

        # Calculate statistics
        rule_frequencies = {}
        for violation in self.violation_history:
            rule_code = violation.get("code")
            if rule_code not in rule_frequencies:
                rule_frequencies[rule_code] = 0
            rule_frequencies[rule_code] += 1

        # Generate summary
        summary = {
            "total_violations": total_violations,
            "unique_rules": len(unique_rules),
            "unique_files": len(unique_files),
            "rule_frequencies": rule_frequencies,
            "most_common_violations": sorted(
                rule_frequencies.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "violation_history": self.violation_history,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info("Summary statistics:")
        logger.info(f"  - Total violations: {total_violations}")
        logger.info(f"  - Unique rules: {len(unique_rules)}")
        logger.info(f"  - Unique files: {len(unique_files)}")

        if rule_frequencies:
            logger.info("  - Most common violations:")
            for rule_code, count in summary["most_common_violations"]:
                logger.info(f"    - {rule_code}: {count} occurrences")

        return summary


def main() -> None:
    """Test the intelligent linter system"""
    logger.info("🧪 **INTELLIGENT LINTER SYSTEM TEST**")
    logger.info("=" * 50)

    system = IntelligentLinterSystem()

    # Setup AI-powered linters
    setup_results = system.setup_ai_powered_linters()
    logger.info(f"Setup results: {setup_results}")

    # Test with a sample file
    test_file = "tests/test_python_quality_enforcement.py"

    if Path(test_file).exists():
        # Run comprehensive analysis
        system.run_comprehensive_analysis(test_file)

        # Generate summary report
        system.generate_summary_report()

        # Create configuration files
        system.create_pre_commit_config()
        system.create_ruff_config()

        logger.info("\n✅ **SYSTEM TEST COMPLETED**")
        logger.info("=" * 30)
        logger.info("Files created:")
        logger.info("  - .pre-commit-config.yaml")
        logger.info("  - .ruff.toml")
        logger.info("  - .cursor/rules/dynamic-prevention-rules.mdc")

    else:
        logger.error(f"Test file {test_file} not found")


if __name__ == "__main__":
    main()
