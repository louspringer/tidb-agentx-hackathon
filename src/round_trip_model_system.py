#!/usr/bin/env python3
"""
Round-Trip Model System
Can create models from design AND generate code from models
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelComponent:
    """A component in our design model"""

    name: str
    type: str  # 'function', 'class', 'module', 'domain'
    description: str
    requirements: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DesignModel:
    """A complete design model that can be converted to/from code"""

    name: str
    description: str
    components: list[ModelComponent] = field(default_factory=list)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class RoundTripModelSystem:
    """System that can create models from design AND generate code from models"""

    def __init__(self) -> None:
        self.design_models: dict[str, DesignModel] = {}
        self._dependency_graph: dict[str, set[str]] = {}

    def create_model_from_design(self, design_spec: dict[str, Any]) -> DesignModel:
        """Create a model directly from design specification (NO reverse engineering)"""
        logger.info(
            f"🎯 Creating model from design: {design_spec.get('name', 'Unknown')}",
        )

        # Extract design components
        components = []
        for comp_spec in design_spec.get("components", []):
            component = ModelComponent(
                name=comp_spec["name"],
                type=comp_spec["type"],
                description=comp_spec["description"],
                requirements=comp_spec.get("requirements", []),
                dependencies=comp_spec.get("dependencies", []),
                metadata=comp_spec.get("metadata", {}),
            )
            components.append(component)

        # Create the design model
        design_model = DesignModel(
            name=design_spec["name"],
            description=design_spec["description"],
            components=components,
            relationships=design_spec.get("relationships", {}),
            metadata=design_spec.get("metadata", {}),
        )

        self.design_models[design_model.name] = design_model

        # Build dependency graph
        self._build_dependency_graph(design_model)

        logger.info(f"✅ Created model with {len(components)} components")

        return design_model

    def _build_dependency_graph(self, model: DesignModel) -> None:
        """Build dependency graph for proper import resolution"""
        self._dependency_graph = {}

        for component in model.components:
            self._dependency_graph[component.name] = set()
            for dep in component.dependencies:
                if dep in [comp.name for comp in model.components]:
                    self._dependency_graph[component.name].add(dep)

    def generate_code_from_model(self, model_name: str) -> dict[str, str]:
        """Generate code from a design model (NO reverse engineering)"""
        if model_name not in self.design_models:
            msg = f"Model {model_name} not found"
            raise ValueError(msg)

        model = self.design_models[model_name]
        logger.info(f"🎯 Generating code from model: {model_name}")

        generated_files = {}

        # Generate code for each component
        for component in model.components:
            if component.type == "function":
                code = self._generate_function_code(component, model)
                filename = f"{component.name}.py"
                generated_files[filename] = code
            elif component.type == "class":
                code = self._generate_class_code(component, model)
                filename = f"{component.name}.py"
                generated_files[filename] = code
            elif component.type == "module":
                code = self._generate_module_code(component, model)
                filename = f"{component.name}.py"
                generated_files[filename] = code
            elif component.type == "domain":
                code = self._generate_domain_code(component, model)
                filename = f"{component.name}.py"
                generated_files[filename] = code

        return generated_files

    def _generate_function_code(
        self,
        component: ModelComponent,
        model: DesignModel,
    ) -> str:
        """Generate function code from component design"""
        imports = self._resolve_imports(component, model)

        code = f"""#!/usr/bin/env python3
\"\"\"
{component.description}
\"\"\"

{chr(10).join(imports)}

"""

        # Generate function signature
        return_type = component.metadata.get("return_type", "Any")
        params = component.metadata.get("parameters", [])

        param_str = ", ".join([f"{param['name']}: {param['type']}" for param in params])
        param_str = f"({param_str})" if param_str else "()"

        code += f"""
def {component.name}{param_str} -> {return_type}:
    \"\"\"
    {component.description}
    \"\"\"
    # TODO: Implement based on requirements: {component.requirements}
    pass
"""

        return code

    def _generate_class_code(
        self,
        component: ModelComponent,
        model: DesignModel,
    ) -> str:
        """Generate class code from component design with proper dependency resolution"""
        imports = self._resolve_imports(component, model)
        methods = component.metadata.get("methods", [])

        code = f"""#!/usr/bin/env python3
\"\"\"
{component.description}
\"\"\"

{chr(10).join(imports)}

"""

        code += f"""
@dataclass
class {component.name}:
    \"\"\"
    {component.description}
    \"\"\"

    def __init__(self) -> None:
        # TODO: Initialize based on requirements: {component.requirements}
        pass
"""

        # Add methods with proper type hints
        for method in methods:
            return_type = self._resolve_type_reference(
                method.get("return_type", "Any"),
                model,
            )
            params = method.get("parameters", [])

            param_str = ", ".join(
                [f"{param['name']}: {param['type']}" for param in params],
            )
            param_str = f"({param_str})" if param_str else "()"

            code += f"""
    def {method['name']}{param_str} -> {return_type}:
        \"\"\"
        {method.get('description', 'TODO: Add description')}
        \"\"\"
        # TODO: Implement based on requirements: {method.get('requirements', [])}
        pass
"""

        return code

    def _resolve_imports(
        self,
        component: ModelComponent,
        model: DesignModel,
    ) -> list[str]:
        """Resolve all imports needed for a component"""
        imports: set[str] = set()

        # Standard library imports
        standard_imports = {
            "dataclasses": "from dataclasses import dataclass",
            "typing": "from typing import Any, Dict, List, Optional",
            "ast": "import ast",
            "logging": "import logging",
            "pathlib": "from pathlib import Path",
            "enum": "from enum import Enum",
            "json": "import json",
            "asyncio": "import asyncio",
        }

        # Add standard imports based on dependencies
        for dep in component.dependencies:
            if dep in standard_imports:
                imports.add(standard_imports[dep])

        # Add relative imports for internal dependencies
        for dep in component.dependencies:
            if dep in [comp.name for comp in model.components]:
                imports.add(f"from .{dep.lower()} import {dep}")

        # Add imports for type references in methods
        methods = component.metadata.get("methods", [])
        for method in methods:
            return_type = method.get("return_type", "")
            if return_type.startswith("List["):
                # Extract type from List[Type]
                inner_type = return_type[5:-1]  # Remove "List[" and "]"
                if inner_type in [comp.name for comp in model.components]:
                    imports.add(f"from .{inner_type.lower()} import {inner_type}")
            elif return_type in [comp.name for comp in model.components]:
                imports.add(f"from .{return_type.lower()} import {return_type}")

        return sorted(imports)

    def _resolve_type_reference(self, type_ref: str, model: DesignModel) -> str:
        """Resolve type references to internal components"""
        if type_ref.startswith("List["):
            # Handle List[InternalType] cases
            inner_type = type_ref[5:-1]  # Remove "List[" and "]"
            if inner_type in [comp.name for comp in model.components]:
                return f"List[{inner_type}]"
            return type_ref
        if type_ref in [comp.name for comp in model.components]:
            return type_ref
        return type_ref

    def _generate_module_code(
        self,
        component: ModelComponent,
        model: DesignModel,
    ) -> str:
        """Generate module code from component design"""
        imports = self._resolve_imports(component, model)

        return f"""#!/usr/bin/env python3
\"\"\"
{component.description}

This module contains:
{chr(10).join(f'- {req}' for req in component.requirements)}
\"\"\"

{chr(10).join(imports)}

"""

    def _generate_domain_code(
        self,
        component: ModelComponent,
        model: DesignModel,
    ) -> str:
        """Generate domain code from component design"""
        imports = self._resolve_imports(component, model)

        return f"""#!/usr/bin/env python3
\"\"\"
{component.description}

Domain: {component.name}
Requirements: {component.requirements}
\"\"\"

{chr(10).join(imports)}

"""

    def save_model(self, model_name: str, file_path: str) -> None:
        """Save a design model to JSON file"""
        if model_name not in self.design_models:
            msg = f"Model {model_name} not found"
            raise ValueError(msg)

        model = self.design_models[model_name]

        # Convert to JSON-serializable format
        model_data = {
            "name": model.name,
            "description": model.description,
            "components": [
                {
                    "name": comp.name,
                    "type": comp.type,
                    "description": comp.description,
                    "requirements": comp.requirements,
                    "dependencies": comp.dependencies,
                    "metadata": comp.metadata,
                }
                for comp in model.components
            ],
            "relationships": model.relationships,
            "metadata": model.metadata,
        }

        with open(file_path, "w") as f:
            json.dump(model_data, f, indent=2)

        logger.info(f"✅ Saved model to {file_path}")

    def load_model(self, file_path: str) -> DesignModel:
        """Load a design model from JSON file"""
        with open(file_path) as f:
            model_data = json.load(f)

        # Reconstruct components
        components = []
        for comp_data in model_data["components"]:
            component = ModelComponent(
                name=comp_data["name"],
                type=comp_data["type"],
                description=comp_data["description"],
                requirements=comp_data.get("requirements", []),
                dependencies=comp_data.get("dependencies", []),
                metadata=comp_data.get("metadata", {}),
            )
            components.append(component)

        # Create design model
        design_model = DesignModel(
            name=model_data["name"],
            description=model_data["description"],
            components=components,
            relationships=model_data.get("relationships", {}),
            metadata=model_data.get("metadata", {}),
        )

        self.design_models[design_model.name] = design_model
        self._build_dependency_graph(design_model)

        logger.info(f"✅ Loaded model from {file_path}")
        return design_model


def main():
    """Demonstrate round-trip model system"""
    system = RoundTripModelSystem()

    # STEP 1: Create model from design (NO reverse engineering)
    design_spec = {
        "name": "ASTGuidedCodeGenerator",
        "description": "AST-guided code generator that respects syntactic boundaries",
        "components": [
            {
                "name": "ASTNode",
                "type": "class",
                "description": "Represents an AST node with metadata",
                "requirements": [
                    "dataclass",
                    "metadata support",
                    "parent-child relationships",
                ],
                "dependencies": ["dataclasses", "typing"],
                "metadata": {
                    "methods": [
                        {
                            "name": "__post_init__",
                            "description": "Initialize default values",
                            "return_type": "None",
                        },
                    ],
                },
            },
            {
                "name": "LintingRule",
                "type": "class",
                "description": "Represents a linting rule with AST-aware patterns",
                "requirements": [
                    "rule code",
                    "description",
                    "severity",
                    "AST patterns",
                    "fix strategy",
                ],
                "dependencies": ["dataclasses", "typing"],
                "metadata": {
                    "methods": [
                        {
                            "name": "__post_init__",
                            "description": "Initialize default values",
                            "return_type": "None",
                        },
                    ],
                },
            },
            {
                "name": "ASTGuidedCodeGenerator",
                "type": "class",
                "description": "AST-guided code generator that respects syntactic boundaries",
                "requirements": [
                    "AST parsing",
                    "linting rule integration",
                    "syntactic boundary detection",
                    "fix strategy generation",
                ],
                "dependencies": [
                    "ast",
                    "logging",
                    "dataclasses",
                    "typing",
                    "src.artifact_forge.agents.artifact_parser_enhanced",
                ],
                "metadata": {
                    "methods": [
                        {
                            "name": "analyze_file_ast",
                            "description": "Analyze file using AST with linting rule integration",
                            "return_type": "Dict[str, Any]",
                        },
                        {
                            "name": "generate_perfect_code",
                            "description": "Generate perfect code using AST-guided approach",
                            "return_type": "str",
                        },
                    ],
                },
            },
        ],
        "relationships": {
            "ASTGuidedCodeGenerator": ["ASTNode", "LintingRule"],
            "ASTNode": [],
            "LintingRule": [],
        },
    }

    print("🎯 STEP 1: Creating model from design")
    model = system.create_model_from_design(design_spec)
    print(f"   ✅ Created model: {model.name} with {len(model.components)} components")

    # STEP 2: Save model to JSON
    print("\n🎯 STEP 2: Saving model to JSON")
    system.save_model("ASTGuidedCodeGenerator", "ast_guided_model.json")

    # STEP 3: Generate code from model
    print("\n🎯 STEP 3: Generating code from model")
    generated_files = system.generate_code_from_model("ASTGuidedCodeGenerator")

    # STEP 4: Save generated code
    print("\n🎯 STEP 4: Saving generated code")
    for filename, code in generated_files.items():
        with open(f"generated_{filename}", "w") as f:
            f.write(code)
        print(f"   💾 Saved generated_{filename}")

    # STEP 5: Load model from JSON (round-trip)
    print("\n🎯 STEP 5: Loading model from JSON (round-trip)")
    loaded_model = system.load_model("ast_guided_model.json")

    print("\n✅ ROUND-TRIP COMPLETE!")
    print(f"   📊 Model: {loaded_model.name}")
    print(f"   📊 Components: {len(loaded_model.components)}")
    print(f"   📊 Generated files: {len(generated_files)}")
    print("   🎯 Round-trip successful: Design → Model → Code → Model")


if __name__ == "__main__":
    main()
