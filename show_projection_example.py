#!/usr/bin/env python3
"""
Show Projection Example: Detailed comparison of original vs projected

This script shows exactly what the model projection looks like
compared to the original files.
"""

import json
from pathlib import Path


def load_complete_model():
    """Load the complete project model."""
    with open("complete_project_model.json", 'r') as f:
        return json.load(f)


def get_file_nodes(model, file_path):
    """Get all nodes for a specific file."""
    file_data = model["files"].get(file_path)
    if not file_data:
        return []
    
    nodes = []
    for node_id in file_data["nodes"]:
        node_data = model["nodes"].get(node_id)
        if node_data:
            nodes.append(node_data)
    
    return nodes


def project_file_simple(model, file_path):
    """Project a file by concatenating its nodes."""
    nodes = get_file_nodes(model, file_path)
    if not nodes:
        return ""
    
    # Sort nodes by type (imports first, then functions, then classes)
    type_order = {"import": 0, "function": 1, "class": 2, "markdown_section": 3, "toml_section": 4}
    
    def sort_key(node):
        return type_order.get(node["type"], 999)
    
    sorted_nodes = sorted(nodes, key=sort_key)
    
    # Concatenate content
    content_parts = []
    for node in sorted_nodes:
        content_parts.append(node["content"])
    
    return "\n\n".join(content_parts)


def show_detailed_comparison(file_path):
    """Show detailed comparison of original vs projected."""
    print(f"\n{'='*80}")
    print(f"🔍 DETAILED COMPARISON: {file_path}")
    print(f"{'='*80}")
    
    # Load model
    model = load_complete_model()
    
    # Get original content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except FileNotFoundError:
        print(f"❌ Original file not found: {file_path}")
        return
    
    # Get projected content
    projected_content = project_file_simple(model, file_path)
    
    if not projected_content:
        print(f"❌ No projected content for {file_path}")
        return
    
    # Show node breakdown
    nodes = get_file_nodes(model, file_path)
    print(f"\n📋 NODE BREAKDOWN ({len(nodes)} nodes):")
    for i, node in enumerate(nodes, 1):
        node_type = node["type"]
        content_preview = node["content"][:50].replace('\n', ' ').replace('\r', ' ')
        print(f"  {i:2d}. {node_type:15} | {content_preview}...")
    
    # Show side-by-side comparison
    print(f"\n📄 ORIGINAL vs PROJECTED COMPARISON:")
    print(f"{'='*80}")
    
    original_lines = original_content.split('\n')
    projected_lines = projected_content.split('\n')
    
    # Show first 20 lines of each
    print(f"\n🔴 ORIGINAL (first 20 lines):")
    print("-" * 40)
    for i, line in enumerate(original_lines[:20], 1):
        print(f"{i:2d}: {line}")
    
    print(f"\n🟢 PROJECTED (first 20 lines):")
    print("-" * 40)
    for i, line in enumerate(projected_lines[:20], 1):
        print(f"{i:2d}: {line}")
    
    # Show specific differences
    print(f"\n🔍 KEY DIFFERENCES:")
    print("-" * 40)
    
    # Check for missing imports
    original_imports = [line for line in original_lines if line.strip().startswith('import') or line.strip().startswith('from')]
    projected_imports = [line for line in projected_lines if line.strip().startswith('import') or line.strip().startswith('from')]
    
    missing_imports = set(original_imports) - set(projected_imports)
    extra_imports = set(projected_imports) - set(original_imports)
    
    if missing_imports:
        print(f"❌ Missing imports in projection:")
        for imp in missing_imports:
            print(f"    {imp}")
    
    if extra_imports:
        print(f"➕ Extra imports in projection:")
        for imp in extra_imports:
            print(f"    {imp}")
    
    # Check for function definitions
    original_functions = [line for line in original_lines if line.strip().startswith('def ')]
    projected_functions = [line for line in projected_lines if line.strip().startswith('def ')]
    
    missing_functions = set(original_functions) - set(projected_functions)
    extra_functions = set(projected_functions) - set(original_functions)
    
    if missing_functions:
        print(f"❌ Missing functions in projection:")
        for func in missing_functions:
            print(f"    {func}")
    
    if extra_functions:
        print(f"➕ Extra functions in projection:")
        for func in extra_functions:
            print(f"    {func}")
    
    # Show similarity metrics
    matching_lines = len(set(original_lines) & set(projected_lines))
    total_original_lines = len(original_lines)
    similarity = matching_lines / total_original_lines if total_original_lines > 0 else 0
    
    print(f"\n📊 SIMILARITY METRICS:")
    print(f"  Original lines: {total_original_lines}")
    print(f"  Projected lines: {len(projected_lines)}")
    print(f"  Matching lines: {matching_lines}")
    print(f"  Similarity: {similarity:.1%}")
    
    print(f"\n{'='*80}")


def main():
    """Show detailed projection examples."""
    print("🚀 Model Projection Examples")
    print("=" * 80)
    
    # Test files that showed interesting results
    test_files = [
        "pyproject.toml",  # Best result (84.1% similar)
        "src/security_first/input_validator.py",  # Lower similarity (20.3%)
        "README.md"  # Markdown example
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            show_detailed_comparison(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n🎯 SUMMARY:")
    print("The model projection works best for:")
    print("✅ Configuration files (TOML, YAML, JSON)")
    print("✅ Structured content with clear boundaries")
    print("⚠️  Python files need better node extraction")
    print("⚠️  Markdown needs better section handling")


if __name__ == "__main__":
    main() 