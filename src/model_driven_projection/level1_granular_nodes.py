#!/usr/bin/env python3
"""
Level 1: Granular Code Nodes Implementation

This implements the first level of model-driven projection:
- Granular code nodes (≤50 lines)
- Basic projection engine
- Dependency resolution
- Composition into files
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeNode:
    """A granular code node (≤50 lines)."""
    
    id: str
    type: str  # import, function, class, config, etc.
    content: str
    context: str
    dependencies: List[str]
    metadata: Dict[str, Any]
    projection_rules: Dict[str, Any]
    
    def validate_granularity(self) -> bool:
        """Ensure node is paragraph-sized (≤50 lines)."""
        lines = self.content.split('\n')
        return len(lines) <= 50 and len(self.content) <= 2000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class DependencyResolver:
    """Resolve dependencies between nodes."""
    
    def __init__(self):
        self.nodes: Dict[str, CodeNode] = {}
    
    def add_node(self, node: CodeNode) -> None:
        """Add a node to the resolver."""
        if not node.validate_granularity():
            raise ValueError(f"Node {node.id} exceeds granularity constraints")
        self.nodes[node.id] = node
    
    def resolve_order(self, node_ids: List[str]) -> List[str]:
        """Resolve node ordering based on dependencies."""
        logger.info(f"🔍 Resolving order for {len(node_ids)} nodes")
        
        # Build dependency graph
        graph = {node_id: set() for node_id in node_ids}
        for node_id in node_ids:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                for dep in node.dependencies:
                    if dep in node_ids:
                        graph[node_id].add(dep)
        
        # Topological sort
        result = []
        visited = set()
        temp_visited = set()
        
        def visit(node_id: str) -> None:
            if node_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {node_id}")
            if node_id in visited:
                return
            
            temp_visited.add(node_id)
            
            for dep in graph[node_id]:
                visit(dep)
            
            temp_visited.remove(node_id)
            visited.add(node_id)
            result.append(node_id)
        
        for node_id in node_ids:
            if node_id not in visited:
                visit(node_id)
        
        logger.info(f"✅ Resolved order: {result}")
        return result
    
    def detect_cycles(self, node_ids: List[str]) -> List[str]:
        """Detect circular dependencies."""
        cycles = []
        
        def find_cycles(node_id: str, path: List[str]) -> None:
            if node_id in path:
                cycle = path[path.index(node_id):] + [node_id]
                cycles.append(cycle)
                return
            
            if node_id not in self.nodes:
                return
            
            node = self.nodes[node_id]
            for dep in node.dependencies:
                if dep in node_ids:
                    find_cycles(dep, path + [node_id])
        
        for node_id in node_ids:
            find_cycles(node_id, [])
        
        return cycles


class NodeProjector:
    """Project nodes into code."""
    
    def __init__(self):
        self.resolver = DependencyResolver()
    
    def add_node(self, node: CodeNode) -> None:
        """Add a node to the projector."""
        self.resolver.add_node(node)
    
    def project_node(self, node_id: str, context: Dict[str, Any]) -> str:
        """Project a single node into code."""
        if node_id not in self.resolver.nodes:
            raise ValueError(f"Node {node_id} not found")
        
        node = self.resolver.nodes[node_id]
        
        # Apply projection rules
        content = node.content
        
        # Add context-specific modifications
        if context.get("add_type_hints") and node.type == "function":
            content = self._add_type_hints(content)
        
        if context.get("add_docstring") and node.type == "function":
            content = self._add_docstring(content)
        
        return content
    
    def compose_nodes(self, node_ids: List[str], context: Dict[str, Any]) -> str:
        """Compose multiple nodes into a file."""
        logger.info(f"🔧 Composing {len(node_ids)} nodes into file")
        
        # Resolve dependencies
        try:
            ordered_nodes = self.resolver.resolve_order(node_ids)
        except ValueError as e:
            logger.error(f"❌ Dependency resolution failed: {e}")
            return ""
        
        # Check for cycles
        cycles = self.resolver.detect_cycles(node_ids)
        if cycles:
            logger.warning(f"⚠️ Circular dependencies detected: {cycles}")
        
        # Project each node
        file_content = []
        
        # Add file header
        file_content.append(self._generate_file_header(context))
        
        # Add imports first
        import_nodes = [n for n in ordered_nodes if self.resolver.nodes[n].type == "import"]
        for node_id in import_nodes:
            content = self.project_node(node_id, context)
            file_content.append(content)
        
        # Add blank line after imports
        if import_nodes:
            file_content.append("")
        
        # Add other nodes
        other_nodes = [n for n in ordered_nodes if n not in import_nodes]
        for node_id in other_nodes:
            content = self.project_node(node_id, context)
            file_content.append(content)
            file_content.append("")  # Add blank line between nodes
        
        # Add file footer
        file_content.append(self._generate_file_footer(context))
        
        return "\n".join(file_content)
    
    def validate_composition(self, composition: str) -> bool:
        """Validate the composed result."""
        try:
            # Try to parse as Python
            compile(composition, "<string>", "exec")
            return True
        except SyntaxError:
            logger.error("❌ Composition has syntax errors")
            return False
    
    def _generate_file_header(self, context: Dict[str, Any]) -> str:
        """Generate file header."""
        header = [
            "#!/usr/bin/env python3",
            f'"""',
            f"Generated from model nodes",
            f"Context: {context.get('context', 'unknown')}",
            f"Generated: {datetime.now().isoformat()}",
            f'"""',
            ""
        ]
        return "\n".join(header)
    
    def _generate_file_footer(self, context: Dict[str, Any]) -> str:
        """Generate file footer."""
        return ""
    
    def _add_type_hints(self, content: str) -> str:
        """Add type hints to function content."""
        # Simple type hint addition (could be more sophisticated)
        if "def " in content and "(" in content and ")" in content:
            # Add basic type hints
            content = content.replace("def ", "def ")  # Placeholder for type hint logic
        return content
    
    def _add_docstring(self, content: str) -> str:
        """Add docstring to function content."""
        if "def " in content:
            # Add basic docstring
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    # Insert docstring after function definition
                    indent = len(line) - len(line.lstrip())
                    docstring = ' ' * (indent + 4) + '"""Generated function."""'
                    lines.insert(i + 1, docstring)
                    break
            content = "\n".join(lines)
        return content


class ModelRegistry:
    """Registry for managing model nodes."""
    
    def __init__(self):
        self.nodes: Dict[str, CodeNode] = {}
        self.projector = NodeProjector()
    
    def add_node(self, node: CodeNode) -> None:
        """Add a node to the registry."""
        self.nodes[node.id] = node
        self.projector.add_node(node)
        logger.info(f"✅ Added node: {node.id}")
    
    def create_file(self, file_name: str, node_ids: List[str], context: Dict[str, Any]) -> str:
        """Create a file from nodes."""
        logger.info(f"🔧 Creating file {file_name} from {len(node_ids)} nodes")
        
        # Validate all nodes exist
        missing_nodes = [nid for nid in node_ids if nid not in self.nodes]
        if missing_nodes:
            raise ValueError(f"Missing nodes: {missing_nodes}")
        
        # Compose file
        content = self.projector.compose_nodes(node_ids, context)
        
        # Validate composition
        if not self.projector.validate_composition(content):
            raise ValueError(f"Invalid composition for {file_name}")
        
        return content
    
    def save_model(self, file_path: str) -> None:
        """Save the model to a file."""
        model_data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }
        
        with open(file_path, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"✅ Saved model to {file_path}")
    
    def load_model(self, file_path: str) -> None:
        """Load the model from a file."""
        with open(file_path, 'r') as f:
            model_data = json.load(f)
        
        self.nodes.clear()
        for node_id, node_data in model_data["nodes"].items():
            node = CodeNode(**node_data)
            self.add_node(node)
        
        logger.info(f"✅ Loaded model from {file_path}")


def create_sample_nodes() -> List[CodeNode]:
    """Create sample nodes for demonstration."""
    nodes = [
        CodeNode(
            id="import_pandas",
            type="import",
            content="import pandas as pd",
            context="data_processing",
            dependencies=[],
            metadata={"file_pattern": "*.py", "position": "top"},
            projection_rules={"format": "black"}
        ),
        CodeNode(
            id="import_numpy",
            type="import",
            content="import numpy as np",
            context="data_processing",
            dependencies=[],
            metadata={"file_pattern": "*.py", "position": "top"},
            projection_rules={"format": "black"}
        ),
        CodeNode(
            id="validate_dataframe",
            type="function",
            content="""def validate_dataframe(df):
    \"\"\"Validate that input is a pandas DataFrame.\"\"\"
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    return df""",
            context="validation",
            dependencies=["import_pandas"],
            metadata={"type_hints": True, "docstring": True},
            projection_rules={"format": "black", "lint": "flake8"}
        ),
        CodeNode(
            id="process_data",
            type="function",
            content="""def process_data(df):
    \"\"\"Process the input DataFrame.\"\"\"
    validated_df = validate_dataframe(df)
    # Add processing logic here
    return validated_df""",
            context="data_processing",
            dependencies=["validate_dataframe"],
            metadata={"type_hints": True, "docstring": True},
            projection_rules={"format": "black", "lint": "flake8"}
        )
    ]
    
    return nodes


def main():
    """Demonstrate Level 1 implementation."""
    logger.info("🚀 Starting Level 1: Granular Code Nodes")
    
    # Create registry
    registry = ModelRegistry()
    
    # Add sample nodes
    nodes = create_sample_nodes()
    for node in nodes:
        registry.add_node(node)
    
    # Create a file from nodes
    try:
        content = registry.create_file(
            "data_processor.py",
            ["import_pandas", "import_numpy", "validate_dataframe", "process_data"],
            {"context": "data_processing", "add_type_hints": True, "add_docstring": True}
        )
        
        print("\n" + "="*60)
        print("📄 Generated File: data_processor.py")
        print("="*60)
        print(content)
        print("="*60)
        
        # Save model
        registry.save_model("level1_model.json")
        
        logger.info("✅ Level 1 demonstration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 