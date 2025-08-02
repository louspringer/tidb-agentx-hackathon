#!/usr/bin/env python3
"""
Tests for MDC Generator
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mdc_generator import MDCFile, MDCFrontmatter, MDCGenerator

class TestMDCFrontmatter:
    """Test MDC frontmatter functionality"""
    
    def test_frontmatter_creation(self):
        """Test creating frontmatter"""
        frontmatter = MDCFrontmatter(
            description="Test rule",
            globs=["**/*.py"],
            always_apply=True
        )
        
        assert frontmatter.description == "Test rule"
        assert frontmatter.globs == ["**/*.py"]
        assert frontmatter.always_apply is True
    
    def test_frontmatter_to_yaml(self):
        """Test frontmatter to YAML conversion"""
        frontmatter = MDCFrontmatter(
            description="Test rule",
            globs=["**/*.py", "**/*.md"],
            always_apply=True
        )
        
        yaml_content = frontmatter.to_yaml()
        parsed = yaml.safe_load(yaml_content)
        
        assert parsed["description"] == "Test rule"
        assert parsed["globs"] == ["**/*.py", "**/*.md"]
        assert parsed["alwaysApply"] is True

class TestMDCFile:
    """Test MDC file functionality"""
    
    def test_mdc_file_creation(self):
        """Test creating MDC file"""
        frontmatter = MDCFrontmatter(
            description="Test rule",
            globs=["**/*.py"],
            always_apply=True
        )
        
        content = "# Test Rule\n\nThis is a test rule."
        
        mdc_file = MDCFile(
            frontmatter=frontmatter,
            content=content
        )
        
        assert mdc_file.frontmatter.description == "Test rule"
        assert mdc_file.content == "# Test Rule\n\nThis is a test rule."
    
    def test_mdc_file_to_content(self):
        """Test MDC file to content conversion"""
        frontmatter = MDCFrontmatter(
            description="Test rule",
            globs=["**/*.py"],
            always_apply=True
        )
        
        content = "# Test Rule\n\nThis is a test rule."
        
        mdc_file = MDCFile(
            frontmatter=frontmatter,
            content=content
        )
        
        mdc_content = mdc_file.to_mdc_content()
        
        # Check that it starts with YAML frontmatter
        assert mdc_content.startswith("---\n")
        assert "description: Test rule" in mdc_content
        assert "globs:" in mdc_content
        assert "alwaysApply: true" in mdc_content
        
        # Check that it ends with the content
        assert mdc_content.endswith("\n\n# Test Rule\n\nThis is a test rule.")
    
    def test_mdc_file_from_file(self):
        """Test loading MDC file from disk"""
        # Create a temporary .mdc file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mdc', delete=False) as f:
            f.write("""---
description: Test rule
globs: ["**/*.py"]
alwaysApply: true
---

# Test Rule

This is a test rule.""")
            temp_file = Path(f.name)
        
        try:
            mdc_file = MDCFile.from_file(temp_file)
            
            assert mdc_file.frontmatter.description == "Test rule"
            assert mdc_file.frontmatter.globs == ["**/*.py"]
            assert mdc_file.frontmatter.always_apply is True
            assert "# Test Rule" in mdc_file.content
            assert "This is a test rule." in mdc_file.content
            
        finally:
            temp_file.unlink()
    
    def test_mdc_file_create_rule(self):
        """Test creating MDC rule"""
        mdc_file = MDCFile.create_rule(
            description="Test rule",
            globs=["**/*.py"],
            content="# Test Rule\n\nThis is a test rule.",
            always_apply=True
        )
        
        assert mdc_file.frontmatter.description == "Test rule"
        assert mdc_file.frontmatter.globs == ["**/*.py"]
        assert mdc_file.frontmatter.always_apply is True
        assert "# Test Rule" in mdc_file.content

class TestMDCGenerator:
    """Test MDC generator functionality"""
    
    def test_generator_creation(self):
        """Test creating generator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = MDCGenerator(Path(temp_dir))
            assert generator.base_dir == Path(temp_dir)
            assert generator.rules_dir == Path(temp_dir) / ".cursor" / "rules"
    
    def test_generate_all_rules(self):
        """Test generating all rules"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = MDCGenerator(Path(temp_dir))
            generator.generate_all_rules()
            
            # Check that rules were generated
            rules_dir = Path(temp_dir) / ".cursor" / "rules"
            assert rules_dir.exists()
            
            # Check for specific rules
            expected_rules = ["deterministic-editing.mdc", "security.mdc", "yaml-type-specific.mdc"]
            for rule in expected_rules:
                rule_file = rules_dir / rule
                assert rule_file.exists(), f"Rule {rule} was not generated"
    
    def test_validate_mdc_file(self):
        """Test validating MDC file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = MDCGenerator(Path(temp_dir))
            
            # Create a valid .mdc file
            valid_content = """---
description: Test rule
globs: ["**/*.py"]
alwaysApply: true
---

# Test Rule

This is a test rule."""
            
            mdc_file = Path(temp_dir) / "test.mdc"
            with open(mdc_file, 'w') as f:
                f.write(valid_content)
            
            # Test validation
            assert generator.validate_mdc_file(mdc_file) is True
    
    def test_validate_invalid_mdc_file(self):
        """Test validating invalid MDC file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = MDCGenerator(Path(temp_dir))
            
            # Create an invalid .mdc file (no frontmatter)
            invalid_content = """# Test Rule

This is an invalid rule."""
            
            mdc_file = Path(temp_dir) / "test.mdc"
            with open(mdc_file, 'w') as f:
                f.write(invalid_content)
            
            # Test validation
            assert generator.validate_mdc_file(mdc_file) is False

def test_integration():
    """Integration test for MDC generator"""
    with tempfile.TemporaryDirectory() as temp_dir:
        generator = MDCGenerator(Path(temp_dir))
        
        # Generate rules
        generator.generate_all_rules()
        
        # Validate all generated files
        results = generator.validate_all_mdc_files()
        
        # All generated files should be valid
        assert all(results.values()), "All generated files should be valid"
        
        # Should have generated files
        assert len(results) > 0, "Should have generated some files"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 