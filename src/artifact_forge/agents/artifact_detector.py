#!/usr/bin/env python3
"""
ArtifactDetector Agent
Discovers and classifies artifacts in the codebase
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArtifactInfo:
    """Information about a discovered artifact"""

    path: str
    artifact_type: str  # 'python', 'mdc', 'markdown', 'yaml', 'json', etc.
    size: int
    complexity_score: Optional[float] = None
    last_modified: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ArtifactDetector:
    """Detects and classifies artifacts in the codebase"""

    def __init__(self) -> None:
        self.artifact_patterns = {
            "python": ["*.py", "*.pyx", "*.pyi"],
            "mdc": ["*.mdc"],
            "markdown": ["*.md", "*.markdown"],
            "yaml": ["*.yaml", "*.yml"],
            "json": ["*.json"],
            "sql": ["*.sql"],
            "shell": ["*.sh", "*.bash", "*.zsh"],
            "docker": ["Dockerfile", "*.dockerfile"],
            "terraform": ["*.tf", "*.tfvars"],
            "kubernetes": ["*.yaml", "*.yml"],  # Overlaps with yaml
            "html": ["*.html", "*.htm"],
            "css": ["*.css", "*.scss", "*.sass"],
            "javascript": ["*.js", "*.ts", "*.jsx", "*.tsx"],
        }

        self.exclude_patterns = [
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".venv",
            "venv",
            "node_modules",
            ".DS_Store",
        ]

    def detect_artifacts(self, root_path: str) -> List[ArtifactInfo]:
        """Detect all artifacts in the codebase"""
        artifacts = []
        root = Path(root_path)

        for artifact_type, patterns in self.artifact_patterns.items():
            for pattern in patterns:
                for file_path in root.rglob(pattern):
                    if self._should_include_file(file_path):
                        artifact_info = self._create_artifact_info(
                            file_path, artifact_type
                        )
                        artifacts.append(artifact_info)

        return artifacts

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in analysis"""
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in str(file_path):
                return False

        # Check if file exists and is readable
        if not file_path.is_file():
            return False

        return True

    def _create_artifact_info(
        self, file_path: Path, artifact_type: str
    ) -> ArtifactInfo:
        """Create ArtifactInfo for a file"""
        stat = file_path.stat()

        return ArtifactInfo(
            path=str(file_path),
            artifact_type=artifact_type,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            metadata={
                "lines": self._count_lines(file_path),
                "extension": file_path.suffix,
                "depth": len(file_path.parts) - 1,
            },
        )

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def classify_artifact(self, artifact_info: ArtifactInfo) -> Dict[str, Any]:
        """Classify artifact based on content and structure"""
        classification = {
            "type": artifact_info.artifact_type,
            "complexity": self._assess_complexity(artifact_info),
            "category": self._categorize_artifact(artifact_info),
            "priority": self._assess_priority(artifact_info),
        }

        return classification

    def _assess_complexity(self, artifact_info: ArtifactInfo) -> str:
        """Assess complexity of artifact"""
        size = artifact_info.size
        lines = artifact_info.metadata.get("lines", 0) if artifact_info.metadata else 0

        if size > 100000 or lines > 1000:
            return "high"
        elif size > 10000 or lines > 100:
            return "medium"
        else:
            return "low"

    def _categorize_artifact(self, artifact_info: ArtifactInfo) -> str:
        """Categorize artifact based on type and location"""
        path_parts = Path(artifact_info.path).parts

        if "tests" in path_parts:
            return "test"
        elif "docs" in path_parts or "documentation" in path_parts:
            return "documentation"
        elif "config" in path_parts or "settings" in path_parts:
            return "configuration"
        elif "src" in path_parts or "lib" in path_parts:
            return "source"
        else:
            return "other"

    def _assess_priority(self, artifact_info: ArtifactInfo) -> str:
        """Assess priority for processing"""
        if artifact_info.artifact_type in ["python", "mdc"]:
            return "high"
        elif artifact_info.artifact_type in ["yaml", "json", "markdown"]:
            return "medium"
        else:
            return "low"


def main() -> None:
    """Test ArtifactDetector"""
    detector = ArtifactDetector()
    artifacts = detector.detect_artifacts(".")

    print("🔍 **ARTIFACT DETECTION RESULTS:**")
    print(f"Total artifacts found: {len(artifacts)}")

    # Group by type
    by_type: Dict[str, List[ArtifactInfo]] = {}
    for artifact in artifacts:
        artifact_type = artifact.artifact_type
        if artifact_type not in by_type:
            by_type[artifact_type] = []
        by_type[artifact_type].append(artifact)

    print("\n📊 **BY TYPE:**")
    for artifact_type, artifacts_list in by_type.items():
        print(f"  {artifact_type}: {len(artifacts_list)} artifacts")

    print("\n🎯 **HIGH PRIORITY ARTIFACTS:**")
    high_priority = [a for a in artifacts if a.artifact_type in ["python", "mdc"]]
    for artifact in high_priority[:10]:  # Show first 10
        print(f"  - {artifact.path} ({artifact.artifact_type})")


if __name__ == "__main__":
    main()
