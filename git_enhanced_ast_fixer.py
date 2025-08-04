#!/usr/bin/env python3
"""
Git-Enhanced AST Fixer
Uses Git history to restore previous working versions and guide AST-based reconstruction
"""

import subprocess
import tempfile
import os
import ast
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from broken_python_interpreter import BrokenPythonInterpreter


class GitEnhancedASTFixer:
    """Git-enhanced AST fixer that uses previous working commits to guide reconstruction"""
    
    def __init__(self):
        self.interpreter = BrokenPythonInterpreter()
        self.temp_dir = None
    
    def fix_file_with_git_history(self, file_path: str) -> str:
        """Fix a broken file using Git history to guide reconstruction"""
        print(f"🔧 Git-enhanced fixing: {file_path}")
        
        # Step 1: Find previous working version
        previous_working = self.find_previous_working_version(file_path)
        if not previous_working:
            print(f"  ⚠️  No previous working version found, using standard AST fixer")
            return self.fix_without_git_history(file_path)
        
        print(f"  📋 Found previous working version: {previous_working['commit']}")
        
        # Step 2: Restore previous version to temp area
        temp_file = self.restore_to_temp(file_path, previous_working['commit'])
        if not temp_file:
            print(f"  ❌ Failed to restore previous version")
            return self.fix_without_git_history(file_path)
        
        # Step 3: AST parse the previous working version
        previous_ast = self.parse_previous_version(temp_file)
        if not previous_ast:
            print(f"  ❌ Failed to parse previous version")
            return self.fix_without_git_history(file_path)
        
        print(f"  ✅ Previous version parsed successfully")
        print(f"    Functions: {len(previous_ast.get('functions', []))}")
        print(f"    Classes: {len(previous_ast.get('classes', []))}")
        print(f"    Imports: {len(previous_ast.get('imports', []))}")
        
        # Step 4: Interpret current broken version
        current_interpretation = self.interpreter.interpret_broken_file(file_path)
        
        # Step 5: Use previous AST to guide reconstruction
        reconstructed_content = self.reconstruct_with_guidance(
            file_path, current_interpretation, previous_ast
        )
        
        # Step 6: Clean up temp file
        self.cleanup_temp_file(temp_file)
        
        return reconstructed_content
    
    def find_previous_working_version(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Find the most recent working version of a file in Git history"""
        try:
            # Get Git log for the file
            result = subprocess.run(
                ['git', 'log', '--oneline', '--follow', '--', file_path],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            
            if result.returncode != 0:
                print(f"  ⚠️  Git log failed: {result.stderr}")
                return None
            
            commits = result.stdout.strip().split('\n')
            if not commits or commits[0] == '':
                print(f"  ⚠️  No Git history found for {file_path}")
                return None
            
            # Check each commit to find the most recent working version
            for commit_line in commits:
                commit_hash = commit_line.split()[0]
                
                # Try to restore this version
                temp_file = self.restore_to_temp(file_path, commit_hash)
                if temp_file:
                    # Check if this version is valid Python
                    if self.is_valid_python_file(temp_file):
                        print(f"  ✅ Found working version at commit {commit_hash}")
                        return {
                            'commit': commit_hash,
                            'message': commit_line,
                            'temp_file': temp_file
                        }
                    else:
                        # Clean up invalid temp file
                        self.cleanup_temp_file(temp_file)
            
            print(f"  ⚠️  No working version found in Git history")
            return None
            
        except Exception as e:
            print(f"  ❌ Error finding previous version: {e}")
            return None
    
    def restore_to_temp(self, file_path: str, commit_hash: str) -> Optional[str]:
        """Restore a file from a specific commit to a temporary location"""
        try:
            # Create temp directory if needed
            if not self.temp_dir:
                self.temp_dir = tempfile.mkdtemp(prefix="git_ast_fixer_")
            
            # Get the file content from the specific commit
            result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{file_path}'],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            
            if result.returncode != 0:
                print(f"  ⚠️  Failed to restore {file_path} from {commit_hash}: {result.stderr}")
                return None
            
            # Create temp file
            temp_file = os.path.join(self.temp_dir, f"{Path(file_path).name}.{commit_hash[:8]}")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            return temp_file
            
        except Exception as e:
            print(f"  ❌ Error restoring to temp: {e}")
            return None
    
    def parse_previous_version(self, temp_file: str) -> Optional[Dict[str, Any]]:
        """Parse the previous working version with AST"""
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST
            tree = ast.parse(content)
            
            # Extract structure information
            return {
                'functions': self.extract_functions_from_ast(tree),
                'classes': self.extract_classes_from_ast(tree),
                'imports': self.extract_imports_from_ast(tree),
                'variables': self.extract_variables_from_ast(tree),
                'content': content,
                'ast_tree': tree
            }
            
        except Exception as e:
            print(f"  ❌ Error parsing previous version: {e}")
            return None
    
    def extract_functions_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract functions from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [self.extract_decorator(d) for d in node.decorator_list],
                    'docstring': ast.get_docstring(node)
                })
        return functions
    
    def extract_classes_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract classes from AST"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'bases': [self.extract_base(base) for base in node.bases],
                    'methods': self.extract_class_methods(node),
                    'docstring': ast.get_docstring(node)
                })
        return classes
    
    def extract_imports_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract imports from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'asname': alias.asname,
                        'lineno': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': node.module,
                        'name': alias.name,
                        'asname': alias.asname,
                        'lineno': node.lineno
                    })
        return imports
    
    def extract_variables_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract variables from AST"""
        variables = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            'name': target.id,
                            'lineno': node.lineno,
                            'value_type': type(node.value).__name__
                        })
        return variables
    
    def extract_decorator(self, node: ast.expr) -> str:
        """Extract decorator name from AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
        return "unknown"
    
    def extract_base(self, node: ast.expr) -> str:
        """Extract base class name from AST"""
        if isinstance(node, ast.Name):
            return node.id
        return "unknown"
    
    def extract_class_methods(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract class methods from AST"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    'name': item.name,
                    'lineno': item.lineno,
                    'args': [arg.arg for arg in item.args.args],
                    'docstring': ast.get_docstring(item)
                })
        return methods
    
    def is_valid_python_file(self, file_path: str) -> bool:
        """Check if a file is valid Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except (SyntaxError, IndentationError):
            return False
    
    def reconstruct_with_guidance(self, file_path: str, current_interpretation: Dict[str, Any], previous_ast: Dict[str, Any]) -> str:
        """Reconstruct file using previous AST as guidance"""
        print(f"  🔧 Reconstructing with guidance from previous version")
        
        # Read current broken content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            current_content = f.read()
        
        # Use previous version as template
        previous_content = previous_ast['content']
        
        # Apply guided reconstruction
        reconstructed = self.apply_guided_reconstruction(
            current_content, previous_content, current_interpretation, previous_ast
        )
        
        return reconstructed
    
    def apply_guided_reconstruction(self, current_content: str, previous_content: str, 
                                  current_interpretation: Dict[str, Any], previous_ast: Dict[str, Any]) -> str:
        """Apply guided reconstruction using previous version as reference"""
        
        # Start with previous working content as base
        reconstructed_lines = previous_content.split('\n')
        
        # Get current interpretation details
        current_functions = current_interpretation.get('interpretation', {}).get('functions', [])
        current_classes = current_interpretation.get('interpretation', {}).get('classes', [])
        current_imports = current_interpretation.get('interpretation', {}).get('imports', [])
        
        # Get previous AST details
        previous_functions = previous_ast.get('functions', [])
        previous_classes = previous_ast.get('classes', [])
        previous_imports = previous_ast.get('imports', [])
        
        print(f"    📊 Current: {len(current_functions)} functions, {len(current_classes)} classes, {len(current_imports)} imports")
        print(f"    📊 Previous: {len(previous_functions)} functions, {len(previous_classes)} classes, {len(previous_imports)} imports")
        
        # If structure is similar, use previous as template
        if (len(current_functions) == len(previous_functions) and 
            len(current_classes) == len(previous_classes)):
            print(f"    ✅ Structure matches, using previous version as template")
            return previous_content
        
        # Otherwise, apply selective fixes based on previous structure
        print(f"    🔧 Structure differs, applying selective fixes")
        
        # Apply fixes based on previous structure
        fixed_content = self.apply_structure_based_fixes(
            current_content, previous_ast, current_interpretation
        )
        
        return fixed_content
    
    def apply_structure_based_fixes(self, current_content: str, previous_ast: Dict[str, Any], 
                                  current_interpretation: Dict[str, Any]) -> str:
        """Apply fixes based on previous structure"""
        lines = current_content.split('\n')
        fixed_lines = []
        
        # Use previous imports as reference
        previous_imports = [imp['module'] for imp in previous_ast.get('imports', [])]
        
        # Use previous function signatures as reference
        previous_functions = {func['name']: func for func in previous_ast.get('functions', [])}
        
        # Use previous class structures as reference
        previous_classes = {cls['name']: cls for cls in previous_ast.get('classes', [])}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Fix imports based on previous version
            if stripped.startswith(('import ', 'from ')):
                line = self.fix_import_based_on_previous(stripped, previous_imports)
            
            # Fix function definitions based on previous version
            elif stripped.startswith('def '):
                line = self.fix_function_based_on_previous(stripped, previous_functions)
            
            # Fix class definitions based on previous version
            elif stripped.startswith('class '):
                line = self.fix_class_based_on_previous(stripped, previous_classes)
            
            # Fix indentation based on previous structure
            elif stripped and not stripped.startswith(('import ', 'from ', 'def ', 'class ')):
                line = self.fix_indentation_based_on_previous(line, i, lines, previous_ast)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_import_based_on_previous(self, line: str, previous_imports: List[str]) -> str:
        """Fix import based on previous version"""
        # If this import exists in previous version, keep it
        for prev_import in previous_imports:
            if prev_import in line:
                return line
        
        # Otherwise, use a common import pattern
        if 'typing' in line and 'typing' not in previous_imports:
            return 'from typing import List, Any'
        
        return line
    
    def fix_function_based_on_previous(self, line: str, previous_functions: Dict[str, Any]) -> str:
        """Fix function definition based on previous version"""
        # Extract function name
        import re
        match = re.match(r'def\s+(\w+)', line)
        if match:
            func_name = match.group(1)
            
            # If function exists in previous version, use its signature
            if func_name in previous_functions:
                prev_func = previous_functions[func_name]
                args = ', '.join(prev_func.get('args', []))
                return f"def {func_name}({args}):"
        
        # Otherwise, add missing colon
        if not line.endswith(':'):
            line = line + ':'
        
        return line
    
    def fix_class_based_on_previous(self, line: str, previous_classes: Dict[str, Any]) -> str:
        """Fix class definition based on previous version"""
        # Extract class name
        import re
        match = re.match(r'class\s+(\w+)', line)
        if match:
            class_name = match.group(1)
            
            # If class exists in previous version, use its structure
            if class_name in previous_classes:
                prev_class = previous_classes[class_name]
                bases = ', '.join(prev_class.get('bases', []))
                if bases:
                    return f"class {class_name}({bases}):"
        
        # Otherwise, add missing colon
        if not line.endswith(':'):
            line = line + ':'
        
        return line
    
    def fix_indentation_based_on_previous(self, line: str, line_num: int, all_lines: List[str], previous_ast: Dict[str, Any]) -> str:
        """Fix indentation based on previous structure"""
        # Use previous AST to determine proper indentation
        if ' = ' in line and not line.startswith(('def ', 'class ', 'if ', 'for ', 'while ')):
            # Check if we're in a function context
            if self.is_in_function_context(line_num, all_lines):
                return '        ' + line.strip()
        
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
    
    def fix_without_git_history(self, file_path: str) -> str:
        """Fallback to standard AST fixer when Git history is not available"""
        print(f"  🔧 Using standard AST fixer")
        
        # Use the semantic reconstructor as fallback
        from semantic_reconstructor import SemanticReconstructor
        reconstructor = SemanticReconstructor()
        return reconstructor.reconstruct_file(file_path)
    
    def cleanup_temp_file(self, temp_file: str) -> None:
        """Clean up temporary file"""
        try:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"  ⚠️  Failed to cleanup temp file: {e}")
    
    def cleanup_temp_dir(self) -> None:
        """Clean up temporary directory"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"  ⚠️  Failed to cleanup temp directory: {e}")


def main() -> None:
    """Test the Git-enhanced AST fixer"""
    print("🔧 Git-Enhanced AST Fixer")
    print("=" * 50)
    
    fixer = GitEnhancedASTFixer()
    
    # Test with known broken files
    test_files = [
        '.cursor/plugins/rule-compliance-checker.py'
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Git-enhanced fixing: {file_path}")
            
            # Create backup
            backup_path = f"{file_path}.backup5"
            if not Path(backup_path).exists():
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"  💾 Created backup: {backup_path}")
            
            # Fix the file
            fixed_content = fixer.fix_file_with_git_history(file_path)
            
            if fixed_content:
                # Save the fixed file
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    print(f"  ✅ Saved fixed file")
                    
                    # Test if it's now valid Python
                    try:
                        ast.parse(fixed_content)
                        print(f"  ✅ File is now valid Python")
                    except Exception as e:
                        print(f"  ⚠️  File still has issues: {e}")
                except Exception as e:
                    print(f"  ❌ Failed to save file: {e}")
            else:
                print(f"  ❌ Fixing failed")
    
    # Cleanup
    fixer.cleanup_temp_dir()


if __name__ == "__main__":
    main() 