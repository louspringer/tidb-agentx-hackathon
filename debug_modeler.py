#!/usr/bin/env python3
"""Debug script to test PythonASTModeler"""

from comprehensive_ast_modeler import PythonASTModeler
import ast

def test_modeler():
    modeler = PythonASTModeler()
    
    # Test AST parsing directly
    print("Testing AST parsing...")
    with open('src/security_first/https_enforcement.py', 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    
    print(f"AST parsing successful:")
    print(f"  Functions: {len(functions)}")
    print(f"  Classes: {len(classes)}")
    print(f"  Imports: {len(imports)}")
    
    # Test the modeler
    print("\nTesting PythonASTModeler...")
    try:
        model = modeler.model_python_file('src/security_first/https_enforcement.py')
        print(f"Model type: {model.model_type}")
        print(f"Functions in model: {len(model.model_data.get('functions', []))}")
        print(f"Classes in model: {len(model.model_data.get('classes', []))}")
        print(f"Imports in model: {len(model.model_data.get('imports', []))}")
        
        if model.model_type == 'basic':
            print("ERROR: Model fell back to basic!")
            print(f"Error in model data: {model.model_data.get('basic_error', 'No error')}")
        else:
            print("SUCCESS: Model is AST-based!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modeler() 