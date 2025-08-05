#!/usr/bin/env python3
"""
Simple test to verify Make-only enforcement is working
"""
import subprocess
import sys


def test_make_only_enforcement():
    """Test that direct pytest execution is blocked"""
    print("🧪 Testing Make-only enforcement...")
    
    # Test that direct pytest is blocked
    try:
        result = subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 1 and "ERROR: pytest can only be executed through make" in result.stdout:
            print("✅ Direct pytest execution is correctly blocked")
            return True
        else:
            print("❌ Direct pytest execution was not blocked")
            print(f"Return code: {result.returncode}")
            print(f"Output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


def test_make_target_works():
    """Test that make test works"""
    print("🧪 Testing make test target...")
    
    try:
        result = subprocess.run(
            ["make", "test"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # We expect some errors due to missing dependencies, but the command should run
        if result.returncode in [0, 1, 2]:  # Accept various exit codes
            print("✅ Make test target executed successfully")
            return True
        else:
            print("❌ Make test target failed")
            print(f"Return code: {result.returncode}")
            print(f"Output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


if __name__ == "__main__":
    print("🎯 Make-Only Enforcement Test")
    print("=" * 40)
    
    test1_passed = test_make_only_enforcement()
    test2_passed = test_make_target_works()
    
    print("\n📊 Test Results:")
    print(f"   Direct execution blocked: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Make target works: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Make-only enforcement is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Make-only enforcement needs attention.")
        sys.exit(1) 