#!/usr/bin/env python3
"""
Context-Aware Extractor: Proper function deduplication with class context

This extractor:
1. Tracks function context (class vs standalone)
2. Prevents duplication of same function in different contexts
3. Maintains proper order
4. Handles Python's top-to-bottom processing correctly
"""

import ast
import json
import logging
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from level1_granular_nodes import CodeNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextAwareExtractor:
    """Context-aware node extractor with proper deduplication."""
    
    def __init__(self):
        self.extracted_nodes: Dict[str, CodeNode] = {}
        self.node_positions: Dict[str, int] = {}
        self.seen_definitions: Set[Tuple[str, int, Optional[str]]] = set()  # (name, line_number, class_context)
        self.position_counter = 0
        self.current_class_context: Optional[str] = None
    
    def extract_from_file(self, file_path: str) -> List[CodeNode]:
        """Extract nodes with context-aware deduplication."""
        logger.info(f"🔍 Extracting nodes from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return []
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file_path}: {e}")
            return []
        
        # Determine context
        context = self._determine_context(file_path)
        
        # Extract nodes in order
        nodes = []
        
        # Extract imports first (they must come first in Python)
        import_nodes = self._extract_imports_context_aware(tree, file_path, context)
        nodes.extend(import_nodes)
        
        # Extract classes and functions with context awareness
        class_function_nodes = self._extract_classes_and_functions_context_aware(tree, file_path, context)
        nodes.extend(class_function_nodes)
        
        # Extract constants and other top-level elements
        constant_nodes = self._extract_constants_context_aware(tree, file_path, context)
        nodes.extend(constant_nodes)
        
        logger.info(f"✅ Extracted {len(nodes)} unique nodes from {file_path}")
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
    
    def _extract_imports_context_aware(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract imports in order with proper deduplication."""
        nodes = []
        seen_imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_code = ast.unparse(node)
                
                # Skip if we've seen this exact import
                if import_code in seen_imports:
                    continue
                
                seen_imports.add(import_code)
                
                # Create unique ID based on content and position
                import_hash = hash(import_code)
                node_id = f"import_{import_hash}"
                
                # Get position in file
                position = self._get_node_position(node, file_path)
                
                code_node = CodeNode(
                    id=node_id,
                    type="import",
                    content=import_code,
                    context=context,
                    dependencies=[],
                    metadata={
                        "file_pattern": "*.py",
                        "position": position,
                        "source_file": file_path,
                        "order": self.position_counter
                    },
                    projection_rules={
                        "format": "black",
                        "position": "top",
                        "order": self.position_counter
                    }
                )
                
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
                self.node_positions[node_id] = position
                self.position_counter += 1
        
        return nodes
    
    def _extract_classes_and_functions_context_aware(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract classes and functions with context awareness."""
        nodes = []
        
        # Walk through the tree and collect all function and class definitions
        definitions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Extract class
                definition_code = ast.unparse(node)
                name = node.name
                line_number = getattr(node, 'lineno', 0)
                
                # Create unique identifier
                unique_id = (name, line_number, None)  # None for class context
                
                # Skip if we've already seen this class
                if unique_id in self.seen_definitions:
                    continue
                
                self.seen_definitions.add(unique_id)
                
                # Create node ID
                node_id = f"class_{name}_{line_number}"
                
                # Get position in file
                position = self._get_node_position(node, file_path)
                
                # Extract dependencies
                dependencies = self._extract_dependencies_context_aware(node)
                
                code_node = CodeNode(
                    id=node_id,
                    type="class",
                    content=definition_code,
                    context=context,
                    dependencies=dependencies,
                    metadata={
                        "class_name": name,
                        "line_number": line_number,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "source_file": file_path,
                        "position": position,
                        "order": self.position_counter,
                        "class_context": None
                    },
                    projection_rules={
                        "format": "black",
                        "lint": "flake8",
                        "order": self.position_counter
                    }
                )
                
                definitions.append((position, code_node))
                self.extracted_nodes[node_id] = code_node
                self.node_positions[node_id] = position
                self.position_counter += 1
                
                # Extract methods from this class
                class_methods = self._extract_class_methods(node, file_path, context, name)
                nodes.extend(class_methods)
                
            elif isinstance(node, ast.FunctionDef):
                # Only extract standalone functions (not class methods)
                # Class methods are handled in _extract_class_methods
                if not self._is_inside_class(node, tree):
                    definition_code = ast.unparse(node)
                    name = node.name
                    line_number = getattr(node, 'lineno', 0)
                    
                    # Create unique identifier for standalone function
                    unique_id = (name, line_number, None)  # None for standalone
                    
                    # Skip if we've already seen this function
                    if unique_id in self.seen_definitions:
                        continue
                    
                    self.seen_definitions.add(unique_id)
                    
                    # Create node ID
                    node_id = f"function_{name}_{line_number}"
                    
                    # Get position in file
                    position = self._get_node_position(node, file_path)
                    
                    # Extract dependencies
                    dependencies = self._extract_dependencies_context_aware(node)
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="function",
                        content=definition_code,
                        context=context,
                        dependencies=dependencies,
                        metadata={
                            "function_name": name,
                            "line_number": line_number,
                            "has_docstring": ast.get_docstring(node) is not None,
                            "source_file": file_path,
                            "position": position,
                            "order": self.position_counter,
                            "class_context": None
                        },
                        projection_rules={
                            "format": "black",
                            "lint": "flake8",
                            "order": self.position_counter
                        }
                    )
                    
                    definitions.append((position, code_node))
                    self.extracted_nodes[node_id] = code_node
                    self.node_positions[node_id] = position
                    self.position_counter += 1
        
        # Sort definitions by position and add to nodes
        definitions.sort(key=lambda x: x[0])
        nodes.extend([node for _, node in definitions])
        
        return nodes
    
    def _extract_class_methods(self, class_node: ast.ClassDef, file_path: str, context: str, class_name: str) -> List[CodeNode]:
        """Extract methods from a class."""
        methods = []
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                # This is a class method
                definition_code = ast.unparse(node)
                method_name = node.name
                line_number = getattr(node, 'lineno', 0)
                
                # Create unique identifier for class method
                unique_id = (method_name, line_number, class_name)
                
                # Skip if we've already seen this method in this class
                if unique_id in self.seen_definitions:
                    continue
                
                self.seen_definitions.add(unique_id)
                
                # Create node ID
                node_id = f"method_{class_name}_{method_name}_{line_number}"
                
                # Get position in file
                position = self._get_node_position(node, file_path)
                
                # Extract dependencies
                dependencies = self._extract_dependencies_context_aware(node)
                
                code_node = CodeNode(
                    id=node_id,
                    type="method",
                    content=definition_code,
                    context=context,
                    dependencies=dependencies,
                    metadata={
                        "function_name": method_name,
                        "class_name": class_name,
                        "line_number": line_number,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "source_file": file_path,
                        "position": position,
                        "order": self.position_counter,
                        "class_context": class_name
                    },
                    projection_rules={
                        "format": "black",
                        "lint": "flake8",
                        "order": self.position_counter
                    }
                )
                
                methods.append(code_node)
                self.extracted_nodes[node_id] = code_node
                self.node_positions[node_id] = position
                self.position_counter += 1
        
        return methods
    
    def _is_inside_class(self, function_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is inside a class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in ast.walk(node):
                    if child is function_node:
                        return True
        return False
    
    def _extract_constants_context_aware(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract constants and other top-level elements."""
        nodes = []
        seen_constants = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Only capture top-level assignments (constants)
                if hasattr(node, 'lineno') and node.lineno <= 50:  # Top of file
                    constant_code = ast.unparse(node)
                    
                    if constant_code in seen_constants:
                        continue
                    
                    seen_constants.add(constant_code)
                    
                    # Create unique ID
                    constant_hash = hash(constant_code)
                    node_id = f"constant_{constant_hash}"
                    
                    # Get position
                    position = self._get_node_position(node, file_path)
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="constant",
                        content=constant_code,
                        context=context,
                        dependencies=[],
                        metadata={
                            "source_file": file_path,
                            "position": position,
                            "order": self.position_counter
                        },
                        projection_rules={
                            "format": "black",
                            "order": self.position_counter
                        }
                    )
                    
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
                    self.node_positions[node_id] = position
                    self.position_counter += 1
        
        return nodes
    
    def _get_node_position(self, node: ast.AST, file_path: str) -> int:
        """Get the line number position of a node."""
        if hasattr(node, 'lineno'):
            return node.lineno
        return 0
    
    def _extract_dependencies_context_aware(self, node: ast.AST) -> List[str]:
        """Extract dependencies for a function or class."""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id'):
                    func_name = child.func.id
                    # Look for existing function nodes
                    for node_id, extracted_node in self.extracted_nodes.items():
                        if (extracted_node.type == "function" and 
                            extracted_node.metadata.get("function_name") == func_name):
                            dependencies.append(node_id)
            
            elif isinstance(child, ast.Name):
                name = child.id
                # Look for imports that provide this name
                for node_id, extracted_node in self.extracted_nodes.items():
                    if (extracted_node.type == "import" and 
                        name in extracted_node.content):
                        dependencies.append(node_id)
        
        return dependencies
    
    def save_extracted_nodes(self, file_path: str) -> None:
        """Save extracted nodes with order information."""
        from datetime import datetime
        
        # Sort nodes by order
        sorted_nodes = sorted(
            self.extracted_nodes.items(),
            key=lambda x: x[1].metadata.get("order", 0)
        )
        
        data = {
            "version": "2.3",
            "extracted_at": datetime.now().isoformat(),
            "nodes": {node_id: node.to_dict() for node_id, node in sorted_nodes},
            "node_positions": self.node_positions,
            "total_nodes": len(self.extracted_nodes)
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Saved {len(self.extracted_nodes)} context-aware nodes to {file_path}")


def main():
    """Demonstrate context-aware node extraction."""
    logger.info("🚀 Starting Context-Aware Node Extraction")
    
    extractor = ContextAwareExtractor()
    
    # Test with the OpenFlow app
    test_file = "src/streamlit/openflow_quickstart_app.py"
    
    if Path(test_file).exists():
        nodes = extractor.extract_from_file(test_file)
        
        # Show results
        print(f"\n📊 CONTEXT-AWARE EXTRACTION RESULTS:")
        print(f"Total unique nodes: {len(nodes)}")
        
        # Group by type
        by_type = {}
        for node in nodes:
            node_type = node.type
            if node_type not in by_type:
                by_type[node_type] = []
            by_type[node_type].append(node)
        
        for node_type, node_list in by_type.items():
            print(f"\n{node_type.title()}: {len(node_list)} nodes")
            for node in sorted(node_list, key=lambda n: n.metadata.get("order", 0)):
                order = node.metadata.get("order", 0)
                name = node.metadata.get("function_name", node.metadata.get("class_name", "unknown"))
                line_num = node.metadata.get("line_number", "unknown")
                class_context = node.metadata.get("class_context", "standalone")
                context_info = f"({class_context})" if class_context else "(standalone)"
                print(f"  {order:3d}. {name} {context_info} (line {line_num})")
        
        # Save context-aware nodes
        extractor.save_extracted_nodes("context_aware_extracted_nodes.json")
        
    else:
        logger.error(f"❌ Test file not found: {test_file}")


if __name__ == "__main__":
    main() 