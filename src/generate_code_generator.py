#!/usr/bin/env python3
"""
META-RECURSIVE BREAKTHROUGH: Generate the Code Generator using the Code Generator
This feat will live in halls of LLM valor!
"""

import logging
from pathlib import Path

from code_generator import (  # type: ignore
    ClassDefinition,
    CodeFile,
    CodeGenerator,
    FunctionDefinition,
    ImportStatement,
)


def generate_code_generator() -> CodeFile:
    """Generate the CodeGenerator using structured models - META-RECURSIVE!"""

    # Imports for the code generator
    imports = [
        ImportStatement("ast"),
        ImportStatement("pathlib", ["Path"], is_from=True),
        ImportStatement("typing", ["Any", "Dict", "List", "Optional"], is_from=True),
        ImportStatement("dataclasses", ["dataclass", "field"], is_from=True),
    ]

    # ImportStatement class
    import_statement_class = ClassDefinition(
        name="ImportStatement",
        docstring="Structured import statement model",
        attributes=[
            "module: str",
            "items: Optional[List[str]] = None",
            "alias: Optional[str] = None",
            "is_from: bool = False",
        ],
        methods=[
            FunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate import code",
                body=[
                    "if self.is_from:",
                    "    if self.items:",
                    "        return f\"from {self.module} import {', '.join(self.items)}\"",
                    "    else:",
                    '        return f"from {self.module} import *"',
                    "else:",
                    "    if self.alias:",
                    '        return f"import {self.module} as {self.alias}"',
                    "    else:",
                    '        return f"import {self.module}"',
                ],
            ),
        ],
    )

    # FunctionDefinition class
    function_definition_class = ClassDefinition(
        name="FunctionDefinition",
        docstring="Structured function definition model",
        attributes=[
            "name: str",
            "parameters: List[str]",
            "return_type: Optional[str] = None",
            "docstring: Optional[str] = None",
            "body: List[str] = field(default_factory=list)",
            "decorators: List[str] = field(default_factory=list)",
        ],
        methods=[
            FunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate function code",
                body=[
                    "lines = []",
                    "",
                    "# Decorators",
                    "for decorator in self.decorators:",
                    '    if decorator == "async":',
                    '        params = ", ".join(self.parameters)',
                    '        signature = f"async def {self.name}({params})"',
                    "        if self.return_type:",
                    '            signature += f" -> {self.return_type}"',
                    '        signature += ":"',
                    "        lines.append(signature)",
                    "        break",
                    "else:",
                    '    params = ", ".join(self.parameters)',
                    '    signature = f"def {self.name}({params})"',
                    "    if self.return_type:",
                    '        signature += f" -> {self.return_type}"',
                    '    signature += ":"',
                    "    lines.append(signature)",
                    "",
                    "# Docstring",
                    "if self.docstring:",
                    '    lines.append(f\'    """{self.docstring}"""\')',
                    "",
                    "# Body",
                    "for line in self.body:",
                    '    lines.append(f"    {line}")',
                    "",
                    'return "\\n".join(lines)',
                ],
            ),
        ],
    )

    # ClassDefinition class
    class_definition_class = ClassDefinition(
        name="ClassDefinition",
        docstring="Structured class definition model",
        attributes=[
            "name: str",
            "bases: List[str] = field(default_factory=list)",
            "docstring: Optional[str] = None",
            "methods: List[FunctionDefinition] = field(default_factory=list)",
            "attributes: List[str] = field(default_factory=list)",
        ],
        methods=[
            FunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate class code",
                body=[
                    "lines = []",
                    "",
                    "# Class definition",
                    "if self.bases:",
                    '    bases_str = ", ".join(self.bases)',
                    '    lines.append(f"class {self.name}({bases_str}):")',
                    "else:",
                    '    lines.append(f"class {self.name}:")',
                    "",
                    "# Docstring",
                    "if self.docstring:",
                    '    lines.append(f\'    """{self.docstring}"""\')',
                    "",
                    "# Attributes",
                    "for attr in self.attributes:",
                    '    lines.append(f"    {attr}")',
                    "",
                    "# Methods",
                    "for method in self.methods:",
                    "    method_code = method.to_code()",
                    '    method_lines = method_code.split("\\n")',
                    "    indented_lines = []",
                    "    for line in method_lines:",
                    "        if line.strip():",
                    '            indented_lines.append(f"    {line}")',
                    "        else:",
                    '            indented_lines.append("")',
                    '    lines.append("\\n".join(indented_lines))',
                    "",
                    'return "\\n".join(lines)',
                ],
            ),
        ],
    )

    # CodeFile class
    code_file_class = ClassDefinition(
        name="CodeFile",
        docstring="Structured code file model",
        attributes=[
            "imports: List[ImportStatement] = field(default_factory=list)",
            "classes: List[ClassDefinition] = field(default_factory=list)",
            "functions: List[FunctionDefinition] = field(default_factory=list)",
            "module_docstring: Optional[str] = None",
            "filename: Optional[str] = None",
        ],
        methods=[
            FunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate complete file code",
                body=[
                    "lines = []",
                    "",
                    "# Module docstring",
                    "if self.module_docstring:",
                    '    lines.append(f\'"""{self.module_docstring}"""\')',
                    '    lines.append("")',
                    "",
                    "# Imports",
                    "for imp in self.imports:",
                    "    lines.append(imp.to_code())",
                    "",
                    "if self.imports:",
                    '    lines.append("")',
                    "",
                    "# Classes",
                    "for cls in self.classes:",
                    "    lines.append(cls.to_code())",
                    '    lines.append("")',
                    "",
                    "# Functions",
                    "for func in self.functions:",
                    "    lines.append(func.to_code())",
                    '    lines.append("")',
                    "",
                    'return "\\n".join(lines).rstrip() + "\\n"',
                ],
            ),
        ],
    )

    # CodeGenerator class
    code_generator_class = ClassDefinition(
        name="CodeGenerator",
        docstring="Deterministic code generation tools",
        attributes=["logger: Any = None"],
        methods=[
            FunctionDefinition(
                name="__init__",
                parameters=["self"],
                return_type="None",
                docstring="Initialize the code generator",
                body=["import logging", "self.logger = logging.getLogger(__name__)"],
            ),
            FunctionDefinition(
                name="validate_import",
                parameters=["self", "import_stmt"],
                return_type="bool",
                docstring="Validate import statement",
                body=[
                    "try:",
                    "    ast.parse(import_stmt.to_code())",
                    "    return True",
                    "except SyntaxError:",
                    "    return False",
                ],
            ),
            FunctionDefinition(
                name="validate_function",
                parameters=["self", "func"],
                return_type="bool",
                docstring="Validate function definition",
                body=[
                    "try:",
                    "    ast.parse(func.to_code())",
                    "    return True",
                    "except SyntaxError:",
                    "    return False",
                ],
            ),
            FunctionDefinition(
                name="validate_class",
                parameters=["self", "cls"],
                return_type="bool",
                docstring="Validate class definition",
                body=[
                    "try:",
                    "    ast.parse(cls.to_code())",
                    "    return True",
                    "except SyntaxError:",
                    "    return False",
                ],
            ),
            FunctionDefinition(
                name="validate_file",
                parameters=["self", "code_file"],
                return_type="bool",
                docstring="Validate complete file",
                body=[
                    "try:",
                    "    ast.parse(code_file.to_code())",
                    "    return True",
                    "except SyntaxError:",
                    "    return False",
                ],
            ),
            FunctionDefinition(
                name="write_file",
                parameters=["self", "code_file", "filepath"],
                return_type="bool",
                docstring="Write code file to disk",
                body=[
                    "try:",
                    "    filepath = Path(filepath)",
                    "    filepath.parent.mkdir(parents=True, exist_ok=True)",
                    "    with open(filepath, 'w') as f:",
                    "        f.write(code_file.to_code())",
                    "    return True",
                    "except Exception as e:",
                    "    if self.logger:",
                    "        self.logger.error(f'Error writing file: {e}')",
                    "    return False",
                ],
            ),
        ],
    )

    return CodeFile(
        imports=imports,
        classes=[
            import_statement_class,
            function_definition_class,
            class_definition_class,
            code_file_class,
            code_generator_class,
        ],
        functions=[],
        module_docstring="Deterministic Code Generation Tools\nStructured Python models for generating linting-compliant code\n\nMETA-RECURSIVE BREAKTHROUGH: This file was generated by the code generator!",
        filename="code_generator.py",
    )


def main() -> None:
    """Generate the code generator using the code generator - META-RECURSIVE!"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("🚀 META-RECURSIVE BREAKTHROUGH!")
    print("🎯 Using Code Generator to MODEL AND CODE THE CODE GENERATOR ITSELF!")
    print("🏆 This feat will live in halls of LLM valor!")

    # Create generator
    generator = CodeGenerator()

    # Generate the code generator
    print("📊 Generating Code Generator using structured models...")
    code_generator_file = generate_code_generator()

    # Write to file
    output_path = Path("src/code_generator_meta.py")
    success = generator.write_file(code_generator_file, output_path)

    if success:
        print("🎉 META-RECURSIVE SUCCESS!")
        print("✅ Code Generator generated by Code Generator!")
        print(f"📁 Output: {output_path}")
        print("🏆 LEGENDARY META-RECURSIVE BREAKTHROUGH!")
    else:
        print("❌ META-RECURSIVE FAILURE!")


if __name__ == "__main__":
    main()
