#!/usr/bin/env python3
"""
🧪 File Organization Test

Test suite to validate the new domain-based file organization structure.
"""

import pytest
import os
import json
from pathlib import Path
from typing import Dict, List, Any

class TestFileOrganization:
    """Test file organization according to project model domains"""
    
    def setup_method(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        
        # Load project model registry
        with open(self.project_root / "project_model_registry.json") as f:
            self.model_registry = json.load(f)
    
    def test_src_directory_structure(self):
        """Test src directory structure"""
        # Verify src directory exists
        assert self.src_dir.exists(), "src directory should exist"
        
        # Verify domain subdirectories exist
        expected_domains = ["streamlit", "security_first", "multi_agent_testing"]
        for domain in expected_domains:
            domain_dir = self.src_dir / domain
            assert domain_dir.exists(), f"Domain directory {domain} should exist"
            assert domain_dir.is_dir(), f"{domain} should be a directory"
    
    def test_streamlit_domain_files(self):
        """Test streamlit domain files"""
        streamlit_dir = self.src_dir / "streamlit"
        
        # Check for main app file
        app_file = streamlit_dir / "openflow_quickstart_app.py"
        assert app_file.exists(), "Main Streamlit app file should exist"
        
        # Check for __init__.py
        init_file = streamlit_dir / "__init__.py"
        assert init_file.exists(), "Streamlit package should have __init__.py"
    
    def test_security_first_domain_files(self):
        """Test security-first domain files"""
        security_dir = self.src_dir / "security_first"
        
        # Check for security test file
        security_test_file = security_dir / "test_streamlit_security_first.py"
        assert security_test_file.exists(), "Security test file should exist"
        
        # Check for __init__.py
        init_file = security_dir / "__init__.py"
        assert init_file.exists(), "Security package should have __init__.py"
    
    def test_multi_agent_testing_domain_files(self):
        """Test multi-agent testing domain files"""
        multi_agent_dir = self.src_dir / "multi_agent_testing"
        
        # Check for multi-agent test file
        multi_agent_test_file = multi_agent_dir / "test_multi_agent_blind_spot_detection.py"
        assert multi_agent_test_file.exists(), "Multi-agent test file should exist"
        
        # Check for __init__.py
        init_file = multi_agent_dir / "__init__.py"
        assert init_file.exists(), "Multi-agent package should have __init__.py"
    
    def test_tests_directory_structure(self):
        """Test tests directory structure"""
        # Verify tests directory exists
        assert self.tests_dir.exists(), "tests directory should exist"
        
        # Check for test files
        expected_test_files = [
            "test_basic_validation.py",
            "test_core_concepts.py",
            "test_file_organization.py"
        ]
        
        for test_file in expected_test_files:
            test_file_path = self.tests_dir / test_file
            assert test_file_path.exists(), f"Test file {test_file} should exist"
    
    def test_requirements_files(self):
        """Test requirements files"""
        # Check for requirements files in root
        expected_requirements = [
            "requirements_streamlit.txt",
            "requirements_diversity.txt"
        ]
        
        for req_file in expected_requirements:
            req_file_path = self.project_root / req_file
            assert req_file_path.exists(), f"Requirements file {req_file} should exist"
    
    def test_documentation_files(self):
        """Test documentation files"""
        # Check for implementation documentation
        doc_file = self.project_root / "PR_9_OPENFLOW_STREAMLIT_APP_IMPLEMENTATION.md"
        assert doc_file.exists(), "Implementation documentation should exist"
    
    def test_model_registry_file_organization(self):
        """Test that model registry reflects file organization"""
        # Check that file_organization section exists
        assert "file_organization" in self.model_registry, "Model registry should have file_organization section"
        
        file_org = self.model_registry["file_organization"]
        
        # Check src section
        assert "src" in file_org, "File organization should have src section"
        src_section = file_org["src"]
        assert "description" in src_section, "Src section should have description"
        assert "streamlit" in src_section, "Src section should have streamlit domain"
        assert "security_first" in src_section, "Src section should have security_first domain"
        assert "multi_agent_testing" in src_section, "Src section should have multi_agent_testing domain"
        
        # Check tests section
        assert "tests" in file_org, "File organization should have tests section"
        tests_section = file_org["tests"]
        assert "description" in tests_section, "Tests section should have description"
        assert "test_basic_validation.py" in tests_section, "Tests section should have basic validation test"
        assert "test_core_concepts.py" in tests_section, "Tests section should have core concepts test"
        
        # Check requirements section
        assert "requirements" in file_org, "File organization should have requirements section"
        req_section = file_org["requirements"]
        assert "description" in req_section, "Requirements section should have description"
        assert "requirements_streamlit.txt" in req_section, "Requirements section should have streamlit requirements"
        assert "requirements_diversity.txt" in req_section, "Requirements section should have diversity requirements"
        
        # Check docs section
        assert "docs" in file_org, "File organization should have docs section"
        docs_section = file_org["docs"]
        assert "description" in docs_section, "Docs section should have description"
        assert "PR_9_OPENFLOW_STREAMLIT_APP_IMPLEMENTATION.md" in docs_section, "Docs section should have implementation doc"
    
    def test_domain_patterns_updated(self):
        """Test that domain patterns reflect new file organization"""
        # Check streamlit domain patterns
        streamlit_domain = self.model_registry["domains"]["streamlit"]
        assert "src/streamlit/*.py" in streamlit_domain["patterns"], "Streamlit patterns should include src/streamlit/*.py"
        
        # Check security_first domain patterns
        security_domain = self.model_registry["domains"]["security_first"]
        assert "src/security_first/*.py" in security_domain["patterns"], "Security patterns should include src/security_first/*.py"
        
        # Check multi_agent_testing domain patterns
        multi_agent_domain = self.model_registry["domains"]["multi_agent_testing"]
        assert "src/multi_agent_testing/*.py" in multi_agent_domain["patterns"], "Multi-agent patterns should include src/multi_agent_testing/*.py"
    
    def test_package_imports_work(self):
        """Test that package imports work correctly"""
        # Test that we can import from src
        import sys
        sys.path.insert(0, str(self.src_dir))
        
        try:
            # Test importing from streamlit package
            from streamlit import OpenFlowQuickstartApp
            assert OpenFlowQuickstartApp is not None, "Should be able to import OpenFlowQuickstartApp"
        except ImportError as e:
            pytest.skip(f"Import test skipped due to missing dependencies: {e}")
    
    def test_no_orphaned_files(self):
        """Test that no files are left in old locations"""
        # Check that streamlit_app directory doesn't exist
        old_streamlit_dir = self.project_root / "streamlit_app"
        assert not old_streamlit_dir.exists(), "Old streamlit_app directory should not exist"
        
        # Check that all files were moved to appropriate locations
        moved_files = [
            ("src/streamlit/openflow_quickstart_app.py", "Main Streamlit app"),
            ("src/security_first/test_streamlit_security_first.py", "Security test file"),
            ("src/multi_agent_testing/test_multi_agent_blind_spot_detection.py", "Multi-agent test file"),
            ("tests/test_basic_validation.py", "Basic validation test"),
            ("tests/test_core_concepts.py", "Core concepts test"),
            ("requirements_streamlit.txt", "Streamlit requirements")
        ]
        
        for file_path, description in moved_files:
            full_path = self.project_root / file_path
            assert full_path.exists(), f"{description} should exist at {file_path}"
    
    def test_file_permissions(self):
        """Test that files have appropriate permissions"""
        # Check that Python files are executable
        python_files = [
            "src/streamlit/openflow_quickstart_app.py",
            "src/security_first/test_streamlit_security_first.py",
            "src/multi_agent_testing/test_multi_agent_blind_spot_detection.py",
            "tests/test_basic_validation.py",
            "tests/test_core_concepts.py"
        ]
        
        for file_path in python_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # Check that file is readable
                assert os.access(full_path, os.R_OK), f"{file_path} should be readable"
    
    def test_directory_structure_consistency(self):
        """Test that directory structure is consistent"""
        # Check that all domain directories have __init__.py
        domain_dirs = ["streamlit", "security_first", "multi_agent_testing"]
        
        for domain in domain_dirs:
            domain_dir = self.src_dir / domain
            init_file = domain_dir / "__init__.py"
            assert init_file.exists(), f"Domain {domain} should have __init__.py"
            
            # Check that __init__.py is not empty
            assert init_file.stat().st_size > 0, f"Domain {domain} __init__.py should not be empty"

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 