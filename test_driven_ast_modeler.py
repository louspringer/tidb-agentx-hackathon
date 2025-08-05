#!/usr/bin/env python3
"""
Test-Driven AST Modeler with Requirements Analysis and Recovery Targets
"""

import ast
import json
import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import yaml


@dataclass
class TestRequirement:
    """Test requirement with recovery targets"""
    requirement_id: str
    description: str
    test_files: List[str]
    target_files: List[str]
    recovery_targets: List[str]
    validation_method: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    status: str  # 'passing', 'failing', 'error', 'missing'


@dataclass
class RecoveryTarget:
    """Recovery target for failed tests"""
    target_file: str
    target_type: str  # 'syntax', 'import', 'class', 'function', 'test'
    failure_pattern: str
    recovery_strategy: str
    dependencies: List[str]
    test_requirements: List[str]


@dataclass
class TestDrivenASTModel:
    """Enhanced AST model with test-driven requirements"""
    file_path: str
    file_type: str
    model_type: str
    model_data: Dict[str, Any]
    complexity_score: float
    structure_hash: str
    lines_of_code: int
    created_at: str
    commit_hash: Optional[str] = None
    
    # Test-driven analysis
    test_requirements: List[TestRequirement] = None
    recovery_targets: List[RecoveryTarget] = None
    test_coverage: Dict[str, Any] = None
    requirement_traceability: Dict[str, Any] = None


class TestRequirementAnalyzer:
    """Analyze test files for requirements and recovery targets"""
    
    def __init__(self):
        self.requirement_patterns = {
            'test_requirement': r'test_requirement_\d+',
            'requirement_description': r'"""([^"]+)"""',
            'target_files': r'target.*file|file.*target',
            'recovery_target': r'recovery.*target|target.*recovery',
            'validation_method': r'pytest|unittest|assert',
            'priority': r'critical|high|medium|low'
        }
    
    def analyze_test_file(self, file_path: str) -> List[TestRequirement]:
        """Analyze test file for requirements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            requirements = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    req = self._extract_requirement_from_function(node, content)
                    if req:
                        requirements.append(req)
            
            return requirements
            
        except Exception as e:
            return []
    
    def _extract_requirement_from_function(self, node: ast.FunctionDef, content: str) -> Optional[TestRequirement]:
        """Extract requirement from test function"""
        # Look for requirement patterns in function name and docstring
        func_name = node.name
        
        # Check if it's a requirement test
        if not re.search(self.requirement_patterns['test_requirement'], func_name):
            return None
        
        # Extract requirement ID
        req_id_match = re.search(r'test_requirement_(\d+)', func_name)
        if not req_id_match:
            return None
        
        req_id = req_id_match.group(1)
        
        # Extract description from docstring
        docstring = ast.get_docstring(node) or ""
        
        # Extract target files from function body
        target_files = self._extract_target_files_from_body(node, content)
        
        # Extract recovery targets
        recovery_targets = self._extract_recovery_targets_from_body(node, content)
        
        # Determine validation method
        validation_method = self._determine_validation_method(node, content)
        
        # Determine priority
        priority = self._determine_priority(node, content)
        
        return TestRequirement(
            requirement_id=f"requirement_{req_id}",
            description=docstring,
            test_files=[node.name],
            target_files=target_files,
            recovery_targets=recovery_targets,
            validation_method=validation_method,
            priority=priority,
            status="unknown"  # Will be determined by test execution
        )
    
    def _extract_target_files_from_body(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Extract target files from test function body"""
        target_files = []
        
        # Look for file paths in string literals
        for child in ast.walk(node):
            if isinstance(child, ast.Str):
                if any(ext in child.s for ext in ['.py', '.mdc', '.md', '.yaml', '.json']):
                    target_files.append(child.s)
        
        # Look for file patterns in comments
        lines = content.split('\n')
        for line in lines:
            if '#' in line and any(ext in line for ext in ['.py', '.mdc', '.md', '.yaml', '.json']):
                # Extract file path from comment
                match = re.search(r'([^\s]+\.(py|mdc|md|yaml|json))', line)
                if match:
                    target_files.append(match.group(1))
        
        return list(set(target_files))
    
    def _extract_recovery_targets_from_body(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Extract recovery targets from test function body"""
        recovery_targets = []
        
        # Look for recovery patterns
        for child in ast.walk(node):
            if isinstance(child, ast.Str):
                if 'recovery' in child.s.lower() or 'fix' in child.s.lower():
                    recovery_targets.append(child.s)
        
        return recovery_targets
    
    def _determine_validation_method(self, node: ast.FunctionDef, content: str) -> str:
        """Determine validation method used in test"""
        if 'pytest' in content.lower():
            return 'pytest'
        elif 'unittest' in content.lower():
            return 'unittest'
        elif 'assert' in content.lower():
            return 'assert'
        else:
            return 'unknown'
    
    def _determine_priority(self, node: ast.FunctionDef, content: str) -> str:
        """Determine priority of requirement"""
        if 'critical' in content.lower():
            return 'critical'
        elif 'high' in content.lower():
            return 'high'
        elif 'medium' in content.lower():
            return 'medium'
        else:
            return 'low'


class RecoveryTargetAnalyzer:
    """Analyze files for recovery targets based on test failures"""
    
    def __init__(self):
        self.recovery_patterns = {
            'syntax_error': r'SyntaxError|IndentationError',
            'import_error': r'ImportError|ModuleNotFoundError',
            'name_error': r'NameError|AttributeError',
            'type_error': r'TypeError',
            'assertion_error': r'AssertionError',
            'test_failure': r'FAILED|ERROR'
        }
    
    def analyze_recovery_targets(self, test_results: Dict[str, Any]) -> List[RecoveryTarget]:
        """Analyze test results for recovery targets"""
        recovery_targets = []
        
        for test_file, result in test_results.items():
            if result.get('status') in ['FAILED', 'ERROR']:
                targets = self._extract_recovery_targets_from_failure(test_file, result)
                recovery_targets.extend(targets)
        
        return recovery_targets
    
    def _extract_recovery_targets_from_failure(self, test_file: str, result: Dict[str, Any]) -> List[RecoveryTarget]:
        """Extract recovery targets from test failure"""
        targets = []
        error_message = result.get('error', '')
        
        # Check for syntax errors
        if re.search(self.recovery_patterns['syntax_error'], error_message):
            targets.append(RecoveryTarget(
                target_file=test_file,
                target_type='syntax',
                failure_pattern='syntax_error',
                recovery_strategy='fix_indentation_and_syntax',
                dependencies=[],
                test_requirements=[]
            ))
        
        # Check for import errors
        if re.search(self.recovery_patterns['import_error'], error_message):
            targets.append(RecoveryTarget(
                target_file=test_file,
                target_type='import',
                failure_pattern='import_error',
                recovery_strategy='fix_imports_and_dependencies',
                dependencies=[],
                test_requirements=[]
            ))
        
        # Check for name errors (missing classes/functions)
        if re.search(self.recovery_patterns['name_error'], error_message):
            targets.append(RecoveryTarget(
                target_file=test_file,
                target_type='class',
                failure_pattern='name_error',
                recovery_strategy='implement_missing_classes_and_functions',
                dependencies=[],
                test_requirements=[]
            ))
        
        return targets


class TestDrivenASTModeler:
    """Enhanced AST modeler with test-driven requirements analysis"""
    
    def __init__(self, database_path: str = "test_driven_ast_models.json"):
        self.database_path = database_path
        self.requirement_analyzer = TestRequirementAnalyzer()
        self.recovery_analyzer = RecoveryTargetAnalyzer()
        self.database_lock = Lock()
        
        # Load existing database
        self.database = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load existing database"""
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'file_models': {},
            'test_requirements': {},
            'recovery_targets': {},
            'test_results': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '2.0.0',
                'total_files': 0,
                'total_requirements': 0,
                'total_recovery_targets': 0,
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def _save_database(self):
        """Save database with test-driven analysis"""
        with self.database_lock:
            self.database['metadata']['last_updated'] = datetime.now().isoformat()
            self.database['metadata']['total_files'] = len(self.database['file_models'])
            self.database['metadata']['total_requirements'] = len(self.database['test_requirements'])
            self.database['metadata']['total_recovery_targets'] = len(self.database['recovery_targets'])
            
            with open(self.database_path, 'w') as f:
                json.dump(self.database, f, indent=2, default=str)
    
    def analyze_test_requirements(self, test_directory: str = "tests/") -> Dict[str, Any]:
        """Analyze test files for requirements"""
        print("🧪 Analyzing test requirements...")
        
        test_files = list(Path(test_directory).rglob("*.py"))
        all_requirements = []
        
        for test_file in test_files:
            requirements = self.requirement_analyzer.analyze_test_file(str(test_file))
            all_requirements.extend(requirements)
            
            # Store in database
            self.database['test_requirements'][str(test_file)] = [
                asdict(req) for req in requirements
            ]
        
        print(f"✅ Found {len(all_requirements)} test requirements")
        return {
            'total_requirements': len(all_requirements),
            'requirements': all_requirements,
            'test_files_analyzed': len(test_files)
        }
    
    def analyze_recovery_targets(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results for recovery targets"""
        print("🔧 Analyzing recovery targets...")
        
        recovery_targets = self.recovery_analyzer.analyze_recovery_targets(test_results)
        
        # Store in database
        self.database['recovery_targets'] = [
            asdict(target) for target in recovery_targets
        ]
        
        print(f"✅ Found {len(recovery_targets)} recovery targets")
        return {
            'total_recovery_targets': len(recovery_targets),
            'recovery_targets': recovery_targets
        }
    
    def get_requirements_for_file(self, file_path: str) -> List[TestRequirement]:
        """Get test requirements that target a specific file"""
        requirements = []
        
        for test_file, reqs in self.database['test_requirements'].items():
            for req_data in reqs:
                if file_path in req_data.get('target_files', []):
                    requirements.append(TestRequirement(**req_data))
        
        return requirements
    
    def get_recovery_targets_for_file(self, file_path: str) -> List[RecoveryTarget]:
        """Get recovery targets for a specific file"""
        targets = []
        
        for target_data in self.database['recovery_targets']:
            if target_data['target_file'] == file_path:
                targets.append(RecoveryTarget(**target_data))
        
        return targets
    
    def update_test_results(self, test_results: Dict[str, Any]):
        """Update test results and analyze for recovery targets"""
        self.database['test_results'] = test_results
        
        # Analyze for recovery targets
        recovery_analysis = self.analyze_recovery_targets(test_results)
        
        # Update requirement statuses
        self._update_requirement_statuses(test_results)
        
        self._save_database()
    
    def _update_requirement_statuses(self, test_results: Dict[str, Any]):
        """Update requirement statuses based on test results"""
        for test_file, result in test_results.items():
            if test_file in self.database['test_requirements']:
                for req_data in self.database['test_requirements'][test_file]:
                    # Update status based on test result
                    if result.get('status') == 'PASSED':
                        req_data['status'] = 'passing'
                    elif result.get('status') == 'FAILED':
                        req_data['status'] = 'failing'
                    elif result.get('status') == 'ERROR':
                        req_data['status'] = 'error'
    
    def generate_recovery_plan(self) -> Dict[str, Any]:
        """Generate recovery plan based on test failures"""
        failing_requirements = []
        recovery_targets = []
        
        # Find failing requirements
        for test_file, reqs in self.database['test_requirements'].items():
            for req_data in reqs:
                if req_data.get('status') in ['failing', 'error']:
                    failing_requirements.append(req_data)
        
        # Get recovery targets
        for target_data in self.database['recovery_targets']:
            recovery_targets.append(target_data)
        
        return {
            'failing_requirements': failing_requirements,
            'recovery_targets': recovery_targets,
            'priority_order': self._prioritize_recovery_targets(recovery_targets)
        }
    
    def _prioritize_recovery_targets(self, targets: List[Dict[str, Any]]) -> List[str]:
        """Prioritize recovery targets by impact"""
        # Critical syntax errors first
        syntax_targets = [t for t in targets if t['target_type'] == 'syntax']
        
        # Import errors second
        import_targets = [t for t in targets if t['target_type'] == 'import']
        
        # Missing classes/functions third
        class_targets = [t for t in targets if t['target_type'] == 'class']
        
        # Test failures last
        test_targets = [t for t in targets if t['target_type'] == 'test']
        
        return syntax_targets + import_targets + class_targets + test_targets


def main():
    """Main function for testing"""
    print("🧪 Test-Driven AST Modeler")
    print("=" * 50)
    
    modeler = TestDrivenASTModeler()
    
    # Analyze test requirements
    req_analysis = modeler.analyze_test_requirements()
    
    # Simulate test results (in real usage, this would come from pytest)
    test_results = {
        'tests/test_syntax_fixes.py': {'status': 'FAILED', 'error': 'IndentationError'},
        'tests/test_imports.py': {'status': 'ERROR', 'error': 'ModuleNotFoundError'},
        'tests/test_classes.py': {'status': 'FAILED', 'error': 'NameError: name \'CodeQualityModel\' is not defined'}
    }
    
    # Update test results and analyze recovery targets
    modeler.update_test_results(test_results)
    
    # Generate recovery plan
    recovery_plan = modeler.generate_recovery_plan()
    
    print(f"\n📊 Analysis Results:")
    print(f"  Test Requirements: {req_analysis['total_requirements']}")
    print(f"  Recovery Targets: {len(recovery_plan['recovery_targets'])}")
    print(f"  Failing Requirements: {len(recovery_plan['failing_requirements'])}")
    
    print(f"\n🎯 Priority Recovery Order:")
    for i, target in enumerate(recovery_plan['priority_order'][:5], 1):
        print(f"  {i}. {target['target_file']} ({target['target_type']})")
    
    print(f"\n✅ Test-driven analysis complete! Database saved to: {modeler.database_path}")


if __name__ == "__main__":
    main() 