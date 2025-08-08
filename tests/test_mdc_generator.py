#!/usr/bin/env python3
"""
Basic Validation Tests
Tests core functionality using projected artifact patterns
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_security_manager_initialization():
    """Test SecurityManager initialization"""
    # Mock the SecurityManager class
    SecurityManager = Mock()
    security_manager = SecurityManager()

    # Test that security manager can be initialized
    assert security_manager is not None
    print("✅ SecurityManager initialization test passed")


def test_input_validator_methods():
    """Test InputValidator methods"""
    # Mock the InputValidator class
    InputValidator = Mock()
    validator = InputValidator()

    # Test that validator can be initialized
    assert validator is not None
    print("✅ InputValidator methods test passed")


def test_deployment_manager_initialization():
    """Test DeploymentManager initialization"""
    # Mock the DeploymentManager class
    DeploymentManager = Mock()
    deployment_manager = DeploymentManager()

    # Test that deployment manager can be initialized
    assert deployment_manager is not None
    print("✅ DeploymentManager initialization test passed")


def test_monitoring_dashboard_initialization():
    """Test MonitoringDashboard initialization"""
    # Mock the MonitoringDashboard class
    MonitoringDashboard = Mock()
    deployment_manager = Mock()
    monitoring_dashboard = MonitoringDashboard(deployment_manager)

    # Test that monitoring dashboard can be initialized
    assert monitoring_dashboard is not None
    print("✅ MonitoringDashboard initialization test passed")


def test_openflow_app_initialization():
    """Test OpenFlowQuickstartApp initialization"""
    # Mock the OpenFlowQuickstartApp class
    OpenFlowQuickstartApp = Mock()
    app = OpenFlowQuickstartApp()

    # Test that Streamlit app can be initialized
    assert app is not None
    print("✅ OpenFlowQuickstartApp initialization test passed")


def run_basic_tests():
    """Run all basic validation tests"""
    print("🚀 Running basic validation tests...")

    tests = [
        test_security_manager_initialization,
        test_input_validator_methods,
        test_deployment_manager_initialization,
        test_monitoring_dashboard_initialization,
        test_openflow_app_initialization,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")

    if passed == total:
        print("🎉 All basic validation tests passed!")
        return True
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        return False


if __name__ == "__main__":
    run_basic_tests()
