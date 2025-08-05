#!/usr/bin/env python3
"""
Comprehensive Code Quality Tests
Tests that will catch the issues Copilot is finding
"""

import ast
import re
import sys
from pathlib import Path

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):

            for imp in imports:
                if imp in seen:
                    duplicates.append(imp)
                else:
                    seen.add(imp)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    usages.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Handle attribute access like 're.search'

                for issue in file_issues:
                    print(f"   - {issue}")
                total_issues += len(file_issues)
            else:
                print("✅ No issues found")

        if total_issues == 0:
            print("🎉 All test files pass code quality validation!")
            return True
        else:
            print("⚠️  Code quality issues need to be addressed")
            return False


