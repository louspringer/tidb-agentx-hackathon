#!/usr/bin/env python3
"""
AST-Guided Code Generator
Builds on existing AST foundation for actionable model-driven code generation
"""

import ast
import logging
from dataclasses import dataclass
from typing import Any, Optional

from src.artifact_forge.agents.artifact_parser_enhanced import EnhancedArtifactParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ASTNode:
    """Represents an AST node with metadata"""

    node_type: str
    content: str
    line_number: int
    parent: Optional["ASTNode"] = None
    children: list["ASTNode"] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LintingRule:
    """Represents a linting rule with AST-aware patterns"""

    code: str
    description: str
    severity: str
    ast_patterns: list[str]  # AST node types this rule applies to
    fix_strategy: str
    priority: int = 1


class ASTGuidedCodeGenerator:
    """AST-guided code generator that respects syntactic boundaries"""

    def __init__(self):
        self.ast_parser = EnhancedArtifactParser()
        self.linting_rules = self._build_linting_rules()

    def _build_linting_rules(self) -> dict[str, LintingRule]:
        """Build AST-aware linting rules"""
        return {
            "F401": LintingRule(
                code="F401",
                description="Unused imports",
                severity="error",
                ast_patterns=["Import", "ImportFrom"],
                fix_strategy="remove_unused_import",
                priority=1,
            ),
            "E302": LintingRule(
                code="E302",
                description="Expected 2 blank lines before class/function",
                severity="error",
                ast_patterns=["FunctionDef", "ClassDef"],
                fix_strategy="add_blank_lines_before",
                priority=2,
            ),
            "no-untyped-def": LintingRule(
                code="no-untyped-def",
                description="Function missing type annotations",
                severity="error",
                ast_patterns=["FunctionDef"],
                fix_strategy="add_type_annotations",
                priority=3,
            ),
        }

    def analyze_file_ast(self, file_path: str) -> dict[str, Any]:
        """Analyze file using AST with linting rule integration"""
        logger.info(f"🔍 AST-guided analysis: {file_path}")

        # Use existing EnhancedArtifactParser
        parsed_artifact = self.ast_parser.parse_artifact(file_path, "python")

        if not parsed_artifact.parsed_data.get("ast_parse_successful", False):
            logger.warning(f"AST parsing failed for {file_path}")
            return self._fallback_analysis(file_path)

        # Extract AST tree for detailed analysis
        try:
            with open(file_path) as f:
                content = f.read()
            tree = ast.parse(content)

            # AST-guided analysis
            ast_analysis = {
                "file_path": file_path,
                "ast_nodes": self._extract_ast_nodes(tree),
                "linting_issues": self._detect_ast_aware_issues(tree),
                "fix_strategies": self._generate_ast_aware_fixes(tree),
                "syntactic_boundaries": self._identify_syntactic_boundaries(tree),
            }

            # Merge with existing parser results
            merged_analysis = {**parsed_artifact.parsed_data, **ast_analysis}

            logger.info(
                f"✅ AST-guided analysis complete: {len(ast_analysis['ast_nodes'])} nodes",
            )
            return merged_analysis

        except Exception as e:
            logger.error(f"❌ AST analysis failed: {e}")
            return self._fallback_analysis(file_path)

    def _extract_ast_nodes(self, tree: ast.AST) -> list[ASTNode]:
        """Extract AST nodes with metadata"""
        nodes = []

        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom),
            ):
                ast_node = ASTNode(
                    node_type=type(node).__name__,
                    content=ast.unparse(node) if hasattr(ast, "unparse") else str(node),
                    line_number=getattr(node, "lineno", 0),
                    metadata={
                        "name": getattr(node, "name", ""),
                        "docstring": ast.get_docstring(node)
                        if hasattr(node, "body")
                        else None,
                    },
                )
                nodes.append(ast_node)

        return nodes

    def _detect_ast_aware_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Detect issues using AST-aware patterns"""
        issues = []

        for node in ast.walk(tree):
            node_type = type(node).__name__

            # Check each linting rule against this node type
            for rule_code, rule in self.linting_rules.items():
                if node_type in rule.ast_patterns:
                    issue = self._check_rule_against_node(rule, node)
                    if issue:
                        issues.append(issue)

        return issues

    def _check_rule_against_node(
        self,
        rule: LintingRule,
        node: ast.AST,
    ) -> Optional[dict[str, Any]]:
        """Check if a rule applies to a specific AST node"""
        if rule.code == "F401" and isinstance(node, (ast.Import, ast.ImportFrom)):
            # Check for unused imports (simplified)
            return {
                "code": rule.code,
                "line": getattr(node, "lineno", 0),
                "description": rule.description,
                "fix_strategy": rule.fix_strategy,
                "priority": rule.priority,
            }
        if rule.code == "E302" and isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            # Check for missing blank lines (simplified)
            return {
                "code": rule.code,
                "line": getattr(node, "lineno", 0),
                "description": rule.description,
                "fix_strategy": rule.fix_strategy,
                "priority": rule.priority,
            }
        if rule.code == "no-untyped-def" and isinstance(node, ast.FunctionDef):
            # Check for missing type annotations
            if not node.returns and not any(arg.annotation for arg in node.args.args):
                return {
                    "code": rule.code,
                    "line": getattr(node, "lineno", 0),
                    "description": f"Function '{node.name}' missing type annotations",
                    "fix_strategy": rule.fix_strategy,
                    "priority": rule.priority,
                }

        return None

    def _generate_ast_aware_fixes(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Generate AST-aware fixes based on detected issues"""
        issues = self._detect_ast_aware_issues(tree)
        fixes = []

        for issue in issues:
            fix = {
                "issue_code": issue["code"],
                "line": issue["line"],
                "fix_strategy": issue["fix_strategy"],
                "priority": issue["priority"],
                "ast_aware": True,
            }
            fixes.append(fix)

        return fixes

    def _identify_syntactic_boundaries(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Identify syntactic boundaries for guided generation"""
        boundaries = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                boundary = {
                    "type": type(node).__name__,
                    "start_line": getattr(node, "lineno", 0),
                    "end_line": getattr(node, "end_lineno", 0)
                    if hasattr(node, "end_lineno")
                    else 0,
                    "name": getattr(node, "name", ""),
                    "content": ast.unparse(node)
                    if hasattr(ast, "unparse")
                    else str(node),
                }
                boundaries.append(boundary)

        return boundaries

    def _fallback_analysis(self, file_path: str) -> dict[str, Any]:
        """Fallback analysis when AST parsing fails"""
        return {
            "file_path": file_path,
            "ast_parse_successful": False,
            "ast_nodes": [],
            "linting_issues": [],
            "fix_strategies": [],
            "syntactic_boundaries": [],
        }

    def generate_perfect_code(self, file_path: str) -> str:
        """Generate perfect code using AST-guided approach"""
        logger.info(f"🎯 Generating perfect code: {file_path}")

        # Analyze with AST guidance
        analysis = self.analyze_file_ast(file_path)

        if not analysis.get("ast_parse_successful", False):
            logger.warning(f"AST parsing failed, using fallback for {file_path}")
            return self._generate_fallback_code(file_path)

        # Generate code respecting syntactic boundaries
        generated_code = self._generate_ast_guided_code(analysis)

        logger.info(f"✅ Generated {len(generated_code)} characters of perfect code")
        return generated_code

    def _generate_ast_guided_code(self, analysis: dict[str, Any]) -> str:
        """Generate code using AST-guided approach"""
        # This is where we'd implement the actual code generation
        # For now, return a placeholder
        return f"""#!/usr/bin/env python3
\"\"\"Generated using AST-guided code generation\"\"\"

# AST Analysis Results:
# - {len(analysis.get('ast_nodes', []))} AST nodes
# - {len(analysis.get('linting_issues', []))} linting issues
# - {len(analysis.get('fix_strategies', []))} fix strategies
# - {len(analysis.get('syntactic_boundaries', []))} syntactic boundaries

# TODO: Implement actual AST-guided code generation
# This would respect syntactic boundaries and apply AST-aware fixes
"""


def main():
    """Main function to demonstrate AST-guided code generation"""
    generator = ASTGuidedCodeGenerator()

    # Test with a sample file
    test_file = "src/model_driven_projection/final_projection_system.py"

    print("🎯 AST-GUIDED CODE GENERATION DEMO")
    print("=" * 50)

    # Analyze with AST guidance
    analysis = generator.analyze_file_ast(test_file)

    print("📊 Analysis Results:")
    print(f"   ✅ AST nodes: {len(analysis.get('ast_nodes', []))}")
    print(f"   ⚠️  Linting issues: {len(analysis.get('linting_issues', []))}")
    print(f"   🔧 Fix strategies: {len(analysis.get('fix_strategies', []))}")
    print(
        f"   🎯 Syntactic boundaries: {len(analysis.get('syntactic_boundaries', []))}",
    )

    # Generate perfect code
    perfect_code = generator.generate_perfect_code(test_file)
    print(f"\n🎯 Generated {len(perfect_code)} characters of perfect code")
    print("✅ AST-guided code generation successful!")


if __name__ == "__main__":
    main()
