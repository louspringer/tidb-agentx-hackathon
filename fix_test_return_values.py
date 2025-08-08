#!/usr/bin/env python3
"""
Fix Test Function Return Values - Remove returns from test functions
"""

import re
from pathlib import Path

from src.secure_shell_service.secure_executor import secure_execute


def fix_test_return_values(filepath: str) -> bool:
    """Fix test functions that return values when they shouldn't"""
    try:
        with open(filepath) as f:
            content = f.read()

        original_content = content
        lines = content.split("\n")
        fixed_lines = []
        changes_made = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for test function definitions with -> None
            if re.match(r"^\s*def\s+test_\w+\s*\([^)]*\)\s*->\s*None\s*:$", line):
                func_name = re.search(r"def\s+(test_\w+)", line)
                if not func_name:
                    fixed_lines.append(line)
                    i += 1
                    continue

                func_name = func_name.group(1)
                func_start = i

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
                    # Remove return statements from test functions
                    modified_body = []
                    for body_line in func_body:
                        if re.search(r"^\s*return\s+[^#\n]+", body_line.strip()):
                            # Replace return value with pass or comment
                            indent = len(body_line) - len(body_line.lstrip())
                            modified_body.append(
                                " " * indent + "# Removed return statement",
                            )
                            changes_made = True
                        else:
                            modified_body.append(body_line)

                    # Replace the function body
                    fixed_lines.append(line)
                    fixed_lines.extend(modified_body)
                    i = j  # Skip to end of function
                    continue

            fixed_lines.append(line)
            i += 1

        if changes_made:
            fixed_content = "\n".join(fixed_lines)
            with open(filepath, "w") as f:
                f.write(fixed_content)
            print(f"✅ Fixed test return values: {filepath}")
            return True
        else:
            print(f"⚠️  No test return value issues found: {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False


def main() -> None:
    """Main function to fix test return value issues"""
    print("🎯 Fixing Test Function Return Values")
    print("=" * 50)

    # Find all Python files
    src_path = Path("src")
    python_files = list(src_path.rglob("*.py"))

    total_fixed = 0

    for py_file in python_files:
        if fix_test_return_values(str(py_file)):
            total_fixed += 1

    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print(f"📊 Files with test return value fixes: {total_fixed}")
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
            return_value_errors = [
                line
                for line in result.stdout.split("\n")
                if "No return value expected" in line
            ]
            print(f"📊 Remaining return value errors: {len(return_value_errors)}")
        else:
            print("✅ No MyPy errors found!")


if __name__ == "__main__":
    main()
