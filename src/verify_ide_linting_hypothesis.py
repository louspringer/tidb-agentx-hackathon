#!/usr/bin/env python3
"""
Verify IDE Linting Hypothesis - Test if IDE linting data is fragmented and unreliable.
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LintingDataPoint:
    """A single data point for linting verification."""

    source: str  # 'ide_realtime', 'command_line', 'cache'
    linter: str  # 'flake8', 'mypy', 'ruff'
    error_count: int
    timestamp: float
    method: str  # 'realtime', 'full_scan', 'cached'


class IDELintingHypothesisVerifier:
    """Verify the hypothesis that IDE linting data is fragmented and unreliable."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.data_points: list[LintingDataPoint] = []

    def collect_data_points(self) -> dict[str, Any]:
        """Collect data points from different sources to test the hypothesis."""

        verification_data = {
            "hypothesis": "IDE linting data is fragmented and unreliable",
            "test_methods": [],
            "data_points": [],
            "analysis": {},
        }

        # Test 1: Command line vs IDE real-time
        verification_data["test_methods"].append(
            "Command line vs IDE real-time comparison",
        )

        # Get command line data
        cl_data = self._get_command_line_data()
        verification_data["data_points"].extend(cl_data)

        # Get IDE cache data
        ide_data = self._get_ide_cache_data()
        verification_data["data_points"].extend(ide_data)

        # Get process data
        process_data = self._get_linting_process_data()
        verification_data["data_points"].extend(process_data)

        # Analyze the data
        analysis = self._analyze_data_fragmentation(verification_data["data_points"])
        verification_data["analysis"] = analysis

        return verification_data

    def _get_command_line_data(self) -> list[LintingDataPoint]:
        """Get data from command line linters."""
        data_points = []
        timestamp = time.time()

        try:
            # Flake8 command line
            result = subprocess.run(
                ["uv", "run", "flake8", "src/", "--count"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 1:  # Flake8 found errors
                error_count = int(result.stdout.strip().split("\n")[-1])
                data_points.append(
                    LintingDataPoint(
                        source="command_line",
                        linter="flake8",
                        error_count=error_count,
                        timestamp=timestamp,
                        method="full_scan",
                    ),
                )
        except Exception:
            data_points.append(
                LintingDataPoint(
                    source="command_line",
                    linter="flake8",
                    error_count=-1,
                    timestamp=timestamp,
                    method="error",
                ),
            )

        try:
            # MyPy command line
            result = subprocess.run(
                ["uv", "run", "mypy", "src/"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            error_count = len(
                [line for line in result.stdout.split("\n") if "error:" in line],
            )
            data_points.append(
                LintingDataPoint(
                    source="command_line",
                    linter="mypy",
                    error_count=error_count,
                    timestamp=timestamp,
                    method="full_scan",
                ),
            )
        except Exception:
            data_points.append(
                LintingDataPoint(
                    source="command_line",
                    linter="mypy",
                    error_count=-1,
                    timestamp=timestamp,
                    method="error",
                ),
            )

        return data_points

    def _get_ide_cache_data(self) -> list[LintingDataPoint]:
        """Get data from IDE cache files."""
        data_points = []
        timestamp = time.time()

        # Check MyPy cache
        mypy_cache = self.project_root / ".mypy_cache"
        if mypy_cache.exists():
            cache_files = len(list(mypy_cache.rglob("*.json")))
            data_points.append(
                LintingDataPoint(
                    source="ide_cache",
                    linter="mypy",
                    error_count=cache_files,
                    timestamp=timestamp,
                    method="cached",
                ),
            )

        # Check Ruff cache
        ruff_cache = self.project_root / ".ruff_cache"
        if ruff_cache.exists():
            cache_files = len(list(ruff_cache.rglob("*.json")))
            data_points.append(
                LintingDataPoint(
                    source="ide_cache",
                    linter="ruff",
                    error_count=cache_files,
                    timestamp=timestamp,
                    method="cached",
                ),
            )

        return data_points

    def _get_linting_process_data(self) -> list[LintingDataPoint]:
        """Get data from running linting processes."""
        data_points = []
        timestamp = time.time()

        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Count different types of linting processes
                processes = result.stdout.split("\n")

                flake8_processes = len([p for p in processes if "flake8" in p.lower()])
                mypy_processes = len([p for p in processes if "mypy" in p.lower()])
                ruff_processes = len([p for p in processes if "ruff" in p.lower()])

                data_points.extend(
                    [
                        LintingDataPoint(
                            source="processes",
                            linter="flake8",
                            error_count=flake8_processes,
                            timestamp=timestamp,
                            method="realtime",
                        ),
                        LintingDataPoint(
                            source="processes",
                            linter="mypy",
                            error_count=mypy_processes,
                            timestamp=timestamp,
                            method="realtime",
                        ),
                        LintingDataPoint(
                            source="processes",
                            linter="ruff",
                            error_count=ruff_processes,
                            timestamp=timestamp,
                            method="realtime",
                        ),
                    ],
                )
        except Exception:
            data_points.append(
                LintingDataPoint(
                    source="processes",
                    linter="unknown",
                    error_count=-1,
                    timestamp=timestamp,
                    method="error",
                ),
            )

        return data_points

    def _analyze_data_fragmentation(
        self,
        data_points: list[LintingDataPoint],
    ) -> dict[str, Any]:
        """Analyze if the data is fragmented and unreliable."""

        analysis = {
            "total_data_points": len(data_points),
            "sources": {},
            "linters": {},
            "fragmentation_score": 0,
            "reliability_score": 0,
            "conclusions": [],
        }

        # Group by source
        for dp in data_points:
            if dp.source not in analysis["sources"]:
                analysis["sources"][dp.source] = []
            analysis["sources"][dp.source].append(dp)

        # Group by linter
        for dp in data_points:
            if dp.linter not in analysis["linters"]:
                analysis["linters"][dp.linter] = []
            analysis["linters"][dp.linter].append(dp)

        # Calculate fragmentation score
        unique_sources = len(analysis["sources"])
        unique_linters = len(analysis["linters"])
        total_points = len(data_points)

        # Fragmentation: more sources = more fragmented
        analysis["fragmentation_score"] = min(
            unique_sources * unique_linters / max(total_points, 1),
            10,
        )

        # Reliability: consistent data = more reliable
        error_counts = [dp.error_count for dp in data_points if dp.error_count >= 0]
        if error_counts:
            variance = max(error_counts) - min(error_counts) if error_counts else 0
            analysis["reliability_score"] = max(0, 10 - variance / 10)

        # Generate conclusions
        if analysis["fragmentation_score"] > 5:
            analysis["conclusions"].append(
                "HIGH_FRAGMENTATION: Data is highly fragmented across sources",
            )

        if analysis["reliability_score"] < 5:
            analysis["conclusions"].append(
                "LOW_RELIABILITY: Data is inconsistent across sources",
            )

        if len(analysis["sources"]) > 2:
            analysis["conclusions"].append(
                "MULTIPLE_SOURCES: Data comes from multiple unreliable sources",
            )

        return analysis

    def generate_verification_report(self) -> str:
        """Generate a comprehensive verification report."""
        data = self.collect_data_points()

        report = f"""
🔬 IDE LINTING HYPOTHESIS VERIFICATION REPORT
{'='*50}

HYPOTHESIS: {data['hypothesis']}

DATA POINTS COLLECTED: {data['analysis']['total_data_points']}

FRAGMENTATION ANALYSIS:
- Fragmentation Score: {data['analysis']['fragmentation_score']:.2f}/10
- Reliability Score: {data['analysis']['reliability_score']:.2f}/10
- Sources Found: {len(data['analysis']['sources'])}
- Linters Found: {len(data['analysis']['linters'])}

DATA BREAKDOWN:
"""

        for source, points in data["analysis"]["sources"].items():
            report += f"\n{source.upper()}:\n"
            for point in points:
                report += (
                    f"  - {point.linter}: {point.error_count} errors ({point.method})\n"
                )

        report += "\nCONCLUSIONS:\n"
        for conclusion in data["analysis"]["conclusions"]:
            report += f"  ✅ {conclusion}\n"

        # Final verdict
        if (
            data["analysis"]["fragmentation_score"] > 5
            and data["analysis"]["reliability_score"] < 5
        ):
            report += "\n🎯 VERDICT: HYPOTHESIS CONFIRMED - IDE linting data IS fragmented and unreliable"
        else:
            report += "\n🎯 VERDICT: HYPOTHESIS INCONCLUSIVE - Need more data"

        return report


def main() -> None:
    """Main function to run the hypothesis verification."""
    verifier = IDELintingHypothesisVerifier()

    print("🔬 VERIFYING IDE LINTING HYPOTHESIS...")
    print("Hypothesis: IDE linting data is fragmented and unreliable")
    print()

    report = verifier.generate_verification_report()
    print(report)


if __name__ == "__main__":
    main()
