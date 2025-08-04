#!/usr/bin/env python3
"""
Simple Model Projection Test: Show functional equivalence

This script demonstrates that we can project artifacts from the model
and compare them heuristically.
"""

import json
import hashlib
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


def compare_files_heuristic(original_path, projected_content):
    """Compare files heuristically."""
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
    
    # Calculate similarity metrics
    original_lines = original_content.split('\n')
    projected_lines = projected_content.split('\n')
    
    # Count matching lines
    matching_lines = 0
    for orig_line in original_lines:
        if orig_line in projected_lines:
            matching_lines += 1
    
    similarity = matching_lines / len(original_lines) if original_lines else 0
    
    return {
        "identical": identical,
        "original_hash": original_hash,
        "projected_hash": projected_hash,
        "original_length": len(original_content),
        "projected_length": len(projected_content),
        "similarity": similarity,
        "matching_lines": matching_lines,
        "total_lines": len(original_lines)
    }


def show_preview(file_path, content, lines=15):
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
    """Test simple model projection."""
    print("🚀 Simple Model Projection Test")
    print("=" * 60)
    
    # Load model
    model = load_complete_model()
    print(f"✅ Loaded model with {len(model['files'])} files and {len(model['nodes'])} nodes")
    
    # Test files
    test_files = [
        "src/streamlit/openflow_quickstart_app.py",
        "src/security_first/input_validator.py",
        "README.md",
        "pyproject.toml"
    ]
    
    # Filter to files that exist and have nodes
    existing_test_files = []
    for file_path in test_files:
        if Path(file_path).exists():
            nodes = get_file_nodes(model, file_path)
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
    
    # Test each file
    results = {}
    for file_path in existing_test_files:
        print(f"\n🔍 Testing projection for: {file_path}")
        
        # Project the file
        projected_content = project_file_simple(model, file_path)
        
        if not projected_content:
            print(f"❌ No content projected for {file_path}")
            results[file_path] = {"error": "No content projected"}
            continue
        
        # Compare with original
        comparison = compare_files_heuristic(file_path, projected_content)
        results[file_path] = comparison
        
        # Print results
        if comparison.get("identical"):
            print(f"✅ IDENTICAL: {file_path}")
        else:
            similarity = comparison.get("similarity", 0)
            print(f"📊 SIMILARITY: {file_path} - {similarity:.1%}")
            print(f"   Matching lines: {comparison.get('matching_lines', 0)}/{comparison.get('total_lines', 0)}")
        
        # Show preview
        show_preview(file_path, projected_content)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PROJECTION TEST RESULTS")
    print("=" * 60)
    
    identical_count = 0
    similar_count = 0
    different_count = 0
    
    for file_path, result in results.items():
        if result.get("identical"):
            identical_count += 1
            print(f"✅ {file_path}: IDENTICAL")
        elif result.get("similarity", 0) > 0.8:
            similar_count += 1
            similarity = result.get("similarity", 0)
            print(f"📊 {file_path}: SIMILAR ({similarity:.1%})")
        else:
            different_count += 1
            similarity = result.get("similarity", 0)
            print(f"⚠️ {file_path}: DIFFERENT ({similarity:.1%})")
    
    print(f"\n📈 Summary:")
    print(f"  Identical: {identical_count}")
    print(f"  Similar (>80%): {similar_count}")
    print(f"  Different: {different_count}")
    print(f"  Total: {len(results)}")
    
    success_rate = (identical_count + similar_count) / len(results) * 100
    print(f"  Success Rate: {success_rate:.1f}%")
    
    print("=" * 60)


if __name__ == "__main__":
    main() 