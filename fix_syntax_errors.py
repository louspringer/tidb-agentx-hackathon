#!/usr/bin/env python3
"""
Fix syntax errors in problematic files
"""

import re
import sys
from pathlib import Path

def fix_file(file_path: str) -> bool:
    """Fix syntax errors in a file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix common indentation issues
        lines = content.split('\n')
        fixed_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fixed_lines.append('')
                continue
                
            # Fix function definitions
            if stripped.startswith('def ') and ':' in stripped:
                indent_level = 0
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('class ') and ':' in stripped:
                indent_level = 0
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('if ') and ':' in stripped:
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('elif ') and ':' in stripped:
                indent_level -= 1
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('else:') or stripped.startswith('except:') or stripped.startswith('finally:'):
                indent_level -= 1
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('try:') or stripped.startswith('with '):
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('return ') or stripped.startswith('raise '):
                fixed_lines.append('    ' * indent_level + stripped)
            elif stripped.startswith('import ') or stripped.startswith('from '):
                indent_level = 0
                fixed_lines.append(stripped)
            else:
                # Regular code line
                fixed_lines.append('    ' * indent_level + stripped)
        
        # Write fixed content
        with open(file_path, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all problematic files"""
    files_to_fix = [
        'src/multi_agent_testing/multi_dimensional_smoke_test.py',
        'src/multi_agent_testing/test_anthropic_simple.py',
        'src/security_first/test_security_model.py',
        'src/multi_agent_testing/live_smoke_test_langchain.py'
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            print(f"Fixing {file_path}...")
            if fix_file(file_path):
                print(f"✅ Fixed {file_path}")
            else:
                print(f"❌ Failed to fix {file_path}")

if __name__ == "__main__":
    main() 