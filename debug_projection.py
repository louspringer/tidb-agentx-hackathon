#!/usr/bin/env python3
"""
Debug Projection: Understand what's happening in the projection process
"""

import json
from pathlib import Path


def debug_projection():
    """Debug the projection process."""
    print("🔍 DEBUGGING PROJECTION PROCESS")
    print("=" * 60)
    
    # Load the fixed extracted nodes
    with open('fixed_extracted_nodes.json', 'r') as f:
        data = json.load(f)
    
    # Get all nodes sorted by order
    nodes = []
    for node_id, node_data in data['nodes'].items():
        nodes.append(node_data)
    
    nodes.sort(key=lambda n: n['metadata'].get('order', 0))
    
    print(f"📊 Total nodes loaded: {len(nodes)}")
    
    # Group by type
    imports = []
    constants = []
    classes = []
    functions = []
    
    for node in nodes:
        if node['type'] == "import":
            imports.append(node)
        elif node['type'] == "constant":
            constants.append(node)
        elif node['type'] == "class":
            classes.append(node)
        elif node['type'] == "function":
            functions.append(node)
    
    print(f"\n📄 NODES BY TYPE:")
    print(f"  Imports: {len(imports)}")
    print(f"  Constants: {len(constants)}")
    print(f"  Classes: {len(classes)}")
    print(f"  Functions: {len(functions)}")
    
    # Show projection order
    print(f"\n📄 PROJECTION ORDER:")
    
    # Add imports first
    for node in sorted(imports, key=lambda n: n['metadata'].get('order', 0)):
        order = node['metadata'].get('order', 0)
        print(f"  {order:3d}. IMPORT: {node['content'][:50]}...")
    
    # Add constants
    for node in sorted(constants, key=lambda n: n['metadata'].get('order', 0)):
        order = node['metadata'].get('order', 0)
        print(f"  {order:3d}. CONSTANT: {node['content'][:50]}...")
    
    # Add classes
    for node in sorted(classes, key=lambda n: n['metadata'].get('order', 0)):
        order = node['metadata'].get('order', 0)
        name = node['metadata'].get('class_name', 'unknown')
        print(f"  {order:3d}. CLASS: {name}")
    
    # Add functions
    for node in sorted(functions, key=lambda n: n['metadata'].get('order', 0)):
        order = node['metadata'].get('order', 0)
        name = node['metadata'].get('function_name', 'unknown')
        print(f"  {order:3d}. FUNCTION: {name}")
    
    # Test the projection logic
    print(f"\n🔧 TESTING PROJECTION LOGIC:")
    
    content_parts = []
    
    # Add imports first
    for node in sorted(imports, key=lambda n: n['metadata'].get('order', 0)):
        content_parts.append(node['content'])
    
    if imports:
        content_parts.append("")
    
    # Add constants
    for node in sorted(constants, key=lambda n: n['metadata'].get('order', 0)):
        content_parts.append(node['content'])
    
    if constants:
        content_parts.append("")
    
    # Add classes
    for node in sorted(classes, key=lambda n: n['metadata'].get('order', 0)):
        content_parts.append(node['content'])
        content_parts.append("")
    
    # Add functions
    for node in sorted(functions, key=lambda n: n['metadata'].get('order', 0)):
        content_parts.append(node['content'])
        content_parts.append("")
    
    projected_content = "\n".join(content_parts)
    
    print(f"📄 PROJECTED CONTENT LENGTH: {len(projected_content)} characters")
    print(f"📄 PROJECTED CONTENT LINES: {len(projected_content.split(chr(10)))}")
    
    # Show first few lines
    print(f"\n📄 FIRST 10 LINES OF PROJECTED CONTENT:")
    lines = projected_content.split('\n')[:10]
    for i, line in enumerate(lines, 1):
        print(f"{i:2d}: {line}")
    
    # Save the debug projection
    with open('debug_projected.py', 'w') as f:
        f.write(projected_content)
    
    print(f"\n✅ Saved debug projection to debug_projected.py")


if __name__ == "__main__":
    debug_projection() 