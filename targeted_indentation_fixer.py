#!/usr/bin/env python3
"""
Targeted Indentation Fixer
Fixes specific indentation issues identified in problematic files
"""

import ast
from pathlib import Path
from typing import List

def fix_file_indentation(file_path: str) -> bool:
    """Fix indentation issues in a specific file"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Track changes
        changes_made = False

        # Process each line
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                # Get current indentation
                current_indent = len(line) - len(line.lstrip())
                stripped = line.strip()

                # Determine proper indentation based on context
                proper_indent = determine_proper_indentation(lines, i)

                if proper_indent is not None and proper_indent != current_indent:
                    # Apply the fix
                    new_line = ' ' * proper_indent + stripped + '\n'
                    lines[i] = new_line
                    changes_made = True
                    print(f"  Fixed line {i+1}: {current_indent} -> {proper_indent} spaces")

        # Write back if changes were made
        if changes_made:
            with open(file_path, 'w') as f:
                f.writelines(lines)
            print(f"✅ Fixed {file_path}")
            return True
        else:
            print(f"⚠️  No changes needed for {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def determine_proper_indentation(lines: List[str], line_idx: int) -> int:
    """Determine proper indentation for a line"""
    line = lines[line_idx]
    stripped = line.strip()

    # Skip empty lines and comments
    if not stripped or stripped.startswith('#'):
        return 0

    # Find the previous non-empty line
    prev_line_idx = line_idx - 1
    while prev_line_idx >= 0:
        prev_line = lines[prev_line_idx].strip()
        if prev_line and not prev_line.startswith('#'):
            break
        prev_line_idx -= 1

    if prev_line_idx < 0:
        # First non-empty line
        return 0

    prev_line = lines[prev_line_idx]
    prev_indent = len(prev_line) - len(prev_line.lstrip())

    # Determine indentation based on context
    if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
        # New block starts - same level as previous
        return prev_indent
    elif stripped.startswith(('elif ', 'else:', 'except', 'finally:')):
        # Control flow continuation - same level as previous
        return prev_indent
    elif prev_line.strip().endswith(':'):
        # Inside a block - increase indentation
        return prev_indent + 4
    elif stripped.endswith(':'):
        # Block start - same level as previous
        return prev_indent
    else:
        # Regular line - same level as previous
        return prev_indent

def test_file_parsing(file_path: str) -> bool:
    """Test if a file parses correctly"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"❌ {file_path}: {e}")
        return False

def main() -> None:
    """Fix all problematic files"""
    print("🔧 **TARGETED INDENTATION FIXER**")
    print("=" * 40)

    # List of problematic files identified
    problematic_files = [
        "ast_to_neo4j_converter.py",
        "scripts/mdc-linter.py",
        ".cursor/plugins/rule-compliance-checker.py",
        "src/security_first/rate_limiting.py",
        "src/security_first/test_streamlit_security_first.py",
        "src/security_first/test_security_model.py",
        "src/multi_agent_testing/test_anthropic_simple.py",
        "src/multi_agent_testing/test_diversity_hypothesis.py",
        "src/multi_agent_testing/test_live_smoke_test.py",
        "src/multi_agent_testing/test_model_traceability.py",
        "src/multi_agent_testing/multi_dimensional_smoke_test.py",
        "src/multi_agent_testing/test_meta_cognitive_orchestrator.py",
        "src/multi_agent_testing/live_smoke_test_langchain.py"
    ]

    print("🔍 **STEP 1: TESTING ORIGINAL FILES**")
    original_failures = []
    for file_path in problematic_files:
        if Path(file_path).exists():
            if not test_file_parsing(file_path):
                original_failures.append(file_path)

    print(f"  Found {len(original_failures)} files with syntax errors")

    print("\n🔧 **STEP 2: APPLYING TARGETED FIXES**")
    successful_fixes = 0
    for file_path in original_failures:
        print(f"\n📝 Fixing {file_path}...")
        if fix_file_indentation(file_path):
            successful_fixes += 1

    print("\n✅ **STEP 3: VALIDATING FIXES**")
    final_failures = []
    for file_path in original_failures:
        if not test_file_parsing(file_path):
            final_failures.append(file_path)

    print("\n📊 **RESULTS:**")
    print(f"Original failures: {len(original_failures)}")
    print(f"Successful fixes: {successful_fixes}")
    print(f"Remaining failures: {len(final_failures)}")

    if len(final_failures) == 0:
        print("🎉 **SUCCESS! ALL SYNTAX ERRORS FIXED!**")
    else:
        print("⚠️  **PARTIAL SUCCESS**")
        for file_path in final_failures:
            print(f"  ❌ {file_path} still has issues")

if __name__ == "__main__":
    main()
