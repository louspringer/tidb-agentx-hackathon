#!/usr/bin/env python3
"""
Fix critical syntax errors in Python files
"""

import os
from pathlib import Path


def fix_file(filepath: str) -> bool:
    """Fix syntax errors in a Python file"""
    try:
        with open(filepath) as f:
            content = f.read()

        original_content = content

        # Fix common indentation issues
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # Skip lines that are clearly not Python code
            if line.strip().startswith("You are a") and "analyzing" in line:
                continue
            if line.strip().startswith("Context:") and "{" in line:
                continue
            if line.strip().startswith("Analyze this context"):
                continue
            if line.strip().startswith("Return your analysis"):
                continue
            if line.strip().startswith("Focus on"):
                continue
            if (
                line.strip().startswith("- question:")
                or line.strip().startswith("- confidence:")
                or line.strip().startswith("- blind_spots:")
                or line.strip().startswith("- recommendation:")
            ):
                continue

            # Fix indentation issues
            if (
                line.strip()
                and not line.startswith(" ")
                and not line.startswith("\t")
                and not line.startswith("#")
            ):
                # This might be a class or function definition that needs proper indentation
                if line.strip().startswith("class ") or line.strip().startswith("def "):
                    fixed_lines.append(line)
                else:
                    # Skip malformed lines
                    continue
            else:
                fixed_lines.append(line)

        fixed_content = "\n".join(fixed_lines)

        # Only write if content changed
        if fixed_content != original_content:
            with open(filepath, "w") as f:
                f.write(fixed_content)
            print(f"Fixed: {filepath}")
            return True

        return False

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def main():
    """Fix syntax errors in Python files"""
    Path("src")

    # List of files with known issues
    problematic_files = [
        "src/multi_agent_testing/cost_analysis.py",
        "src/multi_agent_testing/diversity_synthesis_orchestrator.py",
        "src/multi_agent_testing/debug_anthropic_api.py",
        "src/multi_agent_testing/meta_cognitive_orchestrator.py",
        "src/multi_agent_testing/langgraph_diversity_orchestrator.py",
        "src/multi_agent_testing/live_smoke_test.py",
        "src/multi_agent_testing/diversity_hypothesis_demo.py",
        "src/multi_agent_testing/test_meta_cognitive_orchestrator.py",
        "src/mdc_generator/mdc_model.py",
    ]

    fixed_count = 0
    for filepath in problematic_files:
        if os.path.exists(filepath) and fix_file(filepath):
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
