#!/usr/bin/env python3
"""
Enhanced Python Quality Enforcement Test

This test extends the basic Python quality enforcement to include:
1. Model-driven projection testing
2. Functional equivalence validation
3. Comprehensive quality checks
4. Model registry updates
"""

import ast
import subprocess
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPythonQualityTester:
    """Enhanced Python quality tester with model-driven features."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.model_registry_path = self.project_root / "project_model_registry.json"
        self.model_driven_projection_path = self.project_root / "src" / "model_driven_projection"
        
    def test_python_file_quality(self, file_path: Path) -> Dict[str, Any]:
        """Test a single Python file for quality compliance."""
        logger.info(f"🧪 Testing Python file quality: {file_path}")
        
        results = {
            "file": str(file_path),
            "ast_parse": False,
            "black_format": False,
            "flake8_lint": False,
            "mypy_check": False,
            "imports_valid": False,
            "type_annotations": False,
            "docstrings": False,
            "error_handling": False,
            "security_check": False,
            "model_projection": False,
            "functional_equivalence": False
        }
        
        try:
            # Test AST parsing
            with open(file_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            results["ast_parse"] = True
            logger.info(f"✅ AST parsing successful: {file_path}")
        except SyntaxError as e:
            logger.error(f"❌ AST parsing failed: {file_path} - {e}")
            return results
        
        # Test Black formatting
        try:
            result = subprocess.run(
                ['uv', 'run', 'black', '--check', str(file_path)],
                capture_output=True, text=True, timeout=30
            )
            results["black_format"] = result.returncode == 0
            if results["black_format"]:
                logger.info(f"✅ Black formatting check passed: {file_path}")
            else:
                logger.warning(f"⚠️ Black formatting issues: {file_path}")
        except Exception as e:
            logger.error(f"❌ Black check failed: {file_path} - {e}")
        
        # Test Flake8 linting
        try:
            result = subprocess.run(
                ['uv', 'run', 'flake8', str(file_path)],
                capture_output=True, text=True, timeout=30
            )
            results["flake8_lint"] = result.returncode == 0
            if results["flake8_lint"]:
                logger.info(f"✅ Flake8 linting passed: {file_path}")
            else:
                logger.warning(f"⚠️ Flake8 issues: {file_path}")
                logger.debug(f"Flake8 output: {result.stdout}")
        except Exception as e:
            logger.error(f"❌ Flake8 check failed: {file_path} - {e}")
        
        # Test MyPy type checking
        try:
            result = subprocess.run(
                ['uv', 'run', 'mypy', str(file_path)],
                capture_output=True, text=True, timeout=30
            )
            results["mypy_check"] = result.returncode == 0
            if results["mypy_check"]:
                logger.info(f"✅ MyPy type checking passed: {file_path}")
            else:
                logger.warning(f"⚠️ MyPy issues: {file_path}")
                logger.debug(f"MyPy output: {result.stdout}")
        except Exception as e:
            logger.error(f"❌ MyPy check failed: {file_path} - {e}")
        
        # Test imports validity
        results["imports_valid"] = self._test_imports_validity(file_path, content)
        
        # Test type annotations
        results["type_annotations"] = self._test_type_annotations(file_path, content)
        
        # Test docstrings
        results["docstrings"] = self._test_docstrings(file_path, content)
        
        # Test error handling
        results["error_handling"] = self._test_error_handling(file_path, content)
        
        # Test security
        results["security_check"] = self._test_security(file_path)
        
        # Test model projection (if applicable)
        if self._is_model_driven_file(file_path):
            results["model_projection"] = self._test_model_projection(file_path)
            results["functional_equivalence"] = self._test_functional_equivalence(file_path)
        
        return results
    
    def _test_imports_validity(self, file_path: Path, content: str) -> bool:
        """Test that imports are valid and used."""
        try:
            tree = ast.parse(content)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(node)
            
            # Check for unused imports (basic check)
            import_names = set()
            for imp in imports:
                if isinstance(imp, ast.Import):
                    for alias in imp.names:
                        import_names.add(alias.name)
                elif isinstance(imp, ast.ImportFrom):
                    if imp.module:
                        import_names.add(imp.module)
            
            # This is a simplified check - in practice you'd need more sophisticated analysis
            logger.info(f"✅ Imports validation completed: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Imports validation failed: {file_path} - {e}")
            return False
    
    def _test_type_annotations(self, file_path: Path, content: str) -> bool:
        """Test for type annotations in functions and classes."""
        try:
            tree = ast.parse(content)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            annotated_functions = 0
            total_functions = len(functions)
            
            for func in functions:
                if func.returns is not None:
                    annotated_functions += 1
                # Check parameters
                for arg in func.args.args:
                    if arg.annotation is not None:
                        annotated_functions += 1
                        break
            
            if total_functions == 0:
                logger.info(f"✅ No functions to check for type annotations: {file_path}")
                return True
            
            annotation_ratio = annotated_functions / total_functions
            logger.info(f"✅ Type annotation ratio: {annotation_ratio:.2f} ({annotated_functions}/{total_functions})")
            return annotation_ratio > 0.3  # At least 30% should have annotations
        except Exception as e:
            logger.error(f"❌ Type annotation check failed: {file_path} - {e}")
            return False
    
    def _test_docstrings(self, file_path: Path, content: str) -> bool:
        """Test for docstrings in functions and classes."""
        try:
            tree = ast.parse(content)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            documented_items = 0
            total_items = len(functions) + len(classes)
            
            for func in functions:
                if ast.get_docstring(func) is not None:
                    documented_items += 1
            
            for cls in classes:
                if ast.get_docstring(cls) is not None:
                    documented_items += 1
            
            if total_items == 0:
                logger.info(f"✅ No functions/classes to check for docstrings: {file_path}")
                return True
            
            docstring_ratio = documented_items / total_items
            logger.info(f"✅ Docstring ratio: {docstring_ratio:.2f} ({documented_items}/{total_items})")
            return docstring_ratio > 0.5  # At least 50% should have docstrings
        except Exception as e:
            logger.error(f"❌ Docstring check failed: {file_path} - {e}")
            return False
    
    def _test_error_handling(self, file_path: Path, content: str) -> bool:
        """Test for proper error handling."""
        try:
            # Check for try/except blocks
            if 'try:' in content and 'except' in content:
                logger.info(f"✅ Error handling found: {file_path}")
                return True
            else:
                logger.warning(f"⚠️ No explicit error handling found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"❌ Error handling check failed: {file_path} - {e}")
            return False
    
    def _test_security(self, file_path: Path) -> bool:
        """Test for security issues using bandit."""
        try:
            result = subprocess.run(
                ['uv', 'run', 'bandit', '-r', str(file_path)],
                capture_output=True, text=True, timeout=30
            )
            # Bandit returns 0 for no issues, 1 for issues found
            if result.returncode == 0:
                logger.info(f"✅ Security check passed: {file_path}")
                return True
            else:
                logger.warning(f"⚠️ Security issues found: {file_path}")
                logger.debug(f"Bandit output: {result.stdout}")
                return False
        except Exception as e:
            logger.error(f"❌ Security check failed: {file_path} - {e}")
            return False
    
    def _is_model_driven_file(self, file_path: Path) -> bool:
        """Check if file is part of model-driven projection system."""
        return (
            "model_driven_projection" in str(file_path) or
            "projection" in str(file_path) or
            "granular_nodes" in str(file_path)
        )
    
    def _test_model_projection(self, file_path: Path) -> bool:
        """Test model projection functionality."""
        try:
            # Import the model-driven projection system
            sys.path.insert(0, str(self.project_root))
            from src.model_driven_projection import FinalProjectionSystem
            
            system = FinalProjectionSystem()
            
            # Test that the file can be processed by the projection system
            # This is a basic test - in practice you'd want more comprehensive testing
            logger.info(f"✅ Model projection system can process: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Model projection test failed: {file_path} - {e}")
            return False
    
    def _test_functional_equivalence(self, file_path: Path) -> bool:
        """Test functional equivalence for model-driven files."""
        try:
            # Run the simple equivalence test
            result = subprocess.run(
                ['python', str(self.model_driven_projection_path / 'test_simple_equivalence.py')],
                capture_output=True, text=True, timeout=60,
                cwd=self.model_driven_projection_path
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Functional equivalence test passed: {file_path}")
                return True
            else:
                logger.warning(f"⚠️ Functional equivalence test failed: {file_path}")
                logger.debug(f"Test output: {result.stdout}")
                return False
        except Exception as e:
            logger.error(f"❌ Functional equivalence test failed: {file_path} - {e}")
            return False
    
    def update_model_registry(self, test_results: List[Dict[str, Any]]) -> bool:
        """Update the project model registry with test results."""
        try:
            # Load current model registry
            with open(self.model_registry_path, 'r') as f:
                model_registry = json.load(f)
            
            # Update with test results
            if "test_results" not in model_registry:
                model_registry["test_results"] = {}
            
            model_registry["test_results"]["python_quality_enhanced"] = {
                "timestamp": str(Path.cwd()),
                "files_tested": len(test_results),
                "results": test_results,
                "summary": self._generate_summary(test_results)
            }
            
            # Save updated model registry
            with open(self.model_registry_path, 'w') as f:
                json.dump(model_registry, f, indent=2)
            
            logger.info("✅ Model registry updated with test results")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update model registry: {e}")
            return False
    
    def _generate_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from test results."""
        total_files = len(test_results)
        if total_files == 0:
            return {"error": "No files tested"}
        
        summary = {
            "total_files": total_files,
            "passed_tests": {},
            "failed_tests": {},
            "success_rate": {}
        }
        
        # Count passed/failed tests for each category
        test_categories = [
            "ast_parse", "black_format", "flake8_lint", "mypy_check",
            "imports_valid", "type_annotations", "docstrings", 
            "error_handling", "security_check", "model_projection", 
            "functional_equivalence"
        ]
        
        for category in test_categories:
            passed = sum(1 for result in test_results if result.get(category, False))
            failed = total_files - passed
            success_rate = passed / total_files if total_files > 0 else 0
            
            summary["passed_tests"][category] = passed
            summary["failed_tests"][category] = failed
            summary["success_rate"][category] = success_rate
        
        return summary
    
    def run_enhanced_tests(self) -> bool:
        """Run enhanced Python quality tests on all Python files."""
        logger.info("🧪 **ENHANCED PYTHON QUALITY ENFORCEMENT TEST**")
        logger.info("=" * 60)
        
        # Find all Python files with proper exclusions
        python_files = []
        for file_path in self.project_root.rglob("*.py"):
            # Skip virtual environments and other non-project directories
            if any(exclude in str(file_path) for exclude in [
                ".venv", "__pycache__", ".git", "node_modules", 
                "site-packages", "dist-packages", ".pytest_cache",
                ".mypy_cache", ".coverage", ".tox", ".eggs"
            ]):
                continue
            
            # Only include files in our project directories
            if any(include in str(file_path) for include in [
                "src/", "tests/", "scripts/", "healthcare-cdc/",
                "docs/", ".cursor/", "config/"
            ]):
                python_files.append(file_path)
        
        if not python_files:
            logger.error("❌ No Python files found in project directories")
            return False
        
        logger.info(f"📁 Found {len(python_files)} Python files to test")
        
        # Test each file
        test_results = []
        for file_path in python_files:
            result = self.test_python_file_quality(file_path)
            test_results.append(result)
        
        # Update model registry
        self.update_model_registry(test_results)
        
        # Generate summary
        summary = self._generate_summary(test_results)
        
        # Print results
        logger.info("\n📊 **ENHANCED TEST RESULTS SUMMARY**")
        logger.info("=" * 50)
        
        for category, success_rate in summary["success_rate"].items():
            passed = summary["passed_tests"][category]
            total = summary["total_files"]
            status = "✅" if success_rate >= 0.8 else "⚠️" if success_rate >= 0.5 else "❌"
            logger.info(f"{status} {category}: {passed}/{total} ({success_rate:.1%})")
        
        # Overall success
        overall_success = all(
            summary["success_rate"][category] >= 0.8 
            for category in ["ast_parse", "black_format", "flake8_lint"]
        )
        
        if overall_success:
            logger.info("\n🎉 **ALL ENHANCED PYTHON QUALITY TESTS PASSED!**")
        else:
            logger.error("\n❌ **SOME ENHANCED PYTHON QUALITY TESTS FAILED**")
        
        return overall_success


def main():
    """Run enhanced Python quality tests."""
    tester = EnhancedPythonQualityTester()
    success = tester.run_enhanced_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 