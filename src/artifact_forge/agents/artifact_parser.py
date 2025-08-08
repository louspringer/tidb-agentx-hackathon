#!/usr/bin/env python3
"""
Enhanced ArtifactParser Agent
Uses recursive descent to find enclosing blocks and handle indentation errors gracefully
"""

import ast
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BlockBoundary:
    """Represents a code block boundary"""

    start_line: int
    end_line: int
    block_type: str  # 'function', 'class', 'i', 'for', 'while', 'try', 'with'
    indent_level: int
    content: str
    parent_block: Optional["BlockBoundary"] = None


@dataclass
class ParsedArtifact:
    """Enhanced parsed artifact model with block analysis"""

    path: str
    artifact_type: str
    parsed_data: dict[str, Any]
    parsing_errors: list[str]
    parsing_timestamp: datetime
    block_analysis: dict[str, Any] = None  # type: ignore


class ArtifactParser:
    """Enhanced parser with recursive descent block analysis"""

    def __init__(self) -> None:
        self.parsers = {
            "python": self._parse_python_enhanced,
            "mdc": self._parse_mdc,
            "markdown": self._parse_markdown,
            "yaml": self._parse_yaml,
            "json": self._parse_json,
            "sql": self._parse_sql,
        }

    def parse_artifact(self, artifact_path: str, artifact_type: str) -> ParsedArtifact:
        """Parse an artifact with enhanced error recovery"""
        errors = []
        parsed_data = {}  # type: ignore
        block_analysis = {}  # type: ignore

        try:
            if artifact_type in self.parsers:
                parsed_data, block_analysis = self.parsers[artifact_type](artifact_path)
            else:
                parsed_data = self._parse_generic(artifact_path)
        except Exception as e:
            errors.append(f"Parsing failed: {str(e)}")

        return ParsedArtifact(
            path=artifact_path,
            artifact_type=artifact_type,
            parsed_data=parsed_data,
            parsing_errors=errors,
            parsing_timestamp=datetime.now(),
            block_analysis=block_analysis,
        )

    def _parse_python_enhanced(
        self,
        file_path: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Enhanced Python parsing with recursive descent block analysis"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        parsed_data = {}
        block_analysis = {}

        # First try standard AST parsing
        try:
            tree = ast.parse(content)
            parsed_data = {
                "imports": self._extract_imports(tree),
                "functions": self._extract_functions(tree),
                "classes": self._extract_classes(tree),
                "variables": self._extract_variables(tree),
                "complexity": self._calculate_complexity(tree),
                "line_count": len(lines),
                "ast_parse_successful": True,
            }
        except SyntaxError as e:
            logger.warning(f"AST parsing failed for {file_path}: {e}")
            parsed_data["ast_parse_successful"] = False
            parsed_data["ast_error"] = str(e)

            # Fall back to recursive descent block analysis
            block_analysis = self._analyze_blocks_recursive_descent(lines)
            parsed_data.update(self._extract_from_blocks(block_analysis))

        return parsed_data, block_analysis

    def _analyze_blocks_recursive_descent(self, lines: list[str]) -> dict[str, Any]:
        """Use recursive descent to find block boundaries despite indentation errors"""
        logger.info("Starting recursive descent block analysis")

        blocks = []
        current_block = None
        block_stack = []  # type: ignore

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Determine indentation level
            indent_level = len(line) - len(line.lstrip())

            # Check for block start patterns
            block_start = self._detect_block_start(stripped)
            if block_start:
                # Start new block
                new_block = BlockBoundary(
                    start_line=line_num,
                    end_line=line_num,  # Will be updated
                    block_type=block_start,
                    indent_level=indent_level,
                    content=line,
                    parent_block=current_block,
                )

                if current_block:
                    block_stack.append(current_block)
                current_block = new_block
                blocks.append(new_block)

            # Check for block end
            elif current_block and self._is_block_end(
                stripped,
                current_block.block_type,
            ):
                # End current block
                current_block.end_line = line_num
                current_block.content += "\n" + line

                # Pop back to parent block
                current_block = block_stack.pop() if block_stack else None

            # Update current block content
            elif current_block:
                current_block.content += "\n" + line
                current_block.end_line = line_num

        # Close any unclosed blocks
        while current_block:
            if block_stack:
                current_block = block_stack.pop()
            else:
                break

        return {
            "blocks": [self._block_to_dict(block) for block in blocks],
            "total_blocks": len(blocks),
            "block_types": self._count_block_types(blocks),
            "indentation_issues": self._detect_indentation_issues(lines),
        }

    def _detect_block_start(self, line: str) -> Optional[str]:
        """Detect if line starts a new block"""
        line = line.strip()

        # Function definitions
        if re.match(r"^def\s+\w+", line):
            return "function"

        # Class definitions
        if re.match(r"^class\s+\w+", line):
            return "class"

        # Control flow blocks
        if re.match(r"^if\s+", line):
            return "i"
        if re.match(r"^elif\s+", line):
            return "eli"
        if re.match(r"^else\s*:", line):
            return "else"
        if re.match(r"^for\s+", line):
            return "for"
        if re.match(r"^while\s+", line):
            return "while"
        if re.match(r"^try\s*:", line):
            return "try"
        if re.match(r"^except\s+", line):
            return "except"
        if re.match(r"^finally\s*:", line):
            return "finally"
        if re.match(r"^with\s+", line):
            return "with"

        return None

    def _is_block_end(self, line: str, block_type: str) -> bool:
        """Check if line ends the current block"""
        line = line.strip()

        # Check for dedentation (same or less indentation than block start)
        # This is a simplified check - in practice, we'd track indent levels more carefully

        # Specific end patterns
        if block_type == "function" and re.match(r"^def\s+", line):
            return True  # New function starts
        if block_type == "class" and re.match(r"^class\s+", line):
            return True  # New class starts
        if block_type in ["i", "eli", "else"] and re.match(
            r"^(elif|else|if)\s+",
            line,
        ):
            return True  # New control flow starts

        return False

    def _extract_from_blocks(self, block_analysis: dict[str, Any]) -> dict[str, Any]:
        """Extract structured data from block analysis"""
        blocks = block_analysis.get("blocks", [])

        functions = []
        classes = []
        imports = []

        for block in blocks:
            if block["block_type"] == "function":
                # Extract function info from block content
                func_info = self._extract_function_from_block(block)
                if func_info:
                    functions.append(func_info)
            elif block["block_type"] == "class":
                # Extract class info from block content
                class_info = self._extract_class_from_block(block)
                if class_info:
                    classes.append(class_info)

        # Try to extract imports from the beginning of the file
        if blocks:
            first_block = blocks[0]
            imports = self._extract_imports_from_content(first_block["content"])

        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity": len(functions) + len(classes),  # Simplified complexity
            "line_count": sum(
                block["end_line"] - block["start_line"] + 1 for block in blocks
            ),
        }

    def _extract_function_from_block(
        self,
        block: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """Extract function information from block content"""
        content = block["content"]
        lines = content.splitlines()

        if not lines:
            return None

        # Parse first line for function definition
        first_line = lines[0].strip()
        match = re.match(r"^def\s+(\w+)\s*\(([^)]*)\)", first_line)

        if match:
            func_name = match.group(1)
            args_str = match.group(2)

            # Count arguments (simplified)
            args_count = len(
                [arg.strip() for arg in args_str.split(",") if arg.strip()],
            )

            return {
                "name": func_name,
                "line_number": block["start_line"],
                "args": args_count,
                "block_size": block["end_line"] - block["start_line"] + 1,
            }

        return None

    def _extract_class_from_block(
        self,
        block: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """Extract class information from block content"""
        content = block["content"]
        lines = content.splitlines()

        if not lines:
            return None

        # Parse first line for class definition
        first_line = lines[0].strip()
        match = re.match(r"^class\s+(\w+)", first_line)

        if match:
            class_name = match.group(1)

            # Count methods (functions within the class)
            method_count = 0
            for line in lines:
                if re.match(r"^\s+def\s+", line):
                    method_count += 1

            return {
                "name": class_name,
                "line_number": block["start_line"],
                "methods": method_count,
                "block_size": block["end_line"] - block["start_line"] + 1,
            }

        return None

    def _extract_imports_from_content(self, content: str) -> list[str]:
        """Extract import statements from content"""
        imports = []
        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            if line.startswith(("import ", "from ")):
                imports.append(line)

        return imports

    def _detect_indentation_issues(self, lines: list[str]) -> list[dict[str, Any]]:
        """Detect indentation issues in the code"""
        issues = []

        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith("#"):
                # Check for mixed tabs and spaces
                if "\t" in line and "    " in line:
                    issues.append(
                        {
                            "line": i,
                            "type": "mixed_tabs_spaces",
                            "description": "Mixed tabs and spaces",
                        },
                    )

                # Check for inconsistent indentation
                if line.startswith(" "):
                    indent_level = len(line) - len(line.lstrip())
                    if indent_level % 4 != 0:
                        issues.append(
                            {
                                "line": i,
                                "type": "inconsistent_indentation",
                                "description": f"Indentation not multiple of 4: {indent_level} spaces",
                            },
                        )

        return issues

    def _block_to_dict(self, block: BlockBoundary) -> dict[str, Any]:
        """Convert BlockBoundary to dictionary"""
        return {
            "start_line": block.start_line,
            "end_line": block.end_line,
            "block_type": block.block_type,
            "indent_level": block.indent_level,
            "content": block.content,
            "parent_block": (
                block.parent_block.block_type if block.parent_block else None
            ),
        }

    def _count_block_types(self, blocks: list[BlockBoundary]) -> dict[str, int]:
        """Count blocks by type"""
        counts = {}  # type: ignore
        for block in blocks:
            counts[block.block_type] = counts.get(block.block_type, 0) + 1
        return counts

    # Standard parsing methods (unchanged)
    def _parse_mdc(self, file_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """Parse MDC file (Markdown with YAML frontmatter)"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Split frontmatter and markdown
        parts = content.split("---", 2)

        frontmatter = {}  # type: ignore
        markdown_content = content

        if len(parts) >= 3:
            try:
                import yaml  # type: ignore

                frontmatter = yaml.safe_load(parts[1]) or {}
                markdown_content = parts[2]
            except Exception:
                pass

        parsed_data = {
            "frontmatter": frontmatter,
            "markdown_content": markdown_content,
            "line_count": len(content.splitlines()),
            "has_frontmatter": len(parts) >= 3,
        }

        return parsed_data, {}

    def _parse_markdown(self, file_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """Parse Markdown file"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        parsed_data = {
            "content": content,
            "line_count": len(content.splitlines()),
            "headings": self._extract_headings(content),
            "links": self._extract_links(content),
        }

        return parsed_data, {}

    def _parse_yaml(self, file_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """Parse YAML file"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            import yaml

            data = yaml.safe_load(content)
            parsed_data = {
                "data": data,
                "line_count": len(content.splitlines()),
                "structure": self._analyze_yaml_structure(data),
            }
        except Exception as e:
            parsed_data = {"error": str(e), "line_count": len(content.splitlines())}

        return parsed_data, {}

    def _parse_json(self, file_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """Parse JSON file"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            import json

            data = json.loads(content)
            parsed_data = {
                "data": data,
                "line_count": len(content.splitlines()),
                "structure": self._analyze_json_structure(data),
            }
        except Exception as e:
            parsed_data = {"error": str(e), "line_count": len(content.splitlines())}

        return parsed_data, {}

    def _parse_sql(self, file_path: str) -> tuple[dict[str, Any], dict[str, Any]]:
        """Parse SQL file"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        parsed_data = {
            "content": content,
            "line_count": len(content.splitlines()),
            "statements": self._extract_sql_statements(content),
        }

        return parsed_data, {}

    def _parse_generic(self, file_path: str) -> dict[str, Any]:
        """Parse generic file"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        return {
            "content": content,
            "line_count": len(content.splitlines()),
            "file_size": len(content.encode("utf-8")),
        }

    # Helper methods (unchanged from original)
    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
        return imports

    def _extract_functions(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "line_number": node.lineno,
                        "args": len(node.args.args),
                    },
                )
        return functions

    def _extract_classes(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "line_number": node.lineno,
                        "methods": len(
                            [n for n in node.body if isinstance(n, ast.FunctionDef)],
                        ),
                    },
                )
        return classes

    def _extract_variables(self, tree: ast.AST) -> list[str]:
        """Extract variable assignments"""
        variables = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
        return variables

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def _extract_headings(self, content: str) -> list[str]:
        """Extract markdown headings"""
        headings = []
        for line in content.splitlines():
            if line.startswith("#"):
                headings.append(line.strip())
        return headings

    def _extract_links(self, content: str) -> list[str]:
        """Extract markdown links"""
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        return [f"{text} -> {url}" for text, url in links]

    def _extract_sql_statements(self, content: str) -> list[str]:
        """Extract SQL statements"""
        statements = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("--") and not line.startswith("/*"):
                statements.append(line)
        return statements

    def _analyze_yaml_structure(self, data: Any) -> dict[str, Any]:
        """Analyze YAML structure"""
        if isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "depth": self._calculate_depth(data),
            }
        if isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "depth": self._calculate_depth(data),
            }
        return {"type": "primitive"}

    def _analyze_json_structure(self, data: Any) -> dict[str, Any]:
        """Analyze JSON structure"""
        return self._analyze_yaml_structure(data)  # Same logic

    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate depth of nested structure"""
        if isinstance(obj, dict):
            return max(
                current_depth,
                max(self._calculate_depth(v, current_depth + 1) for v in obj.values()),
            )
        if isinstance(obj, list):
            return max(
                current_depth,
                max(self._calculate_depth(item, current_depth + 1) for item in obj),
            )
        return current_depth


def main() -> None:
    """Test Enhanced ArtifactParser"""
    parser = ArtifactParser()

    # Test with a problematic file
    test_file = "src/artifact_forge/agents/artifact_detector.py"
    if Path(test_file).exists():
        parsed = parser.parse_artifact(test_file, "python")
        print("🔍 **ENHANCED PARSED ARTIFACT:**")
        print(f"Path: {parsed.path}")
        print(f"Type: {parsed.artifact_type}")
        print(
            f"AST Parse Successful: {parsed.parsed_data.get('ast_parse_successful', False)}",
        )
        print(f"Functions: {len(parsed.parsed_data.get('functions', []))}")
        print(f"Classes: {len(parsed.parsed_data.get('classes', []))}")
        print(f"Imports: {len(parsed.parsed_data.get('imports', []))}")

        if parsed.block_analysis:
            print(f"Blocks Found: {parsed.block_analysis.get('total_blocks', 0)}")
            print(f"Block Types: {parsed.block_analysis.get('block_types', {})}")
            print(
                f"Indentation Issues: {len(parsed.block_analysis.get('indentation_issues', []))}",
            )

        if parsed.parsing_errors:
            print(f"Parsing Errors: {len(parsed.parsing_errors)}")
    else:
        print(f"⚠️  Test file {test_file} not found")


if __name__ == "__main__":
    main()
