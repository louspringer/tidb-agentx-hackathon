#!/usr/bin/env python3
"""
Deterministic Code Generation Tools
Structured Python models for generating linting-compliant code
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ImportStatement:
    """Structured import statement model"""

    module: str
    items: Optional[list[str]] = None
    alias: Optional[str] = None
    is_from: bool = False

    def to_code(self) -> str:
        """Generate import code"""
        if self.is_from:
            if self.items:
                return f"from {self.module} import {', '.join(self.items)}"
            else:
                return f"from {self.module} import *"
        else:
            if self.alias:
                return f"import {self.module} as {self.alias}"
            else:
                return f"import {self.module}"


@dataclass
class FunctionDefinition:
    """Structured function definition model"""

    name: str
    parameters: list[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    body: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)

    def to_code(self) -> str:
        """Generate function code"""
        lines = []

        # Decorators
        for decorator in self.decorators:
            if decorator == "async":
                # Use async def instead of @asyncio.coroutine
                params = ", ".join(self.parameters)
                signature = f"async def {self.name}({params})"
                if self.return_type:
                    signature += f" -> {self.return_type}"
                signature += ":"
                lines.append(signature)
                break
        else:
            # Regular function
            params = ", ".join(self.parameters)
            signature = f"def {self.name}({params})"
            if self.return_type:
                signature += f" -> {self.return_type}"
            signature += ":"
            lines.append(signature)

            # Add other decorators
            for decorator in self.decorators:
                if decorator != "async":
                    lines.insert(-1, f"@{decorator}")

        # Docstring
        if self.docstring:
            lines.append(f'    """{self.docstring}"""')

        # Body
        for line in self.body:
            lines.append(f"    {line}")

        return "\n".join(lines)


@dataclass
class ClassDefinition:
    """Structured class definition model"""

    name: str
    bases: list[str] = field(default_factory=list)
    docstring: Optional[str] = None
    methods: list[FunctionDefinition] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        pass

    def to_code(self) -> str:
        """Generate class code"""
        lines = []

        # Class signature
        if self.bases:
            bases_str = ", ".join(self.bases)
            lines.append(f"class {self.name}({bases_str}):")
        else:
            lines.append(f"class {self.name}:")

        # Docstring
        if self.docstring:
            lines.append(f'    """{self.docstring}"""')

        # Attributes
        for attr in self.attributes:
            lines.append(f"    {attr}")

        # Methods
        for method in self.methods:
            method_code = method.to_code()
            # Indent method body
            method_lines = method_code.split("\n")
            indented_lines = []
            for line in method_lines:
                if line.strip():
                    indented_lines.append(f"    {line}")
                else:
                    indented_lines.append("")
            lines.append("\n".join(indented_lines))

        return "\n".join(lines)


@dataclass
class CodeFile:
    """Structured code file model"""

    imports: list[ImportStatement] = field(default_factory=list)
    classes: list[ClassDefinition] = field(default_factory=list)
    functions: list[FunctionDefinition] = field(default_factory=list)
    module_docstring: Optional[str] = None
    filename: Optional[str] = None

    def to_code(self) -> str:
        """Generate complete file code"""
        lines = []

        # Module docstring
        if self.module_docstring:
            lines.append(f'"""{self.module_docstring}"""')
            lines.append("")

        # Imports
        for imp in self.imports:
            lines.append(imp.to_code())

        if self.imports:
            lines.append("")

        # Classes
        for cls in self.classes:
            lines.append(cls.to_code())
            lines.append("")

        # Functions
        for func in self.functions:
            lines.append(func.to_code())
            lines.append("")

        # Add main execution block if this is the main module
        if self.filename and "billing_analyzer" in self.filename:
            lines.append("")
            lines.append("if __name__ == '__main__':")
            lines.append("    import asyncio")
            lines.append("    asyncio.run(main())")

        return "\n".join(lines).rstrip() + "\n"


class CodeGenerator:
    """Deterministic code generator using structured models"""

    def __init__(self):
        self.linting_rules = {
            "max_line_length": 88,
            "indent_size": 4,
            "blank_lines_before_class": 2,
            "blank_lines_before_function": 2,
        }

    def validate_import(self, import_stmt: ImportStatement) -> bool:
        """Validate import statement"""
        try:
            # Test if the import is valid Python
            test_code = import_stmt.to_code()
            ast.parse(test_code)
            return True
        except SyntaxError:
            return False

    def validate_function(self, func: FunctionDefinition) -> bool:
        """Validate function definition"""
        try:
            # Test if the function is valid Python
            test_code = func.to_code()
            ast.parse(test_code)
            return True
        except SyntaxError:
            return False

    def validate_class(self, cls: ClassDefinition) -> bool:
        """Validate class definition"""
        try:
            # Test if the class is valid Python
            test_code = cls.to_code()
            ast.parse(test_code)
            return True
        except SyntaxError:
            return False

    def validate_file(self, code_file: CodeFile) -> bool:
        """Validate complete file"""
        try:
            # Test if the file is valid Python
            test_code = code_file.to_code()
            ast.parse(test_code)
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error in generated code: {e}")
            return False

    def generate_test_file(
        self,
        test_name: str,
        test_functions: list[dict[str, Any]],
    ) -> CodeFile:
        """Generate a test file from structured data"""

        # Imports
        imports = [
            ImportStatement("asyncio"),
            ImportStatement("pathlib", ["Path"]),
            ImportStatement(
                "src.gemini_billing_analyzer",
                ["GeminiBillingAnalyzer"],
                is_from=True,
            ),
        ]

        # Test functions
        functions = []
        for test_func in test_functions:
            func = FunctionDefinition(
                name=test_func["name"],
                parameters=test_func.get("parameters", []),
                return_type=test_func.get("return_type", "bool"),
                docstring=test_func.get("docstring", ""),
                body=test_func.get("body", []),
                decorators=test_func.get("decorators", []),
            )
            functions.append(func)

        # Main function
        main_func = FunctionDefinition(
            name="main",
            parameters=[],
            return_type="None",
            docstring="Main test runner",
            body=[
                "print('🧪 Running Gemini Billing Analyzer Tests...')",
                "analyzer = GeminiBillingAnalyzer()",
                'print(f\'🤖 Gemini LLM: {"✅ Available" if analyzer.llm else "❌ Not available"}\')',
                "",
                "# Run tests",
                "for test_func in [test_billing_data_collection, test_gemini_analysis, test_ghostbusters_integration]:",
                "    try:",
                "        result = await test_func(analyzer)",
                '        print(f\'✅ {test_func.__name__}: {"PASS" if result else "FAIL"}\')',
                "    except Exception as e:",
                "        print(f'❌ {test_func.__name__}: {e}')",
                "",
                "print('🎯 Test suite completed!')",
            ],
        )
        functions.append(main_func)

        return CodeFile(
            imports=imports,
            classes=[],
            functions=functions,
            module_docstring=f"Test suite for {test_name}",
            filename=f"test_{test_name}.py",
        )

    def write_file(self, code_file: CodeFile, filepath: Path) -> bool:
        """Write validated code to file"""
        if not self.validate_file(code_file):
            print("❌ Code validation failed")
            return False

        try:
            filepath.write_text(code_file.to_code())
            print(f"✅ Generated: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False


# Example usage
if __name__ == "__main__":
    generator = CodeGenerator()

    # Test data for billing analyzer tests
    test_functions = [
        {
            "name": "test_billing_data_collection",
            "parameters": ["analyzer"],
            "return_type": "bool",
            "docstring": "Test billing data collection",
            "body": [
                "billing_data = analyzer.get_billing_data()",
                "return billing_data is not None and 'project_id' in billing_data",
            ],
            "decorators": ["asyncio.coroutine"],
        },
        {
            "name": "test_gemini_analysis",
            "parameters": ["analyzer"],
            "return_type": "bool",
            "docstring": "Test Gemini analysis",
            "body": [
                "billing_data = analyzer.get_billing_data()",
                "if not billing_data:",
                "    return False",
                "analysis = analyzer.analyze_billing_with_gemini(billing_data)",
                "return 'error' not in analysis",
            ],
            "decorators": ["asyncio.coroutine"],
        },
        {
            "name": "test_ghostbusters_integration",
            "parameters": ["analyzer"],
            "return_type": "bool",
            "docstring": "Test Ghostbusters integration",
            "body": [
                "result = await analyzer.run_ghostbusters_analysis('.')",
                "return 'error' not in result",
            ],
            "decorators": ["asyncio.coroutine"],
        },
    ]

    # Generate test file
    test_file = generator.generate_test_file("billing_api", test_functions)

    # Write to file
    output_path = Path("test_billing_api.py")
    success = generator.write_file(test_file, output_path)

    if success:
        print("🎉 Test file generated successfully!")
    else:
        print("❌ Test file generation failed!")
