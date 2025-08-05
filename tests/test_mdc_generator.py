#!/usr/bin/env python3
"""
Tests for MDC Generator
"""


import pytest
import tempfile
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mdc_generator import MDCFile, MDCFrontmatter, MDCGenerator


        assert parsed["description"] == "Test rule"
        assert parsed["globs"] == ["**/*.py", "**/*.md"]
        assert parsed["alwaysApply"] is True


        # Check that it starts with YAML frontmatter
        assert mdc_content.startswith("---\n")
        assert "description: Test rule" in mdc_content
        assert "globs:" in mdc_content
        assert "alwaysApply: true" in mdc_content

description: Test rule
globs: ["**/*.py"]
alwaysApply: true
---

# Test Rule

This is a test rule."""

