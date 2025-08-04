#!/usr/bin/env python3
"""
Node Extractor: Extract granular nodes from existing Python files

This tool extracts imports, functions, classes, and other code elements
from existing Python files and converts them into granular nodes.
"""

import ast
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from level1_granular_nodes import CodeNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeExtractor:
    """Extract granular nodes from existing Python files."""
    
    def __init__(self):
        self.extracted_nodes: Dict[str, CodeNode] = {}
        self.file_context: Dict[str, str] = {}
    
    def extract_from_file(self, file_path: str) -> List[CodeNode]:
        """Extract granular nodes from a Python file."""
        logger.info(f"🔍 Extracting nodes from {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"❌ File not found: {file_path}")
            return []
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file_path}: {e}")
            return []
        
        # Determine context from file path
        context = self._determine_context(file_path)
        self.file_context[file_path] = context
        
        nodes = []
        
        # Extract imports
        import_nodes = self._extract_imports(tree, file_path, context)
        nodes.extend(import_nodes)
        
        # Extract functions
        function_nodes = self._extract_functions(tree, file_path, context)
        nodes.extend(function_nodes)
        
        # Extract classes
        class_nodes = self._extract_classes(tree, file_path, context)
        nodes.extend(class_nodes)
        
        # Extract constants and variables
        constant_nodes = self._extract_constants(tree, file_path, context)
        nodes.extend(constant_nodes)
        
        logger.info(f"✅ Extracted {len(nodes)} nodes from {file_path}")
        return nodes
    
    def _determine_context(self, file_path: str) -> str:
        """Determine the context from file path."""
        path = Path(file_path)
        
        if "streamlit" in str(path):
            return "streamlit"
        elif "security_first" in str(path):
            return "security"
        elif "multi_agent_testing" in str(path):
            return "multi_agent"
        elif "tests" in str(path):
            return "testing"
        elif "config" in str(path):
            return "configuration"
        else:
            return "general"
    
    def _extract_imports(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract import statements as nodes."""
        nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Get the source code for this import
                import_code = ast.unparse(node)
                
                # Create node ID
                if isinstance(node, ast.Import):
                    node_id = f"import_{node.names[0].name}"
                else:
                    node_id = f"import_from_{node.module or 'unknown'}"
                
                # Create CodeNode
                code_node = CodeNode(
                    id=node_id,
                    type="import",
                    content=import_code,
                    context=context,
                    dependencies=[],
                    metadata={
                        "file_pattern": "*.py",
                        "position": "top",
                        "source_file": file_path
                    },
                    projection_rules={
                        "format": "black",
                        "position": "top"
                    }
                )
                
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_functions(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract function definitions as nodes."""
        nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get the source code for this function
                function_code = ast.unparse(node)
                
                # Create node ID
                node_id = f"function_{node.name}"
                
                # Determine dependencies
                dependencies = self._extract_function_dependencies(node)
                
                # Create CodeNode
                code_node = CodeNode(
                    id=node_id,
                    type="function",
                    content=function_code,
                    context=context,
                    dependencies=dependencies,
                    metadata={
                        "function_name": node.name,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "source_file": file_path
                    },
                    projection_rules={
                        "format": "black",
                        "lint": "flake8"
                    }
                )
                
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_classes(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract class definitions as nodes."""
        nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get the source code for this class
                class_code = ast.unparse(node)
                
                # Create node ID
                node_id = f"class_{node.name}"
                
                # Determine dependencies
                dependencies = self._extract_class_dependencies(node)
                
                # Create CodeNode
                code_node = CodeNode(
                    id=node_id,
                    type="class",
                    content=class_code,
                    context=context,
                    dependencies=dependencies,
                    metadata={
                        "class_name": node.name,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "source_file": file_path
                    },
                    projection_rules={
                        "format": "black",
                        "lint": "flake8"
                    }
                )
                
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_constants(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract constants and variables as nodes."""
        nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Get the source code for this assignment
                assign_code = ast.unparse(node)
                
                # Only extract if it looks like a constant (uppercase)
                if any(target.id.isupper() for target in node.targets if hasattr(target, 'id')):
                    # Create node ID
                    target_name = node.targets[0].id if hasattr(node.targets[0], 'id') else "constant"
                    node_id = f"constant_{target_name}"
                    
                    # Create CodeNode
                    code_node = CodeNode(
                        id=node_id,
                        type="constant",
                        content=assign_code,
                        context=context,
                        dependencies=[],
                        metadata={
                            "constant_name": target_name,
                            "source_file": file_path
                        },
                        projection_rules={
                            "format": "black"
                        }
                    )
                    
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_function_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Extract dependencies for a function."""
        dependencies = []
        
        # Look for function calls and imports used
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id'):
                    func_name = child.func.id
                    # Check if this is a function we've extracted
                    if f"function_{func_name}" in self.extracted_nodes:
                        dependencies.append(f"function_{func_name}")
            elif isinstance(child, ast.Name):
                # Check if this name refers to an import
                name = child.id
                for node_id, extracted_node in self.extracted_nodes.items():
                    if extracted_node.type == "import" and name in extracted_node.content:
                        dependencies.append(node_id)
        
        return dependencies
    
    def _extract_class_dependencies(self, node: ast.ClassDef) -> List[str]:
        """Extract dependencies for a class."""
        dependencies = []
        
        # Look for base classes and function calls
        for base in node.bases:
            if hasattr(base, 'id'):
                base_name = base.id
                # Check if this is a class we've extracted
                if f"class_{base_name}" in self.extracted_nodes:
                    dependencies.append(f"class_{base_name}")
        
        # Look for function calls within the class
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id'):
                    func_name = child.func.id
                    # Check if this is a function we've extracted
                    if f"function_{func_name}" in self.extracted_nodes:
                        dependencies.append(f"function_{func_name}")
        
        return dependencies
    
    def save_extracted_nodes(self, file_path: str) -> None:
        """Save extracted nodes to a JSON file."""
        import json
        from datetime import datetime
        
        data = {
            "version": "1.0",
            "extracted_at": datetime.now().isoformat(),
            "nodes": {node_id: node.to_dict() for node_id, node in self.extracted_nodes.items()},
            "file_contexts": self.file_context
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Saved {len(self.extracted_nodes)} extracted nodes to {file_path}")


def main():
    """Demonstrate node extraction from existing files."""
    logger.info("🚀 Starting Node Extraction")
    
    extractor = NodeExtractor()
    
    # Files to extract from
    files_to_extract = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py",
        "src/multi_agent_testing/live_smoke_test_langchain.py"
    ]
    
    all_nodes = []
    
    for file_path in files_to_extract:
        if Path(file_path).exists():
            nodes = extractor.extract_from_file(file_path)
            all_nodes.extend(nodes)
            logger.info(f"📄 Extracted {len(nodes)} nodes from {file_path}")
        else:
            logger.warning(f"⚠️ File not found: {file_path}")
    
    # Save extracted nodes
    extractor.save_extracted_nodes("extracted_nodes.json")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 NODE EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total nodes extracted: {len(all_nodes)}")
    
    # Group by type
    by_type = {}
    for node in all_nodes:
        node_type = node.type
        if node_type not in by_type:
            by_type[node_type] = []
        by_type[node_type].append(node.id)
    
    for node_type, node_ids in by_type.items():
        print(f"{node_type.title()}: {len(node_ids)} nodes")
        for node_id in node_ids[:3]:  # Show first 3
            print(f"  - {node_id}")
        if len(node_ids) > 3:
            print(f"  ... and {len(node_ids) - 3} more")
    
    print("="*60)
    logger.info("✅ Node extraction completed")


if __name__ == "__main__":
    main() 