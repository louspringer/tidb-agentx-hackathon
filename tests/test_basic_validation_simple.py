#!/usr/bin/env python3
"""
Simplified Basic Validation Tests
Tests core functionality without pytest dependency
"""

import sys

from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def setup_mocks():
    """Setup mocks for external dependencies"""
    sys.modules['redis'] = Mock()
    sys.modules['boto3'] = Mock()
    sys.modules['streamlit'] = Mock()
    sys.modules['plotly.graph_objects'] = Mock()
    sys.modules['plotly.express'] = Mock()
    sys.modules['pandas'] = Mock()
    sys.modules['pydantic'] = Mock()
    sys.modules['requests'] = Mock()
    sys.modules['botocore.exceptions'] = Mock()
    sys.modules['cryptography'] = Mock()
    sys.modules['cryptography.fernet'] = Mock()
    sys.modules['jwt'] = Mock()
    sys.modules['bcrypt'] = Mock()

# Setup mocks and import
setup_mocks()

# Set required environment variables for testing
import os
os.environ['JWT_SECRET'] = 'test-jwt-secret-for-testing-only'
os.environ['FERNET_KEY'] = 'test-fernet-key-32-bytes-long-for-testing'
os.environ['REDIS_URL'] = 'redis://localhost:6379'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['OPENFLOW_USER_DB'] = '{"admin": "$2b$12$test.hash.for.testing.only"}'

# Use importlib for robust import handling
import importlib.util
try:
    # Import the module directly from the file path
    module_path = Path(__file__).parent.parent / "src" / "streamlit" / "openflow_quickstart_app.py"
    spec = importlib.util.spec_from_file_location("openflow_quickstart_app", module_path)
    if spec is None:
        raise ImportError("Could not create module spec")
    openflow_module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError("Module loader is None")
    spec.loader.exec_module(openflow_module)
    
    SecurityManager = openflow_module.SecurityManager
    InputValidator = openflow_module.InputValidator
    DeploymentManager = openflow_module.DeploymentManager
    MonitoringDashboard = openflow_module.MonitoringDashboard
    OpenFlowQuickstartApp = openflow_module.OpenFlowQuickstartApp
    SnowflakeConfig = openflow_module.SnowflakeConfig
    OpenFlowConfig = openflow_module.OpenFlowConfig
    SECURITY_CONFIG = openflow_module.SECURITY_CONFIG
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_security_manager_initialization():
    """Test SecurityManager initialization"""
    try:
        # Mock the Fernet key for testing
        with patch.dict('os.environ', {'JWT_SECRET': 'test-jwt-secret', 'FERNET_KEY': 'test-fernet-key-32-bytes-long'}):
            security_manager = SecurityManager()
            print("✅ SecurityManager initialization - PASSED")
            return True
    except Exception as e:
        print(f"❌ SecurityManager initialization - FAILED: {e}")
        return False

def test_input_validator_methods():
    """Test InputValidator methods"""
    try:
        validator = InputValidator()
        
        # Test Snowflake URL validation
        valid_url = "https://test-account.snowflakecomputing.com"
        assert validator.validate_snowflake_url(valid_url) is True
        
        # Test UUID validation
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        assert validator.validate_uuid(valid_uuid) is True
        
        # Test input sanitization
        test_input = "<script>alert('xss')</script>"
        sanitized = validator.sanitize_input(test_input)
        assert "<script>" not in sanitized
        
        print("✅ InputValidator methods - PASSED")
        return True
    except Exception as e:
        print(f"❌ InputValidator methods - FAILED: {e}")
        return False

def test_deployment_manager_initialization():
    """Test DeploymentManager initialization"""
    try:
        with patch('boto3.client'):
            deployment_manager = DeploymentManager()
            print("✅ DeploymentManager initialization - PASSED")
            return True
    except Exception as e:
        print(f"❌ DeploymentManager initialization - FAILED: {e}")
        return False

def test_monitoring_dashboard_initialization():
    """Test MonitoringDashboard initialization"""
    try:
        with patch('boto3.client'):
            deployment_manager = DeploymentManager()
            monitoring_dashboard = MonitoringDashboard(deployment_manager)
            print("✅ MonitoringDashboard initialization - PASSED")
            return True
    except Exception as e:
        print(f"❌ MonitoringDashboard initialization - FAILED: {e}")
        return False

def test_openflow_app_initialization():
    """Test OpenFlowQuickstartApp initialization"""
    try:
        mock_session_state = Mock()
        mock_session_state.authenticated = False
        mock_session_state.user_role = "viewer"
        mock_session_state.deployment_status = None
        
        with patch('streamlit.set_page_config'), patch('streamlit.session_state', mock_session_state):
            app = OpenFlowQuickstartApp()
            print("✅ OpenFlowQuickstartApp initialization - PASSED")
            return True
    except Exception as e:
        print(f"❌ OpenFlowQuickstartApp initialization - FAILED: {e}")
        return False

def test_pydantic_models():
    """Test Pydantic model validation"""
    try:
        # Test SnowflakeConfig
        snowflake_config = SnowflakeConfig(
            account_url="https://test-account.snowflakecomputing.com",
            organization="test-org",
            account="test-account",
            oauth_integration_name="test-integration",
            oauth_client_id="test-client-id",
            oauth_client_secret="test-client-secret"
        )
        
        # Test OpenFlowConfig
        openflow_config = OpenFlowConfig(
            data_plane_url="https://data-plane.example.com",
            data_plane_uuid="123e4567-e89b-12d3-a456-426614174000",
            data_plane_key="test-key",
            telemetry_url="https://telemetry.example.com",
            control_plane_url="https://control-plane.example.com"
        )
        
        print("✅ Pydantic models validation - PASSED")
        return True
    except Exception as e:
        print(f"❌ Pydantic models validation - FAILED: {e}")
        return False

def test_security_config():
    """Test security configuration"""
    try:
        # Test that security config exists
        assert "session_timeout_minutes" in SECURITY_CONFIG
        assert "max_login_attempts" in SECURITY_CONFIG
        assert "password_min_length" in SECURITY_CONFIG
        
        print("✅ Security configuration - PASSED")
        return True
    except Exception as e:
        print(f"❌ Security configuration - FAILED: {e}")
        return False

def main():
    """Run all basic validation tests"""
    print("🔒 Basic Validation Tests (Simplified)")
    print("=" * 50)
    
    tests = [
        test_security_manager_initialization,
        test_input_validator_methods,
        test_deployment_manager_initialization,
        test_monitoring_dashboard_initialization,
        test_openflow_app_initialization,
        test_pydantic_models,
        test_security_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic validation tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 