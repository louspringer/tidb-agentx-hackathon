#!/usr/bin/env python3
"""
Multi-Agent Blind Spot Detection for Fresh Cline's Healthcare CDC Plan
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class BlindSpot:
    category: str
    severity: str
    description: str
    impact: str
    recommendation: str

class MultiAgentBlindSpotDetector:
    def __init__(self):
        self.agents = {
            "Security Expert": self.security_expert_analysis,
            "DevOps Engineer": self.devops_engineer_analysis,
            "Code Quality Expert": self.code_quality_expert_analysis,
            "User Experience Advocate": self.ux_advocate_analysis,
            "Performance Engineer": self.performance_engineer_analysis,
            "Rule Compliance Expert": self.rule_compliance_expert_analysis
        }
    
    def security_expert_analysis(self, plan: str) -> List[BlindSpot]:
        """Security-focused blind spot detection"""
        blind_spots = []
        
        # Check for missing security tools
        if "bandit" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Security",
                severity="HIGH",
                description="Missing bandit security scanning tool",
                impact="Could miss security vulnerabilities in healthcare code",
                recommendation="Add bandit to Python development tools for security scanning"
            ))
        
        # Check for HIPAA compliance specifics
        if "hipaa" in plan.lower() and "encryption" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Security",
                severity="CRITICAL",
                description="HIPAA compliance mentioned but encryption not detailed",
                impact="HIPAA requires encryption at rest and in transit",
                recommendation="Specify encryption requirements for PHI/PII data"
            ))
        
        # Check for audit trail specifics
        if "audit" in plan.lower() and "immutable" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Security",
                severity="HIGH",
                description="Audit logging mentioned but immutability not specified",
                impact="Audit trails could be tampered with",
                recommendation="Specify immutable audit trail requirements"
            ))
        
        return blind_spots
    
    def devops_engineer_analysis(self, plan: str) -> List[BlindSpot]:
        """DevOps-focused blind spot detection"""
        blind_spots = []
        
        # Check for CI/CD integration
        if "ci/cd" not in plan.lower() and "pipeline" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="DevOps",
                severity="MEDIUM",
                description="No CI/CD pipeline integration mentioned",
                impact="Manual deployment could introduce errors",
                recommendation="Specify CI/CD pipeline for healthcare validation"
            ))
        
        # Check for monitoring/alerting
        if "monitoring" not in plan.lower() and "alerting" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="DevOps",
                severity="MEDIUM",
                description="No monitoring or alerting strategy",
                impact="Healthcare validation failures might go unnoticed",
                recommendation="Specify monitoring and alerting for healthcare validation"
            ))
        
        # Check for infrastructure validation
        if "cfn-lint" in plan.lower() and "aws" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="DevOps",
                severity="LOW",
                description="cfn-lint mentioned but AWS context unclear",
                impact="Infrastructure validation might be incomplete",
                recommendation="Specify AWS-specific validation requirements"
            ))
        
        return blind_spots
    
    def code_quality_expert_analysis(self, plan: str) -> List[BlindSpot]:
        """Code quality-focused blind spot detection"""
        blind_spots = []
        
        # Check for deterministic editing tools
        if "search_replace" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Code Quality",
                severity="HIGH",
                description="Missing search_replace tool for deterministic editing",
                impact="Could use fuzzy editing tools that violate rules",
                recommendation="Explicitly mention search_replace for exact string matching"
            ))
        
        # Check for test coverage
        if "test" in plan.lower() and "coverage" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Code Quality",
                severity="MEDIUM",
                description="Testing mentioned but coverage not specified",
                impact="Healthcare validation might have gaps",
                recommendation="Specify test coverage requirements for healthcare code"
            ))
        
        # Check for code review process
        if "review" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Code Quality",
                severity="MEDIUM",
                description="No code review process mentioned",
                impact="Healthcare code quality might suffer",
                recommendation="Specify code review process for healthcare validation"
            ))
        
        return blind_spots
    
    def ux_advocate_analysis(self, plan: str) -> List[BlindSpot]:
        """UX-focused blind spot detection"""
        blind_spots = []
        
        # Check for user feedback
        if "feedback" not in plan.lower() and "user" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="UX",
                severity="LOW",
                description="No user feedback mechanism mentioned",
                impact="Healthcare validation might not meet user needs",
                recommendation="Specify user feedback collection for healthcare validation"
            ))
        
        # Check for documentation
        if "documentation" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="UX",
                severity="MEDIUM",
                description="No documentation strategy mentioned",
                impact="Healthcare validation might be hard to use",
                recommendation="Specify documentation requirements for healthcare validation"
            ))
        
        return blind_spots
    
    def performance_engineer_analysis(self, plan: str) -> List[BlindSpot]:
        """Performance-focused blind spot detection"""
        blind_spots = []
        
        # Check for performance testing
        if "performance" not in plan.lower() and "load" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Performance",
                severity="MEDIUM",
                description="No performance testing mentioned",
                impact="Healthcare validation might be slow",
                recommendation="Specify performance testing for healthcare validation"
            ))
        
        # Check for scalability
        if "scale" not in plan.lower() and "scalability" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Performance",
                severity="LOW",
                description="No scalability considerations mentioned",
                impact="Healthcare validation might not handle large datasets",
                recommendation="Specify scalability requirements for healthcare validation"
            ))
        
        return blind_spots
    
    def rule_compliance_expert_analysis(self, plan: str) -> List[BlindSpot]:
        """Rule compliance-focused blind spot detection"""
        blind_spots = []
        
        # Check for model-driven orchestration
        if "model-driven" not in plan.lower() and "orchestration" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Rule Compliance",
                severity="HIGH",
                description="Missing model-driven orchestration principle",
                impact="Plan doesn't follow core project philosophy",
                recommendation="Reference .cursor/rules/model-driven-orchestration.mdc"
            ))
        
        # Check for prevention architecture
        if "prevention" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Rule Compliance",
                severity="MEDIUM",
                description="Missing prevention architecture approach",
                impact="Plan focuses on detection rather than prevention",
                recommendation="Reference .cursor/rules/prevention-architecture.mdc"
            ))
        
        # Check for YAML type-specific rules
        if "yaml" in plan.lower() and "type-specific" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Rule Compliance",
                severity="MEDIUM",
                description="Missing YAML type-specific rule reference",
                impact="YAML handling might not follow domain-specific patterns",
                recommendation="Reference .cursor/rules/yaml-type-specific.mdc"
            ))
        
        # Check for investigation analysis
        if "investigation" not in plan.lower() and "analysis" not in plan.lower():
            blind_spots.append(BlindSpot(
                category="Rule Compliance",
                severity="LOW",
                description="Missing investigation and analysis approach",
                impact="Plan might not ask better questions",
                recommendation="Reference .cursor/rules/investigation-analysis.mdc"
            ))
        
        return blind_spots
    
    def detect_blind_spots(self, plan: str) -> Dict[str, List[BlindSpot]]:
        """Run all agent analyses and return blind spots by category"""
        all_blind_spots = {}
        
        for agent_name, analysis_func in self.agents.items():
            blind_spots = analysis_func(plan)
            if blind_spots:
                all_blind_spots[agent_name] = blind_spots
        
        return all_blind_spots
    
    def generate_report(self, blind_spots: Dict[str, List[BlindSpot]]) -> str:
        """Generate a comprehensive blind spot report"""
        report = "# Multi-Agent Blind Spot Analysis Report\n\n"
        
        # Summary
        total_spots = sum(len(spots) for spots in blind_spots.values())
        critical_spots = sum(1 for spots in blind_spots.values() 
                           for spot in spots if spot.severity == "CRITICAL")
        high_spots = sum(1 for spots in blind_spots.values() 
                        for spot in spots if spot.severity == "HIGH")
        
        report += f"## Summary\n"
        report += f"- **Total Blind Spots**: {total_spots}\n"
        report += f"- **Critical Issues**: {critical_spots}\n"
        report += f"- **High Priority Issues**: {high_spots}\n\n"
        
        # Detailed analysis by agent
        for agent_name, spots in blind_spots.items():
            if spots:
                report += f"## {agent_name} Analysis\n\n"
                
                # Group by severity
                by_severity = {}
                for spot in spots:
                    if spot.severity not in by_severity:
                        by_severity[spot.severity] = []
                    by_severity[spot.severity].append(spot)
                
                for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    if severity in by_severity:
                        report += f"### {severity} Priority Issues\n\n"
                        for spot in by_severity[severity]:
                            report += f"**Issue**: {spot.description}\n"
                            report += f"**Impact**: {spot.impact}\n"
                            report += f"**Recommendation**: {spot.recommendation}\n\n"
        
        return report

def test_fresh_cline_plan_blind_spots():
    """Test blind spot detection on fresh Cline's plan"""
    
    # Fresh Cline's plan (abbreviated for testing)
    fresh_cline_plan = """
    # Healthcare CDC Domain Validation Implementation Plan
    
    ## 1. Tool Selection Analysis
    
    ### YAML Files
    - **Editing Tool**: `ruamel.yaml` for parsing and serializing, in compliance with your `.cursor/rules/deterministic-editing.mdc`
    - **Validation Strategy**: 
      - For infrastructure YAML (`healthcare-cdc/models/*.yaml`): Use `cfn-lint` as specified in the `yaml_infrastructure` domain
      - For config YAML: Use `yamllint` with `jsonschema` as specified in the `yaml_config` domain
    
    ### JSON Files
    - **Editing Tool**: Standard `json` library with proper formatting preservation
    - **Validation Strategy**: Use `jsonschema` with healthcare CDC-specific schemas to validate structure and ensure HIPAA compliance
    
    ### Python Files
    - **Development Tools**: 
      - `flake8` for linting (as specified in the `healthcare_cdc` domain)
      - `black` for formatting (as specified in the `healthcare_cdc` domain)
      - `pytest` for validation (as specified in the `healthcare_cdc` domain)
      - `bandit` for security scanning (from `security_first` domain)
    - **Code Quality Assurance**: Add healthcare-specific flake8 plugins like `flake8-hipaa` for HIPAA compliance validation
    
    ### MDC Files
    - **Editing Tool**: `MDCGenerator` from your `src/mdc_generator/mdc_model.py`
    - **Validation Strategy**: Use your existing MDC validation system with `validate_mdc_file` method
    - **YAML Frontmatter Handling**: Parse with `ruamel.yaml` as specified in your `.cursor/rules/deterministic-editing.mdc`
    
    ## 2. Rule Compliance Plan
    
    ### Deterministic Editing Compliance
    - Implement all edits using appropriate deterministic tools as defined in `.cursor/rules/deterministic-editing.mdc`
    - For YAML files: Use `ruamel.yaml` to preserve comments and structure
    - For Python files: Use `ast` or `libcst` for structural edits, followed by `black` formatting
    - For JSON files: Use standard `json` library with proper formatting
    
    ### Credential Management
    - Follow the principles in `.cursor/rules/security.mdc` and `.cursor/rules/security-credentials.mdc`
    - Use environment variables for all credentials with `${CREDENTIAL_NAME}` pattern
    - Implement healthcare-specific credential validation to ensure PHI/PII protection
    - Create healthcare-specific security validation tests
    
    ### Infrastructure Configuration Validation
    - Use `cfn-lint` for CloudFormation templates in `healthcare-cdc/models/`
    - Implement custom validators for healthcare-specific infrastructure requirements
    - Validate HIPAA-compliant infrastructure patterns (encryption, access control, audit logging)
    
    ### Pre-commit Hook Integration
    - Add healthcare-specific validation to `.pre-commit-config.yaml`
    - Create custom pre-commit hook for PHI/PII detection
    - Integrate with existing rule compliance system in `scripts/rule-compliance-check.sh`
    
    ## 3. Domain Organization Plan
    
    ### Healthcare CDC File Placement
    - Maintain existing structure in `healthcare-cdc/` directory
    - Add new subdirectories following established patterns:
      - `healthcare-cdc/validators/` for custom validation code
      - `healthcare-cdc/schemas/` for JSON schemas
      - `healthcare-cdc/rules/` for domain-specific MDC rules
    
    ### Domain Pattern Adherence
    - Follow the existing pattern in `project_model_registry.json` for the `healthcare_cdc` domain
    - Ensure all files match patterns specified in the domain configuration
    - Update content indicators to include healthcare-specific terms
    
    ### Project Model Integration
    - Utilize the `healthcare_cdc` domain from `project_model_registry.json`
    - Create specific traceability between healthcare requirements and implementations
    - Ensure validation steps align with project model requirements
    
    ## 4. Security Implementation Plan
    
    ### Healthcare Credential Handling
    - Implement PHI/PII-specific credential management
    - Create validators that detect potential PHI/PII leakage
    - Ensure all example data is fully anonymized
    - Create data masking utilities for logs and debug output
    
    ### Audit Logging Implementation
    - Implement HIPAA-compliant audit logging for all data access operations
    - Create log validators that ensure sensitive information isn't leaked
    - Design log rotation and retention policies that comply with HIPAA requirements
    
    ### HIPAA Compliance Enforcement
    - Create HIPAA-specific validation rules in `.cursor/rules/healthcare-hipaa.mdc`
    - Implement automatic checking for HIPAA identifiers in code and examples
    - Create test suite for HIPAA compliance validation
    
    ## 5. Testing Strategy
    
    ### Test-Driven Development Approach
    - Extend existing tests in `healthcare-cdc/test_healthcare_cdc_domain_model.py`
    - Create new test categories:
      - PHI/PII handling tests
      - HIPAA compliance tests
      - Encryption validation tests
      - Audit logging tests
    
    ### Multi-Agent Testing Framework Integration
    - Utilize `src/multi_agent_testing/` framework for healthcare validation
    - Create healthcare-specific test agents that understand medical contexts
    - Implement blind spot detection for healthcare data handling
    
    ### Rule Compliance Validation
    - Create specific tests for healthcare MDC rules
    - Extend `tests/test_rule_compliance_enforcement.py` with healthcare-specific checks
    - Implement automated validation of healthcare documentation
    """
    
    # Run blind spot detection
    detector = MultiAgentBlindSpotDetector()
    blind_spots = detector.detect_blind_spots(fresh_cline_plan)
    
    # Generate report
    report = detector.generate_report(blind_spots)
    
    # Print report
    print(report)
    
    # Assertions for critical issues
    total_spots = sum(len(spots) for spots in blind_spots.values())
    critical_spots = sum(1 for spots in blind_spots.values() 
                        for spot in spots if spot.severity == "CRITICAL")
    high_spots = sum(1 for spots in blind_spots.values() 
                     for spot in spots if spot.severity == "HIGH")
    
    print(f"\n📊 Blind Spot Summary:")
    print(f"Total Issues: {total_spots}")
    print(f"Critical: {critical_spots}")
    print(f"High: {high_spots}")
    
    # Test passes if we can identify blind spots
    assert total_spots > 0, "Should identify some blind spots"
    print("\n✅ Blind spot detection test passed!")

if __name__ == "__main__":
    test_fresh_cline_plan_blind_spots() 