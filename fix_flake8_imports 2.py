#!/usr/bin/env python3
"""
Fix flake8 import order issues
"""

from pathlib import Path


def fix_import_order(file_path: str) -> bool:
    """Fix import order in a file"""
    try:
        with open(file_path) as f:
            content = f.read()

        lines = content.split("\n")

        # Find all import lines
        import_lines = []
        other_lines = []
        in_docstring = False

        for line in lines:
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith("#"):
                other_lines.append(line)
                continue

            # Check if we're in a docstring
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring

            # If in docstring, treat as other content
            if in_docstring:
                other_lines.append(line)
                continue

            # Check if it's an import
            if stripped.startswith(("import ", "from ")):
                import_lines.append(line)
            else:
                other_lines.append(line)

        # Reconstruct file with imports at top
        fixed_lines = []

        # Add shebang if present
        if other_lines and other_lines[0].startswith("#!"):
            fixed_lines.append(other_lines.pop(0))
            fixed_lines.append("")  # Add blank line

        # Add docstring if present
        if other_lines and other_lines[0].startswith('"""'):
            fixed_lines.append(other_lines.pop(0))
            while other_lines and not other_lines[0].startswith('"""'):
                fixed_lines.append(other_lines.pop(0))
            if other_lines:
                fixed_lines.append(other_lines.pop(0))
            fixed_lines.append("")  # Add blank line

        # Add all imports
        fixed_lines.extend(import_lines)
        if import_lines:
            fixed_lines.append("")  # Add blank line

        # Add remaining content
        fixed_lines.extend(other_lines)

        # Write fixed content
        with open(file_path, "w") as f:
            f.write("\n".join(fixed_lines))

        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all Python files"""
    print("🔧 Fixing flake8 import order issues...")

    src_dir = Path("src")
    fixed_count = 0

    for py_file in src_dir.rglob("*.py"):
        if fix_import_order(str(py_file)):
            fixed_count += 1
            print(f"✅ Fixed {py_file}")

    print(f"🎉 Fixed {fixed_count} files!")


if __name__ == "__main__":
    main()
