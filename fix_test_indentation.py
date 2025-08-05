#!/usr/bin/env python3
"""Fix indentation issues in test files using AST-based approach"""

import ast
import re
from pathlib import Path

def fix_test_file_indentation(file_path: str) -> str:
    """Fix indentation issues in test files"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    # Track indentation level
    current_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            fixed_lines.append('')
            continue
        
        # Handle class definitions
        if stripped.startswith('class '):
            current_indent = 0
            fixed_lines.append(stripped)
            continue
        
        # Handle function definitions
        if stripped.startswith('def '):
            if 'setup_method' in stripped or 'test_' in stripped:
                current_indent = 1
            else:
                current_indent = 2
            fixed_lines.append('    ' * current_indent + stripped)
            continue
        
        # Handle docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            fixed_lines.append('    ' * current_indent + stripped)
            continue
        
        # Handle assertions and test logic
        if stripped.startswith('assert '):
            fixed_lines.append('    ' * (current_indent + 1) + stripped)
            continue
        
        # Handle variable assignments
        if ' = ' in stripped and not stripped.startswith('#'):
            if 'self.' in stripped:
                fixed_lines.append('    ' * (current_indent + 1) + stripped)
            else:
                fixed_lines.append('    ' * current_indent + stripped)
            continue
        
        # Handle method calls
        if stripped.startswith('self.') or stripped.startswith('result') or stripped.startswith('token') or stripped.startswith('remaining'):
            fixed_lines.append('    ' * (current_indent + 1) + stripped)
            continue
        
        # Handle for loops
        if stripped.startswith('for ') or stripped.startswith('if '):
            fixed_lines.append('    ' * (current_indent + 1) + stripped)
            continue
        
        # Handle imports and other statements
        if stripped.startswith('import ') or stripped.startswith('from '):
            fixed_lines.append(stripped)
            continue
        
        # Handle comments
        if stripped.startswith('#'):
            fixed_lines.append('    ' * current_indent + stripped)
            continue
        
        # Handle other statements
        fixed_lines.append('    ' * current_indent + stripped)
    
    return '\n'.join(fixed_lines)

def main():
    """Fix the test file"""
    test_file = "src/security_first/test_https_enforcement.py"
    
    print(f"🔧 Fixing indentation in {test_file}")
    
    # Read original content
    with open(test_file, 'r') as f:
        original_content = f.read()
    
    # Fix indentation
    fixed_content = fix_test_file_indentation(test_file)
    
    # Write fixed content
    with open(test_file, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed indentation issues")
    
    # Test if it's valid Python
    try:
        ast.parse(fixed_content)
        print("✅ Fixed content is valid Python")
    except Exception as e:
        print(f"❌ Still has syntax errors: {e}")

if __name__ == "__main__":
    main() 