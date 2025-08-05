#!/usr/bin/env python3
"""
Multi-Generational Git Analyzer
Models several commits back to understand file evolution and guide reconstruction
"""

import json
import subprocess
import ast
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from git_enhanced_ast_fixer import GitEnhancedASTFixer


@dataclass
class CommitModel:
    """Model of a file at a specific commit"""
    commit_hash: str
    commit_message: str
    timestamp: str
    model: Dict[str, Any]
    content: str
    is_valid_python: bool
    generation: int  # 0 = most recent, 1 = second most recent, etc.


class MultiGenerationalGitAnalyzer:
    """Analyzes multiple generations of Git history to understand file evolution"""
    
    def __init__(self, max_generations: int = 5):
        self.max_generations = max_generations
        self.git_fixer = GitEnhancedASTFixer()
        self.temp_dir = None
    
    def analyze_file_evolution(self, file_path: str) -> Dict[str, Any]:
        """Analyze file evolution across multiple Git generations"""
        print(f"🔄 Analyzing file evolution: {file_path}")
        
        # Get multiple generations of commits
        commit_models = self.get_commit_models(file_path)
        
        if not commit_models:
            print(f"  ⚠️  No Git history found")
            return {'error': 'No Git history available'}
        
        print(f"  📊 Found {len(commit_models)} generations")
        
        # Analyze evolution patterns
        evolution_analysis = self.analyze_evolution_patterns(commit_models)
        
        # Generate recommendations
        recommendations = self.generate_evolution_recommendations(commit_models, evolution_analysis)
        
        # Create evolution database
        evolution_db = self.create_evolution_database(file_path, commit_models, evolution_analysis)
        
        return {
            'file_path': file_path,
            'generations_analyzed': len(commit_models),
            'commit_models': [asdict(cm) for cm in commit_models],
            'evolution_analysis': evolution_analysis,
            'recommendations': recommendations,
            'evolution_database': evolution_db
        }
    
    def get_commit_models(self, file_path: str) -> List[CommitModel]:
        """Get models for multiple generations of commits"""
        try:
            # Get commit history
            result = subprocess.run(
                ['git', 'log', '--oneline', '--follow', '--', file_path],
                capture_output=True, text=True, cwd=Path(file_path).parent
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                return []
            
            commits = result.stdout.strip().split('\n')
            commit_models = []
            
            # Analyze up to max_generations
            for i, commit_line in enumerate(commits[:self.max_generations]):
                commit_hash = commit_line.split()[0]
                commit_message = ' '.join(commit_line.split()[1:])
                
                # Get commit timestamp
                timestamp_result = subprocess.run(
                    ['git', 'show', '-s', '--format=%ci', commit_hash],
                    capture_output=True, text=True, cwd=Path(file_path).parent
                )
                timestamp = timestamp_result.stdout.strip() if timestamp_result.returncode == 0 else 'unknown'
                
                # Get file content at this commit
                content_result = subprocess.run(
                    ['git', 'show', f'{commit_hash}:{file_path}'],
                    capture_output=True, text=True, cwd=Path(file_path).parent
                )
                
                if content_result.returncode == 0:
                    content = content_result.stdout
                    
                    # Try to parse with AST
                    try:
                        tree = ast.parse(content)
                        model = self.extract_ast_model(tree, content)
                        is_valid_python = True
                    except (SyntaxError, IndentationError):
                        # Use basic analysis for invalid Python
                        model = self.extract_basic_model(content)
                        is_valid_python = False
                    
                    commit_model = CommitModel(
                        commit_hash=commit_hash,
                        commit_message=commit_message,
                        timestamp=timestamp,
                        model=model,
                        content=content,
                        is_valid_python=is_valid_python,
                        generation=i
                    )
                    
                    commit_models.append(commit_model)
            
            return commit_models
            
        except Exception as e:
            print(f"  ❌ Error getting commit models: {e}")
            return []
    
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
            'ast_nodes': len(list(ast.walk(tree))),
            'complexity_metrics': self.calculate_complexity_metrics(tree)
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
                func_name = stripped.split()[1].split('(')[0]
                functions.append({'name': func_name, 'lineno': i+1})
            elif stripped.startswith('class '):
                class_name = stripped.split()[1].split('(')[0]
                classes.append({'name': class_name, 'lineno': i+1})
            elif stripped.startswith(('import ', 'from ')):
                imports.append({'line': stripped, 'lineno': i+1})
        
        return {
            'type': 'basic_analysis',
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'lines_of_code': len(lines),
            'content_length': len(content),
            'complexity_metrics': {'basic_analysis': True}
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
    
    def calculate_complexity_metrics(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate complexity metrics from AST"""
        cyclomatic_complexity = 0
        nesting_depth = 0
        max_nesting = 0
        
        for node in ast.walk(tree):
            # Count decision points for cyclomatic complexity
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                cyclomatic_complexity += 1
            
            # Calculate nesting depth
            if hasattr(node, 'lineno'):
                # This is a simplified approach - in practice you'd track actual nesting
                nesting_depth = max(nesting_depth, getattr(node, 'lineno', 0) // 10)
        
        return {
            'cyclomatic_complexity': cyclomatic_complexity,
            'nesting_depth': nesting_depth,
            'max_nesting': max_nesting
        }
    
    def analyze_evolution_patterns(self, commit_models: List[CommitModel]) -> Dict[str, Any]:
        """Analyze patterns in file evolution"""
        if len(commit_models) < 2:
            return {'error': 'Need at least 2 generations for evolution analysis'}
        
        evolution = {
            'size_trend': self.analyze_size_trend(commit_models),
            'structure_trend': self.analyze_structure_trend(commit_models),
            'complexity_trend': self.analyze_complexity_trend(commit_models),
            'stability_score': self.calculate_stability_score(commit_models),
            'evolution_phases': self.identify_evolution_phases(commit_models)
        }
        
        return evolution
    
    def analyze_size_trend(self, commit_models: List[CommitModel]) -> Dict[str, Any]:
        """Analyze size evolution trend"""
        sizes = [cm.model.get('lines_of_code', 0) for cm in commit_models]
        
        return {
            'sizes': sizes,
            'trend': 'increasing' if len(sizes) > 1 and sizes[0] > sizes[-1] else 'decreasing' if len(sizes) > 1 and sizes[0] < sizes[-1] else 'stable',
            'size_change': sizes[0] - sizes[-1] if len(sizes) > 1 else 0,
            'average_size': sum(sizes) / len(sizes) if sizes else 0
        }
    
    def analyze_structure_trend(self, commit_models: List[CommitModel]) -> Dict[str, Any]:
        """Analyze structural evolution trend"""
        function_counts = [len(cm.model.get('functions', [])) for cm in commit_models]
        class_counts = [len(cm.model.get('classes', [])) for cm in commit_models]
        import_counts = [len(cm.model.get('imports', [])) for cm in commit_models]
        
        return {
            'function_counts': function_counts,
            'class_counts': class_counts,
            'import_counts': import_counts,
            'function_trend': self.calculate_trend(function_counts),
            'class_trend': self.calculate_trend(class_counts),
            'import_trend': self.calculate_trend(import_counts)
        }
    
    def analyze_complexity_trend(self, commit_models: List[CommitModel]) -> Dict[str, Any]:
        """Analyze complexity evolution trend"""
        complexities = []
        for cm in commit_models:
            complexity = cm.model.get('complexity_metrics', {})
            if isinstance(complexity, dict):
                complexities.append(complexity.get('cyclomatic_complexity', 0))
            else:
                complexities.append(0)
        
        return {
            'complexities': complexities,
            'complexity_trend': self.calculate_trend(complexities),
            'average_complexity': sum(complexities) / len(complexities) if complexities else 0
        }
    
    def calculate_trend(self, values: List[int]) -> str:
        """Calculate trend from a list of values"""
        if len(values) < 2:
            return 'stable'
        
        if values[0] > values[-1]:
            return 'decreasing'
        elif values[0] < values[-1]:
            return 'increasing'
        else:
            return 'stable'
    
    def calculate_stability_score(self, commit_models: List[CommitModel]) -> float:
        """Calculate stability score based on model consistency"""
        if len(commit_models) < 2:
            return 1.0
        
        similarities = []
        for i in range(len(commit_models) - 1):
            similarity = self.calculate_model_similarity(
                commit_models[i].model, 
                commit_models[i + 1].model
            )
            similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 1.0
    
    def calculate_model_similarity(self, model1: Dict[str, Any], model2: Dict[str, Any]) -> float:
        """Calculate similarity between two models"""
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
            return 1.0
        
        return matching_elements / total_elements
    
    def identify_evolution_phases(self, commit_models: List[CommitModel]) -> List[Dict[str, Any]]:
        """Identify distinct phases in file evolution"""
        phases = []
        
        for i, cm in enumerate(commit_models):
            phase = {
                'generation': i,
                'commit_hash': cm.commit_hash,
                'commit_message': cm.commit_message,
                'timestamp': cm.timestamp,
                'characteristics': {
                    'size': cm.model.get('lines_of_code', 0),
                    'functions': len(cm.model.get('functions', [])),
                    'classes': len(cm.model.get('classes', [])),
                    'is_valid_python': cm.is_valid_python
                }
            }
            
            # Determine phase type
            if i == 0:
                phase['type'] = 'current'
            elif i == len(commit_models) - 1:
                phase['type'] = 'initial'
            else:
                phase['type'] = 'evolutionary'
            
            phases.append(phase)
        
        return phases
    
    def generate_evolution_recommendations(self, commit_models: List[CommitModel], evolution_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on evolution analysis"""
        recommendations = []
        
        # Check stability
        stability_score = evolution_analysis.get('stability_score', 1.0)
        if stability_score < 0.7:
            recommendations.append("File shows low stability - consider refactoring for consistency")
        
        # Check size trends
        size_trend = evolution_analysis.get('size_trend', {})
        if size_trend.get('trend') == 'increasing' and size_trend.get('size_change', 0) > 50:
            recommendations.append("File has grown significantly - consider splitting into smaller modules")
        
        # Check complexity trends
        complexity_trend = evolution_analysis.get('complexity_trend', {})
        if complexity_trend.get('complexity_trend') == 'increasing':
            recommendations.append("Complexity is increasing - consider simplifying logic")
        
        # Check for valid Python versions
        valid_versions = [cm for cm in commit_models if cm.is_valid_python]
        if len(valid_versions) < len(commit_models):
            recommendations.append("Some versions have syntax errors - use valid versions as templates")
        
        return recommendations
    
    def create_evolution_database(self, file_path: str, commit_models: List[CommitModel], evolution_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a database of evolution information"""
        return {
            'file_path': file_path,
            'total_generations': len(commit_models),
            'evolution_summary': {
                'size_trend': evolution_analysis.get('size_trend', {}).get('trend', 'unknown'),
                'stability_score': evolution_analysis.get('stability_score', 1.0),
                'most_stable_generation': self.find_most_stable_generation(commit_models),
                'best_template_generation': self.find_best_template_generation(commit_models)
            },
            'generation_details': [
                {
                    'generation': cm.generation,
                    'commit_hash': cm.commit_hash,
                    'is_valid_python': cm.is_valid_python,
                    'size': cm.model.get('lines_of_code', 0),
                    'functions': len(cm.model.get('functions', [])),
                    'classes': len(cm.model.get('classes', []))
                }
                for cm in commit_models
            ]
        }
    
    def find_most_stable_generation(self, commit_models: List[CommitModel]) -> int:
        """Find the most stable generation"""
        if len(commit_models) < 2:
            return 0
        
        # For now, return the generation with the most functions (proxy for stability)
        max_functions = 0
        most_stable = 0
        
        for i, cm in enumerate(commit_models):
            func_count = len(cm.model.get('functions', []))
            if func_count > max_functions:
                max_functions = func_count
                most_stable = i
        
        return most_stable
    
    def find_best_template_generation(self, commit_models: List[CommitModel]) -> int:
        """Find the best generation to use as a template"""
        # Prefer valid Python versions
        valid_versions = [i for i, cm in enumerate(commit_models) if cm.is_valid_python]
        
        if valid_versions:
            # Among valid versions, prefer the most recent
            return min(valid_versions)
        else:
            # If no valid versions, use the most recent
            return 0


def main() -> None:
    """Test the multi-generational Git analyzer"""
    print("🔄 Multi-Generational Git Analyzer")
    print("=" * 50)
    
    analyzer = MultiGenerationalGitAnalyzer(max_generations=3)
    
    # Test with files that have Git history
    test_files = [
        'scripts/mdc-linter.py'  # Has Git history
    ]
    
    results = []
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"\n📁 Analyzing evolution: {file_path}")
            result = analyzer.analyze_file_evolution(file_path)
            results.append(result)
            
            if 'error' not in result:
                print(f"  📊 Generations analyzed: {result.get('generations_analyzed', 0)}")
                evolution_db = result.get('evolution_database', {})
                summary = evolution_db.get('evolution_summary', {})
                print(f"  📈 Size trend: {summary.get('size_trend', 'unknown')}")
                print(f"  🎯 Stability score: {summary.get('stability_score', 0):.2f}")
                print(f"  🏆 Best template generation: {summary.get('best_template_generation', 0)}")
            else:
                print(f"  ❌ {result['error']}")
    
    # Save results
    with open('multi_generational_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to multi_generational_analysis.json")


if __name__ == "__main__":
    main() 