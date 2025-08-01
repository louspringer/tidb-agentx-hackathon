#!/usr/bin/env python3
"""
MDC File Linter
Validates .mdc files for proper YAML frontmatter structure and content
"""

import os
import sys
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import argparse

class MDCLinter:
    """Linter for .mdc files with YAML frontmatter"""
    
    def __init__(self):
        self.violations = []
        self.warnings = []
        self.total_files = 0
        
    def log_violation(self, file_path: str, message: str):
        """Log a violation"""
        self.violations.append(f"{file_path}: {message}")
        
    def log_warning(self, file_path: str, message: str):
        """Log a warning"""
        self.warnings.append(f"{file_path}: {message}")
        
    def validate_yaml_frontmatter(self, file_path: str, content: str) -> bool:
        """Validate YAML frontmatter structure"""
        lines = content.split('\n')
        
        # Check for proper YAML frontmatter delimiters
        delimiter_count = 0
        for line in lines:
            if line.strip() == '---':
                delimiter_count += 1
                
        if delimiter_count != 2:
            self.log_violation(file_path, "Invalid YAML frontmatter: must have exactly 2 '---' delimiters")
            return False
            
        # Extract frontmatter
        try:
            frontmatter_start = lines.index('---')
            frontmatter_end = lines.index('---', frontmatter_start + 1)
            frontmatter_lines = lines[frontmatter_start + 1:frontmatter_end]
            frontmatter_text = '\n'.join(frontmatter_lines)
            
            # Parse YAML frontmatter
            frontmatter = yaml.safe_load(frontmatter_text)
            if not frontmatter:
                self.log_violation(file_path, "Empty or invalid YAML frontmatter")
                return False
                
            # Check required fields
            required_fields = ['description', 'globs', 'alwaysApply']
            for field in required_fields:
                if field not in frontmatter:
                    self.log_violation(file_path, f"Missing required field: {field}")
                    return False
                    
            # Validate field types
            if not isinstance(frontmatter['description'], str):
                self.log_violation(file_path, "description must be a string")
                return False
                
            if not isinstance(frontmatter['globs'], list):
                self.log_violation(file_path, "globs must be a list")
                return False
                
            if not isinstance(frontmatter['alwaysApply'], bool):
                self.log_violation(file_path, "alwaysApply must be a boolean")
                return False
                
            # Validate globs patterns
            for glob in frontmatter['globs']:
                if not isinstance(glob, str):
                    self.log_violation(file_path, "globs must contain strings")
                    return False
                    
            return True
            
        except (yaml.YAMLError, ValueError) as e:
            self.log_violation(file_path, f"YAML parsing error: {e}")
            return False
            
    def validate_markdown_content(self, file_path: str, content: str) -> bool:
        """Validate markdown content structure"""
        lines = content.split('\n')
        
        # Check for content after frontmatter
        try:
            frontmatter_start = lines.index('---')
            frontmatter_end = lines.index('---', frontmatter_start + 1)
            content_after_frontmatter = lines[frontmatter_end + 1:]
            
            if not any(line.strip() for line in content_after_frontmatter):
                self.log_violation(file_path, "No content after YAML frontmatter")
                return False
                
            # Check for proper markdown structure
            has_headers = any(line.startswith('#') for line in content_after_frontmatter)
            if not has_headers:
                self.log_warning(file_path, "No markdown headers found in content")
                
            return True
            
        except ValueError:
            self.log_violation(file_path, "Cannot find YAML frontmatter delimiters")
            return False
            
    def validate_file_organization(self, file_path: str) -> bool:
        """Validate file is in appropriate directory"""
        path = Path(file_path)
        parent_dir = path.parent.name
        
        # Check if file is in a .cursor/rules directory
        if '.cursor/rules' in str(path):
            return True
            
        # Check if file is in appropriate domain directory
        valid_dirs = ['src', 'scripts', 'docs', 'config', 'data', 'healthcare-cdc']
        if parent_dir in valid_dirs:
            return True
            
        # Root level .mdc files are also valid
        if path.parent == Path('.'):
            return True
            
        self.log_warning(file_path, f"File may be in wrong directory: {parent_dir}")
        return True
        
    def validate_deterministic_editing_compliance(self, file_path: str, content: str) -> bool:
        """Check for deterministic editing compliance"""
        # Check for non-deterministic patterns
        non_deterministic_patterns = [
            r'edit_file\s*\(',
            r'fuzzy.*edit',
            r'random.*format'
        ]
        
        for pattern in non_deterministic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_violation(file_path, f"Contains non-deterministic pattern: {pattern}")
                return False
                
        return True
        
    def lint_file(self, file_path: str) -> bool:
        """Lint a single .mdc file"""
        self.total_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Validate YAML frontmatter
            if not self.validate_yaml_frontmatter(file_path, content):
                return False
                
            # Validate markdown content
            if not self.validate_markdown_content(file_path, content):
                return False
                
            # Validate file organization
            self.validate_file_organization(file_path)
            
            # Validate deterministic editing compliance
            if not self.validate_deterministic_editing_compliance(file_path, content):
                return False
                
            return True
            
        except Exception as e:
            self.log_violation(file_path, f"Error reading file: {e}")
            return False
            
    def lint_directory(self, directory: str) -> None:
        """Lint all .mdc files in directory"""
        directory_path = Path(directory)
        
        if not directory_path.exists():
            print(f"Error: Directory {directory} does not exist")
            sys.exit(1)
            
        mdc_files = list(directory_path.rglob("*.mdc"))
        
        if not mdc_files:
            print(f"No .mdc files found in {directory}")
            return
            
        print(f"Found {len(mdc_files)} .mdc files to lint")
        
        failed_files = 0
        for file_path in mdc_files:
            if not self.lint_file(str(file_path)):
                failed_files += 1
                
        # Print results
        print(f"\nLinting completed:")
        print(f"Total files: {self.total_files}")
        print(f"Failed files: {failed_files}")
        print(f"Violations: {len(self.violations)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.violations:
            print("\nViolations:")
            for violation in self.violations:
                print(f"  ❌ {violation}")
                
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
                
        if not self.violations:
            print("\n✅ All .mdc files pass linting!")
            return 0
        else:
            print(f"\n❌ Found {len(self.violations)} violations")
            return 1

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Lint .mdc files for proper structure")
    parser.add_argument("directory", nargs="?", default=".", 
                       help="Directory to lint (default: current directory)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    linter = MDCLinter()
    exit_code = linter.lint_directory(args.directory)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 