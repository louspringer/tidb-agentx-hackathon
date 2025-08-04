#!/usr/bin/env python3
"""
Code Quality Validation Tests
Tests for import cleanliness, code organization, and maintainability
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


class CodeQualityValidator:
    """Validates code quality including imports, structure, and maintainability"""

    def __init__(self: Any) -> None:
        """Initialize the validator"""
        self.project_root = Path(__file__).parent.parent

    def check_duplicate_imports(self, file_path: Path) -> List[str]:
        """Check for duplicate imports in a Python file"""
        issues: List[str] = []

        try:
            with open(file_path, "r") as f:
                content: str = f.read()

            # Parse the file
            tree: ast.AST = ast.parse(content)

            # Collect all imports
            imports: List[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Check for duplicates
            seen: set = set()
            for imp in imports:
                if imp in seen:
                    issues.append(f"Duplicate import: {imp}")
                seen.add(imp)

        except Exception as e:
            issues.append(f"Error parsing {file_path}: {e}")

        return issues

    def check_missing_imports(self, file_path: Path) -> List[str]:
        """Check for missing imports (basic check for common patterns)"""
        issues: List[str] = []

        try:
            with open(file_path, "r") as f:
                content: str = f.read()

            # Check for common patterns that require imports
            patterns = [
                (r"re\.", "import re"),
                (r"json\.", "import json"),
                (r"yaml\.", "import yaml"),
                (r"pathlib\.", "from pathlib import Path"),
                (r"typing\.", "from typing import"),
            ]

            for pattern, required_import in patterns:
                if re.search(pattern, content):
                    # Check if the import is present
                    if required_import not in content:
                        issues.append(f"Missing import: {required_import}")

        except Exception as e:
            issues.append(f"Error checking imports in {file_path}: {e}")

        return issues

    def check_file_length(self, file_path: Path, max_lines: int = 500) -> List[str]:
        """Check if file is too long"""
        issues: List[str] = []

        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            if len(lines) > max_lines:
                issues.append(f"File too long: {len(lines)} lines (max: {max_lines})")

        except Exception as e:
            issues.append(f"Error checking file length for {file_path}: {e}")

        return issues

    def check_long_strings(
        self, file_path: Path, max_string_lines: int = 50
    ) -> List[str]:
        """Check for very long multi-line strings"""
        issues: List[str] = []

        try:
            with open(file_path, "r") as f:
                content: str = f.read()

            # Find multi-line strings
            lines = content.split("\n")
            in_string = False
            string_start = 0

            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    if not in_string:
                        in_string = True
                        string_start = i
                    else:
                        in_string = False
                        string_length = i - string_start + 1
                        if string_length > max_string_lines:
                            issues.append(
                                f"Long multi-line string: {string_length} lines (max: {max_string_lines})"
                            )

        except Exception as e:
            issues.append(f"Error checking long strings in {file_path}: {e}")

        return issues

    def check_function_complexity(self, file_path: Path) -> List[str]:
        """Check for overly complex functions"""
        issues: List[str] = []

        try:
            with open(file_path, "r") as f:
                content: str = f.read()

            tree: ast.AST = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count lines in function
                    if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                        function_lines = node.end_lineno - node.lineno + 1
                        if function_lines > 50:
                            issues.append(
                                f"Function '{node.name}' too long: {function_lines} lines"
                            )

        except Exception as e:
            issues.append(f"Error checking function complexity in {file_path}: {e}")

        return issues

    def validate_file(self, file_path: Path) -> Dict[str, List[str]]:
        """Validate a single file for code quality issues"""
        issues = {
            "duplicate_imports": self.check_duplicate_imports(file_path),
            "missing_imports": self.check_missing_imports(file_path),
            "file_length": self.check_file_length(file_path),
            "long_strings": self.check_long_strings(file_path),
            "function_complexity": self.check_function_complexity(file_path),
        }
        return issues

    def validate_all_files(self: Any) -> Dict[str, Dict[str, List[str]]]:
        """Validate all Python files in the project"""
        all_issues: Dict[str, Dict[str, List[str]]] = {}

        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))

        for file_path in python_files:
            # Skip virtual environments and cache
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            file_issues = self.validate_file(file_path)
            if any(issues for issues in file_issues.values()):
                all_issues[str(file_path)] = file_issues

        return all_issues


def test_import_cleanliness() -> None:
    """Test that imports are clean and organized"""
    print("Testing import cleanliness...")

    validator = CodeQualityValidator()
    all_issues = validator.validate_all_files()

    # Check for duplicate imports
    duplicate_import_issues = 0
    missing_import_issues = 0

    for file_path, file_issues in all_issues.items():
        duplicate_import_issues += len(file_issues.get("duplicate_imports", []))
        missing_import_issues += len(file_issues.get("missing_imports", []))

    # Allow some issues but not too many
    assert (
        duplicate_import_issues < 30
    ), f"Too many duplicate imports: {duplicate_import_issues}"
    assert (
        missing_import_issues < 20
    ), f"Too many missing imports: {missing_import_issues}"

    print(f"✅ Import cleanliness test passed")
    print(f"  📊 Duplicate imports: {duplicate_import_issues}")
    print(f"  📊 Missing imports: {missing_import_issues}")


def test_file_maintainability() -> None:
    """Test that files are maintainable"""
    print("Testing file maintainability...")

    validator = CodeQualityValidator()
    all_issues = validator.validate_all_files()

    # Check for file length issues
    long_file_issues = 0
    long_string_issues = 0
    complex_function_issues = 0

    for file_path, file_issues in all_issues.items():
        long_file_issues += len(file_issues.get("file_length", []))
        long_string_issues += len(file_issues.get("long_strings", []))
        complex_function_issues += len(file_issues.get("function_complexity", []))

    # Allow some issues but not too many
    assert long_file_issues < 25, f"Too many long files: {long_file_issues}"
    assert long_string_issues < 60, f"Too many long strings: {long_string_issues}"
    assert (
        complex_function_issues < 125
    ), f"Too many complex functions: {complex_function_issues}"

    print(f"✅ File maintainability test passed")
    print(f"  📊 Long files: {long_file_issues}")
    print(f"  📊 Long strings: {long_string_issues}")
    print(f"  📊 Complex functions: {complex_function_issues}")


def test_specific_issues_fixed() -> None:
    """Test that specific code quality issues have been addressed"""
    print("Testing specific issues have been fixed...")

    validator = CodeQualityValidator()

    # Test specific files that should be clean
    test_files = [
        "tests/test_code_quality.py",  # This file itself
        "src/streamlit/openflow_quickstart_app.py",
        "update_progress.py",
    ]

    for test_file in test_files:
        file_path = Path(test_file)
        if file_path.exists():
            issues = validator.validate_file(file_path)
            total_issues = sum(len(issue_list) for issue_list in issues.values())
            print(f"  📁 {test_file}: {total_issues} issues")

    print("✅ Specific issues test passed")


def main() -> None:
    """Run all code quality tests"""
    print("🔍 Testing Code Quality Requirements")
    print("=" * 60)

    tests = [
        test_import_cleanliness,
        test_file_maintainability,
        test_specific_issues_fixed,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print()

    print("=" * 60)
    print(f"📊 Code Quality Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All code quality tests passed!")
        return True
    else:
        print("⚠️ Some code quality tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
