#!/usr/bin/env python3
"""
Simplified Basic Validation Tests
Tests core functionality without pytest dependency
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def setup_mocks() -> None:
    """Setup mocks for external dependencies"""
    sys.modules["redis"] = Mock()
    sys.modules["boto3"] = Mock()
    sys.modules["streamlit"] = Mock()
    sys.modules["plotly.graph_objects"] = Mock()
    sys.modules["plotly.express"] = Mock()
    sys.modules["pandas"] = Mock()
    # Don't mock pydantic - we need real Pydantic models
    sys.modules["requests"] = Mock()
    sys.modules["botocore.exceptions"] = Mock()
    sys.modules["cryptography"] = Mock()
    sys.modules["cryptography.fernet"] = Mock()
    sys.modules["jwt"] = Mock()
    sys.modules["bcrypt"] = Mock()


# Setup mocks and import
setup_mocks()

# Set required environment variables for testing
os.environ["JWT_SECRET"] = "test-jwt-secret-for-testing-only"
os.environ["FERNET_KEY"] = "test-fernet-key-32-bytes-long-for-testing"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["OPENFLOW_USER_DB"] = '{"admin": "$2b$12$test.hash.for.testing.only"}'

# Import the module directly from the file path
module_path: Any = (
    Path(__file__).parent.parent / "src" / "streamlit" / "openflow_quickstart_app.py"
)
spec: Any = importlib.util.spec_from_file_location(
    "openflow_quickstart_app", module_path
)
if spec is None:
    raise ImportError("Could not create module spec")
openflow_module: Any = importlib.util.module_from_spec(spec)
if spec.loader is None:
    raise ImportError("Module loader is None")
spec.loader.exec_module(openflow_module)

SecurityManager: Any = openflow_module.SecurityManager
InputValidator: Any = openflow_module.InputValidator
DeploymentManager: Any = openflow_module.DeploymentManager
MonitoringDashboard: Any = openflow_module.MonitoringDashboard
OpenFlowQuickstartApp: Any = openflow_module.OpenFlowQuickstartApp
SnowflakeConfig: Any = openflow_module.SnowflakeConfig
OpenFlowConfig: Any = openflow_module.OpenFlowConfig
SECURITY_CONFIG: Any = openflow_module.SECURITY_CONFIG


def test_security_manager_initialization() -> None:
    """Test SecurityManager initialization"""
    # Mock the Fernet key for testing
    with patch.dict(
        "os.environ",
        {
            "JWT_SECRET": "test-jwt-secret",
            "FERNET_KEY": "test-fernet-key-32-bytes-long",
        },
    ):
        manager = SecurityManager()
        assert manager is not None, "SecurityManager should be initialized"
        print("✅ SecurityManager initialization - PASSED")


def test_input_validator_methods() -> None:
    """Test InputValidator methods"""
    validator = InputValidator()

    # Test UUID validation
    test_uuid = "123e4567-e89b-12d3-a456-426614174000"
    result = validator.validate_uuid(test_uuid)
    assert result is True, f"UUID validation failed for {test_uuid}"

    # Test Snowflake URL validation
    test_url = "https://account.snowflakecomputing.com"
    result = validator.validate_snowflake_url(test_url)
    assert result is True, f"Snowflake URL validation failed for {test_url}"

    print("✅ InputValidator methods - PASSED")


def test_deployment_manager_initialization() -> None:
    """Test DeploymentManager initialization"""
    manager = DeploymentManager()
    assert manager is not None, "DeploymentManager should be initialized"
    print("✅ DeploymentManager initialization - PASSED")


def test_monitoring_dashboard_initialization() -> None:
    """Test MonitoringDashboard initialization"""
    # Create a mock deployment manager
    mock_deployment_manager = Mock()
    dashboard = MonitoringDashboard(deployment_manager=mock_deployment_manager)
    assert dashboard is not None, "MonitoringDashboard should be initialized"
    print("✅ MonitoringDashboard initialization - PASSED")


def test_openflow_app_initialization() -> None:
    """Test OpenFlowQuickstartApp initialization"""
    app = OpenFlowQuickstartApp()
    assert app is not None, "OpenFlowQuickstartApp should be initialized"
    print("✅ OpenFlowQuickstartApp initialization - PASSED")


def test_config_classes() -> None:
    """Test configuration classes"""
    # Test SnowflakeConfig
    snowflake_config = SnowflakeConfig(
        account="test-account",
        account_url="https://test-account.snowflakecomputing.com",
        organization="test-org",
        oauth_integration_name="test-oauth",
        oauth_client_id="test-client-id",
        oauth_client_secret="test-client-secret",
    )
    assert snowflake_config.account == "test-account"
    assert snowflake_config.account_url == "https://test-account.snowflakecomputing.com"

    # Test OpenFlowConfig
    openflow_config = OpenFlowConfig(
        data_plane_url="https://test-data-plane.com",
        data_plane_uuid="12345678-1234-1234-1234-123456789012",
        data_plane_key="test-key",
        telemetry_url="https://test-telemetry.com",
        control_plane_url="https://test-control-plane.com",
    )
    assert openflow_config.data_plane_url == "https://test-data-plane.com"
    assert openflow_config.data_plane_uuid == "12345678-1234-1234-1234-123456789012"

    print("✅ Configuration classes - PASSED")


def test_security_config() -> None:
    """Test security configuration"""
    assert SECURITY_CONFIG is not None, "SECURITY_CONFIG should be defined"
    assert "jwt_secret" in SECURITY_CONFIG, "JWT secret should be in config"
    assert "fernet_key" in SECURITY_CONFIG, "Fernet key should be in config"
    print("✅ Security configuration - PASSED")


def main() -> bool:
    """Run all basic validation tests"""
    print("🧪 Running Basic Validation Tests")
    print("=" * 50)

    tests = [
        test_security_manager_initialization,
        test_input_validator_methods,
        test_deployment_manager_initialization,
        test_monitoring_dashboard_initialization,
        test_openflow_app_initialization,
        test_config_classes,
        test_security_config,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic validation tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
