#!/usr/bin/env python3
"""
Model Consistency Analyzer
Analyzes whether files match persisted models or vary from committed models
"""

import json
import subprocess
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from git_enhanced_ast_fixer import GitEnhancedASTFixer


class ModelConsistencyAnalyzer:
    """Analyzes model consistency between current, persisted, and committed models"""
    
    def __init__(self):
        self.git_fixer = GitEnhancedASTFixer()
        self.model_registry_path = "project_model_registry.json"
    
    def analyze_file_consistency(self, file_path: str) -> Dict[str, Any]:
        """Analyze model consistency for a file"""
        print(f"🔍 Analyzing model consistency: {file_path}")
        
        # Check if file has Git history
        has_git_history = self.check_git_history(file_path)
        
        if has_git_history:
            print(f"  📋 File has Git history - analyzing against committed model")
            return self.analyze_with_git_history(file_path)
        else:
            print(f"  🆕 File has no Git history - analyzing against persisted model")
            return self.analyze_new_artifact(file_path)
    
    def check_git_history(self, file_path: str) -> bool:
        """Check if file has Git history"""
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--follow', '--', file_path],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            return result.returncode == 0 and result.stdout.strip() != ''
        except Exception:
            return False
    
    def analyze_with_git_history(self, file_path: str) -> Dict[str, Any]:
        """Analyze file that has Git history"""
        
        # Get current model
        current_model = self.extract_current_model(file_path)
        
        # Get committed model (from most recent commit)
        committed_model = self.extract_committed_model(file_path)
        
        # Get persisted model (from project_model_registry.json)
        persisted_model = self.get_persisted_model(file_path)
        
        # Compare models
        consistency_analysis = {
            'file_path': file_path,
            'has_git_history': True,
            'current_model': current_model,
            'committed_model': committed_model,
            'persisted_model': persisted_model,
            'comparisons': {
                'current_vs_committed': self.compare_models(current_model, committed_model),
                'current_vs_persisted': self.compare_models(current_model, persisted_model),
                'committed_vs_persisted': self.compare_models(committed_model, persisted_model)
            },
            'recommendations': self.generate_recommendations(current_model, committed_model, persisted_model)
        }
        
        return consistency_analysis
    
    def analyze_new_artifact(self, file_path: str) -> Dict[str, Any]:
        """Analyze new artifact with no Git history"""
        
        # Get current model
        current_model = self.extract_current_model(file_path)
        
        # Get persisted model
        persisted_model = self.get_persisted_model(file_path)
        
        # Check if it matches any known patterns
        pattern_match = self.find_pattern_match(current_model)
        
        consistency_analysis = {
            'file_path': file_path,
            'has_git_history': False,
            'current_model': current_model,
            'persisted_model': persisted_model,
            'pattern_match': pattern_match,
            'is_new_artifact': True,
            'recommendations': self.generate_new_artifact_recommendations(current_model, persisted_model, pattern_match)
        }
        
        return consistency_analysis
    
    def extract_current_model(self, file_path: str) -> Dict[str, Any]:
        """Extract current model from file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Try AST parsing first
            try:
                tree = ast.parse(content)
                return self.extract_ast_model(tree, content)
            except (SyntaxError, IndentationError):
                # Fall back to broken interpreter
                interpretation = self.git_fixer.interpreter.interpret_broken_file(file_path)
                return self.extract_interpretation_model(interpretation, content)
                
        except Exception as e:
            return {'error': str(e), 'content': ''}
    
    def extract_committed_model(self, file_path: str) -> Dict[str, Any]:
        """Extract model from most recent committed version"""
        try:
            # Get most recent commit hash
            result = subprocess.run(
                ['git', 'log', '--oneline', '--follow', '--', file_path],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            
            if result.returncode == 0 and result.stdout.strip():
                commit_hash = result.stdout.split('\n')[0].split()[0]
                
                # Get committed content
                result = subprocess.run(
                    ['git', 'show', f'{commit_hash}:{file_path}'],
                    capture_output=True, text=True, cwd=Path(file_path).parent
                )
                
                if result.returncode == 0:
                    content = result.stdout
                    try:
                        tree = ast.parse(content)
                        return self.extract_ast_model(tree, content)
                    except (SyntaxError, IndentationError):
                        # Use basic analysis for committed version
                        return self.extract_basic_model(content)
            
            return {'error': 'No committed version found', 'content': ''}
            
        except Exception as e:
            return {'error': str(e), 'content': ''}
    
    def get_persisted_model(self, file_path: str) -> Dict[str, Any]:
        """Get persisted model from project_model_registry.json"""
        try:
            if Path(self.model_registry_path).exists():
                with open(self.model_registry_path, 'r') as f:
                    registry = json.load(f)
                
                # Look for matching patterns in the registry
                file_name = Path(file_path).name
                for domain_name, config in registry.get('domains', {}).items():
                    patterns = config.get('patterns', [])
                    for pattern in patterns:
                        if file_name.endswith(pattern) or pattern in file_path:
                            return {
                                'domain': domain_name,
                                'patterns': patterns,
                                'content_indicators': config.get('content_indicators', []),
                                'linter': config.get('linter'),
                                'validator': config.get('validator'),
                                'formatter': config.get('formatter')
                            }
            
            return {'error': 'No persisted model found', 'content': ''}
            
        except Exception as e:
            return {'error': str(e), 'content': ''}
    
    def extract_ast_model(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Extract model from AST"""
        return {
            'type': 'ast_parsed',
            'functions': self.extract_functions_from_ast(tree),
            'classes': self.extract_classes_from_ast(tree),
            'imports': self.extract_imports_from_ast(tree),
            'variables': self.extract_variables_from_ast(tree),
            'lines_of_code': len(content.split('\n')),
            'content_length': len(content),
            'ast_nodes': len(list(ast.walk(tree)))
        }
    
    def extract_interpretation_model(self, interpretation: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract model from broken interpreter"""
        return {
            'type': 'interpreted',
            'functions': interpretation.get('interpretation', {}).get('functions', []),
            'classes': interpretation.get('interpretation', {}).get('classes', []),
            'imports': interpretation.get('interpretation', {}).get('imports', []),
            'lines_of_code': len(content.split('\n')),
            'content_length': len(content),
            'syntax_errors': interpretation.get('syntax_errors', [])
        }
    
    def extract_basic_model(self, content: str) -> Dict[str, Any]:
        """Extract basic model from content"""
        lines = content.split('\n')
        functions = []
        classes = []
        imports = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('def '):
                functions.append({'name': stripped.split()[1].split('(')[0], 'lineno': i+1})
            elif stripped.startswith('class '):
                classes.append({'name': stripped.split()[1].split('(')[0], 'lineno': i+1})
            elif stripped.startswith(('import ', 'from ')):
                imports.append({'line': stripped, 'lineno': i+1})
        
        return {
            'type': 'basic_analysis',
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'lines_of_code': len(lines),
            'content_length': len(content)
        }
    
    def extract_functions_from_ast(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract functions from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [self.extract_decorator(d) for d in node.decorator_list]
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
                    'methods': self.extract_class_methods(node)
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
                    'args': [arg.arg for arg in item.args.args]
                })
        return methods
    
    def compare_models(self, model1: Dict[str, Any], model2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two models"""
        if 'error' in model1 or 'error' in model2:
            return {'error': 'One or both models have errors'}
        
        comparison = {
            'functions_match': len(model1.get('functions', [])) == len(model2.get('functions', [])),
            'classes_match': len(model1.get('classes', [])) == len(model2.get('classes', [])),
            'imports_match': len(model1.get('imports', [])) == len(model2.get('imports', [])),
            'lines_of_code_diff': abs(model1.get('lines_of_code', 0) - model2.get('lines_of_code', 0)),
            'content_length_diff': abs(model1.get('content_length', 0) - model2.get('content_length', 0)),
            'structure_similarity': self.calculate_structure_similarity(model1, model2)
        }
        
        return comparison
    
    def calculate_structure_similarity(self, model1: Dict[str, Any], model2: Dict[str, Any]) -> float:
        """Calculate structural similarity between models"""
        total_elements = 0
        matching_elements = 0
        
        # Compare functions
        funcs1 = {f['name']: f for f in model1.get('functions', [])}
        funcs2 = {f['name']: f for f in model2.get('functions', [])}
        
        total_elements += len(funcs1) + len(funcs2)
        matching_elements += len(set(funcs1.keys()) & set(funcs2.keys()))
        
        # Compare classes
        classes1 = {c['name']: c for c in model1.get('classes', [])}
        classes2 = {c['name']: c for c in model2.get('classes', [])}
        
        total_elements += len(classes1) + len(classes2)
        matching_elements += len(set(classes1.keys()) & set(classes2.keys()))
        
        if total_elements == 0:
            return 1.0  # Both empty, consider them similar
        
        return matching_elements / total_elements
    
    def find_pattern_match(self, current_model: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find if current model matches any known patterns"""
        # This would check against a database of known patterns
        # For now, return None
        return None
    
    def generate_recommendations(self, current_model: Dict[str, Any], committed_model: Dict[str, Any], persisted_model: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on model comparison"""
        recommendations = []
        
        # Compare current vs committed
        current_vs_committed = self.compare_models(current_model, committed_model)
        if current_vs_committed.get('structure_similarity', 0) < 0.8:
            recommendations.append("Current model differs significantly from committed model - consider reviewing changes")
        
        # Compare current vs persisted
        current_vs_persisted = self.compare_models(current_model, persisted_model)
        if current_vs_persisted.get('structure_similarity', 0) < 0.8:
            recommendations.append("Current model differs from persisted model - may need model update")
        
        return recommendations
    
    def generate_new_artifact_recommendations(self, current_model: Dict[str, Any], persisted_model: Dict[str, Any], pattern_match: Optional[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for new artifacts"""
        recommendations = []
        
        if pattern_match:
            recommendations.append("New artifact matches known pattern - consider adding to model registry")
        else:
            recommendations.append("New artifact with unknown pattern - may need new model definition")
        
        if current_model.get('syntax_errors'):
            recommendations.append("New artifact has syntax errors - needs fixing before model registration")
        
        return recommendations


def main() -> None:
    """Test the model consistency analyzer"""
    print("🔍 Model Consistency Analyzer")
    print("=" * 50)
    
    analyzer = ModelConsistencyAnalyzer()
    
    # Test with different types of files
    test_files = [
        'scripts/mdc-linter.py',  # Has Git history
        'broken_python_interpreter.py',  # New artifact
        'git_enhanced_ast_fixer.py',  # New artifact
        '.cursor/plugins/rule-compliance-checker.py'  # New artifact
    ]
    
    results = []
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Analyzing: {file_path}")
            result = analyzer.analyze_file_consistency(file_path)
            results.append(result)
            
            # Print summary
            if result.get('has_git_history'):
                print(f"  📋 Has Git history")
                comparisons = result.get('comparisons', {})
                current_vs_committed = comparisons.get('current_vs_committed', {})
                similarity = current_vs_committed.get('structure_similarity', 0)
                print(f"  📊 Structure similarity: {similarity:.2f}")
            else:
                print(f"  🆕 New artifact")
                print(f"  📊 Lines of code: {result.get('current_model', {}).get('lines_of_code', 0)}")
    
    # Save results
    with open('model_consistency_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to model_consistency_analysis.json")


if __name__ == "__main__":
    main() 