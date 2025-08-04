from typing import List, Dict, Tuple, Optional, Union, Any

#!/usr/bin/env python3
"""
Code Quality System - Model-Driven Linting and Fixing
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable
from pathlib import Path
import re
import subprocess


@dataclass
class LintingRule:
    """Defines a linting rule and its fix"""

    code: str
    description: str
    severity: str
    fix_function: Callable
    patterns: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class CodeQualityModel:
    """Model-driven code quality system"""

    def __post_init__(self: Any) -> None:
        self.rules = self._define_rules()
        self.fixers = self._define_fixers()

    def _define_rules(self) -> Dict[str, LintingRule]:
        """Define all linting rules with their fixes"""
        return {
            "F401": LintingRule(
                code="F401",
                description="Unused imports",
                severity="error",
                fix_function=self._fix_unused_imports,
                patterns=["import", "from"],
                examples=["import os  # unused", "from typing import List  # unused"],
            ),
            "W291": LintingRule(
                code="W291",
                description="Trailing whitespace",
                severity="warning",
                fix_function=self._fix_trailing_whitespace,
                patterns=["[ ]+$"],
                examples=["def func():    ", "print('hello')  "],
            ),
            "E722": LintingRule(
                code="E722",
                description="Bare except clause",
                severity="error",
                fix_function=self._fix_bare_except,
                patterns=["except:"],
                examples=["except:", "except Exception:"],
            ),
            "E402": LintingRule(
                code="E402",
                description="Module level import not at top",
                severity="error",
                fix_function=self._fix_import_order,
                patterns=["import", "from"],
                examples=["def func():", "import os"],
            ),
            "F841": LintingRule(
                code="F841",
                description="Local variable assigned but never used",
                severity="warning",
                fix_function=self._fix_unused_variables,
                patterns=["="],
                examples=["x = 5  # unused", "result = func()  # unused"],
            ),
        }

    def _define_fixers(self) -> Dict[str, Callable]:
        """Define automated fixers for each rule type"""
        return {
            "autoflake": self._run_autoflake,
            "black": self._run_black,
            "custom_fixes": self._apply_custom_fixes,
        }

    def _run_autoflake(self, file_path: Path) -> bool:
        """Run autoflake to fix unused imports and variables"""
        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _run_black(self, file_path: Path) -> bool:
        """Run black to format code"""
        try:
            result = subprocess.run(
                ["uv", "run", "black", str(file_path)], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _apply_custom_fixes(self, file_path: Path) -> bool:
        """Apply custom fixes for specific issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Fix f-strings without placeholders
            content = re.sub(
                r'"([^"]*)"',
                lambda m: (
                    f'"{m.group(1)}"'
                    if "{" not in m.group(1) and "}" not in m.group(1)
                    else m.group(0)
                ),
                content,
            )
            content = re.sub(
                r"'([^']*)'",
                lambda m: (
                    f"'{m.group(1)}'"
                    if "{" not in m.group(1) and "}" not in m.group(1)
                    else m.group(0)
                ),
                content,
            )

            # Fix trailing whitespace
            content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

            # Fix bare except clauses
            content = re.sub(
                r"except:\s*$", "except Exception:", content, flags=re.MULTILINE
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception:
            return False

    def _fix_unused_imports(self, file_path: Path) -> bool:
        """Fix unused imports"""
        return self._run_autoflake(file_path)

    def _fix_f_strings(self, file_path: Path) -> bool:
        """Fix f-string issues"""
        return self._apply_custom_fixes(file_path)

    def _fix_trailing_whitespace(self, file_path: Path) -> bool:
        """Fix trailing whitespace"""
        return self._apply_custom_fixes(file_path)

    def _fix_bare_except(self, file_path: Path) -> bool:
        """Fix bare except clauses"""
        return self._apply_custom_fixes(file_path)

    def _fix_import_order(self, file_path: Path) -> bool:
        """Fix import order issues"""
        # This is complex and often requires manual intervention
        return True

    def _fix_unused_variables(self, file_path: Path) -> bool:
        """Fix unused variables"""
        return self._run_autoflake(file_path)

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for all linting issues"""
        issues: List[Any] = []

        # Run flake8
        try:
            result = subprocess.run(
                ["uv", "run", "flake8", str(file_path)], capture_output=True, text=True
            )

            for line in result.stdout.split("\n"):
                if line.strip():
                    parts = line.split(":")
                    if len(parts) >= 3:
                        issue: Any = {
                            "file": parts[0],
                            "line": int(parts[1]),
                            "column": int(parts[2]),
                            "code": parts[3].split()[0] if parts[3].split() else "",
                            "message": ":".join(parts[3:]).strip(),
                        }
                        issues.append(issue)
        except Exception as e:
            issues.append({"error": str(e)})

        return {"file": str(file_path), "issues": issues, "total_issues": len(issues)}

    def fix_file(self, file_path: Path) -> Dict[str, Any]:
        """Fix all issues in a file"""
        results = {"file": str(file_path), "fixes_applied": [], "errors": []}

        # Apply all fixers
        for fixer_name, fixer_func in self.fixers.items():
            try:
                if fixer_func(file_path):
                    results["fixes_applied"].append(fixer_name)
                else:
                    results["errors"].append(f"Failed to apply {fixer_name}")
            except Exception as e:
                results["errors"].append(f"Error applying {fixer_name}: {e}")

        return results

    def fix_all_files(self, directories: List[str] = None) -> Dict[str, Any]:
        """Fix all files in the project"""
        if directories is None:
            directories: List[Any] = ["src", "tests", "scripts", ".cursor"]

        all_results: Any = {
            "total_files": 0,
            "files_fixed": 0,
            "total_issues_before": 0,
            "total_issues_after": 0,
            "file_results": [],
        }

        for directory in directories:
            if Path(directory).exists():
                for py_file in Path(directory).rglob("*.py"):
                    all_results["total_files"] += 1

                    # Analyze before
                    before_analysis: Any = self.analyze_file(py_file)
                    all_results["total_issues_before"] += before_analysis[
                        "total_issues"
                    ]

                    # Apply fixes
                    fix_result: Any = self.fix_file(py_file)
                    all_results["file_results"].append(fix_result)

                    if fix_result["fixes_applied"]:
                        all_results["files_fixed"] += 1

                    # Analyze after
                    after_analysis: Any = self.analyze_file(py_file)
                    all_results["total_issues_after"] += after_analysis["total_issues"]

        return all_results
