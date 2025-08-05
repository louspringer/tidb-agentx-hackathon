#!/usr/bin/env python3
"""
Context-Aware Projection System: Use improved extraction with proper deduplication

This system:
1. Uses the context-aware node extractor
2. Projects nodes in correct order
3. Handles deduplication properly
4. Creates functionally equivalent artifacts
"""

import ast
from pathlib import Path
from typing import Dict, List, Any
from context_aware_extractor import ContextAwareExtractor


class ContextAwareProjectionSystem:
    """Context-aware projection system with proper order preservation."""
    
    def __init__(self):
        self.extractor = ContextAwareExtractor()
    
    def extract_and_project_file(self, file_path: str) -> str:
        """Extract nodes and project them in correct order."""
        print(f"🔍 Extracting and projecting: {file_path}")
        
        # Extract nodes with order
        nodes = self.extractor.extract_from_file(file_path)
        
        if not nodes:
            return ""
        
        # Sort nodes by order
        ordered_nodes = sorted(nodes, key=lambda n: n.metadata.get("order", 0))
        
        # Project in order
        projected_content = self._project_ordered_nodes(ordered_nodes, file_path)
        
        return projected_content
    
    def _project_ordered_nodes(self, nodes: List, file_path: str) -> str:
        """Project nodes in the correct order."""
        content_parts = []
        
        # Add file header
        content_parts.append(self._generate_file_header(file_path))
        
        # Group nodes by type for proper ordering
        imports = []
        constants = []
        classes = []
        methods = []
        functions = []
        
        for node in nodes:
            if node.type == "import":
                imports.append(node)
            elif node.type == "constant":
                constants.append(node)
            elif node.type == "class":
                classes.append(node)
            elif node.type == "method":
                methods.append(node)
            elif node.type == "function":
                functions.append(node)
        
        # Add imports first (Python requirement)
        for node in sorted(imports, key=lambda n: n.metadata.get("order", 0)):
            content_parts.append(node.content)
        
        # Add blank line after imports
        if imports:
            content_parts.append("")
        
        # Add constants
        for node in sorted(constants, key=lambda n: n.metadata.get("order", 0)):
            content_parts.append(node.content)
        
        # Add blank line after constants
        if constants:
            content_parts.append("")
        
        # Add classes with their methods
        for class_node in sorted(classes, key=lambda n: n.metadata.get("order", 0)):
            class_name = class_node.metadata.get("class_name", "unknown")
            content_parts.append(class_node.content)
            
            # Add methods for this class
            class_methods = [m for m in methods if m.metadata.get("class_name") == class_name]
            for method_node in sorted(class_methods, key=lambda n: n.metadata.get("order", 0)):
                content_parts.append(method_node.content)
            
            content_parts.append("")  # Blank line after class
        
        # Add standalone functions
        for node in sorted(functions, key=lambda n: n.metadata.get("order", 0)):
            content_parts.append(node.content)
            content_parts.append("")  # Blank line after function
        
        # Add file footer
        content_parts.append(self._generate_file_footer(file_path))
        
        return "\n".join(content_parts)
    
    def _generate_file_header(self, file_path: str) -> str:
        """Generate file header."""
        if file_path.endswith('.py'):
            return '#!/usr/bin/env python3\n"""Generated from model-driven projection"""\n'
        return ""
    
    def _generate_file_footer(self, file_path: str) -> str:
        """Generate file footer."""
        if file_path.endswith('.py'):
            return '\nif __name__ == "__main__":\n    main()\n'
        return ""
    
    def compare_files_detailed(self, original_path: str, projected_content: str) -> Dict[str, Any]:
        """Compare original and projected files in detail."""
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
        original_stats = self._count_elements(original_tree)
        projected_stats = self._count_elements(projected_tree)
        
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
    
    def _count_elements(self, tree: ast.AST) -> Dict[str, int]:
        """Count different elements in an AST."""
        imports = 0
        functions = 0
        classes = 0
        constants = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
            elif isinstance(node, ast.FunctionDef):
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, ast.Assign):
                constants += 1
        
        return {
            "imports": imports,
            "functions": functions,
            "classes": classes,
            "constants": constants
        }
    
    def test_context_aware_projection(self, test_files: List[str]) -> Dict[str, Any]:
        """Test context-aware projection on multiple files."""
        results = {}
        
        for file_path in test_files:
            if not Path(file_path).exists():
                print(f"❌ File not found: {file_path}")
                continue
            
            print(f"\n🔍 Testing context-aware projection: {file_path}")
            
            # Extract and project
            projected_content = self.extract_and_project_file(file_path)
            
            if not projected_content:
                print(f"❌ No content projected for {file_path}")
                continue
            
            # Compare with original
            comparison = self.compare_files_detailed(file_path, projected_content)
            results[file_path] = comparison
            
            # Show results
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
        
        return results
    
    def save_projected_file(self, file_path: str, projected_content: str) -> None:
        """Save projected content to a file."""
        output_path = Path("context_aware_projected_artifacts") / file_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(projected_content)
        
        print(f"✅ Saved projected file: {output_path}")


def main():
    """Test context-aware projection system."""
    print("🚀 Context-Aware Projection System Test")
    print("=" * 60)
    
    system = ContextAwareProjectionSystem()
    
    # Test files
    test_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py"
    ]
    
    # Run tests
    results = system.test_context_aware_projection(test_files)
    
    # Save projected files
    print(f"\n💾 Saving projected files...")
    for file_path in test_files:
        if Path(file_path).exists():
            projected_content = system.extract_and_project_file(file_path)
            if projected_content:
                system.save_projected_file(file_path, projected_content)
    
    # Summary
    print(f"\n📊 CONTEXT-AWARE PROJECTION RESULTS:")
    print("=" * 60)
    
    total_files = len(results)
    successful_files = 0
    high_similarity_files = 0
    
    for file_path, result in results.items():
        if "error" in result:
            print(f"❌ {file_path}: {result['error']}")
        else:
            similarity = result["similarity"]
            status = "✅" if similarity > 0.8 else "⚠️" if similarity > 0.5 else "❌"
            print(f"{status} {file_path}: {similarity:.1%}")
            
            if similarity > 0.5:
                successful_files += 1
            if similarity > 0.8:
                high_similarity_files += 1
    
    print(f"\n📈 Summary:")
    print(f"  Total files: {total_files}")
    print(f"  Successful (>50%): {successful_files}")
    print(f"  High similarity (>80%): {high_similarity_files}")
    
    success_rate = (successful_files / total_files * 100) if total_files > 0 else 0
    print(f"  Success rate: {success_rate:.1f}%")


if __name__ == "__main__":
    main() 