#!/usr/bin/env python3
"""
Enhanced Python Project Modeler
Uses AST for valid files, fallback strategies for broken files
"""

import ast
import tokenize
import io
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import re
import json


class PythonProjectModeler:
    """Enhanced Python project modeler with AST and fallback capabilities"""
    
    def __init__(self):
        self.valid_files = {}  # AST-based analysis
        self.broken_files = {}  # Fallback analysis
        self.project_structure = {}
        self.dependencies = {}
        self.imports = {}
        self.functions = {}
        self.classes = {}
        self.syntax_issues = []
    
    def model_project(self, project_root: Path) -> Dict[str, Any]:
        """Model the entire Python project"""
        print("🔍 Modeling Python project structure...")
        
        python_files = self._find_python_files(project_root)
        
        for file_path in python_files:
            print(f"📁 Analyzing: {file_path}")
            
            # Try AST parsing first
            if self._can_parse_with_ast(file_path):
                self._analyze_with_ast(file_path)
            else:
                self._analyze_with_fallback(file_path)
        
        return self._generate_project_model()
    
    def _find_python_files(self, project_root: Path) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        for file_path in project_root.rglob("*.py"):
            if "__pycache__" not in str(file_path) and ".git" not in str(file_path):
                python_files.append(file_path)
        return python_files
    
    def _can_parse_with_ast(self, file_path: Path) -> bool:
        """Check if file can be parsed with AST"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            ast.parse(content)
            return True
        except (SyntaxError, IndentationError, UnicodeDecodeError):
            return False
    
    def _analyze_with_ast(self, file_path: Path) -> None:
        """Analyze file using AST for complete understanding"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract comprehensive information
            file_info = {
                "path": str(file_path),
                "type": "valid_python",
                "imports": self._extract_imports(tree),
                "functions": self._extract_functions(tree),
                "classes": self._extract_classes(tree),
                "dependencies": self._extract_dependencies(tree),
                "complexity": self._calculate_complexity(tree),
                "lines_of_code": len(content.split("\n")),
                "ast_nodes": len(list(ast.walk(tree)))
            }
            
            self.valid_files[str(file_path)] = file_info
            
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def _analyze_with_fallback(self, file_path: Path) -> None:
        """Analyze broken file using fallback strategies"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Fallback analysis using regex and line-by-line parsing
            file_info = {
                "path": str(file_path),
                "type": "broken_python",
                "imports": self._extract_imports_fallback(content),
                "functions": self._extract_functions_fallback(content),
                "classes": self._extract_classes_fallback(content),
                "syntax_issues": self._identify_syntax_issues(content),
                "lines_of_code": len(content.split("\n")),
                "estimated_complexity": self._estimate_complexity_fallback(content)
            }
            
            self.broken_files[str(file_path)] = file_info
            
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract imports from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "asname": alias.asname,
                        "lineno": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": node.module,
                        "name": alias.name,
                        "asname": alias.asname,
                        "lineno": node.lineno
                    })
        return imports
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract functions from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": self._extract_function_args(node),
                    "decorators": [self._extract_decorator(d) for d in node.decorator_list],
                    "docstring": ast.get_docstring(node),
                    "complexity": self._calculate_function_complexity(node)
                })
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract classes from AST"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "bases": [self._extract_base(base) for base in node.bases],
                    "methods": self._extract_class_methods(node),
                    "docstring": ast.get_docstring(node)
                })
        return classes
    
    def _extract_dependencies(self, tree: ast.AST) -> Set[str]:
        """Extract dependencies from AST"""
        dependencies = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split(".")[0])
        return list(dependencies)
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate code complexity metrics"""
        complexity = {
            "cyclomatic": 0,
            "cognitive": 0,
            "nesting_depth": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity["cyclomatic"] += 1
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity["cognitive"] += 1
        
        return complexity
    
    def _extract_imports_fallback(self, content: str) -> List[Dict[str, Any]]:
        """Extract imports using regex fallback"""
        imports = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("import "):
                match = re.match(r"import\s+(\w+)(?:\s+as\s+(\w+))?", line)
                if match:
                    imports.append({
                        "type": "import",
                        "module": match.group(1),
                        "asname": match.group(2),
                        "lineno": i + 1
                    })
            elif line.startswith("from "):
                match = re.match(r"from\s+(\w+)\s+import\s+(\w+)(?:\s+as\s+(\w+))?", line)
                if match:
                    imports.append({
                        "type": "from_import",
                        "module": match.group(1),
                        "name": match.group(2),
                        "asname": match.group(3),
                        "lineno": i + 1
                    })
        
        return imports
    
    def _extract_functions_fallback(self, content: str) -> List[Dict[str, Any]]:
        """Extract functions using regex fallback"""
        functions = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("def "):
                match = re.match(r"def\s+(\w+)\s*\(", line)
                if match:
                    functions.append({
                        "name": match.group(1),
                        "lineno": i + 1,
                        "args": "unknown",  # Can't parse args without AST
                        "decorators": [],
                        "docstring": None,
                        "complexity": 1
                    })
        
        return functions
    
    def _extract_classes_fallback(self, content: str) -> List[Dict[str, Any]]:
        """Extract classes using regex fallback"""
        classes = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("class "):
                match = re.match(r"class\s+(\w+)", line)
                if match:
                    classes.append({
                        "name": match.group(1),
                        "lineno": i + 1,
                        "bases": [],
                        "methods": [],
                        "docstring": None
                    })
        
        return classes
    
    def _identify_syntax_issues(self, content: str) -> List[Dict[str, Any]]:
        """Identify syntax issues in broken files"""
        issues = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            # Check for common syntax issues
            if ": Any =" in line and not line.startswith("    "):
                issues.append({
                    "type": "indentation_error",
                    "line": i + 1,
                    "description": "Unindented variable assignment"
                })
            elif line.strip().endswith(":") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith("    ") and not next_line.startswith("#"):
                    issues.append({
                        "type": "indentation_error",
                        "line": i + 2,
                        "description": "Unindented statement after colon"
                    })
        
        return issues
    
    def _estimate_complexity_fallback(self, content: str) -> Dict[str, int]:
        """Estimate complexity using regex patterns"""
        complexity = {
            "cyclomatic": 0,
            "cognitive": 0,
            "nesting_depth": 0
        }
        
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("if ", "for ", "while ", "except")):
                complexity["cyclomatic"] += 1
            if line.startswith(("if ", "for ", "while ", "try", "with")):
                complexity["cognitive"] += 1
        
        return complexity
    
    def _extract_function_args(self, node: ast.FunctionDef) -> List[str]:
        """Extract function arguments from AST"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return args
    
    def _extract_decorator(self, node: ast.expr) -> str:
        """Extract decorator name from AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
        return "unknown"
    
    def _extract_base(self, node: ast.expr) -> str:
        """Extract base class name from AST"""
        if isinstance(node, ast.Name):
            return node.id
        return "unknown"
    
    def _extract_class_methods(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract class methods from AST"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    "name": item.name,
                    "lineno": item.lineno,
                    "args": self._extract_function_args(item),
                    "docstring": ast.get_docstring(item)
                })
        return methods
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate function complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _generate_project_model(self) -> Dict[str, Any]:
        """Generate comprehensive project model"""
        model = {
            "project_summary": {
                "total_files": len(self.valid_files) + len(self.broken_files),
                "valid_files": len(self.valid_files),
                "broken_files": len(self.broken_files),
                "total_lines": sum(f["lines_of_code"] for f in self.valid_files.values()) +
                             sum(f["lines_of_code"] for f in self.broken_files.values())
            },
            "file_analysis": {
                "valid_files": self.valid_files,
                "broken_files": self.broken_files
            },
            "dependencies": self._aggregate_dependencies(),
            "syntax_issues": self._aggregate_syntax_issues(),
            "complexity_analysis": self._aggregate_complexity(),
            "recommendations": self._generate_recommendations()
        }
        
        return model
    
    def _aggregate_dependencies(self) -> Dict[str, int]:
        """Aggregate all dependencies across files"""
        all_deps = {}
        for file_info in self.valid_files.values():
            for dep in file_info.get("dependencies", []):
                all_deps[dep] = all_deps.get(dep, 0) + 1
        return all_deps
    
    def _aggregate_syntax_issues(self) -> List[Dict[str, Any]]:
        """Aggregate all syntax issues"""
        all_issues = []
        for file_path, file_info in self.broken_files.items():
            for issue in file_info.get("syntax_issues", []):
                issue["file"] = file_path
                all_issues.append(issue)
        return all_issues
    
    def _aggregate_complexity(self) -> Dict[str, Any]:
        """Aggregate complexity metrics"""
        total_complexity = {"cyclomatic": 0, "cognitive": 0}
        
        for file_info in self.valid_files.values():
            complexity = file_info.get("complexity", {})
            total_complexity["cyclomatic"] += complexity.get("cyclomatic", 0)
            total_complexity["cognitive"] += complexity.get("cognitive", 0)
        
        for file_info in self.broken_files.values():
            complexity = file_info.get("estimated_complexity", {})
            total_complexity["cyclomatic"] += complexity.get("cyclomatic", 0)
            total_complexity["cognitive"] += complexity.get("cognitive", 0)
        
        return total_complexity
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if self.broken_files:
            recommendations.append(f"Fix syntax issues in {len(self.broken_files)} files")
        
        total_issues = len(self._aggregate_syntax_issues())
        if total_issues > 0:
            recommendations.append(f"Address {total_issues} syntax issues")
        
        complexity = self._aggregate_complexity()
        if complexity["cyclomatic"] > 100:
            recommendations.append("Consider reducing cyclomatic complexity")
        
        return recommendations


def main() -> None:
    """Run the enhanced Python project modeler"""
    print("🔍 Enhanced Python Project Modeler")
    print("=" * 50)
    
    modeler = PythonProjectModeler()
    project_root = Path(".")
    
    model = modeler.model_project(project_root)
    
    # Print summary
    print(f"\n📊 Project Summary:")
    print(f"  Total files: {model['project_summary']['total_files']}")
    print(f"  Valid files: {model['project_summary']['valid_files']}")
    print(f"  Broken files: {model['project_summary']['broken_files']}")
    print(f"  Total lines: {model['project_summary']['total_lines']}")
    
    print(f"\n🔧 Dependencies:")
    for dep, count in sorted(model['dependencies'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {dep}: {count} files")
    
    print(f"\n⚠️  Syntax Issues: {len(model['syntax_issues'])}")
    for issue in model['syntax_issues'][:5]:
        print(f"  {issue['file']}:{issue['line']} - {issue['description']}")
    
    print(f"\n📈 Complexity:")
    complexity = model['complexity_analysis']
    print(f"  Cyclomatic: {complexity['cyclomatic']}")
    print(f"  Cognitive: {complexity['cognitive']}")
    
    print(f"\n💡 Recommendations:")
    for rec in model['recommendations']:
        print(f"  - {rec}")
    
    # Save detailed model
    with open("python_project_model.json", "w") as f:
        json.dump(model, f, indent=2)
    
    print(f"\n💾 Detailed model saved to python_project_model.json")


if __name__ == "__main__":
    main() 