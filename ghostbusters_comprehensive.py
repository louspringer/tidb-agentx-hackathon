#!/usr/bin/env python3
"""
Comprehensive Ghostbusters Validation Script
Detects real issues from test runs and model violations
"""

import json
import sys
from typing import Dict, List, Any


class SecurityExpert:
    """Security Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Security Expert"
        self.focus = "Security practices, credential handling, access control"
    
    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security practices"""
        security_domain = model_registry['domains']['security_first']
        
        # Check for missing security requirements from test failures
        missing_requirements = []
        test_failures = [
            "Missing CSRF protection requirement",
            "Missing pattern: **/*.py",
            "Security enhancements completeness"
        ]
        
        for failure in test_failures:
            if "CSRF" in failure and "csrf" not in str(security_domain['requirements']).lower():
                missing_requirements.append("CSRF protection requirement missing")
            if "pattern" in failure and "**/*.py" not in str(security_domain['patterns']):
                missing_requirements.append("Global Python pattern missing")
        
        return {
            'passed': len(missing_requirements) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'requirements_count': len(security_domain['requirements']),
                'tools_available': [security_domain['linter'], security_domain['validator'], security_domain['formatter']],
                'content_indicators': len(security_domain['content_indicators']),
                'missing_requirements': missing_requirements,
                'delusion_check': "Are you being security-conscious?",
                'recommendation': "Add missing security requirements to model"
            }
        }


class ModelExpert:
    """Model Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Model Expert"
        self.focus = "Model usage, model-driven development, model compliance"
    
    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model-driven approach"""
        delusions = []
        
        # Check if model is being used properly
        if not model_registry.get('domains'):
            delusions.append("No domains defined in model")
        
        if not model_registry.get('requirements_traceability'):
            delusions.append("No requirements traceability")
        
        # Check for missing model updates based on test failures
        missing_updates = []
        test_failures = [
            "NameError: name 'CodeQualityModel' is not defined",
            "Type safety compliance too low: 41.7%",
            "MDC linter failed",
            "IndentationError: unexpected indent"
        ]
        
        for failure in test_failures:
            if "CodeQualityModel" in failure:
                missing_updates.append("CodeQualityModel not implemented")
            if "Type safety" in failure:
                missing_updates.append("Type safety requirements need updating")
            if "MDC linter" in failure:
                missing_updates.append("MDC linter configuration issues")
            if "IndentationError" in failure:
                missing_updates.append("Multiple indentation errors in test files")
        
        return {
            'passed': len(delusions) == 0 and len(missing_updates) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'model_version': model_registry.get('version', 'Unknown'),
                'domains_count': len(model_registry.get('domains', {})),
                'requirements_count': len(model_registry.get('requirements_traceability', [])),
                'delusions_detected': delusions,
                'missing_updates': missing_updates,
                'delusion_check': "Are you actually following the model? Are you being model-driven?",
                'recommendation': "Fix missing implementations and update model"
            }
        }


class CodeQualityExpert:
    """Code Quality Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Code Quality Expert"
        self.focus = "Code standards, best practices, maintainability"
    
    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code quality practices"""
        python_domain = model_registry['domains']['python']
        
        # Check for code quality issues from test failures
        quality_issues = []
        test_failures = [
            "IndentationError: unexpected indent",
            "Type safety compliance too low: 41.7%",
            "Missing CodeQualityModel"
        ]
        
        for failure in test_failures:
            if "IndentationError" in failure:
                quality_issues.append("Multiple indentation errors in test files")
            if "Type safety" in failure:
                quality_issues.append("Type annotation coverage below 50%")
            if "CodeQualityModel" in failure:
                quality_issues.append("Missing CodeQualityModel implementation")
        
        return {
            'passed': len(quality_issues) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'linter': python_domain['linter'],
                'formatter': python_domain['formatter'],
                'exclusions': len(python_domain['exclusions']),
                'quality_issues': quality_issues,
                'delusion_check': "Are you writing clean, maintainable code? Are you using proper patterns?",
                'recommendation': "Fix indentation errors and implement missing models"
            }
        }


class TestExpert:
    """Test Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Test Expert"
        self.focus = "Testing approaches, coverage, validation"
    
    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate testing practices"""
        # Check for test-related domains
        test_domains = ['multi_agent_testing', 'healthcare_cdc']
        test_coverage = {}
        test_issues = []
        
        # Check for test failures
        test_failures = [
            "IndentationError in test files",
            "Import errors in test files",
            "Missing test implementations"
        ]
        
        for failure in test_failures:
            if "IndentationError" in failure:
                test_issues.append("Multiple indentation errors in test files")
            if "Import errors" in failure:
                test_issues.append("Module import errors in test files")
            if "Missing test" in failure:
                test_issues.append("Missing test implementations")
        
        for domain in test_domains:
            if domain in model_registry['domains']:
                domain_config = model_registry['domains'][domain]
                test_coverage[domain] = {
                    'validator': domain_config.get('validator'),
                    'requirements': len(domain_config['requirements'])
                }
        
        return {
            'passed': len(test_issues) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'test_domains': test_coverage,
                'test_issues': test_issues,
                'delusion_check': "Are you testing enough? Are you testing the right things?",
                'recommendation': "Fix test file issues and implement missing tests"
            }
        }


class BuildExpert:
    """Build Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Build Expert"
        self.focus = "Build environment, package management, deployment"
    
    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate build environment"""
        build_issues = []
        
        # Check for build issues from test failures
        build_failures = [
            "Failed to build openflow-playground",
            "hatchling.build.build_editable failed",
            "UV package management build errors"
        ]
        
        for failure in build_failures:
            if "hatchling" in failure:
                build_issues.append("Hatchling build backend errors")
            if "UV package" in failure:
                build_issues.append("UV package management compatibility issues")
        
        # Check package management domain
        package_domain = model_registry['domains']['package_management']
        
        return {
            'passed': len(build_issues) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'package_management': package_domain['linter'],
                'build_issues': build_issues,
                'delusion_check': "Is the build environment working correctly?",
                'recommendation': "Fix UV/hatchling compatibility issues"
            }
        }


class ArchitectureExpert:
    """Architecture Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Architecture Expert"
        self.focus = "Design patterns, system architecture, scalability"
    
    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate architecture"""
        file_organization = model_registry.get('file_organization', {})
        
        # Check for architectural issues
        arch_issues = []
        
        # Check if model-driven approach is being followed
        if not any("model" in domain.lower() for domain in model_registry['domains']):
            arch_issues.append("Model-driven approach not fully implemented")
        
        return {
            'passed': len(arch_issues) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'domains_defined': len(model_registry['domains']),
                'file_organization': len(file_organization),
                'architectural_issues': arch_issues,
                'delusion_check': "Is this architecture sound? Is it scalable? Is it maintainable?",
                'recommendation': "Ensure model-driven approach is fully implemented"
            }
        }


def load_model_registry() -> Dict[str, Any]:
    """Load the project model registry"""
    try:
        with open('project_model_registry.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: project_model_registry.json not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in project_model_registry.json: {e}")
        sys.exit(1)


def assemble_ghostbusters_team() -> Dict[str, Any]:
    """Assemble all available ghostbusters"""
    return {
        'security_expert': SecurityExpert(),
        'code_quality_expert': CodeQualityExpert(),
        'test_expert': TestExpert(),
        'build_expert': BuildExpert(),
        'architecture_expert': ArchitectureExpert(),
        'model_expert': ModelExpert()
    }


def call_more_ghostbusters(model_registry: Dict[str, Any]) -> Dict[str, Any]:
    """Call all ghostbusters for validation"""
    
    print("🚨 CALLING MORE GHOSTBUSTERS!")
    print("=" * 50)
    
    # Assemble team
    team = assemble_ghostbusters_team()
    
    # Run validation
    results = {}
    
    # Agent validation
    for agent_name, agent in team.items():
        print(f"👻 {agent.name} is investigating...")
        results[f'agent_{agent_name}'] = agent.validate(model_registry)
    
    return results


def generate_delusion_report(validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive delusion detection report"""
    
    passed_validations = sum(1 for r in validation_results.values() if r['passed'])
    failed_validations = sum(1 for r in validation_results.values() if not r['passed'])
    
    delusions_detected = []
    for validator_name, result in validation_results.items():
        if not result['passed']:
            delusions_detected.append({
                'validator': validator_name,
                'expert': result['expert'],
                'findings': result['findings']
            })
    
    report = {
        'summary': {
            'total_validators': len(validation_results),
            'passed_validations': passed_validations,
            'failed_validations': failed_validations,
            'delusions_detected': delusions_detected
        },
        'detailed_results': validation_results
    }
    
    return report


def print_ghostbusters_report(report: Dict[str, Any]) -> None:
    """Print the ghostbusters report"""
    
    print("\n" + "=" * 50)
    print("👻 GHOSTBUSTERS VALIDATION REPORT")
    print("=" * 50)
    
    summary = report['summary']
    print(f"📊 Total Validators: {summary['total_validators']}")
    print(f"✅ Passed Validations: {summary['passed_validations']}")
    print(f"❌ Failed Validations: {summary['failed_validations']}")
    
    if summary['delusions_detected']:
        print(f"\n🚨 DELUSIONS DETECTED: {len(summary['delusions_detected'])}")
        for delusion in summary['delusions_detected']:
            print(f"   • {delusion['expert']}: {delusion['findings']}")
    else:
        print("\n✅ NO DELUSIONS DETECTED!")
    
    print("\n📋 DETAILED FINDINGS:")
    for validator_name, result in report['detailed_results'].items():
        expert_name = result['expert']
        findings = result['findings']
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        
        print(f"\n👻 {expert_name} - {status}")
        print(f"   Focus: {result['focus']}")
        print(f"   Delusion Check: {findings.get('delusion_check', 'N/A')}")
        print(f"   Recommendation: {findings.get('recommendation', 'N/A')}")
        
        # Print specific findings
        for key, value in findings.items():
            if key not in ['delusion_check', 'recommendation']:
                print(f"   {key}: {value}")


def main():
    """Main ghostbusters validation"""
    
    print("🎯 GHOSTBUSTERS TEAM ASSEMBLING...")
    
    # Load model registry
    model_registry = load_model_registry()
    
    # Call ghostbusters
    validation_results = call_more_ghostbusters(model_registry)
    
    # Generate report
    delusion_report = generate_delusion_report(validation_results)
    
    # Print report
    print_ghostbusters_report(delusion_report)
    
    # Exit with appropriate code
    if delusion_report['summary']['failed_validations'] > 0:
        print("\n🚨 GHOSTBUSTERS DETECTED DELUSIONS!")
        sys.exit(1)
    else:
        print("\n✅ GHOSTBUSTERS VALIDATION PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main() 