#!/usr/bin/env python3
"""
Dynamic Rule Updater
Updates Cursor rules automatically when linter violations are detected
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ViolationPattern:
    """Represents a violation pattern for rule learning"""

    rule_code: str
    file_path: str
    line_number: int
    context: str
    frequency: int = 1
    prevention_strategy: Optional[str] = None
    ignore_directive: Optional[str] = None


class DynamicRuleUpdater:
    """Updates Cursor rules dynamically based on violations"""

    def __init__(self, rules_dir: str = ".cursor/rules") -> None:
        self.rules_dir = Path(rules_dir)
        self.violation_patterns: Dict[str, ViolationPattern] = {}
        self.rule_templates = self._load_rule_templates()

    def _load_rule_templates(self) -> Dict[str, Dict[str, str]]:
        """Load rule templates for different violation types"""
        return {
            "F401": {
                "title": "Unused Import Prevention",
                "description": "Prevent unused imports before they happen",
                "pattern": "import.*unused",
                "suggestion": "Only import modules that are actually used",
                "prevention_code": '''
# BEFORE writing imports
def validate_imports(imports: List[str], file_content: str):
    """Validate that imports are actually used"""
    used_imports = []
    for imp in imports:
        if is_import_used(imp, file_content):
            used_imports.append(imp)
        else:
            suggest_removal(imp)
    return used_imports
''',
            },
            "E302": {
                "title": "Blank Line Prevention",
                "description": "Prevent missing blank lines before definitions",
                "pattern": "def.*|class.*",
                "suggestion": "Add two blank lines before class/function definitions",
                "prevention_code": '''
# BEFORE writing class/function definitions
def validate_spacing(context: str, definition_type: str):
    """Validate proper spacing around definitions"""
    if definition_type in ['class', 'function']:
        ensure_two_blank_lines_before(context)
''',
            },
            "W291": {
                "title": "Trailing Whitespace Prevention",
                "description": "Prevent trailing whitespace",
                "pattern": ".*\\s+$",
                "suggestion": "Remove trailing whitespace from lines",
                "prevention_code": '''
# BEFORE writing any line
def validate_line_endings(line: str):
    """Validate proper line endings"""
    if line.rstrip() != line:
        suggest_trim_whitespace(line)
''',
            },
            "W292": {
                "title": "Missing Newline Prevention",
                "description": "Prevent missing newline at end of file",
                "pattern": ".*[^\\n]$",
                "suggestion": "Add newline at end of file",
                "prevention_code": '''
# BEFORE finishing file
def validate_file_endings(content: str):
    """Validate proper file endings"""
    if not content.endswith('\\n'):
        suggest_add_newline(content)
''',
            },
        }

    def update_rules_on_violation(self, violation: Dict[str, Any]) -> None:
        """Update rules when a violation is detected"""
        logger.info("🔄 **UPDATING RULES ON VIOLATION**")
        logger.info("=" * 50)

        rule_code = violation.get("code", "UNKNOWN")
        file_path = violation.get("file_path", "unknown")
        line_number = violation.get("line_number", 0)
        message = violation.get("message", "")

        logger.info("Violation detected:")
        logger.info("  - Rule: {}".format(rule_code))
        logger.info("  - File: {}".format(file_path))
        logger.info("  - Line: {}".format(line_number))
        logger.info("  - Message: {}".format(message))

        # Create or update violation pattern
        pattern_key = f"{rule_code}_{file_path}_{line_number}"

        if pattern_key in self.violation_patterns:
            self.violation_patterns[pattern_key].frequency += 1
        else:
            self.violation_patterns[pattern_key] = ViolationPattern(
                rule_code=rule_code,
                file_path=file_path,
                line_number=line_number,
                context=message,
            )

        # Create prevention rule
        prevention_rule = self._create_prevention_rule(
            rule_code, file_path, line_number, message
        )

        # Update Cursor rules
        self._update_cursor_rules(prevention_rule)

        # Log violation pattern
        self._log_violation_pattern(violation)

        # Update project model registry
        self._update_project_model_registry(violation)

    def _create_prevention_rule(
        self, rule_code: str, file_path: str, line_number: int, message: str
    ) -> Dict[str, Any]:
        """Create specific prevention rule based on violation"""
        template: Dict[str, str] = self.rule_templates.get(rule_code, {})

        if rule_code == "F401":
            return {
                "type": "import_prevention",
                "title": template.get("title", "Import Prevention"),
                "description": template.get("description", "Prevent unused imports"),
                "pattern": template.get("pattern", "import.*unused"),
                "suggestion": template.get(
                    "suggestion", "Remove unused import or add # noqa: F401"
                ),
                "prevention_code": template.get("prevention_code", ""),
                "ignore_directive": "# noqa: F401  # Import needed for type checking",
            }

        elif rule_code == "E302":
            return {
                "type": "blank_line_prevention",
                "title": template.get("title", "Blank Line Prevention"),
                "description": template.get(
                    "description", "Prevent missing blank lines"
                ),
                "pattern": template.get("pattern", "def.*|class.*"),
                "suggestion": template.get(
                    "suggestion", "Add two blank lines before definition"
                ),
                "prevention_code": template.get("prevention_code", ""),
                "ignore_directive": "# noqa: E302  # Compact module structure",
            }
        elif rule_code == "W291":
            return {
                "type": "whitespace_prevention",
                "title": template.get("title", "Trailing Whitespace Prevention"),
                "description": template.get(
                    "description", "Prevent trailing whitespace"
                ),
                "pattern": template.get("pattern", ".*\\s+$"),
                "suggestion": template.get("suggestion", "Remove trailing whitespace"),
                "prevention_code": template.get("prevention_code", ""),
                "ignore_directive": "# noqa: W291  # Trailing whitespace acceptable",
            }
        elif rule_code == "W292":
            return {
                "type": "newline_prevention",
                "title": template.get("title", "Missing Newline Prevention"),
                "description": template.get(
                    "description", "Prevent missing newline at end of file"
                ),
                "pattern": template.get("pattern", ".*[^\\n]$"),
                "suggestion": template.get("suggestion", "Add newline at end of file"),
                "prevention_code": template.get("prevention_code", ""),
                "ignore_directive": "# noqa: W292  # No newline acceptable",
            }
        else:
            return {
                "type": "generic_prevention",
                "title": "Generic Prevention",
                "description": "Prevent {} violations".format(rule_code),
                "pattern": ".*",
                "suggestion": "Fix {} violation".format(rule_code),
                "prevention_code": "",
                "ignore_directive": "# noqa: {}  # {}".format(rule_code, message),
            }

    def _update_cursor_rules(self, prevention_rule: Dict[str, Any]) -> None:
        """Update Cursor rules with new prevention rule"""
        rule_file = self.rules_dir / "dynamic-prevention-rules.mdc"

        # Create rules directory if it doesn't exist
        self.rules_dir.mkdir(parents=True, exist_ok=True)

        # Read existing rules or create new file
        if rule_file.exists():
            with open(rule_file, "r") as f:
                content = f.read()
        else:
            content = self._create_rule_file_header()

        # Add new prevention rule
        new_rule = self._format_prevention_rule(prevention_rule)
        content += "\n\n" + new_rule

        # Write updated rules
        with open(rule_file, "w") as f:
            f.write(content)

        logger.info("✅ Updated Cursor rules: {}".format(rule_file))

    def _create_rule_file_header(self) -> str:
        """Create header for rule file"""
        return """# Dynamic Prevention Rules
# Auto-generated by DynamicRuleUpdater
# Generated on: {}

""".format(
            datetime.now().isoformat()
        )

    def _format_prevention_rule(self, rule: Dict[str, Any]) -> str:
        """Format prevention rule for Cursor rules file"""
        return """## {title}

**Rule Code:** {rule_code}
**Description:** {description}
**Pattern:** {pattern}
**Suggestion:** {suggestion}

#### Prevention Code
```python
{prevention_code}
```

#### Ignore Directive (if intentional)
```python
{ignore_directive}
```

#### Implementation
- Check for pattern before writing code
- Apply prevention strategy
- Use ignore directive only when truly intentional
""".format(
            title=rule.get("title", "Generic Prevention"),
            rule_code=rule.get("type", "UNKNOWN"),
            description=rule.get("description", "Prevent violations"),
            pattern=rule.get("pattern", ".*"),
            suggestion=rule.get("suggestion", "Fix violation"),
            prevention_code=rule.get("prevention_code", ""),
            ignore_directive=rule.get("ignore_directive", "# noqa: UNKNOWN"),
        )

    def _log_violation_pattern(self, violation: Dict[str, Any]) -> None:
        """Log violation pattern for analysis"""
        logger.info("📊 **VIOLATION PATTERN LOGGED**")
        logger.info("  - Rule: {}".format(violation.get("code", "UNKNOWN")))
        logger.info("  - File: {}".format(violation.get("file_path", "unknown")))
        logger.info("  - Line: {}".format(violation.get("line_number", 0)))
        logger.info("  - Message: {}".format(violation.get("message", "")))

    def _update_project_model_registry(self, violation: Dict[str, Any]) -> None:
        """Update project model registry with violation data"""
        model_file = Path("project_model_registry.json")

        if not model_file.exists():
            logger.warning("Project model registry not found")
            return

        try:
            with open(model_file, "r") as f:
                model_data = json.load(f)

            # Add violation tracking
            if "violation_tracking" not in model_data:
                model_data["violation_tracking"] = {}

            rule_code = violation.get("code", "UNKNOWN")
            if rule_code not in model_data["violation_tracking"]:
                model_data["violation_tracking"][rule_code] = []

            model_data["violation_tracking"][rule_code].append(
                {
                    "file_path": violation.get("file_path", "unknown"),
                    "line_number": violation.get("line_number", 0),
                    "message": violation.get("message", ""),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Write updated model
            with open(model_file, "w") as f:
                json.dump(model_data, f, indent=2)

            logger.info("✅ Updated project model registry")

        except Exception as e:
            logger.error("Failed to update project model registry: {}".format(e))

    def _get_prevention_strategy(self, rule_code: str) -> str:
        """Get prevention strategy for rule code"""
        strategies = {
            "F401": "Only import modules that are actually used",
            "E302": "Add two blank lines before class/function definitions",
            "W291": "Remove trailing whitespace from lines",
            "W292": "Add newline at end of file",
        }
        return strategies.get(rule_code, "Fix {} violation".format(rule_code))

    def _get_ignore_directive(self, rule_code: str) -> str:
        """Get ignore directive for rule code"""
        directives = {
            "F401": "# noqa: F401  # Import needed for type checking",
            "E302": "# noqa: E302  # Compact module structure",
            "W291": "# noqa: W291  # Trailing whitespace acceptable",
            "W292": "# noqa: W292  # No newline acceptable",
        }
        return directives.get(
            rule_code, "# noqa: {}  # Intentional violation".format(rule_code)
        )

    def learn_from_violations(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn prevention patterns from violations"""
        logger.info("🧠 **LEARNING FROM VIOLATIONS**")
        logger.info("=" * 50)

        patterns: Dict[str, List[Dict[str, Any]]] = {}

        for violation in violations:
            rule = violation.get("code", "UNKNOWN")
            context = violation.get("file_path", "unknown")

            if rule not in patterns:
                patterns[rule] = []

            # Check if context already exists
            existing_context = None
            for p in patterns[rule]:
                if p["context"] == context:
                    existing_context = p
                    break

            if existing_context:
                existing_context["frequency"] += 1
            else:
                patterns[rule].append(
                    {
                        "context": context,
                        "frequency": 1,
                        "prevention_strategy": self._get_prevention_strategy(rule),
                    }
                )

        # Generate learning report
        learning_report = {
            "total_violations": len(violations),
            "unique_rules": len(patterns),
            "patterns": patterns,
            "recommendations": self._generate_recommendations(patterns),
        }

        logger.info("Learning report:")
        logger.info(
            "  - Total violations: {}".format(learning_report["total_violations"])
        )
        logger.info("  - Unique rules: {}".format(learning_report["unique_rules"]))

        for rule, rule_patterns in patterns.items():
            logger.info("  - {}: {} patterns".format(rule, len(rule_patterns)))

        return learning_report

    def _generate_recommendations(
        self, patterns: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate recommendations based on violation patterns"""
        recommendations = []

        for rule, rule_patterns in patterns.items():
            total_frequency = sum(p["frequency"] for p in rule_patterns)

            if total_frequency > 5:
                recommendations.append(
                    "High frequency {} violations: Consider adding specific prevention rule".format(
                        rule
                    )
                )

            if len(rule_patterns) > 3:
                recommendations.append(
                    "{} violations across multiple files: Consider project-wide prevention strategy".format(
                        rule
                    )
                )

            # Check for specific patterns
            for pattern in rule_patterns:
                if pattern["frequency"] > 2:
                    recommendations.append(
                        "Frequent {} violations in {}: Consider file-specific prevention".format(
                            rule, pattern["context"]
                        )
                    )

        return recommendations


def main() -> None:
    """Test the dynamic rule updater"""
    logger.info("🧪 **DYNAMIC RULE UPDATER TEST**")
    logger.info("=" * 50)

    updater = DynamicRuleUpdater()

    # Test with sample violations
    sample_violations = [
        {
            "code": "F401",
            "file_path": "test_file.py",
            "line_number": 5,
            "message": "import json imported but unused",
        },
        {
            "file_path": "test_file.py",
            "line_number": 10,
            "message": "f-string is missing placeholders",
        },
        {
            "code": "E302",
            "file_path": "test_file.py",
            "line_number": 15,
            "message": "expected 2 blank lines, found 1",
        },
    ]

    # Update rules for each violation
    for violation in sample_violations:
        updater.update_rules_on_violation(violation)

    # Learn from violations
    learning_report = updater.learn_from_violations(sample_violations)

    logger.info("\n📊 **LEARNING REPORT**")
    logger.info("=" * 30)
    logger.info("Recommendations:")
    for recommendation in learning_report["recommendations"]:
        logger.info("  - {}".format(recommendation))


if __name__ == "__main__":
    main()
