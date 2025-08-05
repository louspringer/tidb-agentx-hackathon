#!/usr/bin/env python3
"""
ArtifactOptimizer Agent
Identifies optimization opportunities and fixes issues
"""

import logging
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OptimizationOpportunity:
    """An optimization opportunity found in an artifact"""

    artifact_path: str
    opportunity_type: str  # 'syntax_error', 'performance', 'quality', 'security'
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    suggested_fix: str
    confidence: float
    created_at: datetime


class ArtifactOptimizer:
    """Identifies optimization opportunities in artifacts"""

    def __init__(self):
        self.optimization_types = {
            "syntax_error": self._find_syntax_errors,
            "performance": self._find_performance_issues,
            "quality": self._find_quality_issues,
            "security": self._find_security_issues,
        }

    def optimize_artifacts(
        self, artifacts: List[Dict[str, Any]]
    ) -> List[OptimizationOpportunity]:
        """Find optimization opportunities in artifacts"""
        logger.info(f"Starting optimization analysis of {len(artifacts)} artifacts")

        opportunities = []

        for artifact in artifacts:
            try:
                artifact_opportunities = self._analyze_artifact(artifact)
                opportunities.extend(artifact_opportunities)
            except Exception as e:
                logger.error(f"Error analyzing {artifact.get('path', 'unknown')}: {e}")
                continue

        # Sort by severity and confidence
        opportunities.sort(
            key=lambda x: (self._severity_score(x.severity), x.confidence), reverse=True
        )

        logger.info(f"Found {len(opportunities)} optimization opportunities")
        return opportunities

    def _analyze_artifact(
        self, artifact: Dict[str, Any]
    ) -> List[OptimizationOpportunity]:
        """Analyze a single artifact for optimization opportunities"""
        opportunities = []
        artifact_path = artifact.get("path", "")
        artifact_type = artifact.get("artifact_type", "")

        # Run all optimization checks
        for opt_type, finder_func in self.optimization_types.items():
            try:
                opts = finder_func(artifact)
                opportunities.extend(opts)
            except Exception as e:
                logger.debug(f"Error in {opt_type} analysis for {artifact_path}: {e}")

        return opportunities

    def _find_syntax_errors(
        self, artifact: Dict[str, Any]
    ) -> List[OptimizationOpportunity]:
        """Find syntax errors in artifacts"""
        opportunities = []
        artifact_path = artifact.get("path", "")
        artifact_type = artifact.get("artifact_type", "")

        if artifact_type == "python":
            try:
                with open(artifact_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try to parse with ast
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    opportunities.append(
                        OptimizationOpportunity(
                            artifact_path=artifact_path,
                            opportunity_type="syntax_error",
                            severity="critical",
                            description=f"Syntax error: {str(e)}",
                            suggested_fix=self._suggest_syntax_fix(content, str(e)),
                            confidence=0.95,
                            created_at=datetime.now(),
                        )
                    )

                # Check for common indentation issues
                indentation_issues = self._check_indentation(content)
                for issue in indentation_issues:
                    opportunities.append(
                        OptimizationOpportunity(
                            artifact_path=artifact_path,
                            opportunity_type="syntax_error",
                            severity="high",
                            description=f"Indentation issue: {issue}",
                            suggested_fix="Fix indentation using consistent spacing (4 spaces)",
                            confidence=0.8,
                            created_at=datetime.now(),
                        )
                    )

            except Exception as e:
                opportunities.append(
                    OptimizationOpportunity(
                        artifact_path=artifact_path,
                        opportunity_type="syntax_error",
                        severity="critical",
                        description=f"File reading error: {str(e)}",
                        suggested_fix="Check file permissions and encoding",
                        confidence=0.9,
                        created_at=datetime.now(),
                    )
                )

        return opportunities

    def _find_performance_issues(
        self, artifact: Dict[str, Any]
    ) -> List[OptimizationOpportunity]:
        """Find performance issues in artifacts"""
        opportunities = []
        artifact_path = artifact.get("path", "")
        artifact_type = artifact.get("artifact_type", "")

        if artifact_type == "python":
            parsed_data = artifact.get("parsed_data", {})

            # Check for large functions
            functions = parsed_data.get("functions", [])
            for func in functions:
                if func.get("args", 0) > 10:
                    opportunities.append(
                        OptimizationOpportunity(
                            artifact_path=artifact_path,
                            opportunity_type="performance",
                            severity="medium",
                            description=f"Function '{func.get('name', 'unknown')}' has too many parameters",
                            suggested_fix="Consider using a configuration object or data class",
                            confidence=0.7,
                            created_at=datetime.now(),
                        )
                    )

            # Check for high complexity
            complexity = parsed_data.get("complexity", 0)
            if complexity > 10:
                opportunities.append(
                    OptimizationOpportunity(
                        artifact_path=artifact_path,
                        opportunity_type="performance",
                        severity="medium",
                        description=f"High cyclomatic complexity: {complexity}",
                        suggested_fix="Break down complex functions into smaller, simpler functions",
                        confidence=0.8,
                        created_at=datetime.now(),
                    )
                )

        return opportunities

    def _find_quality_issues(
        self, artifact: Dict[str, Any]
    ) -> List[OptimizationOpportunity]:
        """Find code quality issues"""
        opportunities = []
        artifact_path = artifact.get("path", "")
        artifact_type = artifact.get("artifact_type", "")

        if artifact_type == "python":
            try:
                with open(artifact_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for long lines
                lines = content.splitlines()
                long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 100]
                if long_lines:
                    opportunities.append(
                        OptimizationOpportunity(
                            artifact_path=artifact_path,
                            opportunity_type="quality",
                            severity="low",
                            description=f"Long lines found at: {long_lines[:5]}",
                            suggested_fix="Break long lines to improve readability",
                            confidence=0.6,
                            created_at=datetime.now(),
                        )
                    )

                # Check for missing docstrings
                parsed_data = artifact.get("parsed_data", {})
                functions = parsed_data.get("functions", [])
                if functions and len(functions) > 5:
                    opportunities.append(
                        OptimizationOpportunity(
                            artifact_path=artifact_path,
                            opportunity_type="quality",
                            severity="low",
                            description="Multiple functions without docstrings",
                            suggested_fix="Add docstrings to improve code documentation",
                            confidence=0.5,
                            created_at=datetime.now(),
                        )
                    )

            except Exception as e:
                logger.debug(f"Error checking quality for {artifact_path}: {e}")

        return opportunities

    def _find_security_issues(
        self, artifact: Dict[str, Any]
    ) -> List[OptimizationOpportunity]:
        """Find security issues in artifacts"""
        opportunities = []
        artifact_path = artifact.get("path", "")
        artifact_type = artifact.get("artifact_type", "")

        if artifact_type == "python":
            try:
                with open(artifact_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for hardcoded credentials
                credential_patterns = [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']',
                ]

                for pattern in credential_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        opportunities.append(
                            OptimizationOpportunity(
                                artifact_path=artifact_path,
                                opportunity_type="security",
                                severity="high",
                                description="Potential hardcoded credentials found",
                                suggested_fix="Use environment variables or secure configuration management",
                                confidence=0.8,
                                created_at=datetime.now(),
                            )
                        )
                        break

                # Check for dangerous imports
                dangerous_imports = ["pickle", "marshal", "subprocess"]
                imports = artifact.get("parsed_data", {}).get("imports", [])
                for imp in imports:
                    for dangerous in dangerous_imports:
                        if dangerous in imp:
                            opportunities.append(
                                OptimizationOpportunity(
                                    artifact_path=artifact_path,
                                    opportunity_type="security",
                                    severity="medium",
                                    description=f"Potentially dangerous import: {imp}",
                                    suggested_fix="Review and validate the use of this import",
                                    confidence=0.6,
                                    created_at=datetime.now(),
                                )
                            )

            except Exception as e:
                logger.debug(f"Error checking security for {artifact_path}: {e}")

        return opportunities

    def _suggest_syntax_fix(self, content: str, error_msg: str) -> str:
        """Suggest a fix for a syntax error"""
        if "unterminated string literal" in error_msg:
            return "Check for missing quotes or escape sequences in strings"
        elif "unindent does not match" in error_msg:
            return "Fix indentation - ensure consistent use of spaces or tabs"
        elif "unexpected indent" in error_msg:
            return "Remove unexpected indentation or fix indentation level"
        elif "invalid syntax" in error_msg:
            return "Check for missing colons, parentheses, or invalid characters"
        else:
            return "Review the syntax error and fix according to Python syntax rules"

    def _check_indentation(self, content: str) -> List[str]:
        """Check for indentation issues"""
        issues = []
        lines = content.splitlines()

        for i, line in enumerate(lines):
            if line.strip() and not line.startswith("#"):
                # Check for mixed tabs and spaces
                if "\t" in line and "    " in line:
                    issues.append(f"Mixed tabs and spaces at line {i+1}")

                # Check for inconsistent indentation
                if line.startswith(" ") and len(line) - len(line.lstrip()) % 4 != 0:
                    issues.append(f"Inconsistent indentation at line {i+1}")

        return issues

    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting"""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(severity, 0)


def main():
    """Test ArtifactOptimizer"""
    logger.info("Starting ArtifactOptimizer test")

    optimizer = ArtifactOptimizer()

    # Create sample artifacts for testing
    sample_artifacts = [
        {
            "path": "comprehensive_ast_modeler.py",
            "artifact_type": "python",
            "parsed_data": {
                "functions": [{"name": "test_func", "args": 5}],
                "complexity": 15,
                "imports": ["import ast", "import pickle"],
            },
        }
    ]

    logger.info("Running optimization analysis on sample artifacts")
    opportunities = optimizer.optimize_artifacts(sample_artifacts)

    print(f"🔍 **OPTIMIZATION OPPORTUNITIES:**")
    print(f"Total opportunities found: {len(opportunities)}")

    for opp in opportunities[:5]:  # Show first 5
        print(
            f"  {opp.artifact_path} ({opp.opportunity_type}, {opp.severity}): {opp.description}"
        )


if __name__ == "__main__":
    main()
