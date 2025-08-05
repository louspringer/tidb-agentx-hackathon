#!/usr/bin/env python3
"""
Semantic Reconstructor
Reconstructs broken Python files using semantic understanding
"""

import re
from pathlib import Path
from typing import Dict, List, Any
from broken_python_interpreter import BrokenPythonInterpreter


class SemanticReconstructor:
    """Reconstructs broken Python files using semantic understanding"""
    
    def __init__(self):
        self.interpreter = BrokenPythonInterpreter()
        self.fix_patterns = {
            'indentation_fixes': [
                (r'^(\w+):\s*(\w+)\s*=\s*', r'    \1: \2 = '),  # Fix unindented assignments
                (r'^(\w+)\s*=\s*([^=]+)$', r'    \1 = \2'),  # Fix unindented assignments
            ],
            'colon_fixes': [
                (r'^def\s+(\w+)\s*\([^)]*\)\s*$', r'def \1():'),  # Add missing colons
                (r'^class\s+(\w+)\s*\([^)]*\)\s*$', r'class \1():'),  # Add missing colons
                (r'^if\s+([^:]+)\s*$', r'if \1:'),  # Add missing colons
                (r'^for\s+([^:]+)\s*$', r'for \1:'),  # Add missing colons
                (r'^while\s+([^:]+)\s*$', r'while \1:'),  # Add missing colons
                (r'^try\s*$', r'try:'),  # Add missing colons
                (r'^with\s+([^:]+)\s*$', r'with \1:'),  # Add missing colons
            ],
            'subprocess_fixes': [
                (r'subprocess\.run\(([^)]*)\)', r'subprocess.run(\1, check=True)'),  # Fix subprocess calls
            ],
            'import_fixes': [
                (r'^from\s+typing\s+import\s*$', r'from typing import List, Dict, Any, Optional'),  # Fix incomplete imports
            ]
        }
    
    def reconstruct_file(self, file_path: str) -> str:
        """Reconstruct broken Python file"""
        print(f"🔧 Reconstructing: {file_path}")
        
        # Step 1: Interpret the broken file
        interpretation = self.interpreter.interpret_broken_file(file_path)
        
        if interpretation['status'] == 'valid_python':
            print(f"  ✅ File is already valid Python")
            return self.read_file_content(file_path)
        
        # Step 2: Read the original content
        original_content = self.read_file_content(file_path)
        
        # Step 3: Apply semantic fixes
        fixed_content = self.apply_semantic_fixes(original_content, interpretation)
        
        # Step 4: Validate the fix
        if self.validate_fix(fixed_content):
            print(f"  ✅ Reconstruction successful")
            return fixed_content
        else:
            print(f"  ⚠️  Reconstruction may have issues")
            return fixed_content
    
    def read_file_content(self, file_path: str) -> str:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"  ❌ Cannot read file: {e}")
            return ""
    
    def apply_semantic_fixes(self, content: str, interpretation: Dict[str, Any]) -> str:
        """Apply semantic fixes based on interpretation"""
        fixed_content = content
        
        # Apply indentation fixes
        fixed_content = self.apply_indentation_fixes(fixed_content)
        
        # Apply colon fixes
        fixed_content = self.apply_colon_fixes(fixed_content)
        
        # Apply subprocess fixes
        fixed_content = self.apply_subprocess_fixes(fixed_content)
        
        # Apply import fixes
        fixed_content = self.apply_import_fixes(fixed_content)
        
        # Apply specific fixes based on interpretation
        if 'interpretation' in interpretation:
            interp = interpretation['interpretation']
            fixed_content = self.apply_interpretation_based_fixes(fixed_content, interp)
        
        return fixed_content
    
    def apply_indentation_fixes(self, content: str) -> str:
        """Apply indentation fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix unindented assignments after colons
            if ': Any =' in line and not line.startswith('    '):
                line = '    ' + line
                print(f"    Fixed indentation on line {i + 1}")
            
            # Fix unindented assignments
            elif line.strip() and ' = ' in line and not line.startswith('    ') and not line.startswith('def ') and not line.startswith('class '):
                # Check if previous line ends with colon
                if i > 0 and lines[i - 1].strip().endswith(':'):
                    line = '    ' + line
                    print(f"    Fixed indentation on line {i + 1}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def apply_colon_fixes(self, content: str) -> str:
        """Apply missing colon fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix missing colons after function definitions
            if re.match(r'^def\s+\w+\s*\([^)]*\)\s*$', line.strip()):
                line = line.rstrip() + ':'
                print(f"    Added missing colon on line {i + 1}")
            
            # Fix missing colons after class definitions
            elif re.match(r'^class\s+\w+\s*\([^)]*\)\s*$', line.strip()):
                line = line.rstrip() + ':'
                print(f"    Added missing colon on line {i + 1}")
            
            # Fix missing colons after control flow statements
            elif re.match(r'^(if|for|while|try|with)\s+', line.strip()) and not line.strip().endswith(':'):
                line = line.rstrip() + ':'
                print(f"    Added missing colon on line {i + 1}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def apply_subprocess_fixes(self, content: str) -> str:
        """Apply subprocess call fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix subprocess.run calls without check parameter
            if 'subprocess.run(' in line and 'check=True' not in line and 'check=False' not in line:
                line = re.sub(r'subprocess\.run\(([^)]*)\)', r'subprocess.run(\1, check=True)', line)
                print(f"    Fixed subprocess.run call on line {i + 1}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def apply_import_fixes(self, content: str) -> str:
        """Apply import fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix incomplete typing imports
            if line.strip() == 'from typing import':
                line = 'from typing import List, Dict, Any, Optional'
                print(f"    Fixed incomplete typing import on line {i + 1}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def apply_interpretation_based_fixes(self, content: str, interpretation: Dict[str, Any]) -> str:
        """Apply fixes based on interpretation analysis"""
        lines = content.split('\n')
        fixed_lines = []
        
        # Get syntax issues from interpretation
        syntax_issues = interpretation.get('syntax_issues', [])
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check if this line has syntax issues
            for issue in syntax_issues:
                if issue.get('line') == line_num:
                    line = self.fix_syntax_issue(line, issue)
                    print(f"    Fixed syntax issue on line {line_num}: {issue.get('description', 'unknown')}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_syntax_issue(self, line: str, issue: Dict[str, Any]) -> str:
        """Fix a specific syntax issue"""
        issue_type = issue.get('type', '')
        
        if issue_type == 'indentation_error':
            # Fix indentation
            if not line.startswith('    '):
                line = '    ' + line
        
        elif issue_type == 'missing_colon':
            # Add missing colon
            if not line.strip().endswith(':'):
                line = line.rstrip() + ':'
        
        return line
    
    def validate_fix(self, content: str) -> bool:
        """Validate that the fix produces valid Python"""
        try:
            # Try to parse with AST
            import ast
            ast.parse(content)
            return True
        except (SyntaxError, IndentationError):
            return False
    
    def reconstruct_multiple_files(self, file_paths: List[str]) -> Dict[str, str]:
        """Reconstruct multiple files"""
        results = {}
        
        for file_path in file_paths:
            if Path(file_path).exists():
                try:
                    reconstructed_content = self.reconstruct_file(file_path)
                    results[file_path] = reconstructed_content
                except Exception as e:
                    print(f"  ❌ Failed to reconstruct {file_path}: {e}")
                    results[file_path] = None
        
        return results
    
    def save_reconstructed_file(self, file_path: str, content: str) -> bool:
        """Save reconstructed content to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"  ❌ Failed to save {file_path}: {e}")
            return False


def main() -> None:
    """Test the semantic reconstructor"""
    import sys
    
    print("🔧 Semantic Reconstructor")
    print("=" * 50)
    
    reconstructor = SemanticReconstructor()
    
    # Use command line argument if provided, otherwise use default files
    if len(sys.argv) > 1:
        test_files = sys.argv[1:]
    else:
        test_files = [
            'scripts/mdc-linter.py',
            '.cursor/plugins/rule-compliance-checker.py'
        ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Reconstructing: {file_path}")
            
            # Reconstruct the file
            reconstructed_content = reconstructor.reconstruct_file(file_path)
            
            if reconstructed_content:
                # Save the reconstructed file
                backup_path = f"{file_path}.backup"
                if not Path(backup_path).exists():
                    # Create backup
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    print(f"  💾 Created backup: {backup_path}")
                
                # Save reconstructed content
                if reconstructor.save_reconstructed_file(file_path, reconstructed_content):
                    print(f"  ✅ Saved reconstructed file")
                else:
                    print(f"  ❌ Failed to save file")
            else:
                print(f"  ❌ Reconstruction failed")
        else:
            print(f"  ❌ File not found: {file_path}")


if __name__ == "__main__":
    main() 