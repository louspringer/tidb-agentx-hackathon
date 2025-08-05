#!/usr/bin/env python3
"""
Validate No Bash/Zsh Oneliners Rule
Ghostbusters validation for script quality and bash escaping prevention
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


class ScriptQualityExpert:
    """Script Quality Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Script Quality Expert"
        self.focus = "Script structure, error handling, maintainability"
    
    def validate_script_structure(self, file_path: str) -> Dict[str, Any]:
        """Validate script follows proper structure"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            return {
                'passed': False,
                'issues': [f"Cannot read file: {e}"]
            }
        
        issues = []
        
        # Check for shebang
        if not content.startswith('#!/usr/bin/env python3'):
            issues.append("Missing shebang: #!/usr/bin/env python3")
        
        # Check for docstring
        if '"""' not in content and "'''" not in content:
            issues.append("Missing docstring")
        
        # Check for type hints
        if 'from typing import' not in content:
            issues.append("Missing type hints import")
        
        # Check for main function
        if 'def main():' not in content:
            issues.append("Missing main() function")
        
        # Check for if __name__ == "__main__":
        if 'if __name__ == "__main__":' not in content:
            issues.append("Missing if __name__ == '__main__': guard")
        
        # Check for error handling
        if 'try:' not in content and 'except:' not in content:
            issues.append("No error handling found")
        
        # Check for sys.exit
        if 'sys.exit' not in content:
            issues.append("No proper exit codes")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def validate(self, project_path: str) -> Dict[str, Any]:
        """Validate script quality across project"""
        python_files = list(Path(project_path).rglob("*.py"))
        
        script_quality_results = {}
        total_issues = 0
        
        for file_path in python_files:
            if file_path.name.startswith('test_'):
                continue  # Skip test files for now
            
            result = self.validate_script_structure(str(file_path))
            script_quality_results[str(file_path)] = result
            total_issues += len(result['issues'])
        
        return {
            'passed': total_issues == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'python_files_checked': len(python_files),
                'total_issues': total_issues,
                'script_quality_results': script_quality_results,
                'delusion_check': "Are you writing maintainable, well-structured scripts?",
                'recommendation': "Follow script creation guidelines: shebang, docstring, type hints, main function, error handling"
            }
        }


class BashOnelinerDetector:
    """Bash Oneliner Detector Ghostbuster"""
    
    def __init__(self):
        self.name = "Bash Oneliner Detector"
        self.focus = "Detect and prevent bash/zsh oneliners"
    
    def find_bash_oneliners(self, project_path: str) -> List[Dict[str, Any]]:
        """Find bash/zsh oneliners in the project"""
        oneliners = []
        
        # Search for python -c patterns
        python_c_patterns = [
            r'python -c ".*"',
            r'python3 -c ".*"',
            r'python -c \'.*\'',
            r'python3 -c \'.*\''
        ]
        
        # Search for complex bash commands
        bash_patterns = [
            r'python -c ".*{.*}.*"',  # Complex JSON processing
            r'python -c ".*\[.*\].*"',  # Complex list processing
            r'python -c ".*print.*\(.*\).*"',  # Print statements
            r'python -c ".*import.*"',  # Import statements
            r'python -c ".*json\.load.*"',  # JSON processing
        ]
        
        for pattern in python_c_patterns + bash_patterns:
            for file_path in Path(project_path).rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.py', '.sh']:
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        matches = re.finditer(pattern, content, re.MULTILINE)
                        for match in matches:
                            oneliners.append({
                                'file': str(file_path),
                                'line': content[:match.start()].count('\n') + 1,
                                'command': match.group(),
                                'pattern': pattern
                            })
                    except Exception:
                        continue
        
        return oneliners
    
    def validate(self, project_path: str) -> Dict[str, Any]:
        """Validate no bash oneliners rule"""
        oneliners = self.find_bash_oneliners(project_path)
        
        return {
            'passed': len(oneliners) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'bash_oneliners_found': len(oneliners),
                'oneliners': oneliners,
                'delusion_check': "Are you using bash/zsh oneliners instead of proper scripts?",
                'recommendation': "Convert all oneliners to proper Python scripts with error handling"
            }
        }


class ScriptNamingExpert:
    """Script Naming Expert Ghostbuster"""
    
    def __init__(self):
        self.name = "Script Naming Expert"
        self.focus = "Script naming conventions and organization"
    
    def validate(self, project_path: str) -> Dict[str, Any]:
        """Validate script naming conventions"""
        python_files = list(Path(project_path).rglob("*.py"))
        
        naming_issues = []
        good_names = []
        
        for file_path in python_files:
            filename = file_path.name
            
            # Check for good naming patterns
            if re.match(r'^[a-z_]+\.py$', filename):
                good_names.append(filename)
            else:
                naming_issues.append({
                    'file': str(file_path),
                    'issue': f"Filename '{filename}' doesn't follow snake_case convention"
                })
            
            # Check for descriptive names
            if len(filename) < 5:  # Too short
                naming_issues.append({
                    'file': str(file_path),
                    'issue': f"Filename '{filename}' is too short to be descriptive"
                })
        
        return {
            'passed': len(naming_issues) == 0,
            'expert': self.name,
            'focus': self.focus,
            'findings': {
                'total_scripts': len(python_files),
                'good_names': len(good_names),
                'naming_issues': naming_issues,
                'delusion_check': "Are you using descriptive, consistent script names?",
                'recommendation': "Use snake_case naming: action_purpose.py"
            }
        }


def load_model_registry() -> Dict[str, Any]:
    """Load the project model registry"""
    try:
        with open('project_model_registry.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: project_model_registry.json not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in project_model_registry.json: {e}")
        sys.exit(1)


def assemble_ghostbusters_team() -> Dict[str, Any]:
    """Assemble ghostbusters team for script validation"""
    return {
        'script_quality_expert': ScriptQualityExpert(),
        'bash_oneliner_detector': BashOnelinerDetector(),
        'script_naming_expert': ScriptNamingExpert()
    }


def call_ghostbusters_for_scripts(project_path: str) -> Dict[str, Any]:
    """Call ghostbusters for script validation"""
    
    print("🚨 CALLING GHOSTBUSTERS FOR SCRIPT VALIDATION!")
    print("=" * 60)
    
    # Assemble team
    team = assemble_ghostbusters_team()
    
    # Run validation
    results = {}
    
    # Agent validation
    for agent_name, agent in team.items():
        print(f"👻 {agent.name} is investigating...")
        results[f'agent_{agent_name}'] = agent.validate(project_path)
    
    return results


def generate_script_validation_report(validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive script validation report"""
    
    passed_validations = sum(1 for r in validation_results.values() if r['passed'])
    failed_validations = sum(1 for r in validation_results.values() if not r['passed'])
    
    delusions_detected = []
    for validator_name, result in validation_results.items():
        if not result['passed']:
            delusions_detected.append({
                'validator': validator_name,
                'expert': result['expert'],
                'findings': result['findings']
            })
    
    report = {
        'summary': {
            'total_validators': len(validation_results),
            'passed_validations': passed_validations,
            'failed_validations': failed_validations,
            'delusions_detected': delusions_detected
        },
        'detailed_results': validation_results
    }
    
    return report


def print_script_validation_report(report: Dict[str, Any]) -> None:
    """Print the script validation report"""
    
    print("\n" + "=" * 60)
    print("👻 SCRIPT VALIDATION GHOSTBUSTERS REPORT")
    print("=" * 60)
    
    summary = report['summary']
    print(f"📊 Total Validators: {summary['total_validators']}")
    print(f"✅ Passed Validations: {summary['passed_validations']}")
    print(f"❌ Failed Validations: {summary['failed_validations']}")
    
    if summary['delusions_detected']:
        print(f"\n🚨 DELUSIONS DETECTED: {len(summary['delusions_detected'])}")
        for delusion in summary['delusions_detected']:
            print(f"   • {delusion['expert']}: {delusion['findings']}")
    else:
        print("\n✅ NO DELUSIONS DETECTED!")
    
    print("\n📋 DETAILED FINDINGS:")
    for validator_name, result in report['detailed_results'].items():
        expert_name = result['expert']
        findings = result['findings']
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        
        print(f"\n👻 {expert_name} - {status}")
        print(f"   Focus: {result['focus']}")
        print(f"   Delusion Check: {findings.get('delusion_check', 'N/A')}")
        print(f"   Recommendation: {findings.get('recommendation', 'N/A')}")
        
        # Print specific findings
        for key, value in findings.items():
            if key not in ['delusion_check', 'recommendation']:
                print(f"   {key}: {value}")


def main():
    """Main script validation"""
    
    print("🎯 GHOSTBUSTERS SCRIPT VALIDATION TEAM ASSEMBLING...")
    
    # Get project path
    project_path = os.getcwd()
    
    # Call ghostbusters
    validation_results = call_ghostbusters_for_scripts(project_path)
    
    # Generate report
    script_report = generate_script_validation_report(validation_results)
    
    # Print report
    print_script_validation_report(script_report)
    
    # Exit with appropriate code
    if script_report['summary']['failed_validations'] > 0:
        print("\n🚨 GHOSTBUSTERS DETECTED SCRIPT DELUSIONS!")
        sys.exit(1)
    else:
        print("\n✅ GHOSTBUSTERS SCRIPT VALIDATION PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main() 