#!/usr/bin/env python3
"""
Resolve merge conflicts for Healthcare CDC PR #8
This script resolves conflicts by keeping the develop branch version for most files
and the feature branch version for healthcare-specific changes.
"""

import os
import re


def resolve_conflict_keeping_develop(file_path: str) -> None:
    """Resolve conflict by keeping the develop branch version"""
    print(f"🔧 Resolving {file_path} - keeping develop version")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove all conflict markers and keep develop version
    # Pattern: <<<<<<< HEAD ... ======= ... >>>>>>> develop
    pattern = r'<<<<<<< HEAD.*?=======.*?>>>>>>> develop'
    resolved_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Also handle cases where there's no develop marker
    pattern2 = r'<<<<<<< HEAD.*?=======.*?>>>>>>> [^\n]+'
    resolved_content = re.sub(pattern2, '', resolved_content, flags=re.DOTALL)
    
    # Clean up any remaining conflict markers
    resolved_content = re.sub(r'<<<<<<< HEAD.*?=======.*?>>>>>>> [^\n]+', '', resolved_content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(resolved_content)

def resolve_conflict_keeping_feature(file_path: str) -> None:
    """Resolve conflict by keeping the feature branch version"""
    print(f"🔧 Resolving {file_path} - keeping feature version")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove conflict markers and keep the feature branch version (before =======)
    pattern = r'<<<<<<< HEAD.*?=======\s*(.*?)\s*>>>>>>> develop'
    resolved_content = re.sub(pattern, r'\1', content, flags=re.DOTALL)
    
    # Also handle cases where there's no develop marker
    pattern2 = r'<<<<<<< HEAD.*?=======\s*(.*?)\s*>>>>>>> [^\n]+'
    resolved_content = re.sub(pattern2, r'\1', resolved_content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(resolved_content)

def main() -> None:
    """Main conflict resolution function"""
    print("🚀 Starting Healthcare CDC PR #8 conflict resolution...")
    
    # Files to keep develop version (most files)
    develop_files = [
        "project_model.py",
        "project_model_registry.json",
        "scripts/mdc-linter.py",
        "scripts/regenerate_mdc_files.py",
        "scripts/run_live_smoke_test_direct.sh",
        "src/multi_agent_testing/__init__.py",
        "src/multi_agent_testing/cost_analysis.py",
        "src/multi_agent_testing/debug_anthropic_api.py",
        "src/multi_agent_testing/diversity_hypothesis_demo.py",
        "src/multi_agent_testing/diversity_synthesis_orchestrator.py",
        "src/multi_agent_testing/langgraph_diversity_orchestrator.py",
        "src/multi_agent_testing/live_smoke_test.py",
        "src/multi_agent_testing/live_smoke_test_langchain.py",
        "src/multi_agent_testing/meta_cognitive_orchestrator.py",
        "src/multi_agent_testing/test_anthropic_simple.py",
        "src/multi_agent_testing/test_meta_cognitive_orchestrator.py",
        "src/streamlit/__init__.py",
        "src/streamlit/openflow_quickstart_app.py",
        "tests/test_basic_validation.py",
        "tests/test_basic_validation_pytest.py",
        "tests/test_basic_validation_simple.py",
        "tests/test_cline_fresh_plan_blind_spots.py",
        "tests/test_cline_plan_blind_spots.py",
        "tests/test_code_quality.py",
        "tests/test_code_quality_comprehensive.py",
        "tests/test_core_concepts.py",
        "tests/test_data_fresh_cline_plan.py",
        "tests/test_file_existence.py",
        "tests/test_file_organization.py",
        "tests/test_gemini_2_5_flash_lite_pr_review.py",
        "tests/test_gemini_2_5_preview_pr_review.py",
        "tests/test_healthcare_cdc_requirements.py",
        "tests/test_makefile_integration.py",
        "tests/test_mdc_generator.py",
        "tests/test_rule_compliance.py",
        "tests/test_rule_compliance_enforcement.py",
        "tests/test_security_enhancements.py",
        "tests/test_uv_package_management.py",
        "tests/validate_healthcare_cdc_simple.py",
    ]
    
    # Files to keep feature version (healthcare-specific)
    feature_files = [
        "healthcare-cdc/healthcare_cdc_domain_model.py",
        "healthcare-cdc/sql/merge_cdc_operations.sql",
    ]
    
    # Resolve conflicts
    for file_path in develop_files:
        if os.path.exists(file_path):
            resolve_conflict_keeping_develop(file_path)
    
    for file_path in feature_files:
        if os.path.exists(file_path):
            resolve_conflict_keeping_feature(file_path)
    
    print("✅ Conflict resolution completed!")
    print("📝 Next steps:")
    print("   1. Review the resolved files")
    print("   2. Run: git add .")
    print("   3. Run: git commit -m 'Resolve merge conflicts for Healthcare CDC PR #8'")
    print("   4. Push the resolved branch")

if __name__ == "__main__":
    main() 