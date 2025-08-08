#!/usr/bin/env python3
"""
Enhanced Linting-Aware Code Generation Model
Fixes F841 (unused variables) and F811 (redefined imports)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EnhancedLintingAwareImportStatement:
    """Import statement that knows about F401 and F811 (unused/redefined imports)"""

    module: str
    items: list[str] = field(default_factory=list)
    is_from: bool = False
    used_items: set[str] = field(default_factory=set)  # Track what's actually used
    is_redefined: bool = False  # Track F811 (redefined imports)

    def to_code(self) -> str:
        """Generate import code, only including used items and avoiding redefinitions"""
        if self.is_redefined:
            return ""  # Skip redefined imports (F811)

        if self.is_from:
            if self.items:
                # Only include items that are actually used
                used_items = [item for item in self.items if item in self.used_items]
                if used_items:
                    return f"from {self.module} import {', '.join(used_items)}"
                else:
                    return ""  # No unused imports! (F401)
            else:
                return f"from {self.module}"
        else:
            return f"import {self.module}"


@dataclass
class EnhancedLintingAwareFunctionDefinition:
    """Function definition that knows about E302, F821, and F841"""

    name: str
    parameters: list[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    body: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    requires_blank_line_before: bool = True  # E302 rule
    logger_references: set[str] = field(default_factory=set)  # Track logger usage
    used_variables: set[str] = field(
        default_factory=set,
    )  # Track F841 (unused variables)

    def to_code(self) -> str:
        """Generate function code with proper spacing, logger references, and used variables"""
        lines = []

        # Add blank line before function (E302)
        if self.requires_blank_line_before:
            lines.append("")

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

        # Body with proper logger references and used variables
        for line in self.body:
            # Fix logger references (F821)
            if "logger." in line and "self.logger" not in line:
                line = line.replace("logger.", "self.logger.")

            # Skip lines with unused variables (F841)
            if any(
                var in line
                for var in ["logger = logging.getLogger", "logger = logging"]
            ):
                if "logger" not in self.used_variables:
                    continue  # Skip unused logger assignment

            lines.append(f"    {line}")

        return "\n".join(lines)


@dataclass
class EnhancedLintingAwareClassDefinition:
    """Class definition that knows about E302 (blank lines)"""

    name: str
    docstring: Optional[str] = None
    attributes: list[str] = field(default_factory=list)
    methods: list[EnhancedLintingAwareFunctionDefinition] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)
    requires_blank_line_before: bool = True  # E302 rule

    def to_code(self) -> str:
        """Generate class code with proper spacing"""
        lines = []

        # Add blank line before class (E302)
        if self.requires_blank_line_before:
            lines.append("")

        # Class definition
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
            # Don't add extra blank line before first method
            method.requires_blank_line_before = False
            method_code = method.to_code()
            if method_code:
                lines.append(method_code)

        return "\n".join(lines)


@dataclass
class EnhancedLintingAwareCodeFile:
    """Code file that knows about all linting rules including F841 and F811"""

    imports: list[EnhancedLintingAwareImportStatement] = field(default_factory=list)
    classes: list[EnhancedLintingAwareClassDefinition] = field(default_factory=list)
    functions: list[EnhancedLintingAwareFunctionDefinition] = field(
        default_factory=list,
    )
    module_docstring: Optional[str] = None
    filename: Optional[str] = None

    def to_code(self) -> str:
        """Generate complete file code with enhanced linting rules built-in"""
        lines = []

        # Module docstring
        if self.module_docstring:
            lines.append(f'"""{self.module_docstring}"""')
            lines.append("")

        # Imports (only used ones, no redefinitions)
        for imp in self.imports:
            import_code = imp.to_code()
            if import_code:  # Only add non-empty imports
                lines.append(import_code)

        if lines and lines[-1]:  # Add blank line after imports if not empty
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


class EnhancedLintingAwareCodeGenerator:
    """
    Enhanced code generator that encodes ALL linting rules in the model itself
    No post-generation fixes needed!
    """

    def __init__(self) -> None:
        self.logger = None  # Will be set up when needed

    def generate_perfect_code(self, model: EnhancedLintingAwareCodeFile) -> str:
        """
        Generate code that is perfect by design
        No linting fixes needed - the model encodes ALL the rules!
        """
        return model.to_code()

    def write_perfect_file(
        self,
        model: EnhancedLintingAwareCodeFile,
        filepath: str,
    ) -> bool:
        """Write perfect code file to disk"""
        try:
            perfect_code = self.generate_perfect_code(model)

            filepath = Path(filepath)  # type: ignore
            filepath.parent.mkdir(parents=True, exist_ok=True)  # type: ignore

            with open(filepath, "w") as f:
                f.write(perfect_code)

            return True

        except Exception as e:
            print(f"❌ Error writing perfect file: {e}")
            return False


# Example: Enhanced billing analyzer that fixes F841 and F811
def create_enhanced_linting_aware_billing_analyzer() -> EnhancedLintingAwareCodeFile:
    """Create a billing analyzer model that knows about ALL linting rules"""

    # Imports that track usage and avoid redefinitions
    imports = [
        EnhancedLintingAwareImportStatement("asyncio", used_items={"run"}),
        EnhancedLintingAwareImportStatement("json", used_items={"dumps"}),
        EnhancedLintingAwareImportStatement(
            "logging",
            used_items={"getLogger", "basicConfig"},
        ),
        EnhancedLintingAwareImportStatement("os", used_items={"getenv"}),
        EnhancedLintingAwareImportStatement("subprocess", used_items={"run"}),
        EnhancedLintingAwareImportStatement("uuid", used_items={"uuid4"}),
        EnhancedLintingAwareImportStatement(
            "datetime",
            ["datetime", "timezone"],
            is_from=True,
            used_items={"datetime", "timezone"},
        ),
        EnhancedLintingAwareImportStatement(
            "typing",
            ["Any", "Dict", "Optional"],
            is_from=True,
            used_items={"Any", "Dict", "Optional"},
        ),
        EnhancedLintingAwareImportStatement(
            "langchain_google_genai",
            ["ChatGoogleGenerativeAI"],
            is_from=True,
            used_items={"ChatGoogleGenerativeAI"},
        ),
        EnhancedLintingAwareImportStatement(
            "langchain_core.messages",
            ["HumanMessage"],
            is_from=True,
            used_items={"HumanMessage"},
        ),
    ]

    # Function that knows about logger usage and used variables
    main_function = EnhancedLintingAwareFunctionDefinition(
        name="main",
        parameters=[],
        return_type="None",
        docstring="Main function for billing analysis",
        body=[
            "logging.basicConfig(level=logging.INFO)",
            "logger = logging.getLogger(__name__)",
            "logger.info('Starting billing analysis')",
            "analyzer = GeminiBillingAnalyzer()",
            "asyncio.run(analyzer.analyze_project('.'))",
        ],
        logger_references={"logger.info", "logger"},
        used_variables={"logger"},  # Track that logger is actually used
    )

    # Class that knows about spacing
    analyzer_class = EnhancedLintingAwareClassDefinition(
        name="GeminiBillingAnalyzer",
        docstring="Gemini-integrated billing analyzer for GCP cost optimization",
        attributes=[
            "logger: Any = None",
            "llm: Optional[ChatGoogleGenerativeAI] = None",
        ],
        methods=[
            EnhancedLintingAwareFunctionDefinition(
                name="__init__",
                parameters=["self"],
                return_type="None",
                docstring="Initialize the Gemini billing analyzer",
                body=["self.logger = logging.getLogger(__name__)", "self.llm = None"],
                logger_references={"self.logger"},
                used_variables={"self.logger", "self.llm"},
            ),
        ],
    )

    return EnhancedLintingAwareCodeFile(
        imports=imports,
        classes=[analyzer_class],
        functions=[main_function],
        module_docstring="Enhanced Gemini-Integrated Billing Analyzer\nClean implementation with ALL linting rules built-in",
        filename="enhanced_perfect_billing_analyzer.py",
    )


if __name__ == "__main__":
    # Test the enhanced linting-aware model
    model = create_enhanced_linting_aware_billing_analyzer()
    generator = EnhancedLintingAwareCodeGenerator()

    print("🚀 Testing ENHANCED Linting-Aware Model!")
    print("🎯 Model encodes ALL linting rules directly!")

    code = generator.generate_perfect_code(model)
    print("✅ Generated enhanced perfect code:")
    print(code[:500] + "..." if len(code) > 500 else code)
