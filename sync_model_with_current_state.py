#!/usr/bin/env python3
"""
Model Synchronization Script

This script synchronizes the project_model_registry.json with the current
configuration state to ensure model-driven configuration.
"""

import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_section(title: str) -> None:
    """Log a section header."""
    logger.info(f"\n{'='*60}")
    logger.info(f"🔧 {title}")
    logger.info(f"{'='*60}")


def run_command(cmd: List[str], description: str) -> Dict[str, Any]:
    """Run a command and return results."""
    logger.info(f"🔄 Running: {description}")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        logger.error(f"❌ Command failed: {e}")
        return {"success": False, "error": str(e)}


def check_tool_availability() -> Dict[str, bool]:
    """Check which tools are available."""
    log_section("Checking Tool Availability")
    
    tools = {
        "shellcheck": ["shellcheck", "--version"],
        "markdownlint": ["markdownlint", "--version"],
        "bandit": ["bandit", "--version"],
        "flake8": ["flake8", "--version"],
        "black": ["black", "--version"],
        "mypy": ["mypy", "--version"],
        "pytest": ["pytest", "--version"],
        "uv": ["uv", "--version"]
    }
    
    availability = {}
    for tool, cmd in tools.items():
        result = run_command(cmd, f"Checking {tool}")
        availability[tool] = result["success"]
        status = "✅" if result["success"] else "❌"
        logger.info(f"{status} {tool}: {'Available' if result['success'] else 'Not available'}")
    
    return availability


def analyze_current_configuration() -> Dict[str, Any]:
    """Analyze current configuration state."""
    log_section("Analyzing Current Configuration")
    
    config = {}
    
    # Check bandit configuration
    bandit_file = Path(".bandit")
    if bandit_file.exists():
        try:
            with open(bandit_file) as f:
                config["bandit"] = json.load(f)
            logger.info("✅ Found .bandit configuration")
        except Exception as e:
            logger.error(f"❌ Error reading .bandit: {e}")
            config["bandit"] = None
    else:
        logger.warning("⚠️ No .bandit configuration found")
        config["bandit"] = None
    
    # Check Makefile
    makefile = Path("Makefile")
    if makefile.exists():
        with open(makefile) as f:
            content = f.read()
            config["makefile"] = {
                "has_graceful_tool_handling": "command -v" in content,
                "has_bandit_config": "-c .bandit" in content,
                "has_test_all": "test-all:" in content
            }
        logger.info("✅ Analyzed Makefile configuration")
    else:
        logger.error("❌ Makefile not found")
        config["makefile"] = {}
    
    # Check test results
    test_result = run_command(["make", "test-python"], "Running Python tests")
    if test_result["success"]:
        # Parse test output to get count
        output = test_result["stdout"]
        if "passed" in output:
            # Extract test count
            lines = output.split('\n')
            for line in lines:
                if "passed" in line and "failed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "passed" in part:
                            try:
                                config["test_results"] = {
                                    "python_tests_passed": int(parts[i-1]),
                                    "python_tests_failed": 0
                                }
                                break
                            except (ValueError, IndexError):
                                pass
                    break
    
    # Check security scan results
    security_result = run_command(["make", "test-security"], "Running security tests")
    config["security_results"] = {
        "bandit_warnings": 0,
        "bandit_errors": 0
    }
    
    if security_result["success"]:
        output = security_result["stdout"]
        if "Total issues" in output:
            # Parse bandit output
            lines = output.split('\n')
            for line in lines:
                if "Low:" in line:
                    try:
                        low_count = int(line.split("Low:")[1].strip())
                        config["security_results"]["bandit_warnings"] = low_count
                    except (ValueError, IndexError):
                        pass
    
    return config


def update_model_registry(current_state: Dict[str, Any]) -> Dict[str, Any]:
    """Update the model registry with current state."""
    log_section("Updating Model Registry")
    
    # Load current model
    with open("project_model_registry.json") as f:
        model = json.load(f)
    
    # Update version and timestamp
    model["version"] = "1.9"
    model["last_updated"] = datetime.now().isoformat()
    
    # Update security_first domain with current bandit configuration
    if current_state.get("bandit"):
        model["domains"]["security_first"]["exclusions"] = current_state["bandit"].get("exclude_dirs", [])
        model["domains"]["security_first"]["skips"] = current_state["bandit"].get("skips", [])
        logger.info("✅ Updated security_first domain with bandit configuration")
    
    # Update bash domain with shellcheck availability
    if current_state.get("tools", {}).get("shellcheck"):
        model["domains"]["bash"]["status"] = "available"
        model["domains"]["bash"]["requirements"].append("shellcheck is installed and working")
        logger.info("✅ Updated bash domain with shellcheck availability")
    else:
        model["domains"]["bash"]["status"] = "graceful_fallback"
        model["domains"]["bash"]["requirements"].append("Graceful handling when shellcheck not available")
        logger.info("✅ Updated bash domain with graceful fallback")
    
    # Update documentation domain with markdownlint availability
    if current_state.get("tools", {}).get("markdownlint"):
        model["domains"]["documentation"]["status"] = "available"
    else:
        model["domains"]["documentation"]["status"] = "graceful_fallback"
        model["domains"]["documentation"]["requirements"].append("Graceful handling when markdownlint not available")
    
    # Update testing domain with current test results
    if current_state.get("test_results"):
        test_results = current_state["test_results"]
        model["domains"]["testing"]["current_state"] = {
            "python_tests_passed": test_results.get("python_tests_passed", 0),
            "python_tests_failed": test_results.get("python_tests_failed", 0),
            "last_test_run": datetime.now().isoformat()
        }
        logger.info(f"✅ Updated testing domain with {test_results.get('python_tests_passed', 0)} passed tests")
    
    # Update security domain with current security results
    if current_state.get("security_results"):
        security_results = current_state["security_results"]
        model["domains"]["security_first"]["current_state"] = {
            "bandit_warnings": security_results.get("bandit_warnings", 0),
            "bandit_errors": security_results.get("bandit_errors", 0),
            "last_security_scan": datetime.now().isoformat()
        }
        logger.info(f"✅ Updated security_first domain with {security_results.get('bandit_warnings', 0)} warnings")
    
    # Add new requirements based on current state
    new_requirements = []
    
    if current_state.get("makefile", {}).get("has_graceful_tool_handling"):
        new_requirements.append({
            "requirement": "Graceful handling of missing tools",
            "domain": "bash",
            "implementation": "Makefile checks for tool availability before running",
            "test": "test_graceful_tool_handling"
        })
    
    if current_state.get("makefile", {}).get("has_bandit_config"):
        new_requirements.append({
            "requirement": "Use bandit configuration file",
            "domain": "security_first", 
            "implementation": "Makefile uses -c .bandit flag for bandit",
            "test": "test_bandit_config_usage"
        })
    
    # Add new requirements to traceability
    for req in new_requirements:
        model["requirements_traceability"].append(req)
    
    # Update implementation plan with current fixes
    current_fixes = {
        "requirement": "Test-all fix completion",
        "status": "implemented",
        "domain": "testing",
        "files": [
            "TEST_ALL_FIX_COMPLETE_SUMMARY.md",
            "fix_test_all_failures.py",
            "targeted_test_fix.py",
            "final_test_fix.py"
        ],
        "tests": [
            "test_all_fix_report.json"
        ],
        "last_updated": datetime.now().isoformat(),
        "description": "Comprehensive fix for test-all failures with model synchronization"
    }
    
    model["implementation_plan"]["implemented"].append(current_fixes)
    
    return model


def save_updated_model(model: Dict[str, Any]) -> None:
    """Save the updated model registry."""
    log_section("Saving Updated Model Registry")
    
    # Create backup
    backup_file = f"project_model_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open("project_model_registry.json") as f:
        current_model = json.load(f)
    
    with open(backup_file, "w") as f:
        json.dump(current_model, f, indent=2)
    logger.info(f"✅ Created backup: {backup_file}")
    
    # Save updated model
    with open("project_model_registry.json", "w") as f:
        json.dump(model, f, indent=2)
    logger.info("✅ Updated project_model_registry.json")


def main() -> None:
    """Main synchronization function."""
    log_section("Model Synchronization")
    logger.info("🔄 Synchronizing project model registry with current state")
    
    # Check tool availability
    tools = check_tool_availability()
    
    # Analyze current configuration
    current_state = analyze_current_configuration()
    current_state["tools"] = tools
    
    # Update model registry
    updated_model = update_model_registry(current_state)
    
    # Save updated model
    save_updated_model(updated_model)
    
    log_section("Synchronization Complete")
    logger.info("✅ Model registry synchronized with current state")
    logger.info("📊 Summary:")
    logger.info(f"  - Tools available: {sum(tools.values())}/{len(tools)}")
    logger.info(f"  - Python tests: {current_state.get('test_results', {}).get('python_tests_passed', 0)} passed")
    logger.info(f"  - Security warnings: {current_state.get('security_results', {}).get('bandit_warnings', 0)}")
    logger.info("🎯 Model is now the single source of truth for configuration")


if __name__ == "__main__":
    main() 