#!/usr/bin/env python3
"""
Comprehensive Artifact Extractor: Extract nodes from ALL artifacts

This tool extracts granular nodes from all artifact types:
- Python files (functions, classes, imports)
- Markdown files (sections, code blocks, links)
- YAML files (sections, configurations)
- JSON files (objects, arrays)
- Shell scripts (functions, commands)
- Configuration files (sections, settings)
"""

import ast
import json
import yaml
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from level1_granular_nodes import CodeNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveArtifactExtractor:
    """Extract granular nodes from ALL artifact types."""
    
    def __init__(self):
        self.extracted_nodes: Dict[str, CodeNode] = {}
        self.file_context: Dict[str, str] = {}
        self.artifact_types = {
            '.py': self._extract_python_nodes,
            '.md': self._extract_markdown_nodes,
            '.yaml': self._extract_yaml_nodes,
            '.yml': self._extract_yaml_nodes,
            '.json': self._extract_json_nodes,
            '.sh': self._extract_shell_nodes,
            '.toml': self._extract_toml_nodes,
            '.txt': self._extract_text_nodes,
            '.cfg': self._extract_config_nodes,
            '.ini': self._extract_config_nodes
        }
    
    def extract_from_file(self, file_path: str) -> List[CodeNode]:
        """Extract granular nodes from any artifact file."""
        logger.info(f"🔍 Extracting nodes from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return []
        
        # Determine file type and context
        file_ext = Path(file_path).suffix.lower()
        context = self._determine_context(file_path)
        self.file_context[file_path] = context
        
        # Extract nodes based on file type
        if file_ext in self.artifact_types:
            extractor_func = self.artifact_types[file_ext]
            nodes = extractor_func(content, file_path, context)
            logger.info(f"✅ Extracted {len(nodes)} nodes from {file_path}")
            return nodes
        else:
            logger.warning(f"⚠️ No extractor for file type: {file_ext}")
            return []
    
    def _determine_context(self, file_path: str) -> str:
        """Determine the context from file path."""
        path = Path(file_path)
        path_str = str(path)
        
        if "streamlit" in path_str:
            return "streamlit"
        elif "security_first" in path_str:
            return "security"
        elif "multi_agent_testing" in path_str:
            return "multi_agent"
        elif "tests" in path_str:
            return "testing"
        elif "config" in path_str or "config" in path.name:
            return "configuration"
        elif "docs" in path_str or path.suffix == '.md':
            return "documentation"
        elif "scripts" in path_str or path.suffix == '.sh':
            return "automation"
        elif path.suffix == '.yaml' or path.suffix == '.yml':
            return "infrastructure"
        elif path.suffix == '.json':
            return "data"
        else:
            return "general"
    
    def _extract_python_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from Python files."""
        nodes = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file_path}: {e}")
            return []
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_code = ast.unparse(node)
                node_id = f"import_{node.names[0].name if isinstance(node, ast.Import) else node.module or 'unknown'}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="import",
                    content=import_code,
                    context=context,
                    dependencies=[],
                    metadata={"file_pattern": "*.py", "position": "top", "source_file": file_path},
                    projection_rules={"format": "black", "position": "top"}
                )
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        # Extract functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_code = ast.unparse(node)
                node_id = f"function_{node.name}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="function",
                    content=function_code,
                    context=context,
                    dependencies=self._extract_function_dependencies(node),
                    metadata={"function_name": node.name, "has_docstring": ast.get_docstring(node) is not None, "source_file": file_path},
                    projection_rules={"format": "black", "lint": "flake8"}
                )
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        # Extract classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_code = ast.unparse(node)
                node_id = f"class_{node.name}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="class",
                    content=class_code,
                    context=context,
                    dependencies=self._extract_class_dependencies(node),
                    metadata={"class_name": node.name, "has_docstring": ast.get_docstring(node) is not None, "source_file": file_path},
                    projection_rules={"format": "black", "lint": "flake8"}
                )
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_markdown_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from Markdown files."""
        nodes = []
        
        # Split into sections by headers
        sections = re.split(r'^(#{1,6}\s+.+)$', content, flags=re.MULTILINE)
        
        for i, section in enumerate(sections):
            if section.strip():
                # Create node for each section
                node_id = f"section_{Path(file_path).stem}_{i}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="markdown_section",
                    content=section.strip(),
                    context=context,
                    dependencies=[],
                    metadata={"section_index": i, "source_file": file_path},
                    projection_rules={"format": "markdown"}
                )
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_yaml_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from YAML files."""
        nodes = []
        
        try:
            yaml_data = yaml.safe_load(content)
            if isinstance(yaml_data, dict):
                for key, value in yaml_data.items():
                    node_id = f"yaml_{key}"
                    
                    # Convert to YAML string
                    section_content = yaml.dump({key: value}, default_flow_style=False)
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="yaml_section",
                        content=section_content,
                        context=context,
                        dependencies=[],
                        metadata={"yaml_key": key, "source_file": file_path},
                        projection_rules={"format": "yaml"}
                    )
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
        except yaml.YAMLError as e:
            logger.error(f"❌ YAML parsing error in {file_path}: {e}")
        
        return nodes
    
    def _extract_json_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from JSON files."""
        nodes = []
        
        try:
            json_data = json.loads(content)
            if isinstance(json_data, dict):
                for key, value in json_data.items():
                    node_id = f"json_{key}"
                    
                    # Convert to JSON string
                    section_content = json.dumps({key: value}, indent=2)
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="json_section",
                        content=section_content,
                        context=context,
                        dependencies=[],
                        metadata={"json_key": key, "source_file": file_path},
                        projection_rules={"format": "json"}
                    )
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error in {file_path}: {e}")
        
        return nodes
    
    def _extract_shell_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from shell scripts."""
        nodes = []
        
        # Split into functions and commands
        lines = content.split('\n')
        current_function = []
        in_function = False
        
        for line in lines:
            if line.strip().startswith('function ') or re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\(\)\s*{?$', line.strip()):
                # Start of function
                if current_function and in_function:
                    # Save previous function
                    function_content = '\n'.join(current_function)
                    node_id = f"shell_function_{len(nodes)}"
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="shell_function",
                        content=function_content,
                        context=context,
                        dependencies=[],
                        metadata={"source_file": file_path},
                        projection_rules={"format": "shell"}
                    )
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
                
                current_function = [line]
                in_function = True
            elif in_function and line.strip() == '}':
                # End of function
                current_function.append(line)
                function_content = '\n'.join(current_function)
                node_id = f"shell_function_{len(nodes)}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="shell_function",
                    content=function_content,
                    context=context,
                    dependencies=[],
                    metadata={"source_file": file_path},
                    projection_rules={"format": "shell"}
                )
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
                
                current_function = []
                in_function = False
            elif in_function:
                current_function.append(line)
        
        return nodes
    
    def _extract_toml_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from TOML files."""
        nodes = []
        
        # Split into sections
        lines = content.split('\n')
        current_section = []
        current_section_name = "root"
        
        for line in lines:
            if line.strip().startswith('[') and line.strip().endswith(']'):
                # Save previous section
                if current_section:
                    section_content = '\n'.join(current_section)
                    node_id = f"toml_section_{current_section_name}"
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="toml_section",
                        content=section_content,
                        context=context,
                        dependencies=[],
                        metadata={"section_name": current_section_name, "source_file": file_path},
                        projection_rules={"format": "toml"}
                    )
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
                
                # Start new section
                current_section_name = line.strip()[1:-1]
                current_section = [line]
            else:
                current_section.append(line)
        
        # Save last section
        if current_section:
            section_content = '\n'.join(current_section)
            node_id = f"toml_section_{current_section_name}"
            
            code_node = CodeNode(
                id=node_id,
                type="toml_section",
                content=section_content,
                context=context,
                dependencies=[],
                metadata={"section_name": current_section_name, "source_file": file_path},
                projection_rules={"format": "toml"}
            )
            nodes.append(code_node)
            self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_text_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from text files."""
        nodes = []
        
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                node_id = f"text_paragraph_{Path(file_path).stem}_{i}"
                
                code_node = CodeNode(
                    id=node_id,
                    type="text_paragraph",
                    content=paragraph.strip(),
                    context=context,
                    dependencies=[],
                    metadata={"paragraph_index": i, "source_file": file_path},
                    projection_rules={"format": "text"}
                )
                nodes.append(code_node)
                self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_config_nodes(self, content: str, file_path: str, context: str) -> List[CodeNode]:
        """Extract nodes from configuration files."""
        nodes = []
        
        # Split into sections
        lines = content.split('\n')
        current_section = []
        current_section_name = "default"
        
        for line in lines:
            if line.strip().startswith('[') and line.strip().endswith(']'):
                # Save previous section
                if current_section:
                    section_content = '\n'.join(current_section)
                    node_id = f"config_section_{current_section_name}"
                    
                    code_node = CodeNode(
                        id=node_id,
                        type="config_section",
                        content=section_content,
                        context=context,
                        dependencies=[],
                        metadata={"section_name": current_section_name, "source_file": file_path},
                        projection_rules={"format": "config"}
                    )
                    nodes.append(code_node)
                    self.extracted_nodes[node_id] = code_node
                
                # Start new section
                current_section_name = line.strip()[1:-1]
                current_section = [line]
            else:
                current_section.append(line)
        
        # Save last section
        if current_section:
            section_content = '\n'.join(current_section)
            node_id = f"config_section_{current_section_name}"
            
            code_node = CodeNode(
                id=node_id,
                type="config_section",
                content=section_content,
                context=context,
                dependencies=[],
                metadata={"section_name": current_section_name, "source_file": file_path},
                projection_rules={"format": "config"}
            )
            nodes.append(code_node)
            self.extracted_nodes[node_id] = code_node
        
        return nodes
    
    def _extract_function_dependencies(self, node: ast.FunctionDef) -> List[str]:
        """Extract dependencies for a function."""
        dependencies = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id'):
                    func_name = child.func.id
                    if f"function_{func_name}" in self.extracted_nodes:
                        dependencies.append(f"function_{func_name}")
            elif isinstance(child, ast.Name):
                name = child.id
                for node_id, extracted_node in self.extracted_nodes.items():
                    if extracted_node.type == "import" and name in extracted_node.content:
                        dependencies.append(node_id)
        
        return dependencies
    
    def _extract_class_dependencies(self, node: ast.ClassDef) -> List[str]:
        """Extract dependencies for a class."""
        dependencies = []
        
        for base in node.bases:
            if hasattr(base, 'id'):
                base_name = base.id
                if f"class_{base_name}" in self.extracted_nodes:
                    dependencies.append(f"class_{base_name}")
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id'):
                    func_name = child.func.id
                    if f"function_{func_name}" in self.extracted_nodes:
                        dependencies.append(f"function_{func_name}")
        
        return dependencies
    
    def save_extracted_nodes(self, file_path: str) -> None:
        """Save extracted nodes to a JSON file."""
        from datetime import datetime
        
        data = {
            "version": "2.0",
            "extracted_at": datetime.now().isoformat(),
            "nodes": {node_id: node.to_dict() for node_id, node in self.extracted_nodes.items()},
            "file_contexts": self.file_context
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Saved {len(self.extracted_nodes)} extracted nodes to {file_path}")


def main():
    """Demonstrate comprehensive artifact extraction."""
    logger.info("🚀 Starting Comprehensive Artifact Extraction")
    
    extractor = ComprehensiveArtifactExtractor()
    
    # Find all artifact files
    import glob
    artifact_files = glob.glob('**/*', recursive=True)
    artifact_files = [f for f in artifact_files if Path(f).is_file()]
    artifact_files = [f for f in artifact_files if '.venv' not in f and '__pycache__' not in f and '.git' not in f and '.mypy_cache' not in f]
    artifact_files = [f for f in artifact_files if Path(f).suffix.lower() in ['.py', '.md', '.yaml', '.yml', '.json', '.sh', '.toml', '.txt', '.cfg', '.ini']]
    
    logger.info(f"📁 Found {len(artifact_files)} artifact files")
    
    all_nodes = []
    processed_files = 0
    
    for file_path in artifact_files[:50]:  # Process first 50 files for demo
        try:
            nodes = extractor.extract_from_file(file_path)
            all_nodes.extend(nodes)
            processed_files += 1
            
            if processed_files % 10 == 0:
                logger.info(f"📄 Processed {processed_files}/{len(artifact_files)} files")
                
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
    
    # Save extracted nodes
    extractor.save_extracted_nodes("comprehensive_extracted_nodes.json")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE ARTIFACT EXTRACTION SUMMARY")
    print("="*60)
    print(f"Files processed: {processed_files}")
    print(f"Total nodes extracted: {len(all_nodes)}")
    
    # Group by type
    by_type = {}
    for node in all_nodes:
        node_type = node.type
        if node_type not in by_type:
            by_type[node_type] = []
        by_type[node_type].append(node.id)
    
    for node_type, node_ids in by_type.items():
        print(f"{node_type.title()}: {len(node_ids)} nodes")
        for node_id in node_ids[:3]:  # Show first 3
            print(f"  - {node_id}")
        if len(node_ids) > 3:
            print(f"  ... and {len(node_ids) - 3} more")
    
    print("="*60)
    logger.info("✅ Comprehensive artifact extraction completed")


if __name__ == "__main__":
    main() 