#!/usr/bin/env python3
"""
Final Syntax Fixer
Comprehensive fixer for all remaining syntax issues
"""

import re
import ast
from pathlib import Path
from typing import List, Dict


class FinalSyntaxFixer:
    """Final comprehensive syntax fixer"""
    
    def fix_file(self, file_path: str) -> str:
        """Fix all syntax issues in a file"""
        print(f"🔧 Final fixing: {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Apply comprehensive fixes
        fixed_content = self.apply_comprehensive_fixes(content)
        
        # Validate the fix
        if self.validate_fix(fixed_content):
            print(f"  ✅ Final fix successful")
            return fixed_content
        else:
            print(f"  ⚠️  Final fix may have issues")
            return fixed_content
    
    def apply_comprehensive_fixes(self, content: str) -> str:
        """Apply comprehensive syntax fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        # Fix the file structure
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Fix shebang placement
            if i == 0 and line.startswith('from typing'):
                # Move shebang to top
                fixed_lines.append('#!/usr/bin/env python3')
                fixed_lines.append('')
                fixed_lines.append(line)
                i += 1
                continue
            
            # Fix docstring indentation
            if line.strip().startswith('"""') and i > 0:
                # Check if this is a module docstring
                if i == 1 or (i == 2 and lines[0].startswith('#!/usr/bin/env')):
                    line = '"""' + line.strip()[3:]  # Remove extra indentation
                else:
                    line = '        ' + line.strip()  # Proper indentation for class/function docstrings
            
            # Fix class definitions
            elif line.strip().startswith('class '):
                line = 'class ' + line.strip()[6:]  # Remove extra indentation
            
            # Fix function definitions
            elif line.strip().startswith('def '):
                line = '    def ' + line.strip()[4:]  # Proper indentation
            
            # Fix imports (should be at module level)
            elif line.strip().startswith(('import ', 'from ')):
                line = line.strip()  # No indentation for imports
            
            # Fix control flow statements
            elif any(line.strip().startswith(keyword) for keyword in ['if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ', 'else:', 'elif ']):
                line = '        ' + line.strip()  # Proper indentation
            
            # Fix return/break/continue/pass/raise
            elif any(line.strip().startswith(keyword) for keyword in ['return ', 'break', 'continue', 'pass', 'raise ']):
                line = '        ' + line.strip()  # Proper indentation
            
            # Fix variable assignments
            elif ' = ' in line.strip() and not line.strip().startswith(('def ', 'class ', 'if ', 'for ', 'while ')):
                if self.is_in_function_context(i, lines):
                    line = '        ' + line.strip()  # Proper indentation
                else:
                    line = line.strip()  # No indentation for module level
            
            # Fix other statements
            elif line.strip() and not line.strip().startswith(('def ', 'class ', 'import ', 'from ')):
                if self.is_in_function_context(i, lines):
                    line = '        ' + line.strip()  # Proper indentation
                else:
                    line = line.strip()  # No indentation for module level
            
            # Fix empty lines
            elif not line.strip():
                line = ''
            
            fixed_lines.append(line)
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def is_in_function_context(self, line_num: int, all_lines: List[str]) -> bool:
        """Check if we're inside a function or class definition"""
        for i in range(line_num - 1, -1, -1):
            line = all_lines[i].strip()
            if line.startswith(('def ', 'class ')):
                return True
            elif line.startswith(('import ', 'from ')):
                return False
        return False
    
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
    """Test the final syntax fixer"""
    print("🔧 Final Syntax Fixer")
    print("=" * 50)
    
    fixer = FinalSyntaxFixer()
    
    # Test with known broken files
    test_files = [
        'scripts/mdc-linter.py',
        '.cursor/plugins/rule-compliance-checker.py'
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Final fixing: {file_path}")
            
            # Create backup
            backup_path = f"{file_path}.backup3"
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