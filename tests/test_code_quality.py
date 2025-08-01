#!/usr/bin/env python3
"""
Code Quality Validation Tests
Tests for import cleanliness, code organization, and maintainability
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

class CodeQualityValidator:
    """Validates code quality including imports, structure, and maintainability"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def check_duplicate_imports(self, file_path: Path) -> List[str]:
        """Check for duplicate imports in a Python file"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the file
            tree = ast.parse(content)
            
            # Collect all imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Check for duplicates
            seen = set()
            for imp in imports:
                if imp in seen:
                    issues.append(f"Duplicate import: {imp}")
                seen.add(imp)
                
        except Exception as e:
            issues.append(f"Error parsing {file_path}: {e}")
            
        return issues
    
    def check_missing_imports(self, file_path: Path) -> List[str]:
        """Check for missing imports (basic check for common patterns)"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for common patterns that require imports
            patterns = [
                (r're\.', 'import re'),
                (r'json\.', 'import json'),
                (r'yaml\.', 'import yaml'),
                (r'pathlib\.', 'from pathlib import Path'),
                (r'typing\.', 'from typing import'),
            ]
            
            for pattern, required_import in patterns:
                if re.search(pattern, content):
                    # Check if the import is present
                    if required_import not in content:
                        issues.append(f"Missing import: {required_import}")
                        
        except Exception as e:
            issues.append(f"Error checking imports in {file_path}: {e}")
            
        return issues
    
    def check_file_length(self, file_path: Path, max_lines: int = 500) -> List[str]:
        """Check if file is too long"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > max_lines:
                issues.append(f"File too long: {len(lines)} lines (max: {max_lines})")
                
        except Exception as e:
            issues.append(f"Error checking file length for {file_path}: {e}")
            
        return issues
    
    def check_long_strings(self, file_path: Path, max_string_lines: int = 50) -> List[str]:
        """Check for very long multi-line strings"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find multi-line strings
            string_pattern = r'"""(.*?)"""'
            matches = re.findall(string_pattern, content, re.DOTALL)
            
            for match in matches:
                lines = match.split('\n')
                if len(lines) > max_string_lines:
                    issues.append(f"Very long multi-line string: {len(lines)} lines (max: {max_string_lines})")
                    
        except Exception as e:
            issues.append(f"Error checking strings in {file_path}: {e}")
            
        return issues

def test_import_cleanliness():
    """Test that all Python files have clean imports"""
    validator = CodeQualityValidator()
    python_files = list(validator.project_root.rglob("*.py"))
    
    all_issues = []
    
    for file_path in python_files:
        # Skip test files for now to avoid circular imports
        if "test_" in file_path.name and file_path.parent.name == "tests":
            continue
            
        duplicate_issues = validator.check_duplicate_imports(file_path)
        missing_issues = validator.check_missing_imports(file_path)
        
        if duplicate_issues or missing_issues:
            all_issues.append(f"\n{file_path}:")
            all_issues.extend(duplicate_issues)
            all_issues.extend(missing_issues)
    
    if all_issues:
        print("❌ Import issues found:")
        for issue in all_issues:
            print(f"  {issue}")
        assert False, f"Found {len(all_issues)} import issues"
    else:
        print("✅ All imports are clean")

def test_file_maintainability():
    """Test that files are maintainable (not too long, no very long strings)"""
    validator = CodeQualityValidator()
    python_files = list(validator.project_root.rglob("*.py"))
    
    all_issues = []
    
    for file_path in python_files:
        length_issues = validator.check_file_length(file_path)
        string_issues = validator.check_long_strings(file_path)
        
        if length_issues or string_issues:
            all_issues.append(f"\n{file_path}:")
            all_issues.extend(length_issues)
            all_issues.extend(string_issues)
    
    if all_issues:
        print("❌ Maintainability issues found:")
        for issue in all_issues:
            print(f"  {issue}")
        assert False, f"Found {len(all_issues)} maintainability issues"
    else:
        print("✅ All files are maintainable")

def test_specific_issues_fixed():
    """Test that the specific issues Copilot found are fixed"""
    
    # Test 1: No duplicate sys import in test_basic_validation_simple.py
    file_path = Path(__file__).parent / "test_basic_validation_simple.py"
    if file_path.exists():
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Count sys imports
        sys_imports = content.count("import sys")
        assert sys_imports <= 1, f"Found {sys_imports} sys imports (should be <= 1)"
        print("✅ No duplicate sys imports")
    
    # Test 2: re import present in rule compliance test
    file_path = Path(__file__).parent / "test_rule_compliance_enforcement.py"
    if file_path.exists():
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "import re" in content, "Missing import re in rule compliance test"
        print("✅ re import present in rule compliance test")
    
    # Test 3: re import present in healthcare CDC test
    file_path = Path(__file__).parent / "test_healthcare_cdc_requirements.py"
    if file_path.exists():
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "import re" in content, "Missing import re in healthcare CDC test"
        print("✅ re import present in healthcare CDC test")
    
    # Test 4: Long string extracted to separate file
    file_path = Path(__file__).parent / "test_cline_fresh_plan_blind_spots.py"
    if file_path.exists():
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check that the long string is not in the test file
        assert '"""' not in content or content.count('"""') <= 2, "Long string not extracted"
        print("✅ Long string extracted to separate file")

if __name__ == "__main__":
    print("🔍 Testing Code Quality Validation")
    print("=" * 50)
    
    test_import_cleanliness()
    test_file_maintainability()
    test_specific_issues_fixed()
    
    print("\n✅ All code quality tests passed!") 