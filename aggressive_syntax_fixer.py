#!/usr/bin/env python3
"""
Aggressive Syntax Fixer
Fixes complex syntax issues in broken Python files
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Any


class AggressiveSyntaxFixer:
    """Aggressive syntax fixer for severely broken Python files"""
    
    def __init__(self):
        self.fix_patterns = [
            # Fix inconsistent indentation
            (r'^\s{2,}self\.', '        self.'),  # Fix self. indentation
            (r'^\s{6,}"""', '        """'),  # Fix docstring indentation
            (r'^\s{6,}def\s', '    def '),  # Fix function indentation
            (r'^\s{6,}class\s', '    class '),  # Fix class indentation
            (r'^\s{6,}if\s', '        if '),  # Fix if indentation
            (r'^\s{6,}for\s', '        for '),  # Fix for indentation
            (r'^\s{6,}while\s', '        while '),  # Fix while indentation
            (r'^\s{6,}try\s', '        try '),  # Fix try indentation
            (r'^\s{6,}except\s', '        except '),  # Fix except indentation
            (r'^\s{6,}finally\s', '        finally '),  # Fix finally indentation
            (r'^\s{6,}with\s', '        with '),  # Fix with indentation
            (r'^\s{6,}return\s', '        return '),  # Fix return indentation
            (r'^\s{6,}break\s', '        break '),  # Fix break indentation
            (r'^\s{6,}continue\s', '        continue '),  # Fix continue indentation
            (r'^\s{6,}pass\s', '        pass '),  # Fix pass indentation
            (r'^\s{6,}raise\s', '        raise '),  # Fix raise indentation
            (r'^\s{6,}import\s', 'import '),  # Fix import indentation
            (r'^\s{6,}from\s', 'from '),  # Fix from import indentation
        ]
    
    def fix_file(self, file_path: str) -> str:
        """Fix a broken Python file aggressively"""
        print(f"🔧 Aggressively fixing: {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Apply aggressive fixes
        fixed_content = self.apply_aggressive_fixes(content)
        
        # Validate the fix
        if self.validate_fix(fixed_content):
            print(f"  ✅ Aggressive fix successful")
            return fixed_content
        else:
            print(f"  ⚠️  Aggressive fix may have issues")
            return fixed_content
    
    def apply_aggressive_fixes(self, content: str) -> str:
        """Apply aggressive syntax fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix inconsistent indentation
            line = self.fix_indentation_aggressive(line, i, lines)
            
            # Fix missing colons
            line = self.fix_missing_colons(line)
            
            # Fix subprocess calls
            line = self.fix_subprocess_calls(line)
            
            # Fix incomplete imports
            line = self.fix_incomplete_imports(line)
            
            # Fix variable assignments
            line = self.fix_variable_assignments(line, i, lines)
            
            if line != original_line:
                print(f"    Fixed line {i + 1}: {original_line.strip()} -> {line.strip()}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_indentation_aggressive(self, line: str, line_num: int, all_lines: List[str]) -> str:
        """Fix indentation aggressively"""
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            return line
        
        # Fix self. statements
        if stripped.startswith('self.'):
            return '        ' + stripped
        
        # Fix docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return '        ' + stripped
        
        # Fix function definitions
        if stripped.startswith('def '):
            return '    ' + stripped
        
        # Fix class definitions
        if stripped.startswith('class '):
            return '    ' + stripped
        
        # Fix control flow statements
        if any(stripped.startswith(keyword) for keyword in ['if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ', 'else:', 'elif ']):
            return '        ' + stripped
        
        # Fix return/break/continue/pass/raise
        if any(stripped.startswith(keyword) for keyword in ['return ', 'break', 'continue', 'pass', 'raise ']):
            return '        ' + stripped
        
        # Fix imports (should be at module level)
        if stripped.startswith(('import ', 'from ')):
            return stripped  # No indentation for imports
        
        # Fix variable assignments
        if ' = ' in stripped and not stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ')):
            # Check if we're in a function/class context
            if self.is_in_function_context(line_num, all_lines):
                return '        ' + stripped
            else:
                return stripped
        
        # Fix other statements
        if stripped and not stripped.startswith(('def ', 'class ', 'import ', 'from ')):
            # Check if we're in a function/class context
            if self.is_in_function_context(line_num, all_lines):
                return '        ' + stripped
        
        return line
    
    def is_in_function_context(self, line_num: int, all_lines: List[str]) -> bool:
        """Check if we're inside a function or class definition"""
        for i in range(line_num - 1, -1, -1):
            line = all_lines[i].strip()
            if line.startswith(('def ', 'class ')):
                return True
            elif line.startswith(('import ', 'from ')):
                return False
        return False
    
    def fix_missing_colons(self, line: str) -> str:
        """Fix missing colons"""
        stripped = line.strip()
        
        # Fix function definitions
        if re.match(r'^def\s+\w+\s*\([^)]*\)\s*$', stripped):
            return line.rstrip() + ':'
        
        # Fix class definitions
        if re.match(r'^class\s+\w+\s*\([^)]*\)\s*$', stripped):
            return line.rstrip() + ':'
        
        # Fix control flow statements
        if re.match(r'^(if|for|while|try|with)\s+', stripped) and not stripped.endswith(':'):
            return line.rstrip() + ':'
        
        return line
    
    def fix_subprocess_calls(self, line: str) -> str:
        """Fix subprocess.run calls"""
        if 'subprocess.run(' in line and 'check=True' not in line and 'check=False' not in line:
            return re.sub(r'subprocess\.run\(([^)]*)\)', r'subprocess.run(\1, check=True)', line)
        return line
    
    def fix_incomplete_imports(self, line: str) -> str:
        """Fix incomplete imports"""
        stripped = line.strip()
        
        if stripped == 'from typing import':
            return 'from typing import List, Dict, Any, Optional'
        
        return line
    
    def fix_variable_assignments(self, line: str, line_num: int, all_lines: List[str]) -> str:
        """Fix variable assignments"""
        stripped = line.strip()
        
        # Fix type annotations
        if ': Any =' in stripped and not line.startswith('    '):
            return '    ' + line
        
        # Fix other assignments
        if ' = ' in stripped and not stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ')):
            if self.is_in_function_context(line_num, all_lines):
                if not line.startswith('    '):
                    return '    ' + line
        
        return line
    
    def validate_fix(self, content: str) -> bool:
        """Validate that the fix produces valid Python"""
        try:
            ast.parse(content)
            return True
        except (SyntaxError, IndentationError):
            return False
    
    def fix_multiple_files(self, file_paths: List[str]) -> Dict[str, str]:
        """Fix multiple files"""
        results = {}
        
        for file_path in file_paths:
            if Path(file_path).exists():
                try:
                    fixed_content = self.fix_file(file_path)
                    results[file_path] = fixed_content
                except Exception as e:
                    print(f"  ❌ Failed to fix {file_path}: {e}")
                    results[file_path] = None
        
        return results
    
    def save_fixed_file(self, file_path: str, content: str) -> bool:
        """Save fixed content to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"  ❌ Failed to save {file_path}: {e}")
            return False


def main() -> None:
    """Test the aggressive syntax fixer"""
    print("🔧 Aggressive Syntax Fixer")
    print("=" * 50)
    
    fixer = AggressiveSyntaxFixer()
    
    # Test with known broken files
    test_files = [
        'scripts/mdc-linter.py',
        '.cursor/plugins/rule-compliance-checker.py'
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Fixing: {file_path}")
            
            # Create backup
            backup_path = f"{file_path}.backup2"
            if not Path(backup_path).exists():
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"  💾 Created backup: {backup_path}")
            
            # Fix the file
            fixed_content = fixer.fix_file(file_path)
            
            if fixed_content:
                # Save the fixed file
                if fixer.save_fixed_file(file_path, fixed_content):
                    print(f"  ✅ Saved fixed file")
                    
                    # Test if it's now valid Python
                    try:
                        ast.parse(fixed_content)
                        print(f"  ✅ File is now valid Python")
                    except Exception as e:
                        print(f"  ⚠️  File still has issues: {e}")
                else:
                    print(f"  ❌ Failed to save file")
            else:
                print(f"  ❌ Fixing failed")


if __name__ == "__main__":
    main() 