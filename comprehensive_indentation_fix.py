#!/usr/bin/env python3
"""
Comprehensive Indentation Fixer
Fixes all indentation issues in broken Python files
"""

import re
import ast
from pathlib import Path
from typing import List, Dict


class ComprehensiveIndentationFixer:
    """Comprehensive indentation fixer for broken Python files"""
    
    def fix_file(self, file_path: str) -> str:
        """Fix all indentation issues in a file"""
        print(f"🔧 Comprehensive indentation fixing: {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Apply comprehensive indentation fixes
        fixed_content = self.apply_comprehensive_indentation_fixes(content)
        
        # Validate the fix
        if self.validate_fix(fixed_content):
            print(f"  ✅ Comprehensive indentation fix successful")
            return fixed_content
        else:
            print(f"  ⚠️  Comprehensive indentation fix may have issues")
            return fixed_content
    
    def apply_comprehensive_indentation_fixes(self, content: str) -> str:
        """Apply comprehensive indentation fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        # Track indentation context
        current_indent_level = 0
        in_function = False
        in_class = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                fixed_lines.append('')
                continue
            
            # Handle shebang and imports (module level)
            if stripped.startswith('#!/usr/bin/env') or stripped.startswith(('import ', 'from ')):
                fixed_lines.append(stripped)
                continue
            
            # Handle module docstring
            if stripped.startswith('"""') and i < 5:  # Early in file
                fixed_lines.append(stripped)
                continue
            
            # Handle class definitions
            if stripped.startswith('class '):
                in_class = True
                in_function = False
                fixed_lines.append(stripped)
                continue
            
            # Handle function definitions
            if stripped.startswith('def '):
                in_function = True
                fixed_lines.append('    ' + stripped)  # 4 spaces for function definitions
                continue
            
            # Handle control flow statements
            if any(stripped.startswith(keyword) for keyword in ['if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ', 'else:', 'elif ']):
                fixed_lines.append('        ' + stripped)  # 8 spaces for control flow
                continue
            
            # Handle return/break/continue/pass/raise
            if any(stripped.startswith(keyword) for keyword in ['return ', 'break', 'continue', 'pass', 'raise ']):
                fixed_lines.append('        ' + stripped)  # 8 spaces for statements
                continue
            
            # Handle variable assignments and other statements
            if in_function or in_class:
                # Check if this line should be indented
                if self.should_be_indented(stripped, i, lines):
                    fixed_lines.append('        ' + stripped)  # 8 spaces for function/class body
                else:
                    fixed_lines.append('    ' + stripped)  # 4 spaces for class/function definitions
            else:
                # Module level
                fixed_lines.append(stripped)
        
        return '\n'.join(fixed_lines)
    
    def should_be_indented(self, stripped: str, line_num: int, all_lines: List[str]) -> bool:
        """Determine if a line should be indented"""
        
        # Look back to find the context
        for i in range(line_num - 1, -1, -1):
            prev_line = all_lines[i].strip()
            
            # If we find a colon, the next line should be indented
            if prev_line.endswith(':'):
                return True
            
            # If we find a function/class definition, we're in that context
            if prev_line.startswith(('def ', 'class ')):
                return True
            
            # If we find an import, we're back at module level
            if prev_line.startswith(('import ', 'from ')):
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
    """Test the comprehensive indentation fixer"""
    print("🔧 Comprehensive Indentation Fixer")
    print("=" * 50)
    
    fixer = ComprehensiveIndentationFixer()
    
    # Test with known broken files
    test_files = [
        'scripts/mdc-linter.py',
        '.cursor/plugins/rule-compliance-checker.py'
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Comprehensive fixing: {file_path}")
            
            # Create backup
            backup_path = f"{file_path}.backup4"
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