#!/usr/bin/env python3
"""
Fix Return Value Issues - Targeted Fix for Most Common MyPy Pattern
"""

import ast
import re
from pathlib import Path
from typing import Any

from src.secure_shell_service.secure_executor import secure_execute


def find_return_value_issues(filepath: str) -> list[dict[str, Any]]:
    """Find functions with return value issues"""
    issues = []

    try:
        with open(filepath) as f:
            content = f.read()

        # Parse the file
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has -> None annotation
                if (
                    node.returns
                    and isinstance(node.returns, ast.Name)
                    and node.returns.id == "None"
                ):
                    # Check if function actually returns something
                    for child in ast.walk(node):
                        if isinstance(child, ast.Return) and child.value:
                            issues.append(
                                {
                                    "function": node.name,
                                    "line": node.lineno,
                                    "issue": "Function annotated as -> None but returns value",
                                },
                            )
                            break

    except Exception as e:
        print(f"❌ Error parsing {filepath}: {e}")

    return issues


def fix_return_value_issues(filepath: str) -> bool:
    """Fix return value issues in a file"""
    try:
        with open(filepath) as f:
            content = f.read()

        lines = content.split("\n")
        fixed_lines = []
        changes_made = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for function definitions with -> None
            if re.match(r"^\s*def\s+\w+\s*\([^)]*\)\s*->\s*None\s*:$", line):
                re.search(r"def\s+(\w+)", line).group(1)

                # Find function body
                indent_level = len(line) - len(line.lstrip())
                func_body = []
                j = i + 1

                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip() == "":
                        func_body.append(next_line)
                        j += 1
                        continue

                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent_level and next_line.strip():
                        break

                    func_body.append(next_line)
                    j += 1

                # Check if function returns a value
                has_return_value = False
                for body_line in func_body:
                    if re.search(r"^\s*return\s+[^#\n]+", body_line.strip()):
                        if not re.match(
                            r"^\s*return\s*$",
                            body_line.strip(),
                        ) and not re.match(r"^\s*return\s+None\s*$", body_line.strip()):
                            has_return_value = True
                            break

                if has_return_value:
                    # Fix the annotation
                    line = line.replace("-> None:", "-> Any:")
                    changes_made = True

                    # Add Any import if needed
                    if "from typing import Any" not in content and "Any" not in content:
                        # Find where to insert import
                        import_added = False
                        for k, import_line in enumerate(lines):
                            if import_line.strip().startswith("from typing import"):
                                if "Any" not in import_line:
                                    lines[k] = import_line.replace(")", ", Any)")
                                    import_added = True
                                break
                            if import_line.strip().startswith(
                                "import ",
                            ) and not import_line.strip().startswith("import typing"):
                                lines.insert(k, "from typing import Any")
                                import_added = True
                                break

                        if not import_added:
                            lines.insert(0, "from typing import Any")

            fixed_lines.append(line)
            i += 1

        if changes_made:
            fixed_content = "\n".join(lines)
            with open(filepath, "w") as f:
                f.write(fixed_content)
            print(f"✅ Fixed return value issues: {filepath}")
            return True
        print(f"⚠️  No return value issues found: {filepath}")
        return False

    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False


def main():
    """Main function to fix return value issues"""
    print("🎯 Fixing Return Value Issues (Most Common MyPy Pattern)")
    print("=" * 60)

    # Find all Python files
    src_path = Path("src")
    python_files = list(src_path.rglob("*.py"))

    total_issues = 0
    total_fixed = 0

    for py_file in python_files:
        issues = find_return_value_issues(str(py_file))
        if issues:
            total_issues += len(issues)
            print(f"📊 Found {len(issues)} return value issues in {py_file}")

            if fix_return_value_issues(str(py_file)):
                total_fixed += len(issues)

    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print(f"📊 Total return value issues found: {total_issues}")
    print(f"📊 Total issues fixed: {total_fixed}")
    print(f"📊 Files processed: {len(python_files)}")

    if total_fixed > 0:
        print("\n🚀 Running MyPy to check improvements...")
        # import subprocess  # REMOVED - replaced with secure_execute

        result = secure_execute(
            ["uv", "run", "mypy", "src/", "--ignore-missing-imports"],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            errors = [line for line in result.stdout.split("\n") if "error:" in line]
            print(f"📊 Remaining MyPy errors: {len(errors)}")
        else:
            print("✅ No MyPy errors found!")


if __name__ == "__main__":
    main()
