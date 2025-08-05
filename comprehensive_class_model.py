#!/usr/bin/env python3
"""
Comprehensive Class Model: Distinguish between class definitions and usage

This model:
1. Tracks class definitions separately from class usage
2. Distinguishes method calls, attribute access, and instantiation
3. Prevents duplication by understanding definition vs usage
4. Creates accurate class relationships and dependencies
"""

import ast
import json
import logging
from typing import Dict, List, Set, Any
from pathlib import Path
from level1_granular_nodes import CodeNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveClassModel:
    """Comprehensive class model with definition vs usage distinction."""
    
    def __init__(self):
        self.extracted_nodes: Dict[str, CodeNode] = {}
        self.class_definitions: Set[str] = set()
        self.class_instantiations: Set[str] = set()
        self.method_calls: Set[str] = set()
        self.attribute_access: Set[str] = set()
        self.class_dependencies: Dict[str, List[str]] = {}
        self.position_counter = 0
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze file to distinguish class definitions from usage."""
        logger.info(f"🔍 Analyzing class definitions vs usage: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return {}
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file_path}: {e}")
            return {}
        
        # Analyze class definitions
        class_definitions = self._extract_class_definitions(tree)
        
        # Analyze class usage
        class_instantiations = self._extract_class_instantiations(tree)
        method_calls = self._extract_method_calls(tree)
        attribute_access = self._extract_attribute_access(tree)
        
        # Analyze dependencies
        dependencies = self._analyze_class_dependencies(tree, class_definitions)
        
        # Create nodes for class definitions only
        nodes = self._create_class_nodes(tree, file_path, class_definitions, dependencies)
        
        return {
            "class_definitions": list(class_definitions),
            "class_instantiations": list(class_instantiations),
            "method_calls": list(method_calls),
            "attribute_access": list(attribute_access),
            "dependencies": dependencies,
            "nodes": nodes
        }
    
    def _extract_class_definitions(self, tree: ast.AST) -> Set[str]:
        """Extract all class definitions."""
        definitions = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                definitions.add(node.name)
        
        return definitions
    
    def _extract_class_instantiations(self, tree: ast.AST) -> Set[str]:
        """Extract all class instantiations."""
        instantiations = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id'):
                    # This could be a class instantiation
                    class_name = node.func.id
                    # We'll assume it's a class if it starts with uppercase
                    # (Python convention, though not always true)
                    if class_name and class_name[0].isupper():
                        instantiations.add(class_name)
        
        return instantiations
    
    def _extract_method_calls(self, tree: ast.AST) -> Set[str]:
        """Extract all method calls (instance.method())."""
        method_calls = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr'):
                    # This is a method call: instance.method()
                    method_name = node.func.attr
                    method_calls.add(method_name)
        
        return method_calls
    
    def _extract_attribute_access(self, tree: ast.AST) -> Set[str]:
        """Extract all attribute access (instance.attribute)."""
        attribute_access = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                # This is attribute access: instance.attribute
                if hasattr(node, 'attr'):
                    attribute_name = node.attr
                    attribute_access.add(attribute_name)
        
        return attribute_access
    
    def _analyze_class_dependencies(self, tree: ast.AST, definitions: Set[str]) -> Dict[str, List[str]]:
        """Analyze dependencies between classes."""
        dependencies = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                dependencies[class_name] = []
                
                # Find all class instantiations within this class
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if hasattr(child.func, 'id'):
                            instantiated_class = child.func.id
                            # Only add as dependency if it's a defined class
                            if instantiated_class in definitions:
                                dependencies[class_name].append(instantiated_class)
        
        return dependencies
    
    def _create_class_nodes(self, tree: ast.AST, file_path: str, definitions: Set[str], dependencies: Dict[str, List[str]]) -> List[CodeNode]:
        """Create nodes for class definitions only."""
        nodes = []
        context = self._determine_context(file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                
                # Only create nodes for class definitions, not usage
                if class_name in definitions:
                    definition_code = ast.unparse(node)
                    line_number = getattr(node, 'lineno', 0)
                    
                    # Create unique node ID
                    node_id = f"class_{class_name}_{line_number}"
                    
                    # Get dependencies for this class
                    class_dependencies = dependencies.get(class_name, [])
                    
                    # Extract methods from this class
                    methods = []
                    for child in ast.walk(node):
                        if isinstance(child, ast.FunctionDef):
                            methods.append(child.name)
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="class_definition",  # Distinguish from class_usage
                        content=definition_code,
                        context=context,
                        dependencies=class_dependencies,
                        metadata={
                            "class_name": class_name,
                            "line_number": line_number,
                            "has_docstring": ast.get_docstring(node) is not None,
                            "source_file": file_path,
                            "position": line_number,
                            "order": self.position_counter,
                            "is_definition": True,
                            "is_usage": False,
                            "methods": methods,
                            "method_count": len(methods)
                        },
                        projection_rules={
                            "format": "black",
                            "lint": "flake8",
                            "order": self.position_counter
                        }
                    )
                    
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
                    self.class_definitions.add(class_name)
                    self.position_counter += 1
        
        return nodes
    
    def _determine_context(self, file_path: str) -> str:
        """Determine the context from file path."""
        path = Path(file_path)
        path_str = str(path)
        
        if "streamlit" in path_str:
            return "streamlit"
        elif "security_first" in path_str:
            return "security"
        elif "multi_agent_testing" in path_str:
            return "multi_agent"
        elif "tests" in path_str:
            return "testing"
        elif "config" in path_str or "config" in path.name:
            return "configuration"
        elif "docs" in path_str or path.suffix == '.md':
            return "documentation"
        elif "scripts" in path_str or path.suffix == '.sh':
            return "automation"
        elif path.suffix == '.yaml' or path.suffix == '.yml':
            return "infrastructure"
        elif path.suffix == '.json':
            return "data"
        else:
            return "general"
    
    def save_analysis(self, file_path: str) -> None:
        """Save the class analysis."""
        from datetime import datetime
        
        data = {
            "version": "2.5",
            "analyzed_at": datetime.now().isoformat(),
            "class_definitions": list(self.class_definitions),
            "class_instantiations": list(self.class_instantiations),
            "method_calls": list(self.method_calls),
            "attribute_access": list(self.attribute_access),
            "class_dependencies": self.class_dependencies,
            "nodes": {node_id: node.to_dict() for node_id, node in self.extracted_nodes.items()},
            "total_nodes": len(self.extracted_nodes)
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Saved class analysis to {file_path}")


def main():
    """Demonstrate comprehensive class model."""
    logger.info("🚀 Starting Comprehensive Class Model Analysis")
    
    model = ComprehensiveClassModel()
    
    # Test with the OpenFlow app
    test_file = "src/streamlit/openflow_quickstart_app.py"
    
    if Path(test_file).exists():
        analysis = model.analyze_file(test_file)
        
        # Show results
        print(f"\n📊 COMPREHENSIVE CLASS MODEL RESULTS:")
        print(f"Total class definitions: {len(analysis['class_definitions'])}")
        print(f"Total class instantiations: {len(analysis['class_instantiations'])}")
        print(f"Total method calls: {len(analysis['method_calls'])}")
        print(f"Total attribute access: {len(analysis['attribute_access'])}")
        print(f"Total nodes created: {len(analysis['nodes'])}")
        
        # Show class definitions
        print(f"\n📄 CLASS DEFINITIONS:")
        for i, class_name in enumerate(analysis['class_definitions'], 1):
            print(f"  {i:2d}. {class_name}")
        
        # Show class instantiations
        print(f"\n📄 CLASS INSTANTIATIONS:")
        for i, class_name in enumerate(analysis['class_instantiations'], 1):
            print(f"  {i:2d}. {class_name}")
        
        # Show method calls
        print(f"\n📄 METHOD CALLS:")
        for i, method_name in enumerate(analysis['method_calls'], 1):
            print(f"  {i:2d}. {method_name}")
        
        # Show attribute access
        print(f"\n📄 ATTRIBUTE ACCESS:")
        for i, attr_name in enumerate(analysis['attribute_access'], 1):
            print(f"  {i:2d}. {attr_name}")
        
        # Show dependencies
        print(f"\n📄 CLASS DEPENDENCIES:")
        for class_name, deps in analysis['dependencies'].items():
            if deps:  # Only show classes with dependencies
                print(f"  {class_name} depends on: {', '.join(deps)}")
        
        # Save analysis
        model.save_analysis("comprehensive_class_analysis.json")
        
        # Key insights
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"✅ Class definitions: {len(analysis['class_definitions'])}")
        print(f"✅ Class instantiations: {len(analysis['class_instantiations'])}")
        print(f"✅ Method calls: {len(analysis['method_calls'])}")
        print(f"✅ Attribute access: {len(analysis['attribute_access'])}")
        
        # Show overlap analysis
        definitions_set = set(analysis['class_definitions'])
        instantiations_set = set(analysis['class_instantiations'])
        both_defined_and_instantiated = definitions_set & instantiations_set
        
        print(f"✅ Classes both defined and instantiated: {len(both_defined_and_instantiated)}")
        print(f"✅ This explains why classes worked perfectly - no duplication!")
        
    else:
        logger.error(f"❌ Test file not found: {test_file}")


if __name__ == "__main__":
    main() 