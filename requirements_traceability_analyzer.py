#!/usr/bin/env python3
"""
Requirements Traceability Analyzer
Compares coarse-grained project model requirements with fine-grained test-driven requirements
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class RequirementAlignment:
    """Alignment between project model and test-driven requirements"""
    project_requirement: str
    test_requirements: List[str]
    domain: str
    implementation_files: List[str]
    test_files: List[str]
    alignment_score: float
    missing_tests: List[str]
    missing_implementation: List[str]


class RequirementsTraceabilityAnalyzer:
    """Analyze alignment between project model and test-driven requirements"""
    
    def __init__(self):
        self.project_model = self._load_project_model()
        self.test_driven_model = self._load_test_driven_model()
    
    def _load_project_model(self) -> Dict[str, Any]:
        """Load project model registry"""
        try:
            with open('project_model_registry.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project model: {e}")
            return {}
    
    def _load_test_driven_model(self) -> Dict[str, Any]:
        """Load test-driven AST model"""
        try:
            with open('test_driven_ast_models.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading test-driven model: {e}")
            return {}
    
    def analyze_requirements_alignment(self) -> Dict[str, Any]:
        """Analyze alignment between project model and test-driven requirements"""
        print("🔍 Analyzing Requirements Traceability Alignment...")
        
        alignments = []
        project_requirements = self.project_model.get('requirements_traceability', [])
        test_requirements = self.test_driven_model.get('test_requirements', {})
        
        for req in project_requirements:
            alignment = self._analyze_single_requirement(req, test_requirements)
            alignments.append(alignment)
        
        # Calculate overall alignment metrics
        total_requirements = len(project_requirements)
        aligned_requirements = len([a for a in alignments if a.alignment_score > 0.5])
        missing_tests = sum(len(a.missing_tests) for a in alignments)
        missing_implementation = sum(len(a.missing_implementation) for a in alignments)
        
        return {
            'total_requirements': total_requirements,
            'aligned_requirements': aligned_requirements,
            'alignment_rate': aligned_requirements / total_requirements if total_requirements > 0 else 0,
            'missing_tests': missing_tests,
            'missing_implementation': missing_implementation,
            'alignments': [asdict(a) for a in alignments]
        }
    
    def _analyze_single_requirement(self, project_req: Dict[str, Any], test_requirements: Dict[str, Any]) -> RequirementAlignment:
        """Analyze alignment for a single requirement"""
        req_id = project_req.get('requirement', '')
        domain = project_req.get('domain', '')
        implementation = project_req.get('implementation', '')
        expected_test = project_req.get('test', '')
        
        # Find matching test requirements
        matching_tests = []
        for test_file, reqs in test_requirements.items():
            for req in reqs:
                if self._requirements_match(req_id, req.get('description', '')):
                    matching_tests.append(req.get('requirement_id', ''))
        
        # Extract implementation files from project model
        implementation_files = self._extract_implementation_files(domain, implementation)
        
        # Calculate alignment score
        alignment_score = self._calculate_alignment_score(
            expected_test, matching_tests, implementation_files
        )
        
        # Find missing tests and implementation
        missing_tests = self._find_missing_tests(expected_test, matching_tests)
        missing_implementation = self._find_missing_implementation(implementation_files)
        
        return RequirementAlignment(
            project_requirement=req_id,
            test_requirements=matching_tests,
            domain=domain,
            implementation_files=implementation_files,
            test_files=[expected_test] if expected_test else [],
            alignment_score=alignment_score,
            missing_tests=missing_tests,
            missing_implementation=missing_implementation
        )
    
    def _requirements_match(self, project_req: str, test_req: str) -> bool:
        """Check if project requirement matches test requirement"""
        # Simple keyword matching
        project_keywords = set(re.findall(r'\b\w+\b', project_req.lower()))
        test_keywords = set(re.findall(r'\b\w+\b', test_req.lower()))
        
        # Calculate similarity
        if not project_keywords or not test_keywords:
            return False
        
        intersection = project_keywords.intersection(test_keywords)
        union = project_keywords.union(test_keywords)
        
        similarity = len(intersection) / len(union)
        return similarity > 0.3  # 30% keyword overlap
    
    def _extract_implementation_files(self, domain: str, implementation: str) -> List[str]:
        """Extract implementation files from domain and implementation description"""
        files = []
        
        # Look for file patterns in implementation description
        file_patterns = re.findall(r'([^\s]+\.(py|mdc|md|yaml|json|sh))', implementation)
        files.extend([pattern[0] for pattern in file_patterns])
        
        # Add domain-specific files
        if domain in self.project_model.get('domains', {}):
            domain_config = self.project_model['domains'][domain]
            patterns = domain_config.get('patterns', [])
            files.extend(patterns)
        
        return list(set(files))
    
    def _calculate_alignment_score(self, expected_test: str, matching_tests: List[str], implementation_files: List[str]) -> float:
        """Calculate alignment score between project and test requirements"""
        score = 0.0
        
        # Test alignment (40% weight)
        if expected_test and matching_tests:
            test_score = len(matching_tests) / max(len([expected_test]), 1)
            score += test_score * 0.4
        
        # Implementation alignment (60% weight)
        if implementation_files:
            # Check if implementation files exist
            existing_files = [f for f in implementation_files if Path(f).exists()]
            impl_score = len(existing_files) / len(implementation_files) if implementation_files else 0
            score += impl_score * 0.6
        
        return min(1.0, score)
    
    def _find_missing_tests(self, expected_test: str, matching_tests: List[str]) -> List[str]:
        """Find missing tests"""
        missing = []
        if expected_test and not matching_tests:
            missing.append(expected_test)
        return missing
    
    def _find_missing_implementation(self, implementation_files: List[str]) -> List[str]:
        """Find missing implementation files"""
        return [f for f in implementation_files if not Path(f).exists()]
    
    def generate_alignment_report(self) -> str:
        """Generate detailed alignment report"""
        analysis = self.analyze_requirements_alignment()
        
        report = []
        report.append("📊 Requirements Traceability Alignment Report")
        report.append("=" * 60)
        report.append(f"Total Requirements: {analysis['total_requirements']}")
        report.append(f"Aligned Requirements: {analysis['aligned_requirements']}")
        report.append(f"Alignment Rate: {analysis['alignment_rate']:.1%}")
        report.append(f"Missing Tests: {analysis['missing_tests']}")
        report.append(f"Missing Implementation: {analysis['missing_implementation']}")
        report.append("")
        
        # Detailed alignments
        report.append("🔍 Detailed Alignments:")
        for alignment in analysis['alignments'][:10]:  # Show first 10
            report.append(f"\n📋 {alignment['project_requirement']}")
            report.append(f"   Domain: {alignment['domain']}")
            report.append(f"   Test Requirements: {', '.join(alignment['test_requirements'])}")
            report.append(f"   Alignment Score: {alignment['alignment_score']:.1%}")
            if alignment['missing_tests']:
                report.append(f"   Missing Tests: {', '.join(alignment['missing_tests'])}")
            if alignment['missing_implementation']:
                report.append(f"   Missing Implementation: {', '.join(alignment['missing_implementation'])}")
        
        return "\n".join(report)
    
    def find_critical_gaps(self) -> Dict[str, Any]:
        """Find critical gaps between project model and test-driven requirements"""
        analysis = self.analyze_requirements_alignment()
        
        critical_gaps = {
            'high_priority_missing_tests': [],
            'missing_implementation_files': [],
            'low_alignment_requirements': []
        }
        
        for alignment in analysis['alignments']:
            # High priority missing tests
            if alignment['alignment_score'] < 0.3 and alignment['missing_tests']:
                critical_gaps['high_priority_missing_tests'].append({
                    'requirement': alignment['project_requirement'],
                    'missing_tests': alignment['missing_tests']
                })
            
            # Missing implementation files
            if alignment['missing_implementation']:
                critical_gaps['missing_implementation_files'].append({
                    'requirement': alignment['project_requirement'],
                    'missing_files': alignment['missing_implementation']
                })
            
            # Low alignment requirements
            if alignment['alignment_score'] < 0.5:
                critical_gaps['low_alignment_requirements'].append({
                    'requirement': alignment['project_requirement'],
                    'score': alignment['alignment_score']
                })
        
        return critical_gaps


def main():
    """Main function for testing"""
    print("🔍 Requirements Traceability Analyzer")
    print("=" * 50)
    
    analyzer = RequirementsTraceabilityAnalyzer()
    
    # Generate alignment report
    report = analyzer.generate_alignment_report()
    print(report)
    
    # Find critical gaps
    gaps = analyzer.find_critical_gaps()
    
    print(f"\n🚨 Critical Gaps Found:")
    print(f"  High Priority Missing Tests: {len(gaps['high_priority_missing_tests'])}")
    print(f"  Missing Implementation Files: {len(gaps['missing_implementation_files'])}")
    print(f"  Low Alignment Requirements: {len(gaps['low_alignment_requirements'])}")
    
    # Show top critical gaps
    if gaps['high_priority_missing_tests']:
        print(f"\n🔴 High Priority Missing Tests:")
        for gap in gaps['high_priority_missing_tests'][:3]:
            print(f"  - {gap['requirement']}: {gap['missing_tests']}")
    
    if gaps['missing_implementation_files']:
        print(f"\n🔴 Missing Implementation Files:")
        for gap in gaps['missing_implementation_files'][:3]:
            print(f"  - {gap['requirement']}: {gap['missing_files']}")


if __name__ == "__main__":
    main() 