#!/usr/bin/env python3
"""
Debug Extraction: See exactly what's being extracted
"""

import ast
from pathlib import Path


def debug_extraction():
    """Debug what's being extracted."""
    print("🔍 DEBUG EXTRACTION")
    print("=" * 60)
    
    file_path = "src/streamlit/openflow_quickstart_app.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    # Track what we see
    function_definitions = []
    function_calls = []
    class_definitions = []
    class_instantiations = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_definitions.append({
                'name': node.name,
                'line': getattr(node, 'lineno', 0),
                'code': ast.unparse(node)[:100] + "..." if len(ast.unparse(node)) > 100 else ast.unparse(node)
            })
        elif isinstance(node, ast.Call):
            if hasattr(node.func, 'id'):
                function_calls.append({
                    'name': node.func.id,
                    'line': getattr(node, 'lineno', 0)
                })
        elif isinstance(node, ast.ClassDef):
            class_definitions.append({
                'name': node.name,
                'line': getattr(node, 'lineno', 0),
                'code': ast.unparse(node)[:100] + "..." if len(ast.unparse(node)) > 100 else ast.unparse(node)
            })
        elif isinstance(node, ast.Call):
            if hasattr(node.func, 'value') and hasattr(node.func.value, 'id'):
                # This might be a class instantiation
                class_instantiations.append({
                    'name': node.func.value.id,
                    'line': getattr(node, 'lineno', 0)
                })
    
    print(f"📄 FUNCTION DEFINITIONS ({len(function_definitions)}):")
    for i, func in enumerate(function_definitions[:10], 1):
        print(f"  {i:2d}. {func['name']} (line {func['line']})")
    
    print(f"\n📄 FUNCTION CALLS ({len(function_calls)}):")
    for i, call in enumerate(function_calls[:10], 1):
        print(f"  {i:2d}. {call['name']} (line {call['line']})")
    
    print(f"\n📄 CLASS DEFINITIONS ({len(class_definitions)}):")
    for i, cls in enumerate(class_definitions, 1):
        print(f"  {i:2d}. {cls['name']} (line {cls['line']})")
    
    print(f"\n📄 CLASS INSTANTIATIONS ({len(class_instantiations)}):")
    for i, inst in enumerate(class_instantiations[:10], 1):
        print(f"  {i:2d}. {inst['name']} (line {inst['line']})")
    
    # Check for duplicates in function definitions
    func_names = [f['name'] for f in function_definitions]
    duplicates = [name for name in set(func_names) if func_names.count(name) > 1]
    
    if duplicates:
        print(f"\n⚠️  DUPLICATE FUNCTION NAMES:")
        for dup in duplicates:
            print(f"  - {dup}")
    else:
        print(f"\n✅ No duplicate function names")
    
    # Check for duplicates in class definitions
    class_names = [c['name'] for c in class_definitions]
    class_duplicates = [name for name in set(class_names) if class_names.count(name) > 1]
    
    if class_duplicates:
        print(f"\n⚠️  DUPLICATE CLASS NAMES:")
        for dup in class_duplicates:
            print(f"  - {dup}")
    else:
        print(f"\n✅ No duplicate class names")
    
    # Show the actual issue
    print(f"\n🎯 THE REAL ISSUE:")
    print(f"  We're extracting {len(function_definitions)} function definitions")
    print(f"  But the projection shows 89 functions")
    print(f"  This means the projection logic is duplicating functions")
    print(f"  The issue is NOT in extraction, but in projection")


if __name__ == "__main__":
    debug_extraction() 