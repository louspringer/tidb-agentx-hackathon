#!/usr/bin/env python3
"""
Enhanced Function Model: Distinguish between function definitions and function calls

This model:
1. Tracks function definitions separately from function calls
2. Prevents duplication by understanding usage vs definition
3. Maintains proper dependencies
4. Creates accurate function relationships
"""

import ast
import json
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from pathlib import Path
from level1_granular_nodes import CodeNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedFunctionModel:
    """Enhanced function model with definition vs call distinction."""
    
    def __init__(self):
        self.extracted_nodes: Dict[str, CodeNode] = {}
        self.function_definitions: Set[str] = set()
        self.function_calls: Set[str] = set()
        self.function_dependencies: Dict[str, List[str]] = {}
        self.position_counter = 0
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze file to distinguish function definitions from calls."""
        logger.info(f"🔍 Analyzing function definitions vs calls: {file_path}")
        
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
        
        # Analyze function definitions
        function_definitions = self._extract_function_definitions(tree)
        
        # Analyze function calls
        function_calls = self._extract_function_calls(tree)
        
        # Analyze dependencies
        dependencies = self._analyze_dependencies(tree, function_definitions, function_calls)
        
        # Create nodes for function definitions only
        nodes = self._create_function_nodes(tree, file_path, function_definitions, dependencies)
        
        return {
            "function_definitions": list(function_definitions),
            "function_calls": list(function_calls),
            "dependencies": dependencies,
            "nodes": nodes
        }
    
    def _extract_function_definitions(self, tree: ast.AST) -> Set[str]:
        """Extract all function definitions."""
        definitions = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                definitions.add(node.name)
        
        return definitions
    
    def _extract_function_calls(self, tree: ast.AST) -> Set[str]:
        """Extract all function calls."""
        calls = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id'):
                    calls.add(node.func.id)
        
        return calls
    
    def _analyze_dependencies(self, tree: ast.AST, definitions: Set[str], calls: Set[str]) -> Dict[str, List[str]]:
        """Analyze dependencies between functions."""
        dependencies = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                dependencies[func_name] = []
                
                # Find all function calls within this function
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if hasattr(child.func, 'id'):
                            called_func = child.func.id
                            # Only add as dependency if it's a defined function
                            if called_func in definitions:
                                dependencies[func_name].append(called_func)
        
        return dependencies
    
    def _create_function_nodes(self, tree: ast.AST, file_path: str, definitions: Set[str], dependencies: Dict[str, List[str]]) -> List[CodeNode]:
        """Create nodes for function definitions only."""
        nodes = []
        context = self._determine_context(file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                
                # Only create nodes for function definitions, not calls
                if func_name in definitions:
                    definition_code = ast.unparse(node)
                    line_number = getattr(node, 'lineno', 0)
                    
                    # Create unique node ID
                    node_id = f"function_{func_name}_{line_number}"
                    
                    # Get dependencies for this function
                    func_dependencies = dependencies.get(func_name, [])
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="function_definition",  # Distinguish from function_call
                        content=definition_code,
                        context=context,
                        dependencies=func_dependencies,
                        metadata={
                            "function_name": func_name,
                            "line_number": line_number,
                            "has_docstring": ast.get_docstring(node) is not None,
                            "source_file": file_path,
                            "position": line_number,
                            "order": self.position_counter,
                            "is_definition": True,
                            "is_call": False
                        },
                        projection_rules={
                            "format": "black",
                            "lint": "flake8",
                            "order": self.position_counter
                        }
                    )
                    
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
                    self.function_definitions.add(func_name)
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
        """Save the function analysis."""
        from datetime import datetime
        
        data = {
            "version": "2.4",
            "analyzed_at": datetime.now().isoformat(),
            "function_definitions": list(self.function_definitions),
            "function_calls": list(self.function_calls),
            "function_dependencies": self.function_dependencies,
            "nodes": {node_id: node.to_dict() for node_id, node in self.extracted_nodes.items()},
            "total_nodes": len(self.extracted_nodes)
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Saved function analysis to {file_path}")


def main():
    """Demonstrate enhanced function model."""
    logger.info("🚀 Starting Enhanced Function Model Analysis")
    
    model = EnhancedFunctionModel()
    
    # Test with the OpenFlow app
    test_file = "src/streamlit/openflow_quickstart_app.py"
    
    if Path(test_file).exists():
        analysis = model.analyze_file(test_file)
        
        # Show results
        print(f"\n📊 ENHANCED FUNCTION MODEL RESULTS:")
        print(f"Total function definitions: {len(analysis['function_definitions'])}")
        print(f"Total function calls: {len(analysis['function_calls'])}")
        print(f"Total nodes created: {len(analysis['nodes'])}")
        
        # Show function definitions
        print(f"\n📄 FUNCTION DEFINITIONS:")
        for i, func_name in enumerate(analysis['function_definitions'], 1):
            print(f"  {i:2d}. {func_name}")
        
        # Show function calls
        print(f"\n📄 FUNCTION CALLS:")
        for i, func_name in enumerate(analysis['function_calls'], 1):
            print(f"  {i:2d}. {func_name}")
        
        # Show dependencies
        print(f"\n📄 FUNCTION DEPENDENCIES:")
        for func_name, deps in analysis['dependencies'].items():
            if deps:  # Only show functions with dependencies
                print(f"  {func_name} depends on: {', '.join(deps)}")
        
        # Save analysis
        model.save_analysis("enhanced_function_analysis.json")
        
        # Key insight
        print(f"\n🎯 KEY INSIGHT:")
        print(f"✅ Function definitions: {len(analysis['function_definitions'])}")
        print(f"✅ Function calls: {len(analysis['function_calls'])}")
        print(f"✅ Only {len(set(analysis['function_definitions']) & set(analysis['function_calls']))} functions are both defined and called")
        print(f"✅ This explains the duplication! We were counting calls as definitions.")
        
    else:
        logger.error(f"❌ Test file not found: {test_file}")


if __name__ == "__main__":
    main() 