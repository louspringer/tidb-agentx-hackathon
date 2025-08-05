#!/usr/bin/env python3
"""
Fix Common Flake8 Issues - Systematic Style Fixes
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Any


def fix_unused_imports(filepath: str) -> bool:
    """Remove unused imports"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        changes_made = False
        
        # Parse the file to find used names
        try:
            tree = ast.parse(content)
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    used_names.add(node.attr)
        except:
            # If parsing fails, skip this file
            return False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for import lines
            if line.strip().startswith('from ') and ' import ' in line:
                # Parse the import
                match = re.match(r'from\s+(\w+)\s+import\s+(.+)', line.strip())
                if match:
                    module = match.group(1)
                    imports = match.group(2)
                    
                    # Parse individual imports
                    import_list = []
                    for imp in imports.split(','):
                        imp = imp.strip()
                        if ' as ' in imp:
                            name = imp.split(' as ')[0].strip()
                        else:
                            name = imp.strip()
                        
                        # Check if this import is actually used
                        if name in used_names or name == '*':
                            import_list.append(imp)
                        else:
                            changes_made = True
                    
                    if import_list:
                        new_line = f"from {module} import {', '.join(import_list)}"
                        fixed_lines.append(new_line)
                    else:
                        # All imports unused, skip the line
                        changes_made = True
                        i += 1
                        continue
                else:
                    fixed_lines.append(line)
            elif line.strip().startswith('import ') and ' as ' not in line:
                # Simple import
                match = re.match(r'import\s+(\w+)', line.strip())
                if match:
                    module = match.group(1)
                    if module not in used_names:
                        changes_made = True
                        i += 1
                        continue
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            
            i += 1
        
        if changes_made:
            fixed_content = '\n'.join(fixed_lines)
            with open(filepath, 'w') as f:
                f.write(fixed_content)
            print(f"✅ Fixed unused imports: {filepath}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error fixing imports in {filepath}: {e}")
        return False


def fix_f_strings(filepath: str) -> bool:
    """Fix f-strings without placeholders"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        changes_made = False
        
        for line in lines:
            # Find f-strings without placeholders
            if 'f"' in line or "f'" in line:
                # Check if there are any placeholders
                if not re.search(r'\{[^}]*\}', line):
                    # Replace f-string with regular string
                    new_line = line.replace('f"', '"').replace("f'", "'")
                    fixed_lines.append(new_line)
                    changes_made = True
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        if changes_made:
            fixed_content = '\n'.join(fixed_lines)
            with open(filepath, 'w') as f:
                f.write(fixed_content)
            print(f"✅ Fixed f-strings: {filepath}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error fixing f-strings in {filepath}: {e}")
        return False


def fix_unused_variables(filepath: str) -> bool:
    """Fix unused variables by adding underscore prefix"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        changes_made = False
        
        # Parse to find used variables
        try:
            tree = ast.parse(content)
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
        except:
            return False
        
        for line in lines:
            # Look for variable assignments
            if ' = ' in line and not line.strip().startswith('#'):
                match = re.match(r'^(\s*)(\w+)\s*=', line)
                if match:
                    indent = match.group(1)
                    var_name = match.group(2)
                    
                    # Check if variable is used
                    if var_name not in used_names and not var_name.startswith('_'):
                        # Prefix with underscore to indicate unused
                        new_line = line.replace(f"{var_name} =", f"_{var_name} =")
                        fixed_lines.append(new_line)
                        changes_made = True
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        if changes_made:
            fixed_content = '\n'.join(fixed_lines)
            with open(filepath, 'w') as f:
                f.write(fixed_content)
            print(f"✅ Fixed unused variables: {filepath}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error fixing unused variables in {filepath}: {e}")
        return False


def main() -> None:
    """Main function to fix Flake8 issues"""
    print("🎯 Fixing Common Flake8 Issues")
    print("=" * 40)
    
    # Find all Python files
    src_path = Path("src")
    python_files = list(src_path.rglob("*.py"))
    
    total_fixed = 0
    
    for py_file in python_files:
        file_fixed = False
        
        # Fix unused imports
        if fix_unused_imports(str(py_file)):
            file_fixed = True
        
        # Fix f-strings
        if fix_f_strings(str(py_file)):
            file_fixed = True
        
        # Fix unused variables
        if fix_unused_variables(str(py_file)):
            file_fixed = True
        
        if file_fixed:
            total_fixed += 1
    
    print("\n" + "=" * 40)
    print(f"🎯 Summary:")
    print(f"📊 Files with Flake8 fixes: {total_fixed}")
    print(f"📊 Files processed: {len(python_files)}")
    
    if total_fixed > 0:
        print("\n🚀 Running Flake8 to check improvements...")
        import subprocess
        result = subprocess.run(
            ["uv", "run", "flake8", "src/"],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            errors = [line for line in result.stdout.split('\n') if line.strip()]
            print(f"📊 Remaining Flake8 errors: {len(errors)}")
        else:
            print("✅ No Flake8 errors found!")


if __name__ == "__main__":
    main() 