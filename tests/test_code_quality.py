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


            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            for imp in imports:
                if imp in seen:
                    issues.append(f"Duplicate import: {imp}")
                seen.add(imp)

            for pattern, required_import in patterns:
                if re.search(pattern, content):
                    # Check if the import is present
                    if required_import not in content:
                        issues.append(f"Missing import: {required_import}")

