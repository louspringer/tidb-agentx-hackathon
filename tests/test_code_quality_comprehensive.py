#!/usr/bin/env python3
"""
Comprehensive Code Quality Tests
Tests that will catch the issues Copilot is finding
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Any


class ComprehensiveCodeQualityValidator:
    """Validates code quality comprehensively"""

    def __init__(self: Any) -> None:
        self.project_root = Path(__file__).parent.parent
        self.issues = []

    def check_duplicate_imports(self, file_path: Path) -> List[str]:
        """Check for duplicate imports in a Python file"""
        issues: List[Any] = []

        try:
            with open(file_path, "r") as f:
                content: Any = f.read()

            # Parse the file
            tree: Any = ast.parse(content)

            # Find all imports
            imports: List[Any] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module: Any = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Check for duplicates
            seen: Any = set()
            duplicates: List[Any] = []
            for imp in imports:
                if imp in seen:
                    duplicates.append(imp)
                else:
                    seen.add(imp)

            if duplicates:
                issues.append(f"Duplicate imports found: {duplicates}")

        except Exception as e:
            issues.append(f"Error parsing {file_path}: {e}")

        return issues

    def check_unused_imports(self, file_path: Path) -> List[str]:
        """Check for unused imports in a Python file"""
        issues: List[Any] = []

        try:
            with open(file_path, "r") as f:
                content: Any = f.read()

            # Parse the file
            tree: Any = ast.parse(content)

            # Find all imports
            imports: Any = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    node.module or ""
                    for alias in node.names:
                        imports.add(alias.name)

            # Find all name usages
            usages: Any = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    usages.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Handle attribute access like 're.search'
                    parts: List[Any] = []
                    current: Any = node
                    while isinstance(current, ast.Attribute):
                        parts.insert(0, current.attr)
                        current: Any = current.value
                    if isinstance(current, ast.Name):
                        parts.insert(0, current.id)
                        usages.add(".".join(parts))

            # Check for unused imports
            unused: Any = imports - usages
            if unused:
                issues.append(f"Unused imports: {unused}")

        except Exception as e:
            issues.append(f"Error parsing {file_path}: {e}")

        return issues

    def check_sys_path_duplication(self, file_path: Path) -> List[str]:
        """Check for duplicate sys.path.insert calls"""
        issues: List[Any] = []

        try:
            with open(file_path, "r") as f:
                content: Any = f.read()

            # Count sys.path.insert calls
            sys_path_inserts: Any = re.findall(r"sys\.path\.insert", content)

            if len(sys_path_inserts) > 1:
                issues.append(
                    f"Multiple sys.path.insert calls found: {len(sys_path_inserts)}"
                )

        except Exception as e:
            issues.append(f"Error checking {file_path}: {e}")

        return issues

    def check_large_strings(self, file_path: Path) -> List[str]:
        """Check for very large multi-line strings"""
        issues: List[Any] = []

        try:
            with open(file_path, "r") as f:
                content: Any = f.read()

            # Find multi-line strings
            lines: Any = content.split("\n")
            current_string: List[Any] = []
            in_string: bool = False

            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    if not in_string:
                        in_string: bool = True
                        current_string: List[Any] = [line]
                    else:
                        current_string.append(line)
                        in_string: bool = False
                        # Check if string is too long
                        if len(current_string) > 20:  # More than 20 lines
                            issues.append(
                                f"Large multi-line string at line {i-len(current_string)+1}"
                            )
                        current_string: List[Any] = []
                elif in_string:
                    current_string.append(line)

        except Exception as e:
            issues.append(f"Error checking {file_path}: {e}")

        return issues

    def validate_all_test_files(self: Any) -> None:
        """Validate all test files for code quality issues"""
        test_files: Any = list(self.project_root.rglob("tests/*.py"))

        print("🔍 Comprehensive Code Quality Validation")
        print("=" * 50)

        total_issues: int = 0

        for test_file in test_files:
            print(f"\n📁 Checking: {test_file.relative_to(self.project_root)}")

            file_issues: List[Any] = []

            # Check for duplicate imports
            duplicate_issues: Any = self.check_duplicate_imports(test_file)
            file_issues.extend(duplicate_issues)

            # Check for unused imports
            unused_issues: Any = self.check_unused_imports(test_file)
            file_issues.extend(unused_issues)

            # Check for sys.path duplication
            sys_path_issues: Any = self.check_sys_path_duplication(test_file)
            file_issues.extend(sys_path_issues)

            # Check for large strings
            large_string_issues: Any = self.check_large_strings(test_file)
            file_issues.extend(large_string_issues)

            if file_issues:
                print("❌ Issues found:")
                for issue in file_issues:
                    print(f"   - {issue}")
                total_issues += len(file_issues)
            else:
                print("✅ No issues found")

        print(
            f"\n📊 Summary: {total_issues} issues found across {len(test_files)} files"
        )

        if total_issues == 0:
            print("🎉 All test files pass code quality validation!")
            return True
        else:
            print("⚠️  Code quality issues need to be addressed")
            return False


def main() -> None:
    """Run comprehensive code quality validation"""
    validator: Any = ComprehensiveCodeQualityValidator()
    return validator.validate_all_test_files()


if __name__ == "__main__":
    success: Any = main()
    sys.exit(0 if success else 1)
