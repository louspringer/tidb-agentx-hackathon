#!/usr/bin/env python3
"""
AST Data Validation Framework
Validate AST models and conversion results
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of data validation"""

    passed: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]


class ASTDataValidator:
    """Validate AST models and conversion data"""

    def __init__(self) -> None:
        self.results = ValidationResult(True, [], [], {})

    def validate_ast_file(self, ast_file: str) -> ValidationResult:
        """Validate AST model file"""
        try:
            with open(ast_file, "r") as f:
                ast_data = json.load(f)

            # Check required fields
            required_fields = ["file_models", "metadata", "summary"]
            for field in required_fields:
                if field not in ast_data:
                    self.results.errors.append(f"Missing required field: {field}")
                    self.results.passed = False

            # Check file models
            if "file_models" in ast_data:
                file_count = len(ast_data["file_models"])
                self.results.details["file_count"] = file_count

                # Check for mypy cache files
                mypy_cache_count = sum(
                    1
                    for path in ast_data["file_models"].keys()
                    if ".mypy_cache" in path
                )
                if mypy_cache_count > 0:
                    self.results.warnings.append(
                        f"Found {mypy_cache_count} mypy cache files"
                    )

                # Validate individual models
                for file_path, model in ast_data["file_models"].items():
                    self._validate_model(file_path, model)

            return self.results

        except Exception as e:
            self.results.errors.append(f"Validation failed: {str(e)}")
            self.results.passed = False
            return self.results

    def _validate_model(self, file_path: str, model: Dict[str, Any]) -> None:
        """Validate individual AST model"""
        required_model_fields = [
            "file_path",
            "file_type",
            "model_type",
            "complexity_score",
        ]

        for field in required_model_fields:
            if field not in model:
                self.results.errors.append(f"Missing field '{field}' in {file_path}")
                self.results.passed = False

        # Validate complexity score
        if "complexity_score" in model:
            complexity = model["complexity_score"]
            if not isinstance(complexity, (int, float)) or complexity < 0:
                self.results.errors.append(
                    f"Invalid complexity score in {file_path}: {complexity}"
                )
                self.results.passed = False

        # Validate model data
        if "model_data" in model:
            model_data = model["model_data"]
            if not isinstance(model_data, dict):
                self.results.errors.append(f"Invalid model_data in {file_path}")
                self.results.passed = False

    def validate_conversion_results(self, results_file: str) -> ValidationResult:
        """Validate Neo4j conversion results"""
        try:
            with open(results_file, "r") as f:
                results = json.load(f)

            # Check required fields
            required_fields = [
                "files_processed",
                "nodes_created",
                "relationships_created",
            ]
            for field in required_fields:
                if field not in results:
                    self.results.errors.append(f"Missing required field: {field}")
                    self.results.passed = False

            # Validate counts
            if "files_processed" in results and "nodes_created" in results:
                if results["nodes_created"] < results["files_processed"]:
                    self.results.warnings.append("Node count should be >= file count")

            return self.results

        except Exception as e:
            self.results.errors.append(f"Conversion validation failed: {str(e)}")
            self.results.passed = False
            return self.results


def main() -> None:
    """Run validation on AST files"""
    validator = ASTDataValidator()

    # Validate filtered AST file
    if Path("ast_models_filtered.json").exists():
        print("🔍 Validating filtered AST file...")
        result = validator.validate_ast_file("ast_models_filtered.json")

        if result.passed:
            print("✅ Validation passed")
        else:
            print("❌ Validation failed")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

        if result.details:
            print("\nDetails:")
            for key, value in result.details.items():
                print(f"  - {key}: {value}")
    else:
        print("⚠️  ast_models_filtered.json not found")


if __name__ == "__main__":
    main()
