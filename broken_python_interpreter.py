#!/usr/bin/env python3
"""
Broken Python Interpreter
Interprets syntactically incorrect Python files using tokenization and semantic analysis
"""

import ast
import tokenize
import io
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class BrokenPythonInterpreter:
    """Interpreter for syntactically incorrect Python files"""
    
    def __init__(self):
        self.semantic_patterns = {
            'function_patterns': [
                r'def\s+(\w+)\s*\(',
                r'def\s+(\w+)\s*\([^)]*\)\s*->\s*\w+',
                r'def\s+(\w+)\s*\([^)]*\)\s*:',
            ],
            'class_patterns': [
                r'class\s+(\w+)\s*\(',
                r'class\s+(\w+)\s*\([^)]*\)\s*:',
                r'class\s+(\w+)\s*:',
            ],
            'import_patterns': [
                r'import\s+(\w+)',
                r'from\s+(\w+)\s+import\s+(\w+)',
                r'from\s+(\w+)\s+import\s+(\w+)\s+as\s+(\w+)',
            ],
            'variable_patterns': [
                r'(\w+)\s*:\s*(\w+)\s*=',
                r'(\w+)\s*=\s*[^=]',
                r'(\w+)\s*:\s*(\w+)\s*\[',
            ]
        }
    
    def interpret_broken_file(self, file_path: str) -> Dict[str, Any]:
        """Interpret broken Python file with semantic understanding"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {
                'file_path': file_path,
                'error': f'Cannot read file: {e}',
                'interpretation': 'failed'
            }
        
        # Step 1: Try AST parsing
        try:
            tree = ast.parse(content)
            return self.analyze_valid_ast(file_path, tree, content)
        except SyntaxError as e:
            # Step 2: Fallback to token-based analysis
            return self.analyze_with_tokens(file_path, content, str(e))
        except IndentationError as e:
            # Step 3: Fix indentation and retry
            fixed_content = self.fix_indentation(content)
            return self.interpret_broken_file_with_content(file_path, fixed_content)
        except Exception as e:
            # Step 4: Last resort - regex-based analysis
            return self.analyze_with_regex(file_path, content, str(e))
    
    def interpret_broken_file_with_content(self, file_path: str, content: str) -> Dict[str, Any]:
        """Interpret with given content (for recursion)"""
        try:
            tree = ast.parse(content)
            return self.analyze_valid_ast(file_path, tree, content)
        except SyntaxError as e:
            return self.analyze_with_tokens(file_path, content, str(e))
        except Exception as e:
            return self.analyze_with_regex(file_path, content, str(e))
    
    def analyze_valid_ast(self, file_path: str, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Analyze valid AST tree"""
        return {
            'file_path': file_path,
            'status': 'valid_python',
            'interpretation': {
                'imports': self.extract_imports_from_ast(tree),
                'functions': self.extract_functions_from_ast(tree),
                'classes': self.extract_classes_from_ast(tree),
                'variables': self.extract_variables_from_ast(tree),
                'complexity': self.calculate_complexity_from_ast(tree),
                'lines_of_code': len(content.split('\n')),
                'ast_nodes': len(list(ast.walk(tree)))
            }
        }
    
    def analyze_with_tokens(self, file_path: str, content: str, syntax_error: str) -> Dict[str, Any]:
        """Analyze broken code using tokenization"""
        try:
            tokens = list(tokenize.tokenize(io.BytesIO(content.encode()).readline))
            
            return {
                'file_path': file_path,
                'status': 'broken_python_tokenized',
                'syntax_error': syntax_error,
                'interpretation': {
                    'imports': self.extract_imports_from_tokens(tokens),
                    'functions': self.extract_functions_from_tokens(tokens),
                    'classes': self.extract_classes_from_tokens(tokens),
                    'variables': self.extract_variables_from_tokens(tokens),
                    'syntax_issues': self.identify_syntax_issues(tokens),
                    'lines_of_code': len(content.split('\n')),
                    'token_count': len(tokens)
                }
            }
        except Exception as e:
            # Fallback to regex analysis
            return self.analyze_with_regex(file_path, content, f'{syntax_error}; tokenization failed: {e}')
    
    def analyze_with_regex(self, file_path: str, content: str, error: str) -> Dict[str, Any]:
        """Analyze broken code using regex patterns"""
        lines = content.split('\n')
        
        return {
            'file_path': file_path,
            'status': 'broken_python_regex',
            'error': error,
            'interpretation': {
                'imports': self.extract_imports_from_regex(content),
                'functions': self.extract_functions_from_regex(content),
                'classes': self.extract_classes_from_regex(content),
                'variables': self.extract_variables_from_regex(content),
                'syntax_issues': self.identify_syntax_issues_regex(content),
                'lines_of_code': len(lines),
                'estimated_complexity': self.estimate_complexity_regex(content)
            }
        }
    
    def fix_indentation(self, content: str) -> str:
        """Fix basic indentation issues"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix common indentation issues
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                # Check if this line should be indented
                if self.should_be_indented(line, fixed_lines):
                    line = '    ' + line
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def should_be_indented(self, line: str, previous_lines: List[str]) -> bool:
        """Determine if a line should be indented based on context"""
        if not previous_lines:
            return False
        
        # Check if previous line ends with colon
        prev_line = previous_lines[-1].strip()
        if prev_line.endswith(':'):
            return True
        
        # Check if we're in a block (previous line is indented)
        if previous_lines and previous_lines[-1].startswith('    '):
            return True
        
        return False
    
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
                    'docstring': ast.get_docstring(node),
                    'complexity': self.calculate_function_complexity(node)
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
    
    def calculate_complexity_from_ast(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate complexity from AST"""
        complexity = {'cyclomatic': 0, 'cognitive': 0}
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity['cyclomatic'] += 1
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity['cognitive'] += 1
        return complexity
    
    def extract_imports_from_tokens(self, tokens: List) -> List[Dict[str, Any]]:
        """Extract imports from tokens"""
        imports = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == tokenize.NAME and token.string == 'import':
                # Handle 'import module'
                if i + 1 < len(tokens) and tokens[i + 1].type == tokenize.NAME:
                    imports.append({
                        'type': 'import',
                        'module': tokens[i + 1].string,
                        'asname': None,
                        'lineno': token.start[0]
                    })
            elif token.type == tokenize.NAME and token.string == 'from':
                # Handle 'from module import name'
                if i + 3 < len(tokens):
                    module = tokens[i + 1].string if tokens[i + 1].type == tokenize.NAME else None
                    if tokens[i + 2].string == 'import' and tokens[i + 3].type == tokenize.NAME:
                        imports.append({
                            'type': 'from_import',
                            'module': module,
                            'name': tokens[i + 3].string,
                            'asname': None,
                            'lineno': token.start[0]
                        })
            i += 1
        return imports
    
    def extract_functions_from_tokens(self, tokens: List) -> List[Dict[str, Any]]:
        """Extract functions from tokens"""
        functions = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == tokenize.NAME and token.string == 'def':
                # Found function definition
                if i + 1 < len(tokens) and tokens[i + 1].type == tokenize.NAME:
                    functions.append({
                        'name': tokens[i + 1].string,
                        'lineno': token.start[0],
                        'args': 'unknown',  # Can't parse args without AST
                        'decorators': [],
                        'docstring': None,
                        'complexity': 1
                    })
            i += 1
        return functions
    
    def extract_classes_from_tokens(self, tokens: List) -> List[Dict[str, Any]]:
        """Extract classes from tokens"""
        classes = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == tokenize.NAME and token.string == 'class':
                # Found class definition
                if i + 1 < len(tokens) and tokens[i + 1].type == tokenize.NAME:
                    classes.append({
                        'name': tokens[i + 1].string,
                        'lineno': token.start[0],
                        'bases': [],
                        'methods': [],
                        'docstring': None
                    })
            i += 1
        return classes
    
    def extract_variables_from_tokens(self, tokens: List) -> List[Dict[str, Any]]:
        """Extract variables from tokens"""
        variables = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == tokenize.NAME:
                # Check if this is a variable assignment
                if i + 1 < len(tokens) and tokens[i + 1].string == '=':
                    variables.append({
                        'name': token.string,
                        'lineno': token.start[0],
                        'value_type': 'unknown'
                    })
            i += 1
        return variables
    
    def identify_syntax_issues(self, tokens: List) -> List[Dict[str, Any]]:
        """Identify syntax issues from tokens"""
        issues = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check for unindented assignments after colons
            if token.string == ':':
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    if next_token.type == tokenize.NAME and not self.is_indented(next_token):
                        issues.append({
                            'type': 'indentation_error',
                            'line': next_token.start[0],
                            'description': 'Unindented statement after colon'
                        })
            
            # Check for missing colons
            if token.type == tokenize.NAME and token.string in ['def', 'class', 'if', 'for', 'while', 'try', 'with']:
                if i + 1 < len(tokens) and tokens[i + 1].string != ':':
                    issues.append({
                        'type': 'missing_colon',
                        'line': token.start[0],
                        'description': f'Missing colon after {token.string}'
                    })
            
            i += 1
        return issues
    
    def is_indented(self, token) -> bool:
        """Check if token is indented"""
        return token.start[1] > 0
    
    def extract_imports_from_regex(self, content: str) -> List[Dict[str, Any]]:
        """Extract imports using regex"""
        imports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('import '):
                match = re.match(r'import\s+(\w+)', line)
                if match:
                    imports.append({
                        'type': 'import',
                        'module': match.group(1),
                        'asname': None,
                        'lineno': i + 1
                    })
            elif line.startswith('from '):
                match = re.match(r'from\s+(\w+)\s+import\s+(\w+)', line)
                if match:
                    imports.append({
                        'type': 'from_import',
                        'module': match.group(1),
                        'name': match.group(2),
                        'asname': None,
                        'lineno': i + 1
                    })
        
        return imports
    
    def extract_functions_from_regex(self, content: str) -> List[Dict[str, Any]]:
        """Extract functions using regex"""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('def '):
                match = re.match(r'def\s+(\w+)', line)
                if match:
                    functions.append({
                        'name': match.group(1),
                        'lineno': i + 1,
                        'args': 'unknown',
                        'decorators': [],
                        'docstring': None,
                        'complexity': 1
                    })
        
        return functions
    
    def extract_classes_from_regex(self, content: str) -> List[Dict[str, Any]]:
        """Extract classes using regex"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('class '):
                match = re.match(r'class\s+(\w+)', line)
                if match:
                    classes.append({
                        'name': match.group(1),
                        'lineno': i + 1,
                        'bases': [],
                        'methods': [],
                        'docstring': None
                    })
        
        return classes
    
    def extract_variables_from_regex(self, content: str) -> List[Dict[str, Any]]:
        """Extract variables using regex"""
        variables = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            # Look for variable assignments
            match = re.match(r'(\w+)\s*=', line)
            if match:
                variables.append({
                    'name': match.group(1),
                    'lineno': i + 1,
                    'value_type': 'unknown'
                })
        
        return variables
    
    def identify_syntax_issues_regex(self, content: str) -> List[Dict[str, Any]]:
        """Identify syntax issues using regex"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Check for unindented assignments after colons
            if ': Any =' in line and not line.startswith('    '):
                issues.append({
                    'type': 'indentation_error',
                    'line': i + 1,
                    'description': 'Unindented variable assignment'
                })
            
            # Check for missing colons
            if line.strip().endswith(')') and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('    ') and not next_line.startswith('#'):
                    issues.append({
                        'type': 'indentation_error',
                        'line': i + 2,
                        'description': 'Unindented statement after function/class definition'
                    })
        
        return issues
    
    def estimate_complexity_regex(self, content: str) -> Dict[str, int]:
        """Estimate complexity using regex"""
        complexity = {'cyclomatic': 0, 'cognitive': 0}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('if ', 'for ', 'while ', 'except')):
                complexity['cyclomatic'] += 1
            if line.startswith(('if ', 'for ', 'while ', 'try', 'with')):
                complexity['cognitive'] += 1
        
        return complexity
    
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
    
    def calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate function complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
        return complexity


def main() -> None:
    """Test the broken Python interpreter"""
    print("🔍 Broken Python Interpreter")
    print("=" * 50)
    
    interpreter = BrokenPythonInterpreter()
    
    # Test with a few known broken files
    test_files = [
        'scripts/mdc-linter.py',  # Known to have indentation issues
        'scripts/fix_mypy_issues.py',  # Known to have syntax issues
        '.cursor/plugins/rule-compliance-checker.py'  # Known to have issues
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Analyzing: {file_path}")
            interpretation = interpreter.interpret_broken_file(file_path)
            
            print(f"  Status: {interpretation['status']}")
            if 'interpretation' in interpretation:
                interp = interpretation['interpretation']
                print(f"  Functions: {len(interp.get('functions', []))}")
                print(f"  Classes: {len(interp.get('classes', []))}")
                print(f"  Imports: {len(interp.get('imports', []))}")
                print(f"  Variables: {len(interp.get('variables', []))}")
                if 'syntax_issues' in interp:
                    print(f"  Syntax Issues: {len(interp['syntax_issues'])}")
            if 'error' in interpretation:
                print(f"  Error: {interpretation['error']}")


if __name__ == "__main__":
    main() 