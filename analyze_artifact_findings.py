#!/usr/bin/env python3
"""
📊 Artifact Analysis Findings Summary

This script analyzes the comprehensive artifact analysis report and provides
actionable insights for improving model coverage and requirements tracing.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def load_analysis_report() -> Dict[str, Any]:
    """Load the comprehensive analysis report"""
    report_file = Path("comprehensive_artifact_analysis_report.json")
    if not report_file.exists():
        print("❌ Analysis report not found. Run comprehensive_artifact_analysis.py first.")
        return {}
    
    with open(report_file, 'r') as f:
        return json.load(f)

def analyze_untraced_artifacts(report: Dict[str, Any]) -> List[str]:
    """Analyze untraced artifacts to identify patterns"""
    untraced = []
    
    for domain, artifacts in report.get('domain_analysis', {}).get('artifacts_by_domain', {}).items():
        if domain == 'untraced':
            for artifact in artifacts:
                untraced.append(artifact['path'])
    
    return untraced

def analyze_missing_domains(report: Dict[str, Any]) -> List[str]:
    """Get missing domains from the analysis"""
    return report.get('domain_analysis', {}).get('missing_domains', [])

def analyze_missing_requirements(report: Dict[str, Any]) -> List[str]:
    """Get missing requirements from the analysis"""
    return report.get('requirements_analysis', {}).get('missing_requirements', [])

def analyze_python_issues(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get Python files with AST parsing issues"""
    return report.get('python_analysis', {}).get('python_issues', [])

def generate_action_plan(report: Dict[str, Any]) -> Dict[str, List[str]]:
    """Generate actionable plan based on analysis findings"""
    action_plan = {
        'immediate_actions': [],
        'domain_improvements': [],
        'requirements_implementation': [],
        'python_fixes': [],
        'model_updates': []
    }
    
    # Immediate actions
    summary = report.get('summary', {})
    if summary.get('untraced_artifacts', 0) > 0:
        action_plan['immediate_actions'].append(
            f"🔍 Add domain patterns for {summary['untraced_artifacts']} untraced artifacts"
        )
    
    # Domain improvements
    missing_domains = analyze_missing_domains(report)
    if missing_domains:
        action_plan['domain_improvements'].extend([
            f"📁 Create artifacts for domain: {domain}" for domain in missing_domains
        ])
    
    # Requirements implementation
    missing_requirements = analyze_missing_requirements(report)
    if missing_requirements:
        action_plan['requirements_implementation'].extend([
            f"📋 Implement requirement: {req}" for req in missing_requirements[:10]  # Limit to first 10
        ])
    
    # Python fixes
    python_issues = analyze_python_issues(report)
    if python_issues:
        action_plan['python_fixes'].extend([
            f"🐍 Fix AST parsing in: {issue['path']}" for issue in python_issues
        ])
    
    # Model updates
    action_plan['model_updates'].extend([
        "🔄 Update project_model_registry.json with new domain patterns",
        "📝 Add missing requirements to requirements_traceability",
        "🔧 Improve domain detection patterns"
    ])
    
    return action_plan

def print_findings_summary(report: Dict[str, Any]):
    """Print a comprehensive findings summary"""
    print("🔍 COMPREHENSIVE ARTIFACT ANALYSIS FINDINGS")
    print("=" * 60)
    
    # Summary statistics
    summary = report.get('summary', {})
    print(f"\n📊 SUMMARY STATISTICS")
    print(f"Total Artifacts: {summary.get('total_artifacts', 0)}")
    print(f"Traced Artifacts: {summary.get('traced_artifacts', 0)}")
    print(f"Untraced Artifacts: {summary.get('untraced_artifacts', 0)}")
    print(f"Coverage Percentage: {summary.get('coverage_percentage', 0):.1f}%")
    
    # Domain analysis
    domain_analysis = report.get('domain_analysis', {})
    print(f"\n🏷️ DOMAIN COVERAGE")
    for domain, count in domain_analysis.get('domain_counts', {}).items():
        print(f"  {domain}: {count} artifacts")
    
    missing_domains = domain_analysis.get('missing_domains', [])
    if missing_domains:
        print(f"\n❌ MISSING DOMAINS")
        for domain in missing_domains:
            print(f"  • {domain}")
    
    # Requirements analysis
    req_analysis = report.get('requirements_analysis', {})
    print(f"\n📋 REQUIREMENTS COVERAGE")
    print(f"Total Requirements: {req_analysis.get('total_requirements', 0)}")
    print(f"Traced Requirements: {req_analysis.get('traced_requirements', 0)}")
    
    missing_reqs = req_analysis.get('missing_requirements', [])
    if missing_reqs:
        print(f"\n❌ MISSING REQUIREMENTS (first 10)")
        for req in missing_reqs[:10]:
            print(f"  • {req}")
    
    # Python analysis
    python_analysis = report.get('python_analysis', {})
    print(f"\n🐍 PYTHON ANALYSIS")
    print(f"Total Python Files: {python_analysis.get('total_python_files', 0)}")
    print(f"AST Parsing Success: {python_analysis.get('ast_parsing_success', 0)}")
    print(f"AST Parsing Failures: {python_analysis.get('ast_parsing_failures', 0)}")
    
    python_issues = python_analysis.get('python_issues', [])
    if python_issues:
        print(f"\n❌ PYTHON FILES WITH ISSUES")
        for issue in python_issues:
            print(f"  • {issue['path']}: {issue.get('issues', ['Unknown error'])[0]}")

def print_action_plan(action_plan: Dict[str, List[str]]):
    """Print the action plan"""
    print("\n🎯 ACTION PLAN")
    print("=" * 60)
    
    for category, actions in action_plan.items():
        if actions:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for action in actions:
                print(f"  • {action}")

def main():
    """Main function to analyze findings"""
    print("📊 Analyzing Artifact Analysis Findings...")
    
    # Load report
    report = load_analysis_report()
    if not report:
        return
    
    # Print findings summary
    print_findings_summary(report)
    
    # Generate and print action plan
    action_plan = generate_action_plan(report)
    print_action_plan(action_plan)
    
    # Save action plan
    with open("artifact_analysis_action_plan.json", 'w') as f:
        json.dump(action_plan, f, indent=2)
    
    print(f"\n📄 Action plan saved to: artifact_analysis_action_plan.json")

if __name__ == "__main__":
    main()
