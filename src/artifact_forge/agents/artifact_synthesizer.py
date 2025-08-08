#!/usr/bin/env python3
"""
ArtifactSynthesizer Agent
Creates unified artifact insights and recommendations
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ArtifactInsight:
    """A unified insight about the codebase"""

    insight_type: str  # 'health', 'complexity', 'quality', 'security', 'performance'
    title: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    affected_artifacts: list[str]
    recommendations: list[str]
    confidence: float
    created_at: datetime


class ArtifactSynthesizer:
    """Creates unified insights from artifact analysis"""

    def __init__(self) -> None:
        self.insight_types = {
            "health": self._analyze_codebase_health,
            "complexity": self._analyze_complexity_distribution,
            "quality": self._analyze_quality_metrics,
            "security": self._analyze_security_issues,
            "performance": self._analyze_performance_patterns,
        }

    def synthesize_insights(
        self,
        artifacts: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> list[ArtifactInsight]:
        """Create unified insights from all artifact data"""
        logger.info("Starting insight synthesis")

        insights = []

        # Generate insights for each type
        for insight_type, analyzer_func in self.insight_types.items():
            try:
                type_insights = analyzer_func(artifacts, relationships, opportunities)
                insights.extend(type_insights)
            except Exception as e:
                logger.error(f"Error in {insight_type} analysis: {e}")
                continue

        # Sort by severity and confidence
        insights.sort(
            key=lambda x: (self._severity_score(x.severity), x.confidence),
            reverse=True,
        )

        logger.info(f"Generated {len(insights)} insights")
        return insights

    def _analyze_codebase_health(
        self,
        artifacts: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> list[ArtifactInsight]:
        """Analyze overall codebase health"""
        insights = []

        # Count artifacts by type
        type_counts = {}  # type: ignore
        for artifact in artifacts:
            artifact_type = artifact.get("artifact_type", "unknown")
            type_counts[artifact_type] = type_counts.get(artifact_type, 0) + 1

        # Analyze error distribution
        error_opportunities = [
            opp
            for opp in opportunities
            if opp.get("opportunity_type") == "syntax_error"
        ]
        critical_errors = [
            opp for opp in error_opportunities if opp.get("severity") == "critical"
        ]

        if critical_errors:
            insights.append(
                ArtifactInsight(
                    insight_type="health",
                    title="Critical Syntax Errors Detected",
                    description=f"Found {len(critical_errors)} critical syntax errors affecting codebase health",
                    severity="critical",
                    affected_artifacts=[
                        opp.get("artifact_path", "") for opp in critical_errors
                    ],
                    recommendations=[
                        "Fix critical syntax errors immediately",
                        "Implement automated syntax checking in CI/CD",
                        "Add pre-commit hooks for syntax validation",
                    ],
                    confidence=0.95,
                    created_at=datetime.now(),
                ),
            )

        # Analyze artifact distribution
        if type_counts:
            primary_type = max(type_counts.items(), key=lambda x: x[1])
            insights.append(
                ArtifactInsight(
                    insight_type="health",
                    title="Codebase Composition Analysis",
                    description=f"Codebase primarily consists of {primary_type[0]} files ({primary_type[1]} files)",
                    severity="low",
                    affected_artifacts=list(type_counts.keys()),
                    recommendations=[
                        f"Consider adding more documentation for {primary_type[0]} files",
                        "Review artifact type distribution for balance",
                        "Ensure proper testing coverage for all artifact types",
                    ],
                    confidence=0.8,
                    created_at=datetime.now(),
                ),
            )

        return insights

    def _analyze_complexity_distribution(
        self,
        artifacts: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> list[ArtifactInsight]:
        """Analyze complexity distribution across artifacts"""
        insights = []

        # Calculate complexity metrics
        complexities = []
        for artifact in artifacts:
            if artifact.get("artifact_type") == "python":
                parsed_data = artifact.get("parsed_data", {})
                complexity = parsed_data.get("complexity", 0)
                if complexity > 0:
                    complexities.append(complexity)

        if complexities:
            avg_complexity = sum(complexities) / len(complexities)
            max(complexities)
            high_complexity_count = len([c for c in complexities if c > 10])

            if avg_complexity > 8:
                insights.append(
                    ArtifactInsight(
                        insight_type="complexity",
                        title="High Average Complexity",
                        description=f"Average cyclomatic complexity is {avg_complexity:.1f} (recommended < 8)",
                        severity="medium",
                        affected_artifacts=[
                            a.get("path", "")
                            for a in artifacts
                            if a.get("artifact_type") == "python"
                        ],
                        recommendations=[
                            "Refactor complex functions into smaller, simpler functions",
                            "Add unit tests for complex logic",
                            "Consider using design patterns to reduce complexity",
                        ],
                        confidence=0.85,
                        created_at=datetime.now(),
                    ),
                )

            if high_complexity_count > 5:
                insights.append(
                    ArtifactInsight(
                        insight_type="complexity",
                        title="Multiple High-Complexity Files",
                        description=f"{high_complexity_count} files have complexity > 10",
                        severity="high",
                        affected_artifacts=[
                            a.get("path", "")
                            for a in artifacts
                            if a.get("artifact_type") == "python"
                        ],
                        recommendations=[
                            "Prioritize refactoring of high-complexity files",
                            "Implement complexity monitoring in CI/CD",
                            "Add code review guidelines for complexity",
                        ],
                        confidence=0.9,
                        created_at=datetime.now(),
                    ),
                )

        return insights

    def _analyze_quality_metrics(
        self,
        artifacts: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> list[ArtifactInsight]:
        """Analyze code quality metrics"""
        insights = []

        # Analyze quality opportunities
        quality_opportunities = [
            opp for opp in opportunities if opp.get("opportunity_type") == "quality"
        ]

        if quality_opportunities:
            insights.append(
                ArtifactInsight(
                    insight_type="quality",
                    title="Code Quality Issues Detected",
                    description=f"Found {len(quality_opportunities)} quality improvement opportunities",
                    severity="medium",
                    affected_artifacts=[
                        opp.get("artifact_path", "") for opp in quality_opportunities
                    ],
                    recommendations=[
                        "Implement automated code quality checks",
                        "Add linting rules to CI/CD pipeline",
                        "Establish code quality standards",
                    ],
                    confidence=0.75,
                    created_at=datetime.now(),
                ),
            )

        # Analyze documentation coverage
        python_artifacts = [a for a in artifacts if a.get("artifact_type") == "python"]
        markdown_artifacts = [
            a for a in artifacts if a.get("artifact_type") == "markdown"
        ]

        if python_artifacts and markdown_artifacts:
            doc_ratio = len(markdown_artifacts) / len(python_artifacts)
            if doc_ratio < 0.3:
                insights.append(
                    ArtifactInsight(
                        insight_type="quality",
                        title="Low Documentation Coverage",
                        description=f"Documentation ratio is {doc_ratio:.1%} (recommended > 30%)",
                        severity="medium",
                        affected_artifacts=[
                            a.get("path", "") for a in python_artifacts
                        ],
                        recommendations=[
                            "Increase documentation coverage",
                            "Add docstrings to all functions and classes",
                            "Create README files for major components",
                        ],
                        confidence=0.8,
                        created_at=datetime.now(),
                    ),
                )

        return insights

    def _analyze_security_issues(
        self,
        artifacts: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> list[ArtifactInsight]:
        """Analyze security issues"""
        insights = []

        # Analyze security opportunities
        security_opportunities = [
            opp for opp in opportunities if opp.get("opportunity_type") == "security"
        ]

        if security_opportunities:
            critical_security = [
                opp
                for opp in security_opportunities
                if opp.get("severity") in ["critical", "high"]
            ]

            if critical_security:
                insights.append(
                    ArtifactInsight(
                        insight_type="security",
                        title="Critical Security Issues Detected",
                        description=f"Found {len(critical_security)} critical/high security issues",
                        severity="critical",
                        affected_artifacts=[
                            opp.get("artifact_path", "") for opp in critical_security
                        ],
                        recommendations=[
                            "Address security issues immediately",
                            "Implement automated security scanning",
                            "Add security review to code review process",
                        ],
                        confidence=0.95,
                        created_at=datetime.now(),
                    ),
                )

        return insights

    def _analyze_performance_patterns(
        self,
        artifacts: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> list[ArtifactInsight]:
        """Analyze performance patterns"""
        insights = []

        # Analyze performance opportunities
        performance_opportunities = [
            opp for opp in opportunities if opp.get("opportunity_type") == "performance"
        ]

        if performance_opportunities:
            insights.append(
                ArtifactInsight(
                    insight_type="performance",
                    title="Performance Optimization Opportunities",
                    description=f"Found {len(performance_opportunities)} performance improvement opportunities",
                    severity="medium",
                    affected_artifacts=[
                        opp.get("artifact_path", "")
                        for opp in performance_opportunities
                    ],
                    recommendations=[
                        "Profile code to identify bottlenecks",
                        "Optimize algorithms and data structures",
                        "Consider caching for expensive operations",
                    ],
                    confidence=0.7,
                    created_at=datetime.now(),
                ),
            )

        # Analyze relationship patterns
        if relationships:
            import_relationships = [
                rel
                for rel in relationships
                if rel.get("relationship_type") == "imports"
            ]
            if len(import_relationships) > 50:
                insights.append(
                    ArtifactInsight(
                        insight_type="performance",
                        title="High Import Complexity",
                        description=f"Found {len(import_relationships)} import relationships indicating complex dependencies",
                        severity="low",
                        affected_artifacts=[
                            rel.get("source_artifact", "")
                            for rel in import_relationships
                        ],
                        recommendations=[
                            "Review and simplify import dependencies",
                            "Consider using dependency injection",
                            "Implement circular dependency detection",
                        ],
                        confidence=0.6,
                        created_at=datetime.now(),
                    ),
                )

        return insights

    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting"""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(severity, 0)


def main() -> None:
    """Test ArtifactSynthesizer"""
    logger.info("Starting ArtifactSynthesizer test")

    synthesizer = ArtifactSynthesizer()

    # Create sample data for testing
    sample_artifacts = [
        {
            "path": "test_file.py",
            "artifact_type": "python",
            "parsed_data": {
                "complexity": 15,
                "functions": [{"name": "test_func", "args": 5}],
            },
        },
    ]

    sample_relationships = [
        {
            "source_artifact": "file1.py",
            "target_artifact": "file2.py",
            "relationship_type": "imports",
        },
    ]

    sample_opportunities = [
        {
            "artifact_path": "test_file.py",
            "opportunity_type": "syntax_error",
            "severity": "critical",
            "description": "Syntax error detected",
        },
    ]

    logger.info("Running insight synthesis on sample data")
    insights = synthesizer.synthesize_insights(
        sample_artifacts,
        sample_relationships,
        sample_opportunities,
    )

    print("🔍 **ARTIFACT INSIGHTS:**")
    print(f"Total insights generated: {len(insights)}")

    for insight in insights[:3]:  # Show first 3
        print(
            f"  {insight.title} ({insight.insight_type}, {insight.severity}): {insight.description}",
        )


if __name__ == "__main__":
    main()
