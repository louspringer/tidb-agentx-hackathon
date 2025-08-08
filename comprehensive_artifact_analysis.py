#!/usr/bin/env python3
"""
🔍 Comprehensive Artifact Analysis and Requirements Tracing

This script performs a complete analysis of all artifacts in the project:
1. Identifies all artifacts not in .gitignore
2. Traces artifacts to requirements in the project model
3. Uses enhanced AST parser to reverse engineer Python artifacts
4. Validates model completeness and coverage
"""

import ast
import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ArtifactInfo:
    """Information about a project artifact"""

    path: str
    domain: Optional[str]
    file_type: str
    size_bytes: int
    requirements_traced: list[str]
    ast_analysis: Optional[dict[str, Any]] = None
    model_coverage: bool = False
    issues: list[str] = None


@dataclass
class ModelAnalysis:
    """Analysis of the project model"""

    total_artifacts: int
    artifacts_traced: int
    artifacts_untraced: int
    domain_coverage: dict[str, int]
    requirements_coverage: dict[str, int]
    missing_domains: list[str]
    missing_requirements: list[str]
    python_artifacts_analyzed: int
    ast_parsing_success: int
    ast_parsing_failures: int


class EnhancedASTParser:
    """Enhanced AST parser for reverse engineering Python artifacts"""

    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []
        self.variables = []
        self.comments = []
        self.errors = []

    def parse_file(self, file_path: str) -> dict[str, Any]:
        """Parse a Python file and extract comprehensive information"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Reset state
            self.imports = []
            self.functions = []
            self.classes = []
            self.variables = []
            self.comments = []
            self.errors = []

            # Extract line-by-line information
            lines = content.split("\n")

            # Analyze AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports.append(
                            {
                                "module": alias.name,
                                "asname": alias.asname,
                                "lineno": node.lineno,
                            },
                        )
                elif isinstance(node, ast.ImportFrom):
                    self.imports.append(
                        {
                            "module": node.module or "",
                            "names": [alias.name for alias in node.names],
                            "asnames": [alias.asname for alias in node.names],
                            "lineno": node.lineno,
                        },
                    )
                elif isinstance(node, ast.FunctionDef):
                    self.functions.append(
                        {
                            "name": node.name,
                            "lineno": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "decorators": [
                                self._get_decorator_name(d) for d in node.decorator_list
                            ],
                            "docstring": ast.get_docstring(node),
                        },
                    )
                elif isinstance(node, ast.ClassDef):
                    self.classes.append(
                        {
                            "name": node.name,
                            "lineno": node.lineno,
                            "bases": [self._get_base_name(base) for base in node.bases],
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                            "docstring": ast.get_docstring(node),
                        },
                    )
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.variables.append(
                                {
                                    "name": target.id,
                                    "lineno": node.lineno,
                                    "value_type": type(node.value).__name__,
                                },
                            )

            # Extract comments (simple approach)
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    self.comments.append({"line": i, "content": stripped[1:].strip()})

            return {
                "success": True,
                "imports": self.imports,
                "functions": self.functions,
                "classes": self.classes,
                "variables": self.variables,
                "comments": self.comments,
                "total_lines": len(lines),
                "code_lines": len(
                    [
                        line
                        for line in lines
                        if line.strip() and not line.strip().startswith("#")
                    ],
                ),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "imports": [],
                "functions": [],
                "classes": [],
                "variables": [],
                "comments": [],
            }

    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
        return str(decorator)

    def _get_base_name(self, base) -> str:
        """Extract base class name"""
        if isinstance(base, ast.Name):
            return base.id
        return str(base)


class ArtifactAnalyzer:
    """Comprehensive artifact analyzer"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.model_file = self.project_root / "project_model_registry.json"
        self.ast_parser = EnhancedASTParser()
        self.artifacts: list[ArtifactInfo] = []
        self.model_data: dict[str, Any] = {}
        self.analysis: ModelAnalysis = None

        # Load project model
        self._load_model()

        # Define file type patterns
        self.file_patterns = {
            "python": [".py"],
            "yaml": [".yaml", ".yml"],
            "json": [".json"],
            "markdown": [".md", ".markdown"],
            "shell": [".sh", ".bash"],
            "docker": ["Dockerfile"],
            "go": [".go"],
            "proto": [".proto"],
            "toml": [".toml"],
            "requirements": ["requirements.txt", "pyproject.toml"],
            "config": [".env", ".ini", ".cfg"],
            "documentation": [".rst", ".txt"],
            "data": [".csv", ".parquet", ".jsonl"],
            "image": [".png", ".jpg", ".jpeg", ".svg", ".gif"],
            "binary": [".exe", ".bin", ".appimage"],
        }

    def _load_model(self):
        """Load the project model registry"""
        try:
            with open(self.model_file) as f:
                self.model_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_data = {}

    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension and content"""
        path = Path(file_path)
        ext = path.suffix.lower()
        name = path.name.lower()

        for file_type, patterns in self.file_patterns.items():
            if ext in patterns or name in patterns:
                return file_type

        # Check for Python files with shebang
        if ext == "":
            try:
                with open(file_path) as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("#!/usr/bin/env python"):
                        return "python"
            except Exception:
                pass

        return "unknown"

    def _detect_domain(self, file_path: str, file_type: str) -> Optional[str]:
        """Detect domain based on file path and project model patterns"""
        if not self.model_data.get("domains"):
            return None

        file_path_str = str(file_path)
        best_match = None
        best_score = 0

        for domain_name, domain_config in self.model_data["domains"].items():
            patterns = domain_config.get("patterns", [])
            content_indicators = domain_config.get("content_indicators", [])

            # Check patterns with scoring
            for pattern in patterns:
                if self._matches_pattern(file_path_str, pattern):
                    score = self._calculate_pattern_score(pattern)
                    if score > best_score:
                        best_score = score
                        best_match = domain_name
                        # print(f"    🎯 New best match: {domain_name} with pattern '{pattern}' (score: {score})")

        # Check content indicators for Python files (only if no specific pattern matched)
        if file_type == "python" and best_score < 10:
            for domain_name, domain_config in self.model_data["domains"].items():
                content_indicators = domain_config.get("content_indicators", [])
                if content_indicators:
                    try:
                        with open(file_path) as f:
                            content = f.read()
                            for indicator in content_indicators:
                                if indicator in content:
                                    # Content indicators get medium priority (lower than specific patterns)
                                    score = 50
                                    if score > best_score:
                                        best_score = score
                                        best_match = domain_name
                                        # print(f"    🎯 Content indicator match: {domain_name} (score: {score})")
                    except Exception:
                        pass

        return best_match

    def _calculate_pattern_score(self, pattern: str) -> int:
        """Calculate pattern specificity score"""
        if pattern == "*.py":
            return 1  # Lowest priority for generic Python pattern
        if pattern == "*.mdc":
            return 1  # Lowest priority for generic MDC pattern
        if "*" in pattern:
            # Count path segments for specificity
            parts = pattern.split("/")
            # More specific patterns (with more path segments) get higher scores
            specificity = len([p for p in parts if p != "*"])
            # Exact path matches get bonus points
            if pattern.count("*") == 1 and pattern.endswith("*.py"):
                specificity += 10
            # Domain-specific patterns get higher priority
            if any(
                domain in pattern
                for domain in ["mcp", "ghostbusters", "streamlit", "healthcare"]
            ):
                specificity += 20
            return specificity
        # Exact match gets highest priority
        return 100

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern"""
        # Simple pattern matching - could be enhanced with glob
        if "*" in pattern:
            # Convert glob pattern to simple matching
            pattern_parts = pattern.replace("*", "").split("/")
            file_parts = file_path.split("/")

            # Check if pattern parts are in file parts
            pattern_idx = 0
            for part in file_parts:
                if (
                    pattern_idx < len(pattern_parts)
                    and pattern_parts[pattern_idx] in part
                ):
                    pattern_idx += 1
                    if pattern_idx >= len(pattern_parts):
                        return True
            return pattern_idx >= len(pattern_parts)
        return pattern in file_path

    def _trace_requirements(self, domain: Optional[str], file_path: str) -> list[str]:
        """Trace artifact to requirements in the project model"""
        requirements = []

        if not domain or not self.model_data.get("requirements_traceability"):
            return requirements

        # Find requirements for this domain
        for req in self.model_data["requirements_traceability"]:
            if req.get("domain") == domain or req.get("domain") == "*":
                requirements.append(req["requirement"])

        return requirements

    def discover_artifacts(self) -> list[ArtifactInfo]:
        """Discover all artifacts in the project"""
        artifacts = []

        # Get gitignore patterns
        gitignore_patterns = self._load_gitignore_patterns()

        for root, dirs, files in os.walk(self.project_root):
            # Skip git and cache directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", ".venv"]
            ]

            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)

                # Skip if in gitignore
                if self._is_ignored(str(relative_path), gitignore_patterns):
                    continue

                # Get file info
                try:
                    stat = file_path.stat()
                    file_type = self._get_file_type(str(file_path))
                    domain = self._detect_domain(str(file_path), file_type)
                    requirements = self._trace_requirements(domain, str(file_path))

                    # Debug: Check for specific files
                    if (
                        "mcp_integration" in str(file_path)
                        or "ghostbusters_gcp" in str(file_path)
                        or "mdc_generator" in str(file_path)
                    ):
                        print(f"🔍 Found file: {file_path} -> domain: {domain}")

                    artifact = ArtifactInfo(
                        path=str(relative_path),
                        domain=domain,
                        file_type=file_type,
                        size_bytes=stat.st_size,
                        requirements_traced=requirements,
                        issues=[],
                    )

                    # Analyze Python files with AST
                    if file_type == "python":
                        ast_result = self.ast_parser.parse_file(str(file_path))
                        artifact.ast_analysis = ast_result
                        if not ast_result["success"]:
                            artifact.issues.append(
                                f"AST parsing failed: {ast_result.get('error', 'Unknown error')}",
                            )

                    artifacts.append(artifact)

                except Exception as e:
                    print(f"⚠️ Error processing {file_path}: {e}")

        self.artifacts = artifacts
        return artifacts

    def _load_gitignore_patterns(self) -> list[str]:
        """Load gitignore patterns"""
        gitignore_file = self.project_root / ".gitignore"
        patterns = []

        if gitignore_file.exists():
            try:
                with open(gitignore_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except Exception as e:
                print(f"⚠️ Error reading .gitignore: {e}")

        return patterns

    def _is_ignored(self, file_path: str, patterns: list[str]) -> bool:
        """Check if file should be ignored based on gitignore patterns"""
        for pattern in patterns:
            if pattern in file_path or file_path.endswith(pattern):
                return True
        return False

    def analyze_model_coverage(self) -> ModelAnalysis:
        """Analyze model coverage and completeness"""
        if not self.artifacts:
            self.discover_artifacts()

        # Count artifacts by domain
        domain_counts = defaultdict(int)
        traced_artifacts = 0
        untraced_artifacts = 0
        python_artifacts = 0
        ast_success = 0
        ast_failures = 0

        for artifact in self.artifacts:
            if artifact.domain:
                domain_counts[artifact.domain] += 1
                traced_artifacts += 1
            else:
                untraced_artifacts += 1

            if artifact.file_type == "python":
                python_artifacts += 1
                if artifact.ast_analysis:
                    if artifact.ast_analysis["success"]:
                        ast_success += 1
                    else:
                        ast_failures += 1

        # Find missing domains
        model_domains = set(self.model_data.get("domains", {}).keys())
        artifact_domains = set(domain_counts.keys())
        missing_domains = list(model_domains - artifact_domains)

        # Find missing requirements
        all_requirements = set()
        traced_requirements = set()

        for req in self.model_data.get("requirements_traceability", []):
            all_requirements.add(req["requirement"])

        for artifact in self.artifacts:
            traced_requirements.update(artifact.requirements_traced)

        missing_requirements = list(all_requirements - traced_requirements)

        # Count requirements coverage
        requirements_coverage = {}
        for req in self.model_data.get("requirements_traceability", []):
            req_name = req["requirement"]
            count = sum(1 for a in self.artifacts if req_name in a.requirements_traced)
            requirements_coverage[req_name] = count

        self.analysis = ModelAnalysis(
            total_artifacts=len(self.artifacts),
            artifacts_traced=traced_artifacts,
            artifacts_untraced=untraced_artifacts,
            domain_coverage=dict(domain_counts),
            requirements_coverage=requirements_coverage,
            missing_domains=missing_domains,
            missing_requirements=missing_requirements,
            python_artifacts_analyzed=python_artifacts,
            ast_parsing_success=ast_success,
            ast_parsing_failures=ast_failures,
        )

        return self.analysis

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive analysis report"""
        if not self.analysis:
            self.analyze_model_coverage()

        # Group artifacts by domain
        artifacts_by_domain = defaultdict(list)
        for artifact in self.artifacts:
            domain = artifact.domain or "untraced"
            artifacts_by_domain[domain].append(asdict(artifact))

        # Find Python artifacts with issues
        python_issues = [
            a for a in self.artifacts if a.file_type == "python" and a.issues
        ]

        # Find large files
        large_files = [a for a in self.artifacts if a.size_bytes > 1000000]  # > 1MB

        report = {
            "summary": {
                "total_artifacts": self.analysis.total_artifacts,
                "traced_artifacts": self.analysis.artifacts_traced,
                "untraced_artifacts": self.analysis.artifacts_untraced,
                "coverage_percentage": (
                    self.analysis.artifacts_traced / self.analysis.total_artifacts * 100
                )
                if self.analysis.total_artifacts > 0
                else 0,
            },
            "domain_analysis": {
                "domain_counts": self.analysis.domain_coverage,
                "missing_domains": self.analysis.missing_domains,
                "artifacts_by_domain": dict(artifacts_by_domain),
            },
            "requirements_analysis": {
                "requirements_coverage": self.analysis.requirements_coverage,
                "missing_requirements": self.analysis.missing_requirements,
                "total_requirements": len(
                    self.model_data.get("requirements_traceability", []),
                ),
                "traced_requirements": len(
                    set().union(*[a.requirements_traced for a in self.artifacts]),
                ),
            },
            "python_analysis": {
                "total_python_files": self.analysis.python_artifacts_analyzed,
                "ast_parsing_success": self.analysis.ast_parsing_success,
                "ast_parsing_failures": self.analysis.ast_parsing_failures,
                "python_issues": [asdict(a) for a in python_issues],
            },
            "file_type_analysis": {
                "file_types": defaultdict(int),
                "large_files": [asdict(a) for a in large_files],
            },
            "recommendations": self._generate_recommendations(),
        }

        # Add file type counts
        for artifact in self.artifacts:
            report["file_type_analysis"]["file_types"][artifact.file_type] += 1

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Coverage recommendations
        if self.analysis.artifacts_untraced > 0:
            recommendations.append(
                f"🔍 {self.analysis.artifacts_untraced} artifacts are not traced to any domain. Consider adding domain patterns for these files.",
            )

        if self.analysis.missing_domains:
            recommendations.append(
                f"📁 Domains defined in model but no artifacts found: {', '.join(self.analysis.missing_domains)}",
            )

        if self.analysis.missing_requirements:
            recommendations.append(
                f"📋 {len(self.analysis.missing_requirements)} requirements are not traced to any artifacts. Consider implementing these requirements.",
            )

        # Python analysis recommendations
        if self.analysis.ast_parsing_failures > 0:
            recommendations.append(
                f"🐍 {self.analysis.ast_parsing_failures} Python files failed AST parsing. Review these files for syntax issues.",
            )

        # Large file recommendations
        large_files = [a for a in self.artifacts if a.size_bytes > 1000000]
        if large_files:
            recommendations.append(
                f"📦 {len(large_files)} files are larger than 1MB. Consider if these should be in version control.",
            )

        return recommendations


def main():
    """Main analysis function"""
    print("🔍 Comprehensive Artifact Analysis and Requirements Tracing")
    print("=" * 60)

    # Initialize analyzer
    analyzer = ArtifactAnalyzer(".")

    # Discover artifacts
    print("📁 Discovering artifacts...")
    artifacts = analyzer.discover_artifacts()
    print(f"✅ Found {len(artifacts)} artifacts")

    # Analyze model coverage
    print("📊 Analyzing model coverage...")
    analyzer.analyze_model_coverage()

    # Generate report
    print("📋 Generating comprehensive report...")
    report = analyzer.generate_report()

    # Print summary
    print("\n📈 ANALYSIS SUMMARY")
    print("=" * 40)
    print(f"Total Artifacts: {report['summary']['total_artifacts']}")
    print(f"Traced Artifacts: {report['summary']['traced_artifacts']}")
    print(f"Untraced Artifacts: {report['summary']['untraced_artifacts']}")
    print(f"Coverage: {report['summary']['coverage_percentage']:.1f}%")
    print(f"Python Files Analyzed: {report['python_analysis']['total_python_files']}")
    print(f"AST Parsing Success: {report['python_analysis']['ast_parsing_success']}")
    print(f"AST Parsing Failures: {report['python_analysis']['ast_parsing_failures']}")

    # Print domain analysis
    print("\n🏷️ DOMAIN ANALYSIS")
    print("=" * 40)
    for domain, count in report["domain_analysis"]["domain_counts"].items():
        print(f"{domain}: {count} artifacts")

    if report["domain_analysis"]["missing_domains"]:
        print(
            f"Missing domains: {', '.join(report['domain_analysis']['missing_domains'])}",
        )

    # Print requirements analysis
    print("\n📋 REQUIREMENTS ANALYSIS")
    print("=" * 40)
    print(
        f"Total Requirements: {report['requirements_analysis']['total_requirements']}",
    )
    print(
        f"Traced Requirements: {report['requirements_analysis']['traced_requirements']}",
    )

    if report["requirements_analysis"]["missing_requirements"]:
        print(
            f"Missing requirements: {len(report['requirements_analysis']['missing_requirements'])}",
        )

    # Print recommendations
    print("\n💡 RECOMMENDATIONS")
    print("=" * 40)
    for rec in report["recommendations"]:
        print(f"• {rec}")

    # Save detailed report
    report_file = "comprehensive_artifact_analysis_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Detailed report saved to: {report_file}")

    return report


if __name__ == "__main__":
    main()
