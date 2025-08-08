#!/usr/bin/env python3
"""
Recursive Code Generator with AST-Based Decomposition
Based on Python reverse engineering patterns from de4py and Python-Reversal-Bot
"""

import ast
import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

from code_generator import (
    ClassDefinition,
    CodeFile,
    CodeGenerator,
    FunctionDefinition,
    ImportStatement,
)


@dataclass
class DecompositionResult:
    """Result of string decomposition analysis"""

    original_string: str
    decomposed_model: Optional[Any] = None
    confidence: float = 0.0
    decomposition_type: Optional[str] = None
    validation_passed: bool = False
    recursion_depth: int = 0


@dataclass
class StringPattern:
    """Pattern for string decomposition"""

    name: str
    regex_pattern: str
    model_class: type
    confidence_threshold: float = 0.8


class RecursiveCodeGenerator(CodeGenerator):
    """
    Enhanced code generator with recursive AST-based decomposition
    Based on de4py and Python-Reversal-Bot reverse engineering patterns
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.recursion_limit = 3
        self.min_string_length = 10
        self.decomposition_patterns = self._build_patterns()
        self.decomposition_history: list[DecompositionResult] = []

    def _build_patterns(self) -> list[StringPattern]:
        """Build decomposition patterns based on reverse engineering research"""
        return [
            # Import patterns (AST-based, from de4py)
            StringPattern(
                name="import_statement",
                regex_pattern=r"^(from\s+\w+(?:\.\w+)*\s+import\s+[\w\s,]+|import\s+\w+(?:\.\w+)*)$",
                model_class=ImportStatement,
                confidence_threshold=0.95,
            ),
            # Function call patterns (AST-based)
            StringPattern(
                name="function_call",
                regex_pattern=r"^\w+\([^)]*\)$",
                model_class=FunctionDefinition,
                confidence_threshold=0.85,
            ),
            # Class definition patterns (AST-based)
            StringPattern(
                name="class_definition",
                regex_pattern=r"^class\s+\w+(?:\([^)]*\))?:",
                model_class=ClassDefinition,
                confidence_threshold=0.9,
            ),
            # Variable assignment patterns (AST-based)
            StringPattern(
                name="variable_assignment",
                regex_pattern=r"^\w+\s*=\s*[^=]+$",
                model_class=None,  # Will create custom model
                confidence_threshold=0.8,
            ),
            # String literal patterns (Memory analysis, from de4py)
            StringPattern(
                name="string_literal",
                regex_pattern=r'^["\'][^"\']*["\']$',
                model_class=None,  # Will create custom model
                confidence_threshold=0.7,
            ),
        ]

    def decompose_string(
        self,
        string: str,
        depth: int = 0,
    ) -> Optional[DecompositionResult]:
        """
        Recursively decompose strings using established reverse engineering patterns
        Based on de4py AST analysis and Python-Reversal-Bot bytecode patterns
        """
        # Safety limits
        if depth > self.recursion_limit:
            self.logger.debug(f"Recursion limit reached at depth {depth}")
            return None

        if len(string.strip()) < self.min_string_length:
            self.logger.debug(f"String too short: {len(string)} chars")
            return None

        # Try each pattern
        for pattern in self.decomposition_patterns:
            if re.match(pattern.regex_pattern, string.strip()):
                self.logger.info(
                    f"Pattern match: {pattern.name} for string: {string[:50]}...",
                )

                # Attempt decomposition
                try:
                    decomposed_model = self._decompose_with_pattern(string, pattern)
                    if decomposed_model:
                        # Validate decomposition mathematically
                        validation_passed = self._validate_decomposition(
                            string,
                            decomposed_model,
                        )

                        result = DecompositionResult(
                            original_string=string,
                            decomposed_model=decomposed_model,
                            confidence=pattern.confidence_threshold,
                            decomposition_type=pattern.name,
                            validation_passed=validation_passed,
                            recursion_depth=depth,
                        )

                        self.decomposition_history.append(result)
                        self.logger.info(f"✅ Decomposition successful: {pattern.name}")
                        return result

                except Exception as e:
                    self.logger.warning(f"Decomposition failed for {pattern.name}: {e}")
                    continue

        self.logger.debug(f"No pattern matched for string: {string[:50]}...")
        return None

    def _decompose_with_pattern(
        self,
        string: str,
        pattern: StringPattern,
    ) -> Optional[Any]:
        """Decompose string using specific pattern"""
        string = string.strip()

        if pattern.name == "import_statement":
            return self._decompose_import_statement(string)
        if pattern.name == "function_call":
            return self._decompose_function_call(string)
        if pattern.name == "class_definition":
            return self._decompose_class_definition(string)
        if pattern.name == "variable_assignment":
            return self._decompose_variable_assignment(string)
        if pattern.name == "string_literal":
            return self._decompose_string_literal(string)

        return None

    def _decompose_import_statement(self, string: str) -> Optional[ImportStatement]:
        """Decompose import statement using AST analysis (de4py pattern)"""
        try:
            # Parse with AST to validate
            ast.parse(string)

            # Extract components using regex
            if string.startswith("from "):
                # "from typing import Optional, List"
                match = re.match(r"from\s+(\w+(?:\.\w+)*)\s+import\s+(.+)", string)
                if match:
                    module = match.group(1)
                    imports = [imp.strip() for imp in match.group(2).split(",")]
                    return ImportStatement(module=module, imports=imports, is_from=True)
            else:
                # "import typing"
                match = re.match(r"import\s+(\w+(?:\.\w+)*)", string)
                if match:
                    module = match.group(1)
                    return ImportStatement(module=module, imports=[], is_from=False)
        except SyntaxError:
            return None

        return None

    def _decompose_function_call(self, string: str) -> Optional[FunctionDefinition]:
        """Decompose function call using AST analysis"""
        try:
            # Parse with AST to validate
            ast.parse(string)

            # Extract function name and arguments
            match = re.match(r"(\w+)\(([^)]*)\)", string)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)

                # Parse arguments
                args = [arg.strip() for arg in args_str.split(",") if arg.strip()]

                return FunctionDefinition(
                    name=func_name,
                    parameters=args,
                    return_type=None,
                    docstring=None,
                    body=[string],  # Keep original as body
                    decorators=[],
                )
        except SyntaxError:
            return None

        return None

    def _decompose_class_definition(self, string: str) -> Optional[ClassDefinition]:
        """Decompose class definition using AST analysis"""
        try:
            # Parse with AST to validate
            ast.parse(string)

            # Extract class name and inheritance
            match = re.match(r"class\s+(\w+)(?:\(([^)]*)\))?:", string)
            if match:
                class_name = match.group(1)
                inheritance = match.group(2) if match.group(2) else ""

                return ClassDefinition(
                    name=class_name,
                    docstring=f"Decomposed from: {string}",
                    attributes=[],
                    methods=[],
                    inheritance=inheritance.split(",") if inheritance else [],
                )
        except SyntaxError:
            return None

        return None

    def _decompose_variable_assignment(self, string: str) -> Optional[dict[str, Any]]:
        """Decompose variable assignment"""
        try:
            # Parse with AST to validate
            ast.parse(string)

            # Extract variable name and value
            match = re.match(r"(\w+)\s*=\s*(.+)", string)
            if match:
                var_name = match.group(1)
                var_value = match.group(2)

                return {
                    "type": "variable_assignment",
                    "name": var_name,
                    "value": var_value,
                    "original": string,
                }
        except SyntaxError:
            return None

        return None

    def _decompose_string_literal(self, string: str) -> Optional[dict[str, Any]]:
        """Decompose string literal (memory analysis pattern from de4py)"""
        try:
            # Validate it's a proper string literal
            ast.parse(string)

            return {
                "type": "string_literal",
                "value": string.strip("\"'"),
                "quotes": string[0] + string[-1] if len(string) >= 2 else '""',
                "original": string,
            }
        except SyntaxError:
            return None

    def _validate_decomposition(self, original: str, decomposed_model: Any) -> bool:
        """
        Validate decomposition mathematically
        Input == Output validation
        """
        try:
            # Generate code from decomposed model
            if hasattr(decomposed_model, "to_code"):
                generated = decomposed_model.to_code()
            elif isinstance(decomposed_model, dict):
                # Handle custom models
                if decomposed_model.get("type") == "variable_assignment":
                    generated = (
                        f"{decomposed_model['name']} = {decomposed_model['value']}"
                    )
                elif decomposed_model.get("type") == "string_literal":
                    generated = f"{decomposed_model['quotes'][0]}{decomposed_model['value']}{decomposed_model['quotes'][1]}"
                else:
                    generated = str(decomposed_model)
            else:
                generated = str(decomposed_model)

            # Mathematical validation
            validation_passed = original.strip() == generated.strip()

            if not validation_passed:
                self.logger.warning(f"Validation failed: '{original}' != '{generated}'")

            return validation_passed

        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False

    def generate_with_recursion(self, model: CodeFile) -> str:
        """
        Generate code with recursive decomposition
        Enhanced version that analyzes and decomposes generated strings
        """
        # Generate initial code using the model's to_code method
        result = model.to_code()

        self.logger.info("🔍 Starting recursive decomposition analysis...")

        # Extract all strings from the generated code
        strings_to_analyze = self._extract_strings_from_code(result)

        self.logger.info(f"📊 Found {len(strings_to_analyze)} strings to analyze")

        # Analyze each string for decomposition opportunities
        decompositions_found = 0
        for string in strings_to_analyze:
            decomposition = self.decompose_string(string)
            if decomposition and decomposition.validation_passed:
                decompositions_found += 1
                self.logger.info(f"✅ Decomposed: {decomposition.decomposition_type}")

        self.logger.info(
            f"🎯 Recursive decomposition complete: {decompositions_found} decompositions found",
        )

        # Log decomposition history
        self._log_decomposition_summary()

        return result

    def _extract_strings_from_code(self, code: str) -> list[str]:
        """Extract potential strings for decomposition from generated code"""
        strings = []

        # Extract import statements
        import_pattern = (
            r"^(from\s+\w+(?:\.\w+)*\s+import\s+[\w\s,]+|import\s+\w+(?:\.\w+)*)$"
        )
        for line in code.split("\n"):
            line = line.strip()
            if re.match(import_pattern, line):
                strings.append(line)

        # Extract function calls
        func_pattern = r"^\w+\([^)]*\)$"
        for line in code.split("\n"):
            line = line.strip()
            if re.match(func_pattern, line):
                strings.append(line)

        # Extract class definitions
        class_pattern = r"^class\s+\w+(?:\([^)]*\))?:"
        for line in code.split("\n"):
            line = line.strip()
            if re.match(class_pattern, line):
                strings.append(line)

        return strings

    def _log_decomposition_summary(self):
        """Log summary of decomposition analysis"""
        if not self.decomposition_history:
            self.logger.info("📝 No decompositions performed")
            return

        self.logger.info("📊 Decomposition Summary:")
        self.logger.info(f"   Total decompositions: {len(self.decomposition_history)}")

        # Group by type
        by_type = {}
        for result in self.decomposition_history:
            if result.decomposition_type not in by_type:
                by_type[result.decomposition_type] = 0
            by_type[result.decomposition_type] += 1

        for decomp_type, count in by_type.items():
            self.logger.info(f"   {decomp_type}: {count}")

        # Validation stats
        validated = sum(1 for r in self.decomposition_history if r.validation_passed)
        self.logger.info(f"   Validated: {validated}/{len(self.decomposition_history)}")


def main():
    """Test the recursive code generator"""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Testing Recursive Code Generator...")

    # Create recursive generator
    generator = RecursiveCodeGenerator()

    # Test decomposition patterns
    test_strings = [
        "from typing import Optional, List",
        "import os",
        "my_function(arg1, arg2)",
        "class MyClass(BaseClass):",
        "variable = 'value'",
        "'simple string'",
    ]

    print("\n🔍 Testing string decomposition:")
    for test_string in test_strings:
        result = generator.decompose_string(test_string)
        if result:
            print(f"✅ {result.decomposition_type}: {test_string}")
        else:
            print(f"❌ No decomposition: {test_string}")

    print("\n📊 Decomposition Summary:")
    generator._log_decomposition_summary()


if __name__ == "__main__":
    main()
