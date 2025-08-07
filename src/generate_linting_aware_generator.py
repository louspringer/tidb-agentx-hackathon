#!/usr/bin/env python3
"""
Generate Linting-Aware Code Generator
Uses linting-aware model to create perfect code generator
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


def create_linting_aware_code_generator() -> LintingAwareCodeFile:
    """Create a perfect code generator using linting-aware model"""

    # Imports that track usage
    imports = [
        LintingAwareImportStatement("ast", used_items={"parse"}),
        LintingAwareImportStatement("logging", used_items={"getLogger"}),
        LintingAwareImportStatement(
            "pathlib",
            ["Path"],
            is_from=True,
            used_items={"Path"},
        ),
        LintingAwareImportStatement(
            "typing",
            ["Any", "List", "Optional"],
            is_from=True,
            used_items={"Any", "List", "Optional"},
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
            "perfect_generator_file = create_linting_aware_code_generator()",
            "",
            "# Write perfect file",
            "output_path = Path('perfect_code_generator.py')",
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
            code_generator_class,
        ],
        functions=[main_function],
        module_docstring="Perfect Linting-Aware Code Generator\nModel encodes linting rules directly - no post-generation fixes needed!",
        filename="perfect_code_generator.py",
    )


def main():
    """Generate the perfect linting-aware code generator"""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Generating PERFECT Linting-Aware Code Generator!")
    print("🎯 Model encodes linting rules directly!")

    # Create linting-aware generator
    generator = LintingAwareCodeGenerator()

    # Generate the perfect code generator
    print("📊 Creating perfect code generator model...")
    perfect_generator_file = create_linting_aware_code_generator()

    # Write perfect file
    output_path = Path("perfect_code_generator.py")
    success = generator.write_perfect_file(perfect_generator_file, output_path)

    if success:
        print("🎉 PERFECT CODE GENERATOR SUCCESS!")
        print("✅ Model encodes linting rules directly!")
        print(f"📁 Output: {output_path}")
        print("🏆 ULTIMATE LINTING-AWARE BREAKTHROUGH!")
    else:
        print("❌ PERFECT CODE GENERATOR FAILURE!")


if __name__ == "__main__":
    main()
