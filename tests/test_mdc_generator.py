#!/usr/bin/env python3
"""
Tests for MDC Generator
"""

import sys
import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mdc_generator import MDCFile, MDCFrontmatter, MDCGenerator


class TestMDCFrontmatter:
    """Test MDC frontmatter functionality"""

    def test_frontmatter_creation(self: Any) -> None:
        """Test creating frontmatter"""
        frontmatter: Any = MDCFrontmatter(
            description="Test rule", globs=["**/*.py"], always_apply=True
        )

        assert frontmatter.description == "Test rule"
        assert frontmatter.globs == ["**/*.py"]
        assert frontmatter.always_apply is True

    def test_frontmatter_to_yaml(self: Any) -> None:
        """Test frontmatter to YAML conversion"""
        frontmatter: Any = MDCFrontmatter(
            description="Test rule", globs=["**/*.py", "**/*.md"], always_apply=True
        )

        yaml_content: Any = frontmatter.to_yaml()
        parsed: Any = yaml.safe_load(yaml_content)

        assert parsed["description"] == "Test rule"
        assert parsed["globs"] == ["**/*.py", "**/*.md"]
        assert parsed["alwaysApply"] is True


class TestMDCFile:
    """Test MDC file functionality"""

    def test_mdc_file_creation(self: Any) -> None:
        """Test creating MDC file"""
        frontmatter: Any = MDCFrontmatter(
            description="Test rule", globs=["**/*.py"], always_apply=True
        )

        content: str = "# Test Rule\n\nThis is a test rule."

        mdc_file: Any = MDCFile(frontmatter=frontmatter, content=content)

        assert mdc_file.frontmatter.description == "Test rule"
        assert mdc_file.content == "# Test Rule\n\nThis is a test rule."

    def test_mdc_file_to_content(self: Any) -> None:
        """Test MDC file to content conversion"""
        frontmatter: Any = MDCFrontmatter(
            description="Test rule", globs=["**/*.py"], always_apply=True
        )

        content: str = "# Test Rule\n\nThis is a test rule."

        mdc_file: Any = MDCFile(frontmatter=frontmatter, content=content)

        mdc_content: Any = mdc_file.to_mdc_content()

        # Check that it starts with YAML frontmatter
        assert mdc_content.startswith("---\n")
        assert "description: Test rule" in mdc_content
        assert "globs:" in mdc_content
        assert "alwaysApply: true" in mdc_content

        # Check that it ends with the content
        assert mdc_content.endswith("\n\n# Test Rule\n\nThis is a test rule.")

    def test_mdc_file_from_file(self: Any) -> None:
        """Test loading MDC file from disk"""
        # Create a temporary .mdc file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdc", delete=False) as f:
            f.write(
                """---
description: Test rule
globs: ["**/*.py"]
alwaysApply: true
---

# Test Rule

This is a test rule."""
            )
        temp_file: Any = Path(f.name)

        try:
            mdc_file: Any = MDCFile.from_file(temp_file)

            assert mdc_file.frontmatter.description == "Test rule"
            assert mdc_file.frontmatter.globs == ["**/*.py"]
            assert mdc_file.frontmatter.always_apply is True
            assert "# Test Rule" in mdc_file.content
        finally:
            temp_file.unlink()

    def test_mdc_file_create_rule(self: Any) -> None:
        """Test creating a rule from MDC file"""
        frontmatter: Any = MDCFrontmatter(
            description="Test rule", globs=["**/*.py"], always_apply=True
        )

        content: str = "# Test Rule\n\nThis is a test rule."

        rule: Any = MDCFile.create_rule(
            description="Test rule",
            globs=["**/*.py"],
            content="# Test Rule\n\nThis is a test rule.",
        )

        assert rule.frontmatter.description == "Test rule"
        assert rule.frontmatter.globs == ["**/*.py"]
        assert rule.frontmatter.always_apply is True


class TestMDCGenerator:
    """Test MDC generator functionality"""

    def test_generator_creation(self: Any) -> None:
        """Test creating generator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator: Any = MDCGenerator(Path(temp_dir))
            assert generator.base_dir == Path(temp_dir)
            assert generator.rules_dir == Path(temp_dir) / ".cursor" / "rules"

    def test_generate_all_rules(self: Any) -> None:
        """Test generating all rules"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator: Any = MDCGenerator(Path(temp_dir))
            generator.generate_all_rules()

            # Check that rules were generated
            rules_dir: Any = Path(temp_dir) / ".cursor" / "rules"
            assert rules_dir.exists()
            assert rules_dir.is_dir()

            # Check that some .mdc files were created
            mdc_files: Any = list(rules_dir.glob("*.mdc"))
            assert len(mdc_files) > 0

    def test_validate_mdc_file(self: Any) -> None:
        """Test validating a valid MDC file"""
        frontmatter: Any = MDCFrontmatter(
            description="Test rule", globs=["**/*.py"], always_apply=True
        )

        content: str = "# Test Rule\n\nThis is a test rule."

        mdc_file: Any = MDCFile(frontmatter=frontmatter, content=content)

        # Should not raise any exceptions
        mdc_file.validate()

    def test_validate_invalid_mdc_file(self: Any) -> None:
        """Test validating an invalid MDC file"""
        # Create an invalid frontmatter (missing required fields)
        frontmatter: Any = MDCFrontmatter(description="", globs=[], always_apply=False)

        content: str = "# Test Rule\n\nThis is a test rule."

        mdc_file: Any = MDCFile(frontmatter=frontmatter, content=content)

        # Should raise validation error
        with pytest.raises(ValueError):
            mdc_file.validate()


def test_integration() -> None:
    """Test full integration workflow"""
    with tempfile.TemporaryDirectory() as temp_dir:
        generator: Any = MDCGenerator(Path(temp_dir))

        # Generate rules
        generator.generate_all_rules()

        # Validate generated rules
        rules_dir: Any = Path(temp_dir) / ".cursor" / "rules"
        for mdc_file in rules_dir.glob("*.mdc"):
            mdc: Any = MDCFile.from_file(mdc_file)
            mdc.validate()


def test_mdc_generator_static_type_checking() -> None:
    """Test that MDC generator components have proper type annotations"""
    # Test MDCFrontmatter
    frontmatter: MDCFrontmatter = MDCFrontmatter(
        description="Test", globs=["**/*.py"], always_apply=True
    )
    assert isinstance(frontmatter.description, str)
    assert isinstance(frontmatter.globs, list)
    assert isinstance(frontmatter.always_apply, bool)

    # Test MDCFile
    content: str = "# Test\n\nContent"
    mdc_file: MDCFile = MDCFile(frontmatter=frontmatter, content=content)
    assert isinstance(mdc_file.frontmatter, MDCFrontmatter)
    assert isinstance(mdc_file.content, str)

    # Test MDCGenerator
    with tempfile.TemporaryDirectory() as temp_dir:
        generator: MDCGenerator = MDCGenerator(Path(temp_dir))
        assert isinstance(generator.base_dir, Path)
        assert isinstance(generator.rules_dir, Path)
