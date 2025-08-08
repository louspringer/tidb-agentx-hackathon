#!/usr/bin/env python3
"""
Analyze Current Codebase with Enhanced AST Models
Detect model issues as we build the complex model
"""

import os
import sys

# Add src to path
sys.path.append("src")

from artifact_forge.agents.artifact_parser_enhanced import EnhancedArtifactParser


def analyze_codebase() -> None:
    """Analyze current codebase with Enhanced AST Models"""

    print("🔍 ANALYZING CURRENT CODEBASE WITH ENHANCED AST MODELS:")
    print()

    # Initialize Enhanced AST Parser
    parser = EnhancedArtifactParser()

    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    print(f"📊 Found {len(python_files)} Python files to analyze")
    print()

    # Analyze files
    total_functions = 0
    total_classes = 0
    total_imports = 0
    files_with_errors = 0
    model_issues = []

    print("🎯 DETAILED ANALYSIS:")
    for file in python_files[:10]:  # Analyze first 10 files
        try:
            result = parser.parse_artifact(file, "python")

            functions = len(result.parsed_data.get("functions", []))
            classes = len(result.parsed_data.get("classes", []))
            imports = len(result.parsed_data.get("imports", []))

            print(f"   {file}:")
            print(f"      Functions: {functions}")
            print(f"      Classes: {classes}")
            print(f"      Imports: {imports}")
            print(
                f"      AST Parse Successful: {result.parsed_data.get('ast_parse_successful', False)}",
            )

            if result.parsing_errors:
                print(f"      ❌ Errors: {result.parsing_errors}")
                files_with_errors += 1
                model_issues.append(
                    {
                        "file": file,
                        "errors": result.parsing_errors,
                        "ast_successful": result.parsed_data.get(
                            "ast_parse_successful",
                            False,
                        ),
                    },
                )

            total_functions += functions
            total_classes += classes
            total_imports += imports

        except Exception as e:
            print(f"   {file}: ❌ Analysis failed - {e}")
            files_with_errors += 1
            model_issues.append(
                {"file": file, "errors": [str(e)], "ast_successful": False},
            )

    print()
    print("📊 SUMMARY:")
    print(f"   Total Files Analyzed: {len(python_files[:10])}")
    print(f"   Total Functions: {total_functions}")
    print(f"   Total Classes: {total_classes}")
    print(f"   Total Imports: {total_imports}")
    print(f"   Files with Errors: {files_with_errors}")
    print()

    print("🎯 MODEL ISSUES DETECTED:")
    for issue in model_issues:
        print(f"   {issue['file']}:")
        print(f"      AST Successful: {issue['ast_successful']}")
        print(f"      Errors: {issue['errors']}")
        print()

    print("🚀 NEXT STEPS:")
    print("   1. Fix model issues in Enhanced AST Models")
    print("   2. Bolt on Flake8 and MyPy models")
    print("   3. Create Complex Model")
    print("   4. Generate Perfect Code")


if __name__ == "__main__":
    analyze_codebase()
