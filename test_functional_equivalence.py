#!/usr/bin/env python3
"""Test functional equivalence between original and reconstructed Python files"""

import subprocess
import tempfile
import os
import sys
from pathlib import Path
from model_driven_reconstructor import ModelDrivenReconstructor

def test_functional_equivalence(file_path: str, test_file_path: str = None) -> dict:
    """Test functional equivalence using unit tests"""
    
    # Find the test file if not provided
    if test_file_path is None:
        file_name = Path(file_path).stem
        possible_test_files = [
            Path(file_path).parent / f"test_{file_name}.py",
            Path(file_path).parent / f"{file_name}_test.py",
            Path("tests") / f"test_{file_name}.py",
            Path("tests") / f"{file_name}_test.py"
        ]
        
        for test_file in possible_test_files:
            if test_file.exists():
                test_file_path = str(test_file)
                break
    
    if not test_file_path or not Path(test_file_path).exists():
        return {
            "file_path": file_path,
            "error": "No test file found",
            "functional_equivalent": False
        }
    
    # Get the reconstructed content
    reconstructor = ModelDrivenReconstructor()
    try:
        reconstructed_content, metadata = reconstructor.reconstruct_from_model(file_path)
    except Exception as e:
        return {
            "file_path": file_path,
            "error": f"Reconstruction failed: {e}",
            "functional_equivalent": False
        }
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Copy test file to temp directory
        test_content = Path(test_file_path).read_text()
        temp_test_file = temp_dir_path / Path(test_file_path).name
        temp_test_file.write_text(test_content)
        
        # Test original file
        original_result = run_tests(file_path, str(temp_test_file))
        
        # Create reconstructed file
        reconstructed_file = temp_dir_path / Path(file_path).name
        reconstructed_file.write_text(reconstructed_content)
        
        # Test reconstructed file
        reconstructed_result = run_tests(str(reconstructed_file), str(temp_test_file))
        
        return {
            "file_path": file_path,
            "test_file": test_file_path,
            "original_tests": original_result,
            "reconstructed_tests": reconstructed_result,
            "functional_equivalent": original_result["success"] == reconstructed_result["success"],
            "reconstruction_metadata": metadata
        }

def run_tests(module_file: str, test_file: str) -> dict:
    """Run pytest on a test file"""
    try:
        # Add the module file to Python path
        module_dir = str(Path(module_file).parent)
        test_dir = str(Path(test_file).parent)
        
        # Run pytest
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--import-mode=importlib"
            ],
            capture_output=True,
            text=True,
            cwd=test_dir,
            env={**os.environ, "PYTHONPATH": f"{module_dir}:{os.environ.get('PYTHONPATH', '')}"}
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1,
            "stdout": "",
            "stderr": ""
        }

def main():
    """Test functional equivalence for key files"""
    test_cases = [
        {
            "file_path": "/home/lou/Documents/OpenFlow-Playground/src/security_first/https_enforcement.py",
            "test_file": "/home/lou/Documents/OpenFlow-Playground/src/security_first/test_https_enforcement.py"
        },
        {
            "file_path": "/home/lou/Documents/OpenFlow-Playground/scripts/mdc-linter.py",
            "test_file": "/home/lou/Documents/OpenFlow-Playground/tests/test_rule_compliance_enforcement.py"
        }
    ]
    
    print("🔍 Testing Functional Equivalence")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📁 Testing: {test_case['file_path']}")
        result = test_functional_equivalence(
            test_case['file_path'], 
            test_case['test_file']
        )
        
        print(f"  ✅ Functional Equivalent: {result.get('functional_equivalent', False)}")
        
        if result.get('original_tests'):
            orig = result['original_tests']
            print(f"  📊 Original Tests: {'✅ PASS' if orig['success'] else '❌ FAIL'}")
            if not orig['success']:
                print(f"     Error: {orig.get('stderr', 'Unknown error')[:200]}...")
        
        if result.get('reconstructed_tests'):
            recon = result['reconstructed_tests']
            print(f"  📊 Reconstructed Tests: {'✅ PASS' if recon['success'] else '❌ FAIL'}")
            if not recon['success']:
                print(f"     Error: {recon.get('stderr', 'Unknown error')[:200]}...")
        
        if result.get('error'):
            print(f"  ❌ Error: {result['error']}")

if __name__ == "__main__":
    main() 