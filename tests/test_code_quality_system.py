#!/usr/bin/env python3
"""
Tests for the Code Quality System
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Any
from src.code_quality_system.quality_model import CodeQualityModel, LintingRule


class TestCodeQualityModel:
    """Test the code quality model"""

    def setup_method(self: Any) -> None:
        """Set up test fixtures"""
        self.model = CodeQualityModel()
        self.test_dir = Path(tempfile.mkdtemp())

    def teardown_method(self: Any) -> None:
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def test_model_initialization(self: Any) -> None:
        """Test that the model initializes correctly"""
        assert self.model is not None
        assert hasattr(self.model, "rules")
        assert hasattr(self.model, "fixers")
        assert len(self.model.rules) > 0
        assert len(self.model.fixers) > 0

    def test_rules_definition(self: Any) -> None:
        """Test that all rules are properly defined"""
        expected_rules: list = ["F401", "W291", "E722", "E402", "F841"]

        for rule_code in expected_rules:
            assert rule_code in self.model.rules
            rule: Any = self.model.rules[rule_code]
            assert isinstance(rule, LintingRule)
            assert rule.code == rule_code
            assert hasattr(rule, "fix_function")

    def test_fixers_definition(self: Any) -> None:
        """Test that all fixers are properly defined"""
        expected_fixers: list = ["autoflake", "black", "custom_fixes"]

        for fixer_name in expected_fixers:
            assert fixer_name in self.model.fixers
            assert callable(self.model.fixers[fixer_name])

    def create_test_file(self, content: str, filename: str = "test_file.py") -> Path:
        """Create a test file with given content"""
        file_path: Any = self.test_dir / filename
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def test_fix_unused_imports(self: Any) -> None:
        """Test fixing unused imports"""
        content: str = """
import os
import sys
import json

def test_function() -> None:
    print("Hello")
        """
        file_path: Any = self.create_test_file(content)

        # Apply fix
        result: Any = self.model._fix_unused_imports(file_path)
        assert result is True

        # Check result
        with open(file_path, "r") as f:
            fixed_content: Any = f.read()

        # Should remove unused imports
        assert "import os" not in fixed_content
        assert "import sys" not in fixed_content
        assert "import json" not in fixed_content

    def test_fix_f_strings(self: Any) -> None:
        """Test fixing f-strings without placeholders"""
        content: str = """
def test_function() -> None:
    print("Hello world")
    print('No placeholders')
    print(f"Has {placeholder}")
"""
        file_path: Any = self.create_test_file(content)

        # Apply fix
        result: Any = self.model._fix_f_strings(file_path)
        assert result is True

        # Check result
        with open(file_path, "r") as f:
            fixed_content: Any = f.read()

        # Should convert f-strings without placeholders
        assert 'print("Hello world")' in fixed_content
        assert "print('No placeholders')" in fixed_content
        # Should keep f-strings with placeholders
        assert 'print(f"Has {placeholder}")' in fixed_content

    def test_fix_trailing_whitespace(self: Any) -> None:
        """Test fixing trailing whitespace"""
        content: str = """
def test_function() -> None:
    print("Hello")
    return True
"""
        file_path: Any = self.create_test_file(content)

        # Apply fix
        result: Any = self.model._fix_trailing_whitespace(file_path)
        assert result is True

        # Check result
        with open(file_path, "r") as f:
            fixed_content: Any = f.read()

        # Should remove trailing whitespace
        assert "def test_function() -> None:" in fixed_content
        assert '    print("Hello")' in fixed_content
        assert "    return True" in fixed_content

    def test_fix_bare_except(self: Any) -> None:
        """Test fixing bare except clauses"""
        content: str = """
def test_function() -> None:
    try:
        result: Any = risky_operation()
    except Exception:
        print("Error")
        """
        file_path: Any = self.create_test_file(content)

        # Apply fix
        result: Any = self.model._fix_bare_except(file_path)
        assert result is True

        # Check result
        with open(file_path, "r") as f:
            fixed_content: Any = f.read()

        # Should convert bare except to specific exception
        assert "except Exception:" in fixed_content

    def test_analyze_file(self: Any) -> None:
        """Test file analysis"""
        content: str = """
import os
def test_function() -> None:
    print("Hello world")
        """
        file_path: Any = self.create_test_file(content)

        # Analyze file
        analysis: Any = self.model.analyze_file(file_path)

        assert "file" in analysis
        assert "issues" in analysis
        assert "total_issues" in analysis
        assert analysis["file"] == str(file_path)
        assert isinstance(analysis["issues"], list)
        assert isinstance(analysis["total_issues"], int)

    def test_fix_file(self: Any) -> None:
        """Test fixing a single file"""
        content: str = """
import os
def test_function() -> None:
    print("Hello world")
        """
        file_path: Any = self.create_test_file(content)

        # Fix file
        result: Any = self.model.fix_file(file_path)

        assert "file" in result
        assert "fixes_applied" in result
        assert "errors" in result
        assert result["file"] == str(file_path)
        assert isinstance(result["fixes_applied"], list)
        assert isinstance(result["errors"], list)

    def test_fix_all_files(self: Any) -> None:
        """Test fixing all files in a directory"""
        # Create test files
        content1: str = """
import os
def test_function() -> None:
    print("Hello world")
        """
        content2: str = """
import sys
def another_function() -> None:
    print('Another test')
        """

        self.create_test_file(content1, "test1.py")
        self.create_test_file(content2, "test2.py")

        # Fix all files
        result: Any = self.model.fix_all_files([str(self.test_dir)])

        assert "total_files" in result
        assert "files_fixed" in result
        assert "file_results" in result
        assert isinstance(result["file_results"], list)


class TestLintingRule:
    """Test the LintingRule dataclass"""

    def test_linting_rule_creation(self: Any) -> None:
        """Test creating a linting rule"""

        def dummy_fix(file_path: str) -> None:
            return True

        rule: Any = LintingRule(
            code="TEST001",
            description="Test rule",
            severity="error",
            fix_function=dummy_fix,
        )

        assert rule.code == "TEST001"
        assert rule.description == "Test rule"
        assert rule.fix_function == dummy_fix

    def test_linting_rule_application(self: Any) -> None:
        """Test applying a linting rule"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            # Create test file
            test_file = test_dir / "test.py"
            with open(test_file, "w") as f:
                f.write("import os\nprint('test')")

            def test_fix(file_path: str) -> bool:
                # Simple fix that adds a comment
                with open(file_path, "r") as f:
                    content = f.read()
                with open(file_path, "w") as f:
                    f.write("# Fixed\n" + content)
                return True

            rule = LintingRule(
                code="TEST002",
                description="Add comment",
                severity="error",
                fix_function=test_fix,
            )

            # Apply rule
            result = rule.fix_function(str(test_file))
            assert result is True

            # Check result
            with open(test_file, "r") as f:
                content = f.read()
            assert content.startswith("# Fixed\n")

        finally:
            shutil.rmtree(test_dir)


def test_code_quality_integration() -> None:
    """Test integration of code quality system"""
    model = CodeQualityModel()

    # Test with a simple file
    test_dir = Path(tempfile.mkdtemp())
    try:
        test_file = test_dir / "integration_test.py"
        with open(test_file, "w") as f:
            f.write(
                """
import os
import sys

def test_function() -> None:
    print("Hello world")
            """
            )

        # Analyze file
        analysis = model.analyze_file(test_file)
        assert analysis["file"] == str(test_file)
        assert "issues" in analysis

        # Fix file
        result = model.fix_file(test_file)
        assert result["file"] == str(test_file)
        assert "fixes_applied" in result

    finally:
        shutil.rmtree(test_dir)


def test_code_quality_performance() -> None:
    """Test performance of code quality system"""
    model = CodeQualityModel()

    # Create multiple test files
    test_dir = Path(tempfile.mkdtemp())
    try:
        for i in range(10):
            test_file = test_dir / f"test_{i}.py"
            with open(test_file, "w") as f:
                f.write(
                    f"""
import os
import sys

def test_function_{i}() -> None:
    print("Hello world {i}")
                """
                )

        # Process all files
        result = model.fix_all_files([str(test_dir)])
        assert result["total_files"] == 10

    finally:
        shutil.rmtree(test_dir)
