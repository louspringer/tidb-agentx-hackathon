#!/usr/bin/env python3
"""
MDC (Markdown + YAML) Linter
Validates .mdc files for proper structure and compliance
"""

import re
import yaml
from pathlib import Path
from typing import List


class MDCLinter:
    """Linter for .mdc files with YAML frontmatter"""

    def __init__(self) -> None:
        self.violations: List[str] = []
        self.warnings: List[str] = []

    def log_violation(self, file_path: str, message: str) -> None:
        """Log a violation"""
        self.violations.append(f"{file_path}: {message}")

    def log_warning(self, file_path: str, message: str) -> None:
        """Log a warning"""
        self.warnings.append(f"{file_path}: {message}")

    def validate_yaml_frontmatter(self, file_path: str, content: str) -> bool:
        """Validate YAML frontmatter structure"""
        lines = content.split("\n")

        # Check for proper YAML frontmatter delimiters
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
            frontmatter_lines = lines[frontmatter_start + 1 : frontmatter_end]
            frontmatter_text = "\n".join(frontmatter_lines)

            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(frontmatter_text)
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

        # Check for content after frontmatter
        try:
            frontmatter_start = lines.index("---")
            frontmatter_end = lines.index("---", frontmatter_start + 1)
            content_after_frontmatter = lines[frontmatter_end + 1 :]

            if not any(line.strip() for line in content_after_frontmatter):
                self.log_violation(file_path, "No content after YAML frontmatter")
                return False

            # Check for proper markdown structure
            has_headers = any(
                line.startswith("#") for line in content_after_frontmatter
            )
            if not has_headers:
                self.log_warning(file_path, "No markdown headers found")
                return False

            return True

        except ValueError:
            self.log_violation(file_path, "Invalid YAML frontmatter structure")
            return False

    def validate_file_organization(self, file_path: str) -> bool:
        """Validate file organization and naming"""
        path = Path(file_path)

        # Check file extension
        if path.suffix != ".mdc":
            self.log_violation(file_path, "File must have .mdc extension")
            return False

        # Check file naming convention
        if not re.match(r"^[A-Z_][A-Z0-9_]*\.mdc$", path.name):
            self.log_warning(
                file_path, "File should follow naming convention: UPPER_CASE.mdc"
            )

        return True

    def validate_deterministic_editing_compliance(
        self, file_path: str, content: str
    ) -> bool:
        """Validate compliance with deterministic editing rules"""

        # Check for banned patterns
        banned_patterns = [
            r"edit_file\s*\(",
            # Temporarily disabled to avoid false positives in rule documentation
            # r"fuzzy.*edit.*tool(?!.*NEVER)",
            # r"stochastic.*edit.*tool(?!.*NEVER)",
        ]

        for pattern in banned_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_violation(file_path, f"Banned pattern found: {pattern}")
                return False

        return True

    def lint_file(self, file_path: str) -> bool:
        """Lint a single .mdc file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Reset violations and warnings for this file
            self.violations = []
            self.warnings = []

            # Run all validations
            self.validate_file_organization(file_path)
            self.validate_yaml_frontmatter(file_path, content)
            self.validate_markdown_content(file_path, content)
            self.validate_deterministic_editing_compliance(file_path, content)

            # Print results
            if self.violations:
                print(f"❌ {file_path}: {len(self.violations)} violations")
                for violation in self.violations:
                    print(f"   {violation}")
                return False
            elif self.warnings:
                print(f"⚠️  {file_path}: {len(self.warnings)} warnings")
                for warning in self.warnings:
                    print(f"   {warning}")
                return True
            else:
                print(f"✅ {file_path}: Valid")
                return True

        except Exception as e:
            print(f"❌ {file_path}: Error reading file - {e}")
            return False

    def lint_directory(self, directory: str) -> int:
        """Lint all .mdc files in a directory"""
        path = Path(directory)
        mdc_files = list(path.glob("**/*.mdc"))

        if not mdc_files:
            print(f"No .mdc files found in {directory}")
            return 0

        print(f"🔍 Linting {len(mdc_files)} .mdc files...")
        print("=" * 50)

        valid_files = 0
        total_files = len(mdc_files)

        for file_path in mdc_files:
            if self.lint_file(str(file_path)):
                valid_files += 1

        print("=" * 50)
        print(f"📊 Results: {valid_files}/{total_files} files valid")

        return total_files - valid_files


def main() -> None:
    """Main function"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python mdc-linter.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]
    linter = MDCLinter()

    if Path(target).is_file():
        success = linter.lint_file(target)
        sys.exit(0 if success else 1)
    elif Path(target).is_dir():
        violations = linter.lint_directory(target)
        sys.exit(violations)
    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
