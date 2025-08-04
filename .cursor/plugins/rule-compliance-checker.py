#!/usr/bin/env python3
"""Cursor IDE plugin for rule compliance checking"""

import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any
import yaml
import argparse


class RuleComplianceChecker:
    """Cursor IDE plugin for rule compliance checking."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).parent.parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.rules_dir = self.project_root / ".cursor" / "rules"

        def check_file_compliance(self, file_path: str) -> Dict[str, Any]:
            """Check compliance for a single file."""
            try:
        # Run the rule compliance checker
                result = subprocess.run(
                [str(self.scripts_dir / "rule-compliance-check.sh"), file_path],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                )
                return {
                "file": file_path,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                }
                except Exception as e:
                    return {
                    "file": file_path,
                    "success": False,
                    "error": str(e),
                    "return_code": 1,
                    }

                    def check_mdc_compliance(self, file_path: str) -> Dict[str, Any]:
                        """Check .mdc file compliance specifically"""
                        try:
        # Run the MDC linter
                            result = subprocess.run(
                            [sys.executable, str(self.scripts_dir / "mdc-linter.py"), file_path],
                            capture_output=True,
                            text=True,
                            cwd=self.project_root,
                            )
                            return {
                            "file": file_path,
                            "success": result.returncode == 0,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "return_code": result.returncode,
                            }
                            except Exception as e:
                                return {
                                "file": file_path,
                                "success": False,
                                "error": str(e),
                                "return_code": 1,
                                }

                                def get_rule_summary(self) -> Dict[str, Any]:
                                    """Get a summary of all rules"""
                                    rules = {}
                                    for rule_file in self.rules_dir.glob("*.mdc"):
                                    try:
                                    with open(rule_file, "r") as f:
                                        content = f.read()
        # Parse YAML frontmatter
                                        lines = content.split("\n")
                                        if lines[0].strip() == "---":
                                            frontmatter_end = lines.index("---", 1)
                                            frontmatter_text = "\n".join(lines[1:frontmatter_end])
                                            frontmatter = yaml.safe_load(frontmatter_text)
                                            rules[rule_file.name] = {
                                            "description": frontmatter.get("description", ""),
                                            "globs": frontmatter.get("globs", []),
                                            "always_apply": frontmatter.get("alwaysApply", False),
                                            }
                                            except Exception as e:
                                                rules[rule_file.name] = {"error": str(e)}
                                                return rules

                                                def validate_deterministic_editing(self, file_path: str, content: str) -> List[str]:
                                                    """Validate deterministic editing compliance"""
                                                    violations = []
        # Check for non-deterministic patterns
                                                    non_deterministic_patterns = [
                                                    (r"edit_file\s*\(", "Uses edit_file tool (non-deterministic)"),
                                                    (r"fuzzy.*edit", "Uses fuzzy editing"),
                                                    (r"random.*format", "Uses random formatting"),
                                                    ]
                                                    for pattern, message in non_deterministic_patterns:
                                                    if re.search(pattern, content, re.IGNORECASE):
                                                        violations.append(f"{message}: {pattern}")
                                                        return violations

                                                        def provide_immediate_feedback(self, file_path: str) -> Dict[str, Any]:
                                                            """Provide immediate feedback for a file"""
                                                            feedback: Dict[str, Any] = {
                                                            "file": file_path,
                                                            "compliance_checks": [],
                                                            "recommendations": [],
                                                            }

        # Check file compliance
                                                            compliance_result = self.check_file_compliance(file_path)
                                                            feedback["compliance_checks"].append(compliance_result)

        # Check MDC compliance if it's an .mdc file
                                                            if file_path.endswith(".mdc"):
                                                                mdc_result = self.check_mdc_compliance(file_path)
                                                                feedback["compliance_checks"].append(mdc_result)

        # Validate deterministic editing
                                                                try:
                                                                with open(file_path, "r") as f:
                                                                    content = f.read()
                                                                    violations = self.validate_deterministic_editing(file_path, content)
                                                                    if violations:
                                                                        feedback["recommendations"].extend(violations)
                                                                        except Exception as e:
                                                                            feedback["recommendations"].append(f"Error reading file: {e}")

                                                                            return feedback


                                                                            def main() -> None:
                                                                                """Main function for testing"""
                                                                                parser = argparse.ArgumentParser(description="Rule compliance checker")
                                                                                parser.add_argument("file", help="File to check")
                                                                                args = parser.parse_args()

                                                                                checker = RuleComplianceChecker()
                                                                                feedback = checker.provide_immediate_feedback(args.file)

                                                                                print(json.dumps(feedback, indent=2))


                                                                                if __name__ == "__main__":
                                                                                    main()
