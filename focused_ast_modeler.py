#!/usr/bin/env python3
"""Focused AST Modeler - Only model essential Python files"""

import ast
import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

@dataclass
class ASTModel:
    """AST model for a Python file"""
    file_path: str
    file_type: str = "python"
    model_type: str = "ast"
    complexity_score: float = 0.0
    line_count: int = 0
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    error_count: int = 0
    model_data: Dict[str, Any] = None

class FocusedASTModeler:
    """Focused AST modeler that only models essential Python files"""
    
    def __init__(self):
        self.database = {
            "file_models": {},
            "summary": {
                "total_files": 0,
                "valid_files": 0,
                "error_files": 0,
                "model_type_counts": {}
            }
        }
        
        # Exclude patterns for generated/temporary files
        self.exclude_patterns = [
            ".venv", "venv", "__pycache__", ".git", "node_modules",
            ".pytest_cache", ".mypy_cache", "build", "dist", "*.pyc",
            "*.pyo", "*.pyd", "*.so", "*.dll", "*.dylib",
            "backup*", "*.backup*", "*.tmp", "*.temp",
            "comprehensive_ast_modeler.py", "enhanced_python_modeler.py",
            "broken_python_interpreter.py", "semantic_reconstructor.py",
            "git_enhanced_ast_fixer.py", "aggressive_syntax_fixer.py",
            "comprehensive_syntax_fixer.py", "python_ast_fixer.py",
            "fix_*.py", "test_*.py", "*_test.py"
        ]
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded"""
        file_path_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            if pattern in file_path_str:
                return True
        
        return False
    
    def find_python_files(self, directory: str) -> List[str]:
        """Find Python files to model, excluding generated/temporary files"""
        python_files = []
        
        for file_path in Path(directory).rglob("*.py"):
            if not self.should_exclude_file(file_path):
                python_files.append(str(file_path))
        
        return python_files
    
    def model_python_file(self, file_path: str) -> ASTModel:
        """Model a Python file using AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST
            tree = ast.parse(content)
            
            # Extract information
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            # Calculate complexity (simple line-based for now)
            lines = content.split('\n')
            complexity = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Extract docstrings
            docstrings = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(docstring)
            
            # Extract imports
            import_names = []
            for imp in imports:
                if isinstance(imp, ast.Import):
                    for alias in imp.names:
                        import_names.append(alias.name)
                elif isinstance(imp, ast.ImportFrom):
                    module = imp.module or ""
                    for alias in imp.names:
                        import_names.append(f"{module}.{alias.name}")
            
            # Extract function names
            function_names = [func.name for func in functions]
            
            # Extract class names
            class_names = [cls.name for cls in classes]
            
            model_data = {
                "docstrings": docstrings,
                "imports": import_names,
                "functions": [{"name": func.name, "docstring": ast.get_docstring(func)} for func in functions],
                "classes": [{"name": cls.name, "docstring": ast.get_docstring(cls)} for cls in classes],
                "variables": [],  # Could extract variables if needed
                "line_count": len(lines)
            }
            
            return ASTModel(
                file_path=file_path,
                model_type="ast",
                complexity_score=complexity,
                line_count=len(lines),
                function_count=len(functions),
                class_count=len(classes),
                import_count=len(imports),
                error_count=0,
                model_data=model_data
            )
            
        except Exception as e:
            # Create error model
            return ASTModel(
                file_path=file_path,
                model_type="error",
                error_count=1,
                model_data={"error": str(e)}
            )
    
    def model_directory(self, directory: str) -> Dict[str, Any]:
        """Model all Python files in directory"""
        print(f"🔍 Finding Python files in {directory}")
        
        python_files = self.find_python_files(directory)
        print(f"📁 Found {len(python_files)} Python files to model")
        
        for i, file_path in enumerate(python_files, 1):
            print(f"  [{i}/{len(python_files)}] Modeling {file_path}")
            
            model = self.model_python_file(file_path)
            self.database["file_models"][file_path] = asdict(model)
            
            # Update summary
            self.database["summary"]["total_files"] += 1
            if model.model_type == "ast":
                self.database["summary"]["valid_files"] += 1
            else:
                self.database["summary"]["error_files"] += 1
            
            # Update model type counts
            model_type = model.model_type
            self.database["summary"]["model_type_counts"][model_type] = \
                self.database["summary"]["model_type_counts"].get(model_type, 0) + 1
        
        return self.database
    
    def save_database(self, filename: str = "ast_models.json"):
        """Save database to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.database, f, indent=2)
        print(f"💾 Saved database to {filename}")
        print(f"📊 Summary: {self.database['summary']}")

def main():
    """Model the project with focused approach"""
    modeler = FocusedASTModeler()
    
    print("🚀 Starting Focused AST Modeling")
    print("=" * 50)
    
    # Model the current directory
    database = modeler.model_directory(".")
    
    # Save results
    modeler.save_database("ast_models_focused.json")
    
    print("✅ Focused AST modeling complete!")

if __name__ == "__main__":
    main() 