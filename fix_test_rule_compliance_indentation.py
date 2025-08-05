#!/usr/bin/env python3
"""Fix indentation issues in test_rule_compliance.py"""

import ast
from pathlib import Path

def fix_test_rule_compliance_indentation(file_path: str) -> str:
    """Fix indentation issues in test_rule_compliance.py"""
    
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
        
        # Handle variable assignments
        if ' = ' in stripped and not stripped.startswith('#'):
            if 'self.' in stripped:
                fixed_lines.append('    ' * (current_indent + 1) + stripped)
            else:
                fixed_lines.append('    ' * current_indent + stripped)
            continue
        
        # Handle method calls and other statements
        if stripped.startswith('self.') or stripped.startswith('result') or stripped.startswith('valid_content') or stripped.startswith('invalid_content') or stripped.startswith('test_file') or stripped.startswith('f.write') or stripped.startswith('f.name'):
            fixed_lines.append('    ' * (current_indent + 1) + stripped)
            continue
        
        # Handle for loops and conditionals
        if stripped.startswith('for ') or stripped.startswith('if ') or stripped.startswith('try:') or stripped.startswith('except') or stripped.startswith('with ') or stripped.startswith('finally:'):
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
    test_file = "tests/test_rule_compliance.py"
    
    print(f"🔧 Fixing indentation in {test_file}")
    
    # Fix indentation
    fixed_content = fix_test_rule_compliance_indentation(test_file)
    
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