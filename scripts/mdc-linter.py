#!/usr/bin/env python3
"""
MDC Linter - Lint .mdc files for proper structure and content
"""

import os
import sys
from pathlib import Path

import yaml


class MDCLinter:
    """Linter for .mdc files"""

    def __init__(self):
        self.violations = []
        self.warnings = []

    def log_violation(self, file_path: str, message: str) -> None:
        """Log a violation"""
        self.violations.append(f"{file_path}: {message}")

    def log_warning(self, file_path: str, message: str) -> None:
        """Log a warning"""
        self.warnings.append(f"{file_path}: {message}")

    def validate_yaml_frontmatter(self, file_path: str, content: str) -> bool:
        """Validate YAML frontmatter structure"""
        lines = content.split("\n")
        delimiter_count = 0

        for line in lines:
            if line.strip() == "---":
                delimiter_count += 1

        if delimiter_count != 2:
            self.log_violation(
                file_path,
                "Invalid YAML frontmatter: must have exactly 2 '---' delimiters",
            )
            return False

        # Extract frontmatter
        try:
            frontmatter_start = lines.index("---")
            frontmatter_end = lines.index("---", frontmatter_start + 1)
            frontmatter_content = "\n".join(
                lines[frontmatter_start + 1 : frontmatter_end],
            )
            frontmatter = yaml.safe_load(frontmatter_content)

            if not frontmatter:
                self.log_violation(file_path, "Empty or invalid YAML frontmatter")
                return False

            # Check required fields
            required_fields = ["description", "globs", "alwaysApply"]

            for field in required_fields:
                if field not in frontmatter:
                    self.log_violation(file_path, f"Missing required field: {field}")
                    return False

            # Validate field types
            if not isinstance(frontmatter["description"], str):
                self.log_violation(file_path, "description must be a string")
                return False

            if not isinstance(frontmatter["globs"], list):
                self.log_violation(file_path, "globs must be a list")
                return False

            if not isinstance(frontmatter["alwaysApply"], bool):
                self.log_violation(file_path, "alwaysApply must be a boolean")
                return False

            # Validate globs patterns
            for glob in frontmatter["globs"]:
                if not isinstance(glob, str):
                    self.log_violation(file_path, "globs must contain strings")
                    return False

            return True

        except (yaml.YAMLError, ValueError) as e:
            self.log_violation(file_path, f"YAML parsing error: {e}")
            return False

    def validate_markdown_content(self, file_path: str, content: str) -> bool:
        """Validate markdown content structure"""
        lines = content.split("\n")

        try:
            frontmatter_end = lines.index("---", lines.index("---") + 1)
            content_after_frontmatter = lines[frontmatter_end + 1 :]

            if not any(line.strip() for line in content_after_frontmatter):
                self.log_violation(file_path, "No content after YAML frontmatter")
                return False

            # Check for proper markdown structure
            has_content = any(line.strip() for line in content_after_frontmatter)
            if not has_content:
                self.log_violation(file_path, "No meaningful content in markdown")
                return False

            return True

        except ValueError:
            self.log_violation(file_path, "Could not find YAML frontmatter")
            return False

    def validate_deterministic_editing_compliance(
        self,
        file_path: str,
        content: str,
    ) -> bool:
        """Validate deterministic editing compliance"""
        # Check for deterministic patterns
        if "TODO" in content or "FIXME" in content:
            self.log_warning(
                file_path,
                "Contains TODO/FIXME - ensure deterministic resolution",
            )

        return True

    def lint_file(self, file_path: str) -> bool:
        """Lint a single .mdc file"""
        try:
            with open(file_path) as f:
                content = f.read()

            is_valid = True

            # Validate YAML frontmatter
            if not self.validate_yaml_frontmatter(file_path, content):
                is_valid = False

            # Validate markdown content
            if not self.validate_markdown_content(file_path, content):
                is_valid = False

            # Validate deterministic editing compliance
            if not self.validate_deterministic_editing_compliance(file_path, content):
                is_valid = False

            return is_valid

        except Exception as e:
            self.log_violation(file_path, f"Error reading file: {e}")
            return False

    def lint_directory(self, directory: str) -> int:
        """Lint all .mdc files in a directory"""
        mdc_files = list(Path(directory).rglob("*.mdc"))

        if not mdc_files:
            print(f"No .mdc files found in {directory}")
            return 0

        valid_files = 0
        total_files = len(mdc_files)

        for file_path in mdc_files:
            if self.lint_file(str(file_path)):
                valid_files += 1

        # Print results
        print(f"Linted {total_files} .mdc files")
        print(f"Valid: {valid_files}")
        print(f"Invalid: {total_files - valid_files}")

        if self.violations:
            print("\nViolations:")
            for violation in self.violations:
                print(f"  ❌ {violation}")

        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        return total_files - valid_files


def main() -> None:
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python mdc-linter.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        sys.exit(1)

    linter = MDCLinter()
    exit_code = linter.lint_directory(directory)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
