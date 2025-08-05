#!/usr/bin/env python3
"""
Cursor IDE Plugin: Rule Compliance Checker
Provides immediate feedback on rule compliance violations
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import re

class RuleComplianceChecker:
    """Cursor IDE plugin for rule compliance checking"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.rules_dir = self.project_root / ".cursor" / "rules"
        
    def check_file_compliance(self, file_path: str) -> Dict[str, Any]:
        """Check compliance for a single file"""
        try:
            # Run the rule compliance checker
            result = subprocess.run(
                [str(self.scripts_dir / "rule-compliance-check.sh"), file_path],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            return {
                "file": file_path,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
"return_code": result.returncode
            }
            
        except Exception as e:
            return {
                "file": file_path,
                "success": False,
                "error": str(e),
                "return_code": 1
            }
            
    def check_mdc_compliance(self, file_path: str) -> Dict[str, Any]:
        """Check .mdc file compliance specifically"""
        try:
            # Run the MDC linter
            result = subprocess.run(
                [sys.executable, str(self.scripts_dir / "mdc-linter.py"), file_path],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            return {
                "file": file_path,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            return {
                "file": file_path,
                "success": False,
                "error": str(e),
                "return_code": 1
            }
            
    def get_rule_summary(self) -> Dict[str, Any]:
        """Get a summary of all rules"""
        rules = {}
        
        for rule_file in self.rules_dir.glob("*.mdc"):
            try:
                with open(rule_file, 'r') as f:
                    content = f.read()
                    
                # Parse YAML frontmatter
                lines = content.split('\n')
                if lines[0].strip() == '---':
                    frontmatter_end = lines.index('---', 1)
                    frontmatter_text = '\n'.join(lines[1:frontmatter_end])
                    
                    import yaml
                    frontmatter = yaml.safe_load(frontmatter_text)
                    
                    rules[rule_file.name] = {
                        "description": frontmatter.get("description", ""),
                        "globs": frontmatter.get("globs", []),
                        "always_apply": frontmatter.get("alwaysApply", False)
                    }
                    
            except Exception as e:
                rules[rule_file.name] = {"error": str(e)}
                
        return rules
        
    def validate_deterministic_editing(self, file_path: str, content: str) -> List[str]:
        """Validate deterministic editing compliance"""
        violations = []
        
        # Check for non-deterministic patterns
        non_deterministic_patterns = [
            (r'edit_file\s*\(', "Uses edit_file tool (non-deterministic)"),
            (r'fuzzy.*edit', "Uses fuzzy editing"),
            (r'random.*format', "Uses random formatting")
        ]
        
        for pattern, message in non_deterministic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"{message}: {pattern}")
                
        return violations
        
    def provide_immediate_feedback(self, file_path: str) -> Dict[str, Any]:
        """Provide immediate feedback for a file"""
        file_path_obj = Path(file_path)
        
        # Check if file is in scope for rule compliance
        if file_path_obj.suffix in ['.py', '.md', '.yaml', '.yml', '.json', '.mdc', '.sh']:
            compliance_result = self.check_file_compliance(file_path)
            
            # Additional checks for .mdc files
            if file_path_obj.suffix == '.mdc':
                mdc_result = self.check_mdc_compliance(file_path)
                compliance_result["mdc_specific"] = mdc_result
                
            return compliance_result
        else:
            return {
                "file": file_path,
                "success": True,
                "message": "File type not subject to rule compliance checks"
            }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cursor IDE Rule Compliance Checker")
    parser.add_argument("file", help="File to check")
    parser.add_argument("--immediate", action="store_true", help="Provide immediate feedback")
    parser.add_argument("--summary", action="store_true", help="Show rule summary")
    
    args = parser.parse_args()
    
    checker = RuleComplianceChecker()
    
    if args.summary:
        rules = checker.get_rule_summary()
        print(json.dumps(rules, indent=2))
        return
        
    if args.immediate:
        result = checker.provide_immediate_feedback(args.file)
        print(json.dumps(result, indent=2))
        return
        
    # Default: check file compliance
    result = checker.check_file_compliance(args.file)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
