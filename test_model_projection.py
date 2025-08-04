#!/usr/bin/env python3
"""
Test Model-Driven Projection: Generate artifacts from the complete model

This script tests that we can generate functionally equivalent artifacts
from our complete project model.
"""

import json
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from level1_granular_nodes import CodeNode, NodeProjector, DependencyResolver


class ModelProjectionTester:
    """Test projection of artifacts from the complete model."""
    
    def __init__(self, model_file: str = "complete_project_model.json"):
        self.model_file = model_file
        self.complete_model = self._load_complete_model()
        self.projector = NodeProjector()
        self.dependency_resolver = DependencyResolver()
    
    def _load_complete_model(self) -> Dict[str, Any]:
        """Load the complete project model."""
        with open(self.model_file, 'r') as f:
            return json.load(f)
    
    def get_file_nodes(self, file_path: str) -> List[CodeNode]:
        """Get all nodes for a specific file."""
        file_data = self.complete_model["files"].get(file_path)
        if not file_data:
            return []
        
        nodes = []
        for node_id in file_data["nodes"]:
            node_data = self.complete_model["nodes"].get(node_id)
            if node_data:
                node = CodeNode(
                    id=node_data["id"],
                    type=node_data["type"],
                    content=node_data["content"],
                    context=node_data["context"],
                    dependencies=node_data["dependencies"],
                    metadata=node_data["metadata"],
                    projection_rules=node_data["projection_rules"]
                )
                nodes.append(node)
        
        return nodes
    
    def project_file(self, file_path: str) -> str:
        """Project a complete file from its nodes."""
        nodes = self.get_file_nodes(file_path)
        if not nodes:
            return ""
        
        # Add nodes to the projector
        for node in nodes:
            self.projector.add_node(node)
        
        # Resolve dependencies
        node_ids = [node.id for node in nodes]
        ordered_nodes = self.dependency_resolver.resolve_order(node_ids)
        
        # Project the file
        projected_content = self.projector.compose_nodes(ordered_nodes, {"file_path": file_path})
        return projected_content
    
    def compare_files(self, original_path: str, projected_content: str) -> Dict[str, Any]:
        """Compare original file with projected content."""
        try:
            with open(original_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except FileNotFoundError:
            return {"error": f"Original file {original_path} not found"}
        
        # Calculate hashes
        original_hash = hashlib.md5(original_content.encode()).hexdigest()
        projected_hash = hashlib.md5(projected_content.encode()).hexdigest()
        
        # Check if they're identical
        identical = original_hash == projected_hash
        
        # For Python files, also check AST equivalence
        ast_equivalent = False
        if original_path.endswith('.py'):
            try:
                original_ast = ast.parse(original_content)
                projected_ast = ast.parse(projected_content)
                ast_equivalent = self._compare_ast(original_ast, projected_ast)
            except SyntaxError:
                ast_equivalent = False
        
        return {
            "identical": identical,
            "ast_equivalent": ast_equivalent,
            "original_hash": original_hash,
            "projected_hash": projected_hash,
            "original_length": len(original_content),
            "projected_length": len(projected_content),
            "length_diff": abs(len(original_content) - len(projected_content))
        }
    
    def _compare_ast(self, ast1: ast.AST, ast2: ast.AST) -> bool:
        """Compare two ASTs for functional equivalence."""
        # Simple comparison - in practice, you'd want more sophisticated AST comparison
        return ast.dump(ast1) == ast.dump(ast2)
    
    def test_projection(self, test_files: List[str]) -> Dict[str, Any]:
        """Test projection for multiple files."""
        results = {}
        
        for file_path in test_files:
            print(f"\n🔍 Testing projection for: {file_path}")
            
            # Project the file
            projected_content = self.project_file(file_path)
            
            if not projected_content:
                print(f"❌ No nodes found for {file_path}")
                results[file_path] = {"error": "No nodes found"}
                continue
            
            # Compare with original
            comparison = self.compare_files(file_path, projected_content)
            results[file_path] = comparison
            
            # Print results
            if comparison.get("identical"):
                print(f"✅ IDENTICAL: {file_path}")
            elif comparison.get("ast_equivalent"):
                print(f"✅ AST EQUIVALENT: {file_path}")
            else:
                print(f"⚠️ DIFFERENT: {file_path}")
                print(f"   Length diff: {comparison.get('length_diff', 0)} chars")
            
            # Show a preview
            self._show_preview(file_path, projected_content)
        
        return results
    
    def _show_preview(self, file_path: str, content: str, lines: int = 10) -> None:
        """Show a preview of the projected content."""
        print(f"\n📄 Preview of projected {file_path}:")
        print("=" * 60)
        
        lines_content = content.split('\n')[:lines]
        for i, line in enumerate(lines_content, 1):
            print(f"{i:2d}: {line}")
        
        total_lines = len(content.split('\n'))
        if total_lines > lines:
            print(f"... and {total_lines - lines} more lines")
        
        print("=" * 60)


def main():
    """Test model-driven projection."""
    print("🚀 Testing Model-Driven Projection")
    print("=" * 60)
    
    tester = ModelProjectionTester()
    
    # Test files - mix of different types
    test_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py", 
        "src/multi_agent_testing/live_smoke_test_langchain.py",
        "README.md",
        "pyproject.toml",
        "Makefile"
    ]
    
    # Filter to files that exist and have nodes
    existing_test_files = []
    for file_path in test_files:
        if Path(file_path).exists():
            nodes = tester.get_file_nodes(file_path)
            if nodes:
                existing_test_files.append(file_path)
                print(f"✅ Found {len(nodes)} nodes for {file_path}")
            else:
                print(f"❌ No nodes found for {file_path}")
        else:
            print(f"❌ File not found: {file_path}")
    
    if not existing_test_files:
        print("❌ No test files available")
        return
    
    print(f"\n🧪 Testing projection for {len(existing_test_files)} files...")
    
    # Run the tests
    results = tester.test_projection(existing_test_files)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PROJECTION TEST RESULTS")
    print("=" * 60)
    
    identical_count = 0
    ast_equivalent_count = 0
    different_count = 0
    
    for file_path, result in results.items():
        if result.get("identical"):
            identical_count += 1
            print(f"✅ {file_path}: IDENTICAL")
        elif result.get("ast_equivalent"):
            ast_equivalent_count += 1
            print(f"✅ {file_path}: AST EQUIVALENT")
        else:
            different_count += 1
            print(f"⚠️ {file_path}: DIFFERENT")
    
    print(f"\n📈 Summary:")
    print(f"  Identical: {identical_count}")
    print(f"  AST Equivalent: {ast_equivalent_count}")
    print(f"  Different: {different_count}")
    print(f"  Total: {len(results)}")
    
    success_rate = (identical_count + ast_equivalent_count) / len(results) * 100
    print(f"  Success Rate: {success_rate:.1f}%")
    
    print("=" * 60)


if __name__ == "__main__":
    main() 