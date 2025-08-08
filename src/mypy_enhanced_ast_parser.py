#!/usr/bin/env python3
"""
Mypy-Enhanced AST Parser
Enhances AST parsing with mypy type checking rules
"""

import ast
from dataclasses import dataclass, field


@dataclass
class MypyASTNode:
    """AST node with mypy-aware type information"""

    node: ast.AST
    has_return_type: bool = False
    has_param_types: bool = False
    missing_return_type: bool = False
    missing_param_types: bool = False
    mypy_errors: list[str] = field(default_factory=list)


@dataclass
class MypyASTAnalysis:
    """Results of mypy-enhanced AST analysis"""

    functions_without_return_types: list[ast.FunctionDef] = field(default_factory=list)
    functions_without_param_types: list[ast.FunctionDef] = field(default_factory=list)
    missing_imports: list[str] = field(default_factory=list)
    type_annotation_issues: list[str] = field(default_factory=list)
    mypy_errors: list[str] = field(default_factory=list)


class MypyEnhancedASTParser:
    """AST parser enhanced with mypy type checking rules"""

    def __init__(self) -> None:
        self.analysis = MypyASTAnalysis()
        self.imported_modules: set[str] = set()
        self.defined_classes: set[str] = set()
        self.defined_functions: set[str] = set()

    def analyze_code(self, code: str) -> MypyASTAnalysis:
        """Analyze code with mypy-aware AST parsing"""
        try:
            tree = ast.parse(code)
            self.analysis = MypyASTAnalysis()
            self._visit_node(tree)
            return self.analysis
        except SyntaxError as e:
            print(f"❌ Syntax error in code: {e}")
            return MypyASTAnalysis()

    def _visit_node(self, node: ast.AST) -> None:
        """Visit AST node with mypy rules"""
        if isinstance(node, ast.FunctionDef):
            self._analyze_function_def(node)
        elif isinstance(node, ast.AsyncFunctionDef):
            self._analyze_async_function_def(node)
        elif isinstance(node, ast.ClassDef):
            self._analyze_class_def(node)
        elif isinstance(node, ast.Import):
            self._analyze_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._analyze_import_from(node)

        # Visit child nodes
        for child in ast.iter_child_nodes(node):
            self._visit_node(child)

    def _analyze_function_def(self, node: ast.FunctionDef) -> None:
        """Analyze function definition with mypy rules"""
        # Check for missing return type annotation
        if not node.returns:
            self.analysis.functions_without_return_types.append(node)
            self.analysis.mypy_errors.append(
                f"Function '{node.name}' missing return type annotation",
            )

        # Check for missing parameter type annotations
        missing_param_types = []
        for arg in node.args.args:
            if not arg.annotation:
                missing_param_types.append(arg.arg)

        if missing_param_types:
            self.analysis.functions_without_param_types.append(node)
            self.analysis.mypy_errors.append(
                f"Function '{node.name}' missing parameter type annotations: {missing_param_types}",
            )

        # Check for return statements in functions marked as -> None
        if (
            node.returns
            and isinstance(node.returns, ast.Constant)
            and node.returns.value is None
        ):
            self._check_for_unexpected_returns(node)

    def _analyze_async_function_def(self, node: ast.AsyncFunctionDef) -> None:
        """Analyze async function definition with mypy rules"""
        # Same analysis as regular functions
        self._analyze_function_def(node)  # type: ignore

    def _analyze_class_def(self, node: ast.ClassDef) -> None:
        """Analyze class definition with mypy rules"""
        self.defined_classes.add(node.name)

        # Check for missing __init__ return type
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                if not item.returns:
                    self.analysis.mypy_errors.append(
                        f"Class '{node.name}' __init__ method missing return type annotation",
                    )

    def _analyze_import(self, node: ast.Import) -> None:
        """Analyze import statement with mypy rules"""
        for alias in node.names:
            self.imported_modules.add(alias.name)

    def _analyze_import_from(self, node: ast.ImportFrom) -> None:
        """Analyze import from statement with mypy rules"""
        if node.module:
            self.imported_modules.add(node.module)

    def _check_for_unexpected_returns(self, node: ast.FunctionDef) -> None:
        """Check for unexpected return statements in -> None functions"""
        for item in ast.walk(node):
            if isinstance(item, ast.Return) and item.value:
                self.analysis.mypy_errors.append(
                    f"Function '{node.name}' has unexpected return value in -> None function",
                )

    def generate_mypy_fixes(self, analysis: MypyASTAnalysis) -> list[str]:
        """Generate mypy-aware fixes based on analysis"""
        fixes = []

        # Fix missing return type annotations
        for func in analysis.functions_without_return_types:
            if not self._has_return_statement(func):
                fixes.append(f"Add -> None to function '{func.name}'")
            else:
                fixes.append(f"Add return type annotation to function '{func.name}'")

        # Fix missing parameter type annotations
        for func in analysis.functions_without_param_types:
            fixes.append(f"Add parameter type annotations to function '{func.name}'")

        return fixes

    def _has_return_statement(self, node: ast.FunctionDef) -> bool:
        """Check if function has return statements"""
        for item in ast.walk(node):
            if isinstance(item, ast.Return):
                return True
        return False


class MypyEnhancedCodeGenerator:
    """Code generator with mypy-aware AST parsing"""

    def __init__(self) -> None:
        self.ast_parser = MypyEnhancedASTParser()

    def generate_mypy_compliant_code(self, code: str) -> str:
        """Generate mypy-compliant code with automatic type annotation fixes"""
        # Analyze code with mypy rules
        analysis = self.ast_parser.analyze_code(code)

        # Apply mypy fixes
        fixed_code = self._apply_mypy_fixes(code, analysis)

        return fixed_code

    def _apply_mypy_fixes(self, code: str, analysis: MypyASTAnalysis) -> str:
        """Apply mypy fixes to code"""
        lines = code.split("\n")

        # Fix missing return type annotations
        for func in analysis.functions_without_return_types:
            line_num = func.lineno - 1
            if line_num < len(lines):
                line = lines[line_num]
                if "def " in line and ":" in line and "->" not in line:
                    if not self._has_return_statement(func):
                        # Add -> None for functions without return statements
                        fixed_line = line.replace("):", ") -> None:")
                        lines[line_num] = fixed_line
                    else:
                        # Add -> Any for functions with return statements
                        fixed_line = line.replace("):", ") -> Any:")
                        lines[line_num] = fixed_line

        return "\n".join(lines)

    def _has_return_statement(self, node: ast.FunctionDef) -> bool:
        """Check if function has return statements"""
        for item in ast.walk(node):
            if isinstance(item, ast.Return):
                return True
        return False


# Test the mypy-enhanced AST parser
def test_mypy_enhanced_ast_parser() -> None:
    """Test the mypy-enhanced AST parser"""

    # Test code with mypy issues
    test_code = '''
def test_function(param1, param2):
    """Test function without type annotations"""
    result = param1 + param2
    return result

class TestClass:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
'''

    print("🚀 Testing MYPY-ENHANCED AST Parser!")

    # Analyze with mypy rules
    parser = MypyEnhancedASTParser()
    analysis = parser.analyze_code(test_code)

    print("✅ Mypy Analysis Results:")
    print(
        f"Functions without return types: {len(analysis.functions_without_return_types)}",
    )
    print(
        f"Functions without param types: {len(analysis.functions_without_param_types)}",
    )
    print(f"Mypy errors: {len(analysis.mypy_errors)}")

    # Generate fixes
    fixes = parser.generate_mypy_fixes(analysis)
    print(f"Generated fixes: {len(fixes)}")

    # Generate mypy-compliant code
    generator = MypyEnhancedCodeGenerator()
    fixed_code = generator.generate_mypy_compliant_code(test_code)

    print("✅ Generated Mypy-Compliant Code:")
    print(fixed_code)


if __name__ == "__main__":
    test_mypy_enhanced_ast_parser()
