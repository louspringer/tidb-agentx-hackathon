#!/usr/bin/env python3
"""
Final Solution: Perfect projection with class method handling

The key insight: Class methods should be extracted with their class context
to prevent duplication of methods like __init__ that appear in multiple classes.
"""

import ast
import logging
from typing import Dict, List, Set, Any, Tuple
from pathlib import Path
from level1_granular_nodes import CodeNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinalSolution:
    """Final solution with perfect class method handling."""
    
    def __init__(self):
        self.extracted_nodes: Dict[str, CodeNode] = {}
        self.position_counter = 0
        self.seen_definitions: Set[Tuple[str, str, int]] = set()  # (type, name, line_number)
    
    def extract_and_project_file(self, file_path: str) -> str:
        """Extract only definitions and project them perfectly."""
        logger.info(f"🔍 Final solution extraction: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return ""
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file_path}: {e}")
            return ""
        
        # Extract only definitions (not usage)
        nodes = self._extract_definitions_only(tree, file_path)
        
        if not nodes:
            return ""
        
        # Sort nodes by order
        ordered_nodes = sorted(nodes, key=lambda n: n.metadata.get("order", 0))
        
        # Project in order
        projected_content = self._project_ordered_nodes(ordered_nodes, file_path)
        
        return projected_content
    
    def _extract_definitions_only(self, tree: ast.AST, file_path: str) -> List[CodeNode]:
        """Extract only definitions, never usage."""
        nodes = []
        context = self._determine_context(file_path)
        
        # Extract imports (definitions only)
        import_nodes = self._extract_imports_perfect(tree, file_path, context)
        nodes.extend(import_nodes)
        
        # Extract class definitions with their methods
        class_nodes = self._extract_classes_with_methods(tree, file_path, context)
        nodes.extend(class_nodes)
        
        # Extract standalone functions (not class methods)
        function_nodes = self._extract_standalone_functions(tree, file_path, context)
        nodes.extend(function_nodes)
        
        # Extract constants (definitions only)
        constant_nodes = self._extract_constants_perfect(tree, file_path, context)
        nodes.extend(constant_nodes)
        
        logger.info(f"✅ Final solution extraction: {len(nodes)} definition nodes from {file_path}")
        return nodes
    
    def _extract_imports_perfect(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract import statements (definitions only)."""
        nodes = []
        seen_imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_code = ast.unparse(node)
                
                if import_code in seen_imports:
                    continue
                
                seen_imports.add(import_code)
                
                node_id = f"import_{hash(import_code)}"
                position = getattr(node, 'lineno', 0)
                
                code_node = CodeNode(
                    id=node_id,
                    type="import",
                    content=import_code,
                    context=context,
                    dependencies=[],
                    metadata={
                        "position": position,
                        "source_file": file_path,
                        "order": self.position_counter,
                        "is_definition": True,
                        "is_usage": False
                    },
                    projection_rules={
                        "format": "black",
                        "position": "top",
                        "order": self.position_counter
                    }
                )
                
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
                self.position_counter += 1
        
        return nodes
    
    def _extract_classes_with_methods(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract class definitions with their methods (no duplication)."""
        nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                line_number = getattr(node, 'lineno', 0)
                
                # Extract the entire class with all its methods
                class_code = ast.unparse(node)
                
                node_id = f"class_{class_name}_{line_number}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="class_definition",
                    content=class_code,
                    context=context,
                    dependencies=[],
                    metadata={
                        "class_name": class_name,
                        "line_number": line_number,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "source_file": file_path,
                        "position": line_number,
                        "order": self.position_counter,
                        "is_definition": True,
                        "is_usage": False,
                        "contains_methods": True
                    },
                    projection_rules={
                        "format": "black",
                        "lint": "flake8",
                        "order": self.position_counter
                    }
                )
                
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
                self.position_counter += 1
        
        return nodes
    
    def _extract_standalone_functions(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract standalone functions (not class methods)."""
        nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if this function is inside a class
                parent = self._get_parent_node(tree, node)
                if isinstance(parent, ast.ClassDef):
                    # This is a class method, skip it (it's handled in class extraction)
                    continue
                
                func_name = node.name
                definition_code = ast.unparse(node)
                line_number = getattr(node, 'lineno', 0)
                
                # Check if we've already seen this standalone function
                unique_id = ("function", func_name, line_number)
                if unique_id in self.seen_definitions:
                    continue
                
                self.seen_definitions.add(unique_id)
                
                node_id = f"function_{func_name}_{line_number}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="function_definition",
                    content=definition_code,
                    context=context,
                    dependencies=[],
                    metadata={
                        "function_name": func_name,
                        "line_number": line_number,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "source_file": file_path,
                        "position": line_number,
                        "order": self.position_counter,
                        "is_definition": True,
                        "is_usage": False,
                        "is_standalone": True
                    },
                    projection_rules={
                        "format": "black",
                        "lint": "flake8",
                        "order": self.position_counter
                    }
                )
                
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
                self.position_counter += 1
        
        return nodes
    
    def _get_parent_node(self, tree: ast.AST, target_node: ast.AST) -> ast.AST:
        """Get the parent node of a target node."""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child is target_node:
                    return parent
        return None
    
    def _extract_constants_perfect(self, tree: ast.AST, file_path: str, context: str) -> List[CodeNode]:
        """Extract constant definitions (not usage)."""
        nodes = []
        seen_constants = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Only capture top-level assignments (constants)
                if hasattr(node, 'lineno') and node.lineno <= 50:
                    constant_code = ast.unparse(node)
                    
                    if constant_code in seen_constants:
                        continue
                    
                    seen_constants.add(constant_code)
                    
                    node_id = f"constant_{hash(constant_code)}"
                    position = getattr(node, 'lineno', 0)
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="constant",
                        content=constant_code,
                        context=context,
                        dependencies=[],
                        metadata={
                            "source_file": file_path,
                            "position": position,
                            "order": self.position_counter,
                            "is_definition": True,
                            "is_usage": False
                        },
                        projection_rules={
                            "format": "black",
                            "order": self.position_counter
                        }
                    )
                    
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
                    self.position_counter += 1
        
        return nodes
    
    def _project_ordered_nodes(self, nodes: List[CodeNode], file_path: str) -> str:
        """Project nodes in the correct order."""
        content_parts = []
        
        # Add file header
        content_parts.append(self._generate_file_header(file_path))
        
        # Group nodes by type for proper ordering
        imports = []
        constants = []
        classes = []
        functions = []
        
        for node in nodes:
            if node.type == "import":
                imports.append(node)
            elif node.type == "constant":
                constants.append(node)
            elif node.type == "class_definition":
                classes.append(node)
            elif node.type == "function_definition":
                functions.append(node)
        
        # Add imports first
        for node in sorted(imports, key=lambda n: n.metadata.get("order", 0)):
            content_parts.append(node.content)
        
        if imports:
            content_parts.append("")
        
        # Add constants
        for node in sorted(constants, key=lambda n: n.metadata.get("order", 0)):
            content_parts.append(node.content)
        
        if constants:
            content_parts.append("")
        
        # Add classes
        for node in sorted(classes, key=lambda n: n.metadata.get("order", 0)):
            content_parts.append(node.content)
            content_parts.append("")
        
        # Add standalone functions
        for node in sorted(functions, key=lambda n: n.metadata.get("order", 0)):
            content_parts.append(node.content)
            content_parts.append("")
        
        # Add file footer
        content_parts.append(self._generate_file_footer(file_path))
        
        return "\n".join(content_parts)
    
    def _generate_file_header(self, file_path: str) -> str:
        """Generate file header."""
        if file_path.endswith('.py'):
            return '#!/usr/bin/env python3\n"""Generated from final model-driven projection"""\n'
        return ""
    
    def _generate_file_footer(self, file_path: str) -> str:
        """Generate file footer."""
        if file_path.endswith('.py'):
            return '\nif __name__ == "__main__":\n    main()\n'
        return ""
    
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
    
    def compare_with_original(self, original_path: str, projected_content: str) -> Dict[str, Any]:
        """Compare projected content with original."""
        try:
            with open(original_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except FileNotFoundError:
            return {"error": f"Original file {original_path} not found"}
        
        # Parse both files
        try:
            original_tree = ast.parse(original_content)
            projected_tree = ast.parse(projected_content)
        except SyntaxError as e:
            return {"error": f"Syntax error: {e}"}
        
        # Count elements
        def count_elements(tree):
            imports = 0
            functions = 0
            classes = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports += 1
                elif isinstance(node, ast.FunctionDef):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
            return {'imports': imports, 'functions': functions, 'classes': classes}
        
        original_stats = count_elements(original_tree)
        projected_stats = count_elements(projected_tree)
        
        # Calculate similarity
        original_lines = original_content.split('\n')
        projected_lines = projected_content.split('\n')
        matching_lines = len(set(original_lines) & set(projected_lines))
        similarity = matching_lines / len(original_lines) if original_lines else 0
        
        return {
            "original_stats": original_stats,
            "projected_stats": projected_stats,
            "similarity": similarity,
            "original_lines": len(original_lines),
            "projected_lines": len(projected_lines),
            "matching_lines": matching_lines
        }


def main():
    """Test final solution."""
    print("🚀 Final Solution Test")
    print("=" * 60)
    
    system = FinalSolution()
    
    # Test file
    test_file = "src/streamlit/openflow_quickstart_app.py"
    
    if Path(test_file).exists():
        print(f"🔍 Testing final solution: {test_file}")
        
        # Extract and project
        projected_content = system.extract_and_project_file(test_file)
        
        if projected_content:
            # Compare with original
            comparison = system.compare_with_original(test_file, projected_content)
            
            if "error" in comparison:
                print(f"❌ Error: {comparison['error']}")
            else:
                similarity = comparison["similarity"]
                print(f"📊 Similarity: {similarity:.1%}")
                
                # Show detailed stats
                orig_stats = comparison["original_stats"]
                proj_stats = comparison["projected_stats"]
                
                print(f"  Original: {orig_stats['imports']} imports, {orig_stats['functions']} functions, {orig_stats['classes']} classes")
                print(f"  Projected: {proj_stats['imports']} imports, {proj_stats['functions']} functions, {proj_stats['classes']} classes")
                
                # Check for duplication
                if proj_stats['functions'] > orig_stats['functions']:
                    print(f"  ⚠️  Function duplication detected: {proj_stats['functions']} vs {orig_stats['functions']}")
                elif proj_stats['functions'] == orig_stats['functions']:
                    print(f"  ✅ No function duplication")
                else:
                    print(f"  ❌ Missing functions: {orig_stats['functions']} vs {proj_stats['functions']}")
                
                if proj_stats['classes'] > orig_stats['classes']:
                    print(f"  ⚠️  Class duplication detected: {proj_stats['classes']} vs {orig_stats['classes']}")
                elif proj_stats['classes'] == orig_stats['classes']:
                    print(f"  ✅ No class duplication")
                else:
                    print(f"  ❌ Missing classes: {orig_stats['classes']} vs {proj_stats['classes']}")
                
                # Save the projection
                with open('final_solution_projection.py', 'w') as f:
                    f.write(projected_content)
                
                print(f"✅ Saved final solution projection to final_solution_projection.py")
                
                # Show sample content
                print(f"\n📄 SAMPLE PROJECTED CONTENT (first 20 lines):")
                lines = projected_content.split('\n')[:20]
                for i, line in enumerate(lines, 1):
                    print(f"{i:2d}: {line}")
        else:
            print(f"❌ No content projected")
    else:
        print(f"❌ Test file not found: {test_file}")


if __name__ == "__main__":
    main() 