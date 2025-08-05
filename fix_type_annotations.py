#!/usr/bin/env python3
"""
Fix common type annotation issues
"""

import re
from pathlib import Path

def fix_type_annotations_in_file(filepath: str) -> bool:
    """Fix common type annotation issues in a Python file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Fix missing return type annotations for functions
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix function definitions missing return type annotations
            if re.match(r'^\s*def\s+\w+\s*\([^)]*\)\s*:$', line):
                # Add -> None for functions without return type
                if '->' not in line:
                    line = line.replace('):', ') -> None:')
            
            # Fix function definitions with parameters but no return type
            elif re.match(r'^\s*def\s+\w+\s*\([^)]*\)\s*->\s*$', line):
                # Add None for incomplete return type
                line = line.replace('->', '-> None')
            
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        if fixed_content != original_content:
            with open(filepath, 'w') as f:
                f.write(fixed_content)
            print(f"✅ Fixed type annotations: {filepath}")
            return True
        else:
            print(f"⚠️  No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def add_missing_imports(filepath: str) -> bool:
    """Add missing imports for common type issues"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Add missing imports
        imports_to_add = []
        
        # Check if we need to add typing imports
        if 'Any' in content and 'from typing import' not in content:
            imports_to_add.append('from typing import Any')
        if 'Dict' in content and 'from typing import' not in content:
            imports_to_add.append('from typing import Dict')
        if 'List' in content and 'from typing import' not in content:
            imports_to_add.append('from typing import List')
        if 'Optional' in content and 'from typing import' not in content:
            imports_to_add.append('from typing import Optional')
        
        # Add missing standard library imports
        if 're.' in content and 'import re' not in content:
            imports_to_add.append('import re')
        if 'html.' in content and 'import html' not in content:
            imports_to_add.append('import html')
        if 'urlparse' in content and 'from urllib.parse import urlparse' not in content:
            imports_to_add.append('from urllib.parse import urlparse')
        
        if imports_to_add:
            lines = content.split('\n')
            new_lines = []
            
            # Find the right place to insert imports
            import_section_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_section_end = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
            
            # Insert imports
            for i, line in enumerate(lines):
                new_lines.append(line)
                if i == import_section_end - 1:
                    for import_line in imports_to_add:
                        new_lines.append(import_line)
            
            fixed_content = '\n'.join(new_lines)
            
            if fixed_content != original_content:
                with open(filepath, 'w') as f:
                    f.write(fixed_content)
                print(f"✅ Added missing imports: {filepath}")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error adding imports to {filepath}: {e}")
        return False

def main():
    """Fix type annotations in all Python files"""
    
    # Get all Python files in src/
    python_files = []
    for filepath in Path('src').rglob('*.py'):
        python_files.append(str(filepath))
    
    print("🔧 Fixing type annotations...")
    print("=" * 50)
    
    type_fixes = 0
    import_fixes = 0
    
    for filepath in python_files:
        if fix_type_annotations_in_file(filepath):
            type_fixes += 1
        if add_missing_imports(filepath):
            import_fixes += 1
    
    print(f"\n✅ Fixed type annotations in {type_fixes} files")
    print(f"✅ Added missing imports in {import_fixes} files")
    
    # Test MyPy again
    print("\n🧪 Testing MyPy after fixes...")
    import subprocess
    result = subprocess.run(['uv', 'run', 'mypy', 'src/', '--ignore-missing-imports'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ MyPy passed with no errors!")
    else:
        error_count = len(result.stdout.split('\n')) - 1
        print(f"⚠️  MyPy found {error_count} remaining issues")
        print("First few errors:")
        for line in result.stdout.split('\n')[:10]:
            if line.strip():
                print(f"  {line}")

if __name__ == "__main__":
    main() 