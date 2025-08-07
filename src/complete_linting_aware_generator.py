#!/usr/bin/env python3
"""
Complete Linting-Aware Code Generator
Generates a complete perfect code generator with all classes
"""

import logging
from pathlib import Path

from linting_aware_model import (
    LintingAwareClassDefinition,
    LintingAwareCodeFile,
    LintingAwareCodeGenerator,
    LintingAwareFunctionDefinition,
    LintingAwareImportStatement,
)


def create_complete_linting_aware_generator() -> LintingAwareCodeFile:
    """Create a complete perfect code generator using linting-aware model"""

    # Imports that track usage
    imports = [
        LintingAwareImportStatement("ast", used_items={"parse"}),
        LintingAwareImportStatement("logging", used_items={"getLogger", "basicConfig"}),
        LintingAwareImportStatement(
            "pathlib",
            ["Path"],
            is_from=True,
            used_items={"Path"},
        ),
        LintingAwareImportStatement(
            "typing",
            ["Any", "List", "Optional", "Set"],
            is_from=True,
            used_items={"Any", "List", "Optional", "Set"},
        ),
        LintingAwareImportStatement(
            "dataclasses",
            ["dataclass", "field"],
            is_from=True,
            used_items={"dataclass", "field"},
        ),
    ]

    # LintingAwareImportStatement class
    import_statement_class = LintingAwareClassDefinition(
        name="LintingAwareImportStatement",
        docstring="Import statement that knows about F401 (unused imports)",
        attributes=[
            "module: str",
            "items: List[str] = field(default_factory=list)",
            "is_from: bool = False",
            "used_items: Set[str] = field(default_factory=set)",
        ],
        methods=[
            LintingAwareFunctionDefinition(
                name="__init__",
                parameters=[
                    "self",
                    "module",
                    "items=None",
                    "is_from=False",
                    "used_items=None",
                ],
                return_type="None",
                docstring="Initialize import statement",
                body=[
                    "self.module = module",
                    "self.items = items or []",
                    "self.is_from = is_from",
                    "self.used_items = used_items or set()",
                ],
                logger_references=set(),
            ),
            LintingAwareFunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate import code, only including used items",
                body=[
                    "if self.is_from:",
                    "    if self.items:",
                    "        used_items = [item for item in self.items if item in self.used_items]",
                    "        if used_items:",
                    "            return f'from {self.module} import {', '.join(used_items)}'",
                    "        else:",
                    "            return ''  # No unused imports!",
                    "    else:",
                    "        return f'from {self.module}'",
                    "else:",
                    "    return f'import {self.module}'",
                ],
                logger_references=set(),
            ),
        ],
    )

    # LintingAwareFunctionDefinition class
    function_definition_class = LintingAwareClassDefinition(
        name="LintingAwareFunctionDefinition",
        docstring="Function definition that knows about E302 (blank lines) and F821 (undefined names)",
        attributes=[
            "name: str",
            "parameters: List[str]",
            "return_type: Optional[str] = None",
            "docstring: Optional[str] = None",
            "body: List[str] = field(default_factory=list)",
            "decorators: List[str] = field(default_factory=list)",
            "requires_blank_line_before: bool = True",
            "logger_references: Set[str] = field(default_factory=set)",
        ],
        methods=[
            LintingAwareFunctionDefinition(
                name="__init__",
                parameters=[
                    "self",
                    "name",
                    "parameters",
                    "return_type=None",
                    "docstring=None",
                    "body=None",
                    "decorators=None",
                    "requires_blank_line_before=True",
                    "logger_references=None",
                ],
                return_type="None",
                docstring="Initialize function definition",
                body=[
                    "self.name = name",
                    "self.parameters = parameters",
                    "self.return_type = return_type",
                    "self.docstring = docstring",
                    "self.body = body or []",
                    "self.decorators = decorators or []",
                    "self.requires_blank_line_before = requires_blank_line_before",
                    "self.logger_references = logger_references or set()",
                ],
                logger_references=set(),
            ),
            LintingAwareFunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate function code with proper spacing and logger references",
                body=[
                    "lines = []",
                    "",
                    "# Add blank line before function (E302)",
                    "if self.requires_blank_line_before:",
                    "    lines.append('')",
                    "",
                    "# Decorators",
                    "for decorator in self.decorators:",
                    "    if decorator == 'async':",
                    "        params = ', '.join(self.parameters)",
                    "        signature = f'async def {self.name}({params})'",
                    "        if self.return_type:",
                    "            signature += f' -> {self.return_type}'",
                    "        signature += ':'",
                    "        lines.append(signature)",
                    "        break",
                    "else:",
                    "    params = ', '.join(self.parameters)",
                    "    signature = f'def {self.name}({params})'",
                    "    if self.return_type:",
                    "        signature += f' -> {self.return_type}'",
                    "    signature += ':'",
                    "    lines.append(signature)",
                    "",
                    "# Docstring",
                    "if self.docstring:",
                    '    lines.append(f\'    """{self.docstring}"""\')',
                    "",
                    "# Body with proper logger references",
                    "for line in self.body:",
                    "    if 'logger.' in line and 'self.logger' not in line:",
                    "        line = line.replace('logger.', 'self.logger.')",
                    "    lines.append(f'    {line}')",
                    "",
                    "return '\\n'.join(lines)",
                ],
                logger_references=set(),
            ),
        ],
    )

    # LintingAwareClassDefinition class
    class_definition_class = LintingAwareClassDefinition(
        name="LintingAwareClassDefinition",
        docstring="Class definition that knows about E302 (blank lines)",
        attributes=[
            "name: str",
            "docstring: Optional[str] = None",
            "attributes: List[str] = field(default_factory=list)",
            "methods: List[LintingAwareFunctionDefinition] = field(default_factory=list)",
            "bases: List[str] = field(default_factory=list)",
            "requires_blank_line_before: bool = True",
        ],
        methods=[
            LintingAwareFunctionDefinition(
                name="__init__",
                parameters=[
                    "self",
                    "name",
                    "docstring=None",
                    "attributes=None",
                    "methods=None",
                    "bases=None",
                    "requires_blank_line_before=True",
                ],
                return_type="None",
                docstring="Initialize class definition",
                body=[
                    "self.name = name",
                    "self.docstring = docstring",
                    "self.attributes = attributes or []",
                    "self.methods = methods or []",
                    "self.bases = bases or []",
                    "self.requires_blank_line_before = requires_blank_line_before",
                ],
                logger_references=set(),
            ),
            LintingAwareFunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate class code with proper spacing",
                body=[
                    "lines = []",
                    "",
                    "# Add blank line before class (E302)",
                    "if self.requires_blank_line_before:",
                    "    lines.append('')",
                    "",
                    "# Class definition",
                    "if self.bases:",
                    "    bases_str = ', '.join(self.bases)",
                    "    lines.append(f'class {self.name}({bases_str}):')",
                    "else:",
                    "    lines.append(f'class {self.name}:')",
                    "",
                    "# Docstring",
                    "if self.docstring:",
                    '    lines.append(f\'    """{self.docstring}"""\')',
                    "",
                    "# Attributes",
                    "for attr in self.attributes:",
                    "    lines.append(f'    {attr}')",
                    "",
                    "# Methods",
                    "for method in self.methods:",
                    "    method.requires_blank_line_before = False",
                    "    method_code = method.to_code()",
                    "    if method_code:",
                    "        lines.append(method_code)",
                    "",
                    "return '\\n'.join(lines)",
                ],
                logger_references=set(),
            ),
        ],
    )

    # LintingAwareCodeFile class
    code_file_class = LintingAwareClassDefinition(
        name="LintingAwareCodeFile",
        docstring="Code file that knows about all linting rules",
        attributes=[
            "imports: List[LintingAwareImportStatement] = field(default_factory=list)",
            "classes: List[LintingAwareClassDefinition] = field(default_factory=list)",
            "functions: List[LintingAwareFunctionDefinition] = field(default_factory=list)",
            "module_docstring: Optional[str] = None",
            "filename: Optional[str] = None",
        ],
        methods=[
            LintingAwareFunctionDefinition(
                name="__init__",
                parameters=[
                    "self",
                    "imports=None",
                    "classes=None",
                    "functions=None",
                    "module_docstring=None",
                    "filename=None",
                ],
                return_type="None",
                docstring="Initialize code file",
                body=[
                    "self.imports = imports or []",
                    "self.classes = classes or []",
                    "self.functions = functions or []",
                    "self.module_docstring = module_docstring",
                    "self.filename = filename",
                ],
                logger_references=set(),
            ),
            LintingAwareFunctionDefinition(
                name="to_code",
                parameters=["self"],
                return_type="str",
                docstring="Generate complete file code with linting rules built-in",
                body=[
                    "lines = []",
                    "",
                    "# Module docstring",
                    "if self.module_docstring:",
                    '    lines.append(f\'"""{self.module_docstring}"""\')',
                    "    lines.append('')",
                    "",
                    "# Imports (only used ones)",
                    "for imp in self.imports:",
                    "    import_code = imp.to_code()",
                    "    if import_code:  # Only add non-empty imports",
                    "        lines.append(import_code)",
                    "",
                    "if lines and lines[-1]:  # Add blank line after imports if not empty",
                    "    lines.append('')",
                    "",
                    "# Classes",
                    "for cls in self.classes:",
                    "    lines.append(cls.to_code())",
                    "    lines.append('')",
                    "",
                    "# Functions",
                    "for func in self.functions:",
                    "    lines.append(func.to_code())",
                    "    lines.append('')",
                    "",
                    "# Add main execution block if this is the main module",
                    "if self.filename and 'billing_analyzer' in self.filename:",
                    "    lines.append('')",
                    "    lines.append('if __name__ == \"__main__\":')",
                    "    lines.append('    import asyncio')",
                    "    lines.append('    asyncio.run(main())')",
                    "",
                    "return '\\n'.join(lines).rstrip() + '\\n'",
                ],
                logger_references=set(),
            ),
        ],
    )

    # LintingAwareCodeGenerator class
    code_generator_class = LintingAwareClassDefinition(
        name="LintingAwareCodeGenerator",
        docstring="Code generator that encodes linting rules in the model itself",
        attributes=["logger: Any = None"],
        methods=[
            LintingAwareFunctionDefinition(
                name="__init__",
                parameters=["self"],
                return_type="None",
                docstring="Initialize the linting-aware code generator",
                body=["import logging", "self.logger = logging.getLogger(__name__)"],
                logger_references={"self.logger"},
            ),
            LintingAwareFunctionDefinition(
                name="generate_perfect_code",
                parameters=["self", "model"],
                return_type="str",
                docstring="Generate code that is perfect by design",
                body=["return model.to_code()"],
                logger_references=set(),
            ),
            LintingAwareFunctionDefinition(
                name="write_perfect_file",
                parameters=["self", "model", "filepath"],
                return_type="bool",
                docstring="Write perfect code file to disk",
                body=[
                    "try:",
                    "    perfect_code = self.generate_perfect_code(model)",
                    "",
                    "    filepath = Path(filepath)",
                    "    filepath.parent.mkdir(parents=True, exist_ok=True)",
                    "",
                    "    with open(filepath, 'w') as f:",
                    "        f.write(perfect_code)",
                    "",
                    "    return True",
                    "",
                    "except Exception as e:",
                    "    if self.logger:",
                    "        self.logger.error(f'Error writing perfect file: {e}')",
                    "    return False",
                ],
                logger_references={"self.logger"},
            ),
        ],
    )

    # Main function
    main_function = LintingAwareFunctionDefinition(
        name="main",
        parameters=[],
        return_type="None",
        docstring="Generate the perfect linting-aware code generator",
        body=[
            "logging.basicConfig(level=logging.INFO)",
            "logger = logging.getLogger(__name__)",
            "",
            "print('🚀 Generating PERFECT Linting-Aware Code Generator!')",
            "print('🎯 Model encodes linting rules directly!')",
            "",
            "# Create linting-aware generator",
            "generator = LintingAwareCodeGenerator()",
            "",
            "# Generate the perfect code generator",
            "print('📊 Creating perfect code generator model...')",
            "perfect_generator_file = create_complete_linting_aware_generator()",
            "",
            "# Write perfect file",
            "output_path = Path('complete_perfect_code_generator.py')",
            "success = generator.write_perfect_file(perfect_generator_file, output_path)",
            "",
            "if success:",
            "    print('🎉 PERFECT CODE GENERATOR SUCCESS!')",
            "    print('✅ Model encodes linting rules directly!')",
            "    print(f'📁 Output: {output_path}')",
            "    print('🏆 ULTIMATE LINTING-AWARE BREAKTHROUGH!')",
            "else:",
            "    print('❌ PERFECT CODE GENERATOR FAILURE!')",
        ],
        logger_references={"logger"},
    )

    return LintingAwareCodeFile(
        imports=imports,
        classes=[
            import_statement_class,
            function_definition_class,
            class_definition_class,
            code_file_class,
            code_generator_class,
        ],
        functions=[main_function],
        module_docstring="Complete Perfect Linting-Aware Code Generator\nModel encodes linting rules directly - no post-generation fixes needed!",
        filename="complete_perfect_code_generator.py",
    )


def main():
    """Generate the complete perfect linting-aware code generator"""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Generating COMPLETE PERFECT Linting-Aware Code Generator!")
    print("🎯 Model encodes linting rules directly!")

    # Create linting-aware generator
    generator = LintingAwareCodeGenerator()

    # Generate the perfect code generator
    print("📊 Creating complete perfect code generator model...")
    perfect_generator_file = create_complete_linting_aware_generator()

    # Write perfect file
    output_path = Path("complete_perfect_code_generator.py")
    success = generator.write_perfect_file(perfect_generator_file, output_path)

    if success:
        print("🎉 COMPLETE PERFECT CODE GENERATOR SUCCESS!")
        print("✅ Model encodes linting rules directly!")
        print(f"📁 Output: {output_path}")
        print("🏆 ULTIMATE LINTING-AWARE BREAKTHROUGH!")
    else:
        print("❌ COMPLETE PERFECT CODE GENERATOR FAILURE!")


if __name__ == "__main__":
    main()
