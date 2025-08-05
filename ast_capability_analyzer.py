#!/usr/bin/env python3
"""
AST Capability Analyzer
Demonstrates how AST can enhance Python project modeling
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Set


class ASTCapabilityAnalyzer:
    """Analyzer that demonstrates AST capabilities for project modeling"""
    
    def __init__(self):
        self.ast_capabilities = {}
        self.project_insights = {}
    
    def analyze_ast_capabilities(self, project_root: Path) -> Dict[str, Any]:
        """Analyze what AST can tell us about Python projects"""
        print("🔍 Analyzing AST capabilities for Python project modeling...")
        
        python_files = self._find_project_files(project_root)
        
        for file_path in python_files:
            print(f"📁 Analyzing: {file_path}")
            self._analyze_file_capabilities(file_path)
        
        return self._generate_capability_report()
    
    def _find_project_files(self, project_root: Path) -> List[Path]:
        """Find Python files in our project (excluding .venv)"""
        python_files = []
        for file_path in project_root.rglob("*.py"):
            if (".venv" not in str(file_path) and 
                "__pycache__" not in str(file_path) and
                ".git" not in str(file_path)):
                python_files.append(file_path)
        return python_files
    
    def _analyze_file_capabilities(self, file_path: Path) -> None:
        """Analyze what AST can extract from a file"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Try AST parsing
            try:
                tree = ast.parse(content)
                self._extract_ast_insights(file_path, tree, content)
            except SyntaxError:
                # File has syntax errors - AST can't parse it
                self._record_syntax_error(file_path)
                
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def _extract_ast_insights(self, file_path: Path, tree: ast.AST, content: str) -> None:
        """Extract comprehensive insights using AST"""
        file_insights = {
            "path": str(file_path),
            "status": "valid_python",
            "ast_capabilities": {
                "imports": self._extract_imports_ast(tree),
                "functions": self._extract_functions_ast(tree),
                "classes": self._extract_classes_ast(tree),
                "dependencies": self._extract_dependencies_ast(tree),
                "complexity": self._calculate_complexity_ast(tree),
                "structure": self._analyze_structure_ast(tree),
                "patterns": self._detect_patterns_ast(tree),
                "metrics": self._calculate_metrics_ast(tree, content)
            }
        }
        
        self.ast_capabilities[str(file_path)] = file_insights
    
    def _extract_imports_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract imports using AST - much more accurate than regex"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "asname": alias.asname,
                        "lineno": node.lineno,
                        "col_offset": node.col_offset
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": node.module,
                        "name": alias.name,
                        "asname": alias.asname,
                        "lineno": node.lineno,
                        "col_offset": node.col_offset
                    })
        return imports
    
    def _extract_functions_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract functions using AST - complete function analysis"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "col_offset": node.col_offset,
                    "args": self._extract_function_args_ast(node),
                    "decorators": [self._extract_decorator_ast(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                    "complexity": self._calculate_function_complexity_ast(node),
                    "returns": self._extract_return_type_ast(node),
                    "body_lines": len(node.body)
                })
        return functions
    
    def _extract_classes_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract classes using AST - complete class analysis"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "col_offset": node.col_offset,
                    "bases": [self._extract_base_ast(base) for base in node.bases],
                    "keywords": [self._extract_keyword_ast(kw) for kw in node.keywords],
                    "methods": self._extract_class_methods_ast(node),
                    "docstring": ast.get_docstring(node),
                    "decorators": [self._extract_decorator_ast(d) for d in node.decorator_list]
                })
        return classes
    
    def _extract_dependencies_ast(self, tree: ast.AST) -> Set[str]:
        """Extract dependencies using AST - accurate dependency tracking"""
        dependencies = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split(".")[0])
        return list(dependencies)
    
    def _calculate_complexity_ast(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate complexity using AST - precise metrics"""
        complexity = {
            "cyclomatic": 0,
            "cognitive": 0,
            "nesting_depth": 0,
            "branches": 0,
            "loops": 0,
            "exceptions": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity["cyclomatic"] += 1
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity["cognitive"] += 1
            if isinstance(node, (ast.If, ast.Elif)):
                complexity["branches"] += 1
            if isinstance(node, (ast.For, ast.While)):
                complexity["loops"] += 1
            if isinstance(node, (ast.Try, ast.ExceptHandler, ast.Finally)):
                complexity["exceptions"] += 1
        
        return complexity
    
    def _analyze_structure_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code structure using AST"""
        structure = {
            "modules": 0,
            "classes": 0,
            "functions": 0,
            "assignments": 0,
            "calls": 0,
            "expressions": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Module):
                structure["modules"] += 1
            elif isinstance(node, ast.ClassDef):
                structure["classes"] += 1
            elif isinstance(node, ast.FunctionDef):
                structure["functions"] += 1
            elif isinstance(node, ast.Assign):
                structure["assignments"] += 1
            elif isinstance(node, ast.Call):
                structure["calls"] += 1
            elif isinstance(node, ast.Expr):
                structure["expressions"] += 1
        
        return structure
    
    def _detect_patterns_ast(self, tree: ast.AST) -> List[str]:
        """Detect code patterns using AST"""
        patterns = []
        
        for node in ast.walk(tree):
            # Detect common patterns
            if isinstance(node, ast.Try):
                patterns.append("exception_handling")
            if isinstance(node, ast.With):
                patterns.append("context_manager")
            if isinstance(node, ast.ListComp):
                patterns.append("list_comprehension")
            if isinstance(node, ast.DictComp):
                patterns.append("dict_comprehension")
            if isinstance(node, ast.GeneratorExp):
                patterns.append("generator_expression")
            if isinstance(node, ast.Lambda):
                patterns.append("lambda_function")
            if isinstance(node, ast.AsyncFunctionDef):
                patterns.append("async_function")
            if isinstance(node, ast.AsyncWith):
                patterns.append("async_context_manager")
        
        return list(set(patterns))
    
    def _calculate_metrics_ast(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Calculate comprehensive metrics using AST"""
        lines = content.split("\n")
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
            "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "ast_nodes": len(list(ast.walk(tree))),
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
        return metrics
    
    def _extract_function_args_ast(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function arguments using AST"""
        args = []
        for arg in node.args.args:
            args.append({
                "name": arg.arg,
                "annotation": self._extract_annotation_ast(arg.annotation),
                "default": "has_default" if arg.default else "no_default"
            })
        return args
    
    def _extract_decorator_ast(self, node: ast.expr) -> str:
        """Extract decorator information using AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return f"{node.func.id}()"
        return "unknown"
    
    def _extract_base_ast(self, node: ast.expr) -> str:
        """Extract base class information using AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._extract_base_ast(node.value)}.{node.attr}"
        return "unknown"
    
    def _extract_keyword_ast(self, node: ast.keyword) -> Dict[str, Any]:
        """Extract keyword arguments using AST"""
        return {
            "arg": node.arg,
            "value": self._extract_expression_ast(node.value)
        }
    
    def _extract_expression_ast(self, node: ast.expr) -> str:
        """Extract expression information using AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "complex_expression"
    
    def _extract_class_methods_ast(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract class methods using AST"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    "name": item.name,
                    "lineno": item.lineno,
                    "args": self._extract_function_args_ast(item),
                    "docstring": ast.get_docstring(item),
                    "decorators": [self._extract_decorator_ast(d) for d in item.decorator_list]
                })
        return methods
    
    def _extract_return_type_ast(self, node: ast.FunctionDef) -> str:
        """Extract return type using AST"""
        if node.returns:
            return self._extract_annotation_ast(node.returns)
        return "no_return_type"
    
    def _extract_annotation_ast(self, node: ast.expr) -> str:
        """Extract type annotation using AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "complex_annotation"
    
    def _calculate_function_complexity_ast(self, node: ast.FunctionDef) -> int:
        """Calculate function complexity using AST"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _record_syntax_error(self, file_path: Path) -> None:
        """Record files that AST cannot parse"""
        self.ast_capabilities[str(file_path)] = {
            "path": str(file_path),
            "status": "syntax_error",
            "ast_capabilities": {
                "error": "AST cannot parse due to syntax errors",
                "fallback_needed": True
            }
        }
    
    def _generate_capability_report(self) -> Dict[str, Any]:
        """Generate comprehensive AST capability report"""
        valid_files = [f for f in self.ast_capabilities.values() if f["status"] == "valid_python"]
        error_files = [f for f in self.ast_capabilities.values() if f["status"] == "syntax_error"]
        
        # Aggregate insights
        all_imports = []
        all_functions = []
        all_classes = []
        all_dependencies = set()
        all_patterns = set()
        
        for file_info in valid_files:
            capabilities = file_info["ast_capabilities"]
            all_imports.extend(capabilities.get("imports", []))
            all_functions.extend(capabilities.get("functions", []))
            all_classes.extend(capabilities.get("classes", []))
            all_dependencies.update(capabilities.get("dependencies", []))
            all_patterns.update(capabilities.get("patterns", []))
        
        report = {
            "ast_capabilities": {
                "total_files": len(self.ast_capabilities),
                "valid_files": len(valid_files),
                "syntax_error_files": len(error_files),
                "success_rate": len(valid_files) / len(self.ast_capabilities) if self.ast_capabilities else 0
            },
            "project_insights": {
                "total_imports": len(all_imports),
                "total_functions": len(all_functions),
                "total_classes": len(all_classes),
                "unique_dependencies": list(all_dependencies),
                "detected_patterns": list(all_patterns),
                "avg_complexity": self._calculate_avg_complexity(valid_files)
            },
            "ast_advantages": [
                "Complete function signature analysis",
                "Accurate dependency tracking",
                "Precise complexity metrics",
                "Pattern detection",
                "Structure analysis",
                "Type annotation extraction",
                "Decorator analysis",
                "Import resolution"
            ],
            "ast_limitations": [
                "Cannot parse syntactically incorrect code",
                "Requires valid Python syntax",
                "No semantic analysis (only structural)",
                "Cannot understand runtime behavior"
            ],
            "enhancement_opportunities": [
                "Combine AST with fallback parsing for broken files",
                "Use AST for valid files, regex for broken files",
                "AST provides foundation for semantic analysis",
                "AST enables precise code transformation"
            ]
        }
        
        return report
    
    def _calculate_avg_complexity(self, valid_files: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average complexity metrics"""
        if not valid_files:
            return {}
        
        total_complexity = {"cyclomatic": 0, "cognitive": 0, "branches": 0, "loops": 0, "exceptions": 0}
        
        for file_info in valid_files:
            complexity = file_info["ast_capabilities"].get("complexity", {})
            for key in total_complexity:
                total_complexity[key] += complexity.get(key, 0)
        
        return {key: value / len(valid_files) for key, value in total_complexity.items()}


def main() -> None:
    """Run the AST capability analyzer"""
    print("🔍 AST Capability Analyzer")
    print("=" * 50)
    
    analyzer = ASTCapabilityAnalyzer()
    project_root = Path(".")
    
    report = analyzer.analyze_ast_capabilities(project_root)
    
    # Print key insights
    print(f"\n📊 AST Analysis Results:")
    print(f"  Total files: {report['ast_capabilities']['total_files']}")
    print(f"  Valid files: {report['ast_capabilities']['valid_files']}")
    print(f"  Syntax error files: {report['ast_capabilities']['syntax_error_files']}")
    print(f"  Success rate: {report['ast_capabilities']['success_rate']:.1%}")
    
    print(f"\n🔧 Project Insights:")
    print(f"  Total functions: {report['project_insights']['total_functions']}")
    print(f"  Total classes: {report['project_insights']['total_classes']}")
    print(f"  Unique dependencies: {len(report['project_insights']['unique_dependencies'])}")
    print(f"  Detected patterns: {len(report['project_insights']['detected_patterns'])}")
    
    print(f"\n✅ AST Advantages:")
    for advantage in report['ast_advantages']:
        print(f"  - {advantage}")
    
    print(f"\n⚠️  AST Limitations:")
    for limitation in report['ast_limitations']:
        print(f"  - {limitation}")
    
    print(f"\n💡 Enhancement Opportunities:")
    for opportunity in report['enhancement_opportunities']:
        print(f"  - {opportunity}")
    
    # Save detailed report
    with open("ast_capability_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to ast_capability_report.json")


if __name__ == "__main__":
    main() 