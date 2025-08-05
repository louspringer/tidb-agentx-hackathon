#!/usr/bin/env python3
"""
Complete Project Model Builder: Create a comprehensive model of ALL project artifacts

This tool builds a complete project model that includes:
- All artifact files (273+ files)
- All granular nodes (1,000+ nodes)
- Complete project structure
- File relationships and dependencies
- Domain classifications
- Projection rules
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from comprehensive_artifact_extractor import ComprehensiveArtifactExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompleteProjectModelBuilder:
    """Build a complete project model from all artifacts."""
    
    def __init__(self):
        self.complete_model = {
            "version": "2.0",
            "description": "Complete model-driven project registry for OpenFlow Playground",
            "last_updated": "",
            "author": "LLM + Lou (OpenFlow-Playground)",
            "files": {},
            "nodes": {},
            "domains": {},
            "structure": {},
            "relationships": {},
            "projection_rules": {},
            "requirements_traceability": []
        }
        self.extractor = ComprehensiveArtifactExtractor()
    
    def build_complete_model(self) -> Dict[str, Any]:
        """Build the complete project model."""
        logger.info("🏗️ Building Complete Project Model")
        
        # Step 1: Extract all nodes from all artifacts
        self._extract_all_nodes()
        
        # Step 2: Build file registry
        self._build_file_registry()
        
        # Step 3: Build project structure
        self._build_project_structure()
        
        # Step 4: Build relationships
        self._build_relationships()
        
        # Step 5: Build projection rules
        self._build_projection_rules()
        
        # Step 6: Build requirements traceability
        self._build_requirements_traceability()
        
        # Step 7: Update metadata
        self._update_metadata()
        
        logger.info("✅ Complete project model built successfully")
        return self.complete_model
    
    def _extract_all_nodes(self) -> None:
        """Extract nodes from all artifacts."""
        logger.info("🔍 Extracting nodes from all artifacts")
        
        # Find all artifact files
        import glob
        artifact_files = glob.glob('**/*', recursive=True)
        artifact_files = [f for f in artifact_files if Path(f).is_file()]
        artifact_files = [f for f in artifact_files if '.venv' not in f and '__pycache__' not in f and '.git' not in f and '.mypy_cache' not in f]
        artifact_files = [f for f in artifact_files if Path(f).suffix.lower() in ['.py', '.md', '.yaml', '.yml', '.json', '.sh', '.toml', '.txt', '.cfg', '.ini']]
        
        logger.info(f"📁 Found {len(artifact_files)} artifact files")
        
        # Extract nodes from all files
        all_nodes = []
        processed_files = 0
        
        for file_path in artifact_files:
            try:
                nodes = self.extractor.extract_from_file(file_path)
                all_nodes.extend(nodes)
                processed_files += 1
                
                if processed_files % 50 == 0:
                    logger.info(f"📄 Processed {processed_files}/{len(artifact_files)} files")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {file_path}: {e}")
        
        # Add all nodes to the model
        for node_id, node in self.extractor.extracted_nodes.items():
            self.complete_model["nodes"][node_id] = node.to_dict()
        
        logger.info(f"✅ Extracted {len(all_nodes)} nodes from {processed_files} files")
    
    def _build_file_registry(self) -> None:
        """Build a registry of all files."""
        logger.info("📋 Building file registry")
        
        # Group nodes by source file
        files = {}
        for node_id, node_data in self.complete_model["nodes"].items():
            source_file = node_data.get("metadata", {}).get("source_file", "unknown")
            
            if source_file not in files:
                files[source_file] = {
                    "path": source_file,
                    "type": Path(source_file).suffix.lower(),
                    "context": node_data.get("context", "general"),
                    "nodes": [],
                    "dependencies": [],
                    "projection_rules": {}
                }
            
            files[source_file]["nodes"].append(node_id)
        
        # Add file-specific projection rules
        for file_path, file_data in files.items():
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.py':
                file_data["projection_rules"] = {
                    "format": "black",
                    "lint": "flake8",
                    "type_check": "mypy"
                }
            elif file_ext in ['.yaml', '.yml']:
                file_data["projection_rules"] = {
                    "format": "yaml",
                    "validate": "yamllint"
                }
            elif file_ext == '.json':
                file_data["projection_rules"] = {
                    "format": "json",
                    "validate": "json-schema"
                }
            elif file_ext == '.md':
                file_data["projection_rules"] = {
                    "format": "markdown",
                    "lint": "markdownlint"
                }
            elif file_ext == '.sh':
                file_data["projection_rules"] = {
                    "format": "shell",
                    "lint": "shellcheck"
                }
            elif file_ext == '.toml':
                file_data["projection_rules"] = {
                    "format": "toml",
                    "validate": "toml-validate"
                }
        
        self.complete_model["files"] = files
        logger.info(f"✅ Built file registry with {len(files)} files")
    
    def _build_project_structure(self) -> None:
        """Build the complete project structure."""
        logger.info("🏗️ Building project structure")
        
        structure = {}
        
        # Build directory structure
        for file_path in self.complete_model["files"].keys():
            path_parts = Path(file_path).parts
            
            current_level = structure
            for i, part in enumerate(path_parts[:-1]):
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            # Add file reference
            filename = path_parts[-1]
            current_level[filename] = f"files.{file_path}"
        
        self.complete_model["structure"] = structure
        logger.info("✅ Built complete project structure")
    
    def _build_relationships(self) -> None:
        """Build relationships between files and nodes."""
        logger.info("🔗 Building relationships")
        
        relationships = {
            "file_dependencies": {},
            "node_dependencies": {},
            "import_relationships": {},
            "domain_relationships": {}
        }
        
        # Build file dependencies
        for file_path, file_data in self.complete_model["files"].items():
            file_deps = []
            
            # Check for imports in Python files
            if file_data["type"] == '.py':
                for node_id in file_data["nodes"]:
                    node_data = self.complete_model["nodes"].get(node_id, {})
                    if node_data.get("type") == "import":
                        # Extract module name from import
                        import_content = node_data.get("content", "")
                        if "from" in import_content:
                            # Handle "from module import" syntax
                            module_match = import_content.split("from ")[1].split(" import")[0]
                            file_deps.append(module_match)
                        else:
                            # Handle "import module" syntax
                            module_match = import_content.split("import ")[1].split(" as")[0]
                            file_deps.append(module_match)
            
            relationships["file_dependencies"][file_path] = file_deps
        
        # Build node dependencies
        for node_id, node_data in self.complete_model["nodes"].items():
            node_deps = node_data.get("dependencies", [])
            relationships["node_dependencies"][node_id] = node_deps
        
        # Build domain relationships
        domain_files = {}
        for file_path, file_data in self.complete_model["files"].items():
            context = file_data["context"]
            if context not in domain_files:
                domain_files[context] = []
            domain_files[context].append(file_path)
        
        relationships["domain_relationships"] = domain_files
        
        self.complete_model["relationships"] = relationships
        logger.info("✅ Built complete relationships")
    
    def _build_projection_rules(self) -> None:
        """Build projection rules for all artifact types."""
        logger.info("📋 Building projection rules")
        
        projection_rules = {
            "python": {
                "format": "black",
                "lint": "flake8",
                "type_check": "mypy",
                "security": "bandit"
            },
            "markdown": {
                "format": "markdown",
                "lint": "markdownlint"
            },
            "yaml": {
                "format": "yaml",
                "validate": "yamllint"
            },
            "json": {
                "format": "json",
                "validate": "json-schema"
            },
            "shell": {
                "format": "shell",
                "lint": "shellcheck"
            },
            "toml": {
                "format": "toml",
                "validate": "toml-validate"
            },
            "text": {
                "format": "text"
            },
            "config": {
                "format": "config"
            }
        }
        
        self.complete_model["projection_rules"] = projection_rules
        logger.info("✅ Built projection rules")
    
    def _build_requirements_traceability(self) -> None:
        """Build requirements traceability."""
        logger.info("📋 Building requirements traceability")
        
        requirements = [
            {
                "requirement": "All Python files must pass AST parsing",
                "test": "test_python_quality.py",
                "files": ["*.py"],
                "validation": "ast.parse()"
            },
            {
                "requirement": "All Python files must pass linting",
                "test": "test_code_quality.py",
                "files": ["*.py"],
                "validation": "flake8"
            },
            {
                "requirement": "All Python files must be formatted",
                "test": "test_code_quality.py",
                "files": ["*.py"],
                "validation": "black"
            },
            {
                "requirement": "All YAML files must be valid",
                "test": "test_yaml_validation.py",
                "files": ["*.yaml", "*.yml"],
                "validation": "yamllint"
            },
            {
                "requirement": "All JSON files must be valid",
                "test": "test_json_validation.py",
                "files": ["*.json"],
                "validation": "json.loads()"
            },
            {
                "requirement": "All shell scripts must be valid",
                "test": "test_shell_validation.py",
                "files": ["*.sh"],
                "validation": "shellcheck"
            },
            {
                "requirement": "All markdown files must be valid",
                "test": "test_markdown_validation.py",
                "files": ["*.md"],
                "validation": "markdownlint"
            },
            {
                "requirement": "Model-driven projection must work",
                "test": "test_model_projection.py",
                "files": ["project_model_registry.json"],
                "validation": "projection_pipeline"
            }
        ]
        
        self.complete_model["requirements_traceability"] = requirements
        logger.info("✅ Built requirements traceability")
    
    def _update_metadata(self) -> None:
        """Update model metadata."""
        from datetime import datetime
        
        self.complete_model["last_updated"] = datetime.now().isoformat()
        self.complete_model["total_files"] = len(self.complete_model["files"])
        self.complete_model["total_nodes"] = len(self.complete_model["nodes"])
        
        # Count by type
        type_counts = {}
        for file_data in self.complete_model["files"].values():
            file_type = file_data["type"]
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        self.complete_model["file_type_counts"] = type_counts
    
    def save_complete_model(self, file_path: str) -> None:
        """Save the complete model to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.complete_model, f, indent=2)
        
        logger.info(f"✅ Saved complete model to {file_path}")
    
    def print_summary(self) -> None:
        """Print a summary of the complete model."""
        print("\n" + "="*80)
        print("🏗️ COMPLETE PROJECT MODEL SUMMARY")
        print("="*80)
        print(f"Total files: {self.complete_model['total_files']}")
        print(f"Total nodes: {self.complete_model['total_nodes']}")
        print(f"Model version: {self.complete_model['version']}")
        print(f"Last updated: {self.complete_model['last_updated']}")
        
        print("\n📁 File Types:")
        for file_type, count in self.complete_model["file_type_counts"].items():
            print(f"  {file_type}: {count} files")
        
        print("\n🔗 Domains:")
        domain_counts = {}
        for file_data in self.complete_model["files"].values():
            context = file_data["context"]
            domain_counts[context] = domain_counts.get(context, 0) + 1
        
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count} files")
        
        print("\n📋 Node Types:")
        node_type_counts = {}
        for node_data in self.complete_model["nodes"].values():
            node_type = node_data["type"]
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
        
        for node_type, count in sorted(node_type_counts.items()):
            print(f"  {node_type}: {count} nodes")
        
        print("="*80)


def main():
    """Build and save the complete project model."""
    logger.info("🚀 Starting Complete Project Model Builder")
    
    builder = CompleteProjectModelBuilder()
    
    # Build the complete model
    complete_model = builder.build_complete_model()
    
    # Save the model
    builder.save_complete_model("complete_project_model.json")
    
    # Print summary
    builder.print_summary()
    
    logger.info("✅ Complete project model builder finished")


if __name__ == "__main__":
    main() 