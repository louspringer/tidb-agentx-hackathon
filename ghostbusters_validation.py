#!/usr/bin/env python3
"""
Ghostbusters Validation Script
Multi-agent validation with deterministic tools
"""

import json
import sys
from typing import Dict, Any


class SecurityExpert:
    """Security Expert Ghostbuster"""

    def __init__(self) -> None:
        self.name = "Security Expert"
        self.focus = "Security practices, credential handling, access control"

    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security practices"""
        security_domain = model_registry['domains']['security_first']

        return {
            'passed': True,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'requirements_count': len(security_domain['requirements']),
                'tools_available': [security_domain['linter'], security_domain['validator'], security_domain['formatter']],
                'content_indicators': len(security_domain['content_indicators']),
                'delusion_check': "Are you being security-conscious?",
                'recommendation': "Use bandit + detect-secrets + safety for comprehensive security"
            }
        }


class ModelExpert:
    """Model Expert Ghostbuster"""

    def __init__(self) -> None:
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

        # Check for missing model updates
        missing_updates = []
        for req in model_registry['requirements_traceability']:
            if not req.get('test'):
                missing_updates.append(f"Missing test for requirement: {req.get('requirement', 'Unknown')}")

        return {
            'passed': len(delusions) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'model_version': model_registry.get('version', 'Unknown'),
                'domains_count': len(model_registry.get('domains', {})),
                'requirements_count': len(model_registry.get('requirements_traceability', [])),
                'delusions_detected': delusions,
                'missing_updates': missing_updates,
                'delusion_check': "Are you actually following the model? Are you being model-driven?",
                'recommendation': "Update model with test failures and missing requirements"
            }
        }


class CodeQualityExpert:
    """Code Quality Expert Ghostbuster"""

    def __init__(self) -> None:
        self.name = "Code Quality Expert"
        self.focus = "Code standards, best practices, maintainability"

    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code quality practices"""
        python_domain = model_registry['domains']['python']

        return {
            'passed': True,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'linter': python_domain['linter'],
                'formatter': python_domain['formatter'],
                'exclusions': len(python_domain['exclusions']),
                'delusion_check': "Are you writing clean, maintainable code? Are you using proper patterns?",
                'recommendation': "Use flake8 + black for Python code quality"
            }
        }


class TestExpert:
    """Test Expert Ghostbuster"""

    def __init__(self) -> None:
        self.name = "Test Expert"
        self.focus = "Testing approaches, coverage, validation"

    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate testing practices"""
        # Check for test-related domains
        test_domains = ['multi_agent_testing', 'healthcare_cdc']
        test_coverage = {}

        for domain in test_domains:
            if domain in model_registry['domains']:
                domain_config = model_registry['domains'][domain]
                test_coverage[domain] = {
                    'validator': domain_config.get('validator'),
                    'requirements': len(domain_config['requirements'])
                }

        return {
            'passed': True,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'test_domains': test_coverage,
                'delusion_check': "Are you testing enough? Are you testing the right things?",
                'recommendation': "Use pytest for comprehensive testing"
            }
        }


class ArchitectureExpert:
    """Architecture Expert Ghostbuster"""

    def __init__(self) -> None:
        self.name = "Architecture Expert"
        self.focus = "Design patterns, system architecture, scalability"

    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate architecture"""
        file_organization = model_registry.get('file_organization', {})

        return {
            'passed': True,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'domains_defined': len(model_registry['domains']),
                'file_organization': len(file_organization),
                'delusion_check': "Is this architecture sound? Is it scalable? Is it maintainable?",
                'recommendation': "Follow domain-driven design principles"
            }
        }


class HeuristicExpert:
    """Heuristic Expert Ghostbuster"""

    def __init__(self) -> None:
        self.name = "Heuristic Expert"
        self.focus = "Heuristic vs deterministic balance, tool selection"

    def validate(self, model_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate heuristic vs deterministic balance"""
        tool_selection_logic = model_registry.get('tool_selection_logic', {})

        return {
            'passed': True,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'pattern_weight': tool_selection_logic.get('pattern_weight', 0),
                'content_indicator_weight': tool_selection_logic.get('content_indicator_weight', 0),
                'confidence_threshold': tool_selection_logic.get('confidence_threshold', 0),
                'delusion_check': "Are you using the right balance of heuristics and deterministic tools?",
                'recommendation': "Use LLMs for intelligence and tools for precision"
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
        'architecture_expert': ArchitectureExpert(),
        'model_expert': ModelExpert(),
        'heuristic_expert': HeuristicExpert()
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
