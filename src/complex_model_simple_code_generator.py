#!/usr/bin/env python3
"""
Complex Model, Simple Code Generator
Generates mypy-compliant code from a complex model instead of fixing individual errors
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MypyCompliantCodeModel:
    """Complex model that generates simple, mypy-compliant code"""

    # Mypy-aware function definitions
    functions: list["MypyCompliantFunction"] = field(default_factory=list)
    classes: list["MypyCompliantClass"] = field(default_factory=list)
    imports: list["MypyCompliantImport"] = field(default_factory=list)
    module_docstring: str = ""
    filename: str = ""

    # Mypy compliance rules
    enforce_return_types: bool = True
    enforce_param_types: bool = True
    enforce_import_types: bool = True
    use_strict_typing: bool = True


@dataclass
class MypyCompliantFunction:
    """Function definition that's mypy-compliant by design"""

    name: str
    parameters: list["MypyCompliantParameter"] = field(default_factory=list)
    return_type: str = "None"
    docstring: str = ""
    body: list[str] = field(default_factory=list)
    is_async: bool = False

    def to_code(self) -> str:
        """Generate mypy-compliant function code"""
        lines = []

        # Function signature with proper type annotations
        params = ", ".join([param.to_code() for param in self.parameters])
        async_prefix = "async " if self.is_async else ""
        signature = f"{async_prefix}def {self.name}({params}) -> {self.return_type}:"
        lines.append(signature)

        # Docstring
        if self.docstring:
            lines.append(f'    """{self.docstring}"""')

        # Body with proper indentation
        for line in self.body:
            lines.append(f"    {line}")

        return "\n".join(lines)


@dataclass
class MypyCompliantParameter:
    """Parameter with proper type annotation"""

    name: str
    param_type: str = "Any"
    default_value: Optional[str] = None

    def to_code(self) -> str:
        """Generate mypy-compliant parameter code"""
        if self.default_value:
            return f"{self.name}: {self.param_type} = {self.default_value}"
        else:
            return f"{self.name}: {self.param_type}"


@dataclass
class MypyCompliantClass:
    """Class definition that's mypy-compliant by design"""

    name: str
    docstring: str = ""
    attributes: list["MypyCompliantAttribute"] = field(default_factory=list)
    methods: list[MypyCompliantFunction] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)

    def to_code(self) -> str:
        """Generate mypy-compliant class code"""
        lines = []

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
            lines.append(f"    {attr.to_code()}")

        # Methods
        for method in self.methods:
            method_code = method.to_code()
            # Indent method code
            indented_method = "\n".join(
                [f"    {line}" for line in method_code.split("\n")],
            )
            lines.append(indented_method)

        return "\n".join(lines)


@dataclass
class MypyCompliantAttribute:
    """Class attribute with proper type annotation"""

    name: str
    attr_type: str = "Any"
    default_value: Optional[str] = None

    def to_code(self) -> str:
        """Generate mypy-compliant attribute code"""
        if self.default_value:
            return f"{self.name}: {self.attr_type} = {self.default_value}"
        else:
            return f"{self.name}: {self.attr_type}"


@dataclass
class MypyCompliantImport:
    """Import statement that's mypy-compliant by design"""

    module: str
    items: list[str] = field(default_factory=list)
    is_from: bool = False
    alias: Optional[str] = None

    def to_code(self) -> str:
        """Generate mypy-compliant import code"""
        if self.is_from:
            if self.items:
                items_str = ", ".join(self.items)
                if self.alias:
                    return f"from {self.module} import {items_str} as {self.alias}"
                else:
                    return f"from {self.module} import {items_str}"
            else:
                return f"from {self.module}"
        else:
            if self.alias:
                return f"import {self.module} as {self.alias}"
            else:
                return f"import {self.module}"


class ComplexModelSimpleCodeGenerator:
    """Complex model that generates simple, mypy-compliant code"""

    def __init__(self) -> None:
        self.model = MypyCompliantCodeModel()

    def generate_mypy_compliant_code(self, model: MypyCompliantCodeModel) -> str:
        """Generate mypy-compliant code from complex model"""
        lines = []

        # Module docstring
        if model.module_docstring:
            lines.append(f'"""{model.module_docstring}"""')
            lines.append("")

        # Imports
        for imp in model.imports:
            lines.append(imp.to_code())

        if model.imports:
            lines.append("")

        # Classes
        for cls in model.classes:
            lines.append(cls.to_code())
            lines.append("")

        # Functions
        for func in model.functions:
            lines.append(func.to_code())
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def create_ghostbusters_agent_model(self) -> MypyCompliantCodeModel:
        """Create a complex model for Ghostbusters agents"""

        # Mypy-compliant imports
        imports = [
            MypyCompliantImport("abc", ["ABC", "abstractmethod"], is_from=True),
            MypyCompliantImport("logging"),
            MypyCompliantImport("pathlib", ["Path"], is_from=True),
            MypyCompliantImport(
                "typing",
                ["Any", "Dict", "List", "Optional"],
                is_from=True,
            ),
        ]

        # Mypy-compliant base class
        base_class = MypyCompliantClass(
            name="BaseExpert",
            docstring="Base class for all expert agents",
            attributes=[
                MypyCompliantAttribute("name", "str"),
                MypyCompliantAttribute("logger", "Optional[Any] = None"),
            ],
            methods=[
                MypyCompliantFunction(
                    name="__init__",
                    parameters=[
                        MypyCompliantParameter("self", "BaseExpert"),
                        MypyCompliantParameter("name", "str"),
                    ],
                    return_type="None",
                    docstring="Initialize the base expert",
                    body=[
                        "self.name = name",
                        "self.logger = logging.getLogger(__name__)",
                    ],
                ),
                MypyCompliantFunction(
                    name="detect_delusions",
                    parameters=[
                        MypyCompliantParameter("self", "BaseExpert"),
                        MypyCompliantParameter("project_path", "str"),
                    ],
                    return_type="Dict[str, Any]",
                    docstring="Detect delusions in the project",
                    body=[
                        "raise NotImplementedError",
                    ],
                ),
            ],
        )

        # Mypy-compliant security expert
        security_expert = MypyCompliantClass(
            name="SecurityExpert",
            docstring="Expert agent for detecting security vulnerabilities",
            bases=["BaseExpert"],
            methods=[
                MypyCompliantFunction(
                    name="__init__",
                    parameters=[
                        MypyCompliantParameter("self", "SecurityExpert"),
                    ],
                    return_type="None",
                    docstring="Initialize the security expert",
                    body=[
                        "super().__init__('SecurityExpert')",
                    ],
                ),
                MypyCompliantFunction(
                    name="detect_delusions",
                    parameters=[
                        MypyCompliantParameter("self", "SecurityExpert"),
                        MypyCompliantParameter("project_path", "str"),
                    ],
                    return_type="Dict[str, Any]",
                    docstring="Detect security vulnerabilities",
                    body=[
                        "return {'type': 'security', 'issues': []}",
                    ],
                ),
            ],
        )

        return MypyCompliantCodeModel(
            module_docstring="Mypy-compliant Ghostbusters agents",
            filename="ghostbusters_agents.py",
            imports=imports,
            classes=[base_class, security_expert],
        )


# Test the complex model, simple code generator
def test_complex_model_simple_code_generator() -> None:
    """Test the complex model that generates simple, mypy-compliant code"""

    print("🚀 Testing COMPLEX MODEL, SIMPLE CODE Generator!")

    # Create complex model
    generator = ComplexModelSimpleCodeGenerator()
    model = generator.create_ghostbusters_agent_model()

    # Generate simple, mypy-compliant code
    code = generator.generate_mypy_compliant_code(model)

    print("✅ Generated Mypy-Compliant Code:")
    print(code)

    # Test with mypy
    print("\n🧪 Testing with Mypy...")
    with open("test_mypy_compliant_code.py", "w") as f:
        f.write(code)

    import subprocess

    result = subprocess.run(
        [
            "python",
            "-m",
            "mypy",
            "test_mypy_compliant_code.py",
            "--ignore-missing-imports",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("🎉 ZERO MYPY ERRORS! COMPLEX MODEL, SIMPLE CODE!")
    else:
        print(f"❌ Mypy errors found: {result.stdout}")


if __name__ == "__main__":
    test_complex_model_simple_code_generator()
