#!/usr/bin/env python3
"""
AST-Based Usage Tracker
Analyzes generated code to find what's actually used vs. what's imported
"""

import ast
from dataclasses import dataclass, field


@dataclass
class UsageAnalysis:
    """Results of AST usage analysis"""

    used_names: set[str] = field(default_factory=set)
    used_attributes: set[str] = field(default_factory=set)
    used_modules: set[str] = field(default_factory=set)
    used_functions: set[str] = field(default_factory=set)
    used_classes: set[str] = field(default_factory=set)
    unused_imports: set[str] = field(default_factory=set)
    unused_variables: set[str] = field(default_factory=set)


class ASTUsageTracker:
    """
    AST-based usage tracker that analyzes Python code to find actual usage
    """

    def __init__(self):
        self.analysis = UsageAnalysis()

    def analyze_code(self, code: str) -> UsageAnalysis:
        """
        Analyze code using AST to find what's actually used
        """
        try:
            tree = ast.parse(code)
            self.analysis = UsageAnalysis()
            self._visit_node(tree)
            return self.analysis
        except SyntaxError as e:
            print(f"❌ Syntax error in code: {e}")
            return UsageAnalysis()

    def _visit_node(self, node: ast.AST) -> None:
        """Recursively visit AST nodes to extract usage"""

        if isinstance(node, ast.Name):
            # Track variable/function names
            self.analysis.used_names.add(node.id)

        elif isinstance(node, ast.Attribute):
            # Track attribute access (e.g., logging.getLogger)
            if isinstance(node.value, ast.Name):
                self.analysis.used_names.add(node.value.id)
            self.analysis.used_attributes.add(node.attr)

        elif isinstance(node, ast.Import):
            # Track module imports
            for alias in node.names:
                self.analysis.used_modules.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            # Track from imports
            if node.module:
                self.analysis.used_modules.add(node.module)
            for alias in node.names:
                self.analysis.used_names.add(alias.name)

        elif isinstance(node, ast.FunctionDef):
            # Track function definitions
            self.analysis.used_functions.add(node.name)

        elif isinstance(node, ast.ClassDef):
            # Track class definitions
            self.analysis.used_classes.add(node.name)

        elif isinstance(node, ast.Call):
            # Track function calls
            if isinstance(node.func, ast.Name):
                self.analysis.used_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    self.analysis.used_names.add(node.func.value.id)
                self.analysis.used_attributes.add(node.func.attr)

        # Recursively visit child nodes
        for child in ast.iter_child_nodes(node):
            self._visit_node(child)

    def find_unused_imports(self, imports: list[str], used_names: set[str]) -> set[str]:
        """Find imports that are not actually used"""
        unused = set()
        for imp in imports:
            # Extract the imported name from the import statement
            if " as " in imp:
                imported_name = imp.split(" as ")[1].strip()
            elif "from " in imp and " import " in imp:
                imported_name = imp.split(" import ")[1].strip()
            else:
                imported_name = imp.replace("import ", "").strip()

            if imported_name not in used_names:
                unused.add(imp)

        return unused

    def find_unused_variables(
        self,
        assignments: list[str],
        used_names: set[str],
    ) -> set[str]:
        """Find variables that are assigned but not used"""
        unused = set()
        for assignment in assignments:
            # Extract variable name from assignment
            var_name = assignment.split("=")[0].strip()
            if var_name not in used_names:
                unused.add(var_name)

        return unused


class ASTBasedCodeGenerator:
    """
    Code generator that uses AST analysis to ensure only used imports/variables are included
    """

    def __init__(self):
        self.tracker = ASTUsageTracker()

    def generate_perfect_code(self, initial_code: str) -> str:
        """
        Generate perfect code by analyzing usage and removing unused elements
        """
        # Phase 1: Analyze the initial code
        analysis = self.tracker.analyze_code(initial_code)

        # Phase 2: Remove unused imports
        lines = initial_code.split("\n")
        filtered_lines = []

        for line in lines:
            # Skip unused import lines
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                if not self._is_import_used(line, analysis):
                    continue
            filtered_lines.append(line)

        # Phase 3: Remove unused variable assignments
        final_lines = []
        for line in filtered_lines:
            # Skip unused variable assignments
            if " = " in line and not line.strip().startswith("#"):
                var_name = line.split(" = ")[0].strip()
                if var_name not in analysis.used_names:
                    continue
            final_lines.append(line)

        return "\n".join(final_lines)

    def _is_import_used(self, import_line: str, analysis: UsageAnalysis) -> bool:
        """Check if an import line is actually used"""
        if " as " in import_line:
            imported_name = import_line.split(" as ")[1].strip()
        elif "from " in import_line and " import " in import_line:
            imported_name = import_line.split(" import ")[1].strip()
        else:
            imported_name = import_line.replace("import ", "").strip()

        return imported_name in analysis.used_names


# Test the AST usage tracker
def test_ast_usage_tracker():
    """Test the AST usage tracker with sample code"""

    sample_code = """
import asyncio
import logging
import json
import os
import subprocess
from typing import Any, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Starting analysis')
    result = "done"
    return result

if __name__ == '__main__':
    asyncio.run(main())
"""

    print("🧪 Testing AST Usage Tracker!")

    # Test analysis
    tracker = ASTUsageTracker()
    analysis = tracker.analyze_code(sample_code)

    print("📊 Usage Analysis Results:")
    print(f"Used names: {analysis.used_names}")
    print(f"Used attributes: {analysis.used_attributes}")
    print(f"Used modules: {analysis.used_modules}")
    print(f"Used functions: {analysis.used_functions}")

    # Test perfect code generation
    generator = ASTBasedCodeGenerator()
    perfect_code = generator.generate_perfect_code(sample_code)

    print("\n✅ Generated Perfect Code:")
    print(perfect_code)

    return analysis, perfect_code


if __name__ == "__main__":
    test_ast_usage_tracker()
