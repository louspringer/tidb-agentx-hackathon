#!/usr/bin/env python3
"""
File Existence and Structure Validation Tests
Tests that all expected files exist and are properly structured
"""

import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

class FileExistenceValidator:
    """Validates that expected files exist and are properly structured"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def test_rate_limiting_module_exists(self):
        """Test that rate_limiting.py exists and is properly structured"""
        rate_limit_file = self.project_root / "src" / "security_first" / "rate_limiting.py"
        
        # Check file exists
        assert rate_limit_file.exists(), f"Rate limiting module not found: {rate_limit_file}"
        
        # Check file is readable
        with open(rate_limit_file, 'r') as f:
            content = f.read()
        
        # Check it contains the RateLimiting class
        assert "class RateLimiting" in content, "RateLimiting class not found in rate_limiting.py"
        
        # Check it has the required methods
        required_methods = [
            "check_rate_limit",
            "get_remaining_requests", 
            "reset_rate_limit",
            "get_rate_limit_info"
        ]
        
        for method in required_methods:
            assert f"def {method}" in content, f"Method {method} not found in rate_limiting.py"
        
        print("✅ Rate limiting module exists and is properly structured")
        return True
    
    def test_https_enforcement_module_exists(self):
        """Test that https_enforcement.py exists and is properly structured"""
        https_file = self.project_root / "src" / "security_first" / "https_enforcement.py"
        
        # Check file exists
        assert https_file.exists(), f"HTTPS enforcement module not found: {https_file}"
        
        # Check file is readable
        with open(https_file, 'r') as f:
            content = f.read()
        
        # Check it contains the HTTPSEnforcement class
        assert "class HTTPSEnforcement" in content, "HTTPSEnforcement class not found in https_enforcement.py"
        
        # Check it has the required methods
        required_methods = [
            "_create_ssl_context",
            "validate_https_url",
            "enforce_https_redirect",
            "validate_ssl_certificate"
        ]
        
        for method in required_methods:
            assert f"def {method}" in content, f"Method {method} not found in https_enforcement.py"
        
        print("✅ HTTPS enforcement module exists and is properly structured")
        return True
    
    def test_csrf_protection_exists(self):
        """Test that CSRF protection is implemented"""
        https_file = self.project_root / "src" / "security_first" / "https_enforcement.py"
        
        # Check file exists
        assert https_file.exists(), f"HTTPS enforcement module not found: {https_file}"
        
        # Check file is readable
        with open(https_file, 'r') as f:
            content = f.read()
        
        # Check it contains the CSRFProtection class
        assert "class CSRFProtection" in content, "CSRFProtection class not found in https_enforcement.py"
        
        # Check it has the required methods
        required_methods = [
            "generate_csrf_token",
            "validate_csrf_token"
        ]
        
        for method in required_methods:
            assert f"def {method}" in content, f"Method {method} not found in https_enforcement.py"
        
        print("✅ CSRF protection exists and is properly structured")
        return True
    
    def test_security_manager_exists(self):
        """Test that SecurityManager exists and is properly structured"""
        app_file = self.project_root / "src" / "streamlit" / "openflow_quickstart_app.py"
        
        # Check file exists
        assert app_file.exists(), f"Streamlit app not found: {app_file}"
        
        # Check file is readable
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check it contains the SecurityManager class
        assert "class SecurityManager" in content, "SecurityManager class not found in openflow_quickstart_app.py"
        
        # Check it has the required methods
        required_methods = [
            "encrypt_credential",
            "decrypt_credential",
            "store_credential_secure",
            "get_credential_secure",
            "create_session_token",
            "validate_session"
        ]
        
        for method in required_methods:
            assert f"def {method}" in content, f"Method {method} not found in SecurityManager"
        
        print("✅ SecurityManager exists and is properly structured")
        return True
    
    def test_input_validator_exists(self):
        """Test that InputValidator exists and is properly structured"""
        app_file = self.project_root / "src" / "streamlit" / "openflow_quickstart_app.py"
        
        # Check file exists
        assert app_file.exists(), f"Streamlit app not found: {app_file}"
        
        # Check file is readable
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check it contains the InputValidator class
        assert "class InputValidator" in content, "InputValidator class not found in openflow_quickstart_app.py"
        
        # Check it has the required methods
        required_methods = [
            "validate_snowflake_url",
            "validate_uuid",
            "sanitize_input",
            "validate_oauth_credentials"
        ]
        
        for method in required_methods:
            assert f"def {method}" in content, f"Method {method} not found in InputValidator"
        
        print("✅ InputValidator exists and is properly structured")
        return True

def test_all_required_files_exist():
    """Test that all required files exist and are properly structured"""
    validator = FileExistenceValidator()
    
    tests = [
        validator.test_rate_limiting_module_exists,
        validator.test_https_enforcement_module_exists,
        validator.test_csrf_protection_exists,
        validator.test_security_manager_exists,
        validator.test_input_validator_exists
    ]
    
    for test in tests:
        test()
    
    print("✅ All required files exist and are properly structured")

if __name__ == "__main__":
    print("🔍 Testing File Existence and Structure")
    print("=" * 50)
    
    test_all_required_files_exist()
    
    print("\n✅ All file existence tests passed!") 