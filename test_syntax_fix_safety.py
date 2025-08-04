#!/usr/bin/env python3
"""
Test to ensure syntax fix scripts don't introduce structural issues
"""

from pathlib import Path
from typing import List, Dict, Any


def test_no_duplicate_shebangs(file_path: Path) -> List[str]:
    """Test that files don't have duplicate shebang lines"""
    issues = []

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

    lines = content.split("\n")
    shebang_count = 0

    for i, line in enumerate(lines):
        if line.strip().startswith("#!"):
            shebang_count += 1
            if shebang_count > 1:
                issues.append(f"Duplicate shebang at line {i+1}")

    if shebang_count > 1:
        issues.append(f"File has {shebang_count} shebang lines (should be 0 or 1)")

    return issues


def test_no_duplicate_imports(file_path: Path) -> List[str]:
    """Test that files don't have duplicate import statements"""
    issues = []

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

    lines = content.split("\n")
    imports = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append((i + 1, stripped))

    # Check for duplicate imports
    seen_imports = set()
    for line_num, import_stmt in imports:
        if import_stmt in seen_imports:
            issues.append(f"Duplicate import at line {line_num}: {import_stmt}")
        seen_imports.add(import_stmt)

    return issues


def test_proper_structure(file_path: Path) -> List[str]:
    """Test that files have proper Python structure"""
    issues = []

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

    lines = content.split("\n")

    # Check for proper indentation
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith("    ") and not line.startswith("\t"):
            # This should be a top-level statement
            if (
                ":" in line
                and "=" in line
                and not line.strip().startswith("def ")
                and not line.strip().startswith("class ")
            ):
                # This looks like an unindented variable assignment
                issues.append(
                    f"Unindented variable assignment at line {i+1}: {line.strip()}"
                )

    return issues


def test_syntax_fix_safety() -> Dict[str, Any]:
    """Test that syntax fix scripts don't introduce structural issues"""
    print("🧪 Testing syntax fix safety...")

    python_files = []
    for file_path in Path(".").rglob("*.py"):
        if "__pycache__" not in str(file_path) and ".git" not in str(file_path):
            python_files.append(file_path)

    results = {
        "total_files": len(python_files),
        "files_with_issues": 0,
        "total_issues": 0,
        "issues_by_type": {
            "duplicate_shebangs": 0,
            "duplicate_imports": 0,
            "structural_issues": 0,
        },
    }

    for file_path in python_files:
        file_issues = []

        # Test for duplicate shebangs
        shebang_issues = test_no_duplicate_shebangs(file_path)
        if shebang_issues:
            results["issues_by_type"]["duplicate_shebangs"] += len(shebang_issues)
            file_issues.extend(shebang_issues)

        # Test for duplicate imports
        import_issues = test_no_duplicate_imports(file_path)
        if import_issues:
            results["issues_by_type"]["duplicate_imports"] += len(import_issues)
            file_issues.extend(import_issues)

        # Test for structural issues
        structure_issues = test_proper_structure(file_path)
        if structure_issues:
            results["issues_by_type"]["structural_issues"] += len(structure_issues)
            file_issues.extend(structure_issues)

        if file_issues:
            results["files_with_issues"] += 1
            results["total_issues"] += len(file_issues)
            print(f"\n❌ {file_path}:")
            for issue in file_issues:
                print(f"  - {issue}")

    print("\n📊 Results:")
    print(f"Files tested: {results['total_files']}")
    print(f"Files with issues: {results['files_with_issues']}")
    print(f"Total issues: {results['total_issues']}")
    print(f"Issues by type: {results['issues_by_type']}")

    return results


if __name__ == "__main__":
    test_syntax_fix_safety()
