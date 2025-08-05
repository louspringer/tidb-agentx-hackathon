#!/usr/bin/env python3
"""
AST Graph Database Implementation
Execute immediate actions from Ghostbusters analysis
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ImplementationStatus:
    """Track implementation progress"""

    step: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    details: str
    timestamp: str


class ASTGraphImplementer:
    """Implement AST to Graph Database conversion"""

    def __init__(self):
        self.status_log: List[ImplementationStatus] = []
        self.filtered_ast_file = "ast_models_filtered.json"
        self.neo4j_converter_file = "ast_to_neo4j_converter.py"

    def log_status(self, step: str, status: str, details: str) -> None:
        """Log implementation status"""
        status_entry = ImplementationStatus(
            step=step,
            status=status,
            details=details,
            timestamp=datetime.now().isoformat(),
        )
        self.status_log.append(status_entry)
        print(f"📋 {step}: {status.upper()} - {details}")

    def fix_ast_modeler_exclusions(self) -> bool:
        """Fix AST modeler to exclude .mypy_cache files"""
        try:
            self.log_status(
                "Fix AST Modeler Exclusions",
                "in_progress",
                "Updating exclusion patterns",
            )

            # Read the comprehensive AST modeler
            with open("comprehensive_ast_modeler.py", "r") as f:
                content = f.read()

            # Find the exclusion patterns line
            old_pattern = "exclude_patterns = ['.venv', 'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache']"
            new_pattern = "exclude_patterns = ['.venv', 'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache', '.mypy_cache']"

            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)

                # Write back the fixed file
                with open("comprehensive_ast_modeler.py", "w") as f:
                    f.write(content)

                self.log_status(
                    "Fix AST Modeler Exclusions",
                    "completed",
                    "Added .mypy_cache to exclusion patterns",
                )
                return True
            else:
                self.log_status(
                    "Fix AST Modeler Exclusions",
                    "failed",
                    "Could not find exclusion patterns to update",
                )
                return False

        except Exception as e:
            self.log_status("Fix AST Modeler Exclusions", "failed", f"Error: {str(e)}")
            return False

    def create_filtered_ast_dataset(self) -> bool:
        """Create filtered AST dataset (292 files only)"""
        try:
            self.log_status(
                "Create Filtered AST Dataset",
                "in_progress",
                "Filtering out mypy cache files",
            )

            # Read the large AST models file
            with open("ast_models.json", "r") as f:
                ast_data = json.load(f)

            # Filter out mypy cache files
            filtered_models = {}
            total_files = len(ast_data["file_models"])
            filtered_count = 0

            for file_path, model in ast_data["file_models"].items():
                if ".mypy_cache" not in file_path:
                    filtered_models[file_path] = model
                    filtered_count += 1

            # Create filtered dataset
            filtered_data = {
                "file_models": filtered_models,
                "metadata": {
                    "original_file_count": total_files,
                    "filtered_file_count": filtered_count,
                    "noise_removed": total_files - filtered_count,
                    "filtering_criteria": "Excluded .mypy_cache files",
                    "created_at": datetime.now().isoformat(),
                },
                "summary": {
                    "total_files": filtered_count,
                    "file_types": {},
                    "complexity_stats": {
                        "avg_complexity": 0,
                        "max_complexity": 0,
                        "min_complexity": float("inf"),
                    },
                },
            }

            # Calculate summary statistics
            complexity_scores = []
            file_types: Dict[str, int] = {}

            for model in filtered_models.values():
                complexity_scores.append(model.get("complexity_score", 0))
                file_type = model.get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1

            if complexity_scores:
                filtered_data["summary"]["complexity_stats"] = {
                    "avg_complexity": sum(complexity_scores) / len(complexity_scores),
                    "max_complexity": max(complexity_scores),
                    "min_complexity": min(complexity_scores),
                }

            filtered_data["summary"]["file_types"] = file_types

            # Save filtered dataset
            with open(self.filtered_ast_file, "w") as f:
                json.dump(filtered_data, f, indent=2)

            self.log_status(
                "Create Filtered AST Dataset",
                "completed",
                f"Created {self.filtered_ast_file} with {filtered_count} files (removed {total_files - filtered_count} noise files)",
            )
            return True

        except Exception as e:
            self.log_status("Create Filtered AST Dataset", "failed", f"Error: {str(e)}")
            return False

    def setup_neo4j_environment(self) -> bool:
        """Set up Neo4j development environment"""
        try:
            self.log_status(
                "Setup Neo4j Environment", "in_progress", "Checking Neo4j availability"
            )

            # Check if Neo4j is available
            try:
                result = subprocess.run(
                    ["neo4j", "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.log_status(
                        "Setup Neo4j Environment",
                        "completed",
                        "Neo4j already installed",
                    )
                    return True
            except FileNotFoundError:
                pass

            # Check if Docker is available for Neo4j
            try:
                result = subprocess.run(
                    ["docker", "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.log_status(
                        "Setup Neo4j Environment",
                        "in_progress",
                        "Using Docker for Neo4j",
                    )

                    # Create docker-compose.yml for Neo4j
                    docker_compose_content = """version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
"""

                    with open("docker-compose.yml", "w") as f:
                        f.write(docker_compose_content)

                    self.log_status(
                        "Setup Neo4j Environment",
                        "completed",
                        "Created docker-compose.yml for Neo4j. Run: docker-compose up -d",
                    )
                    return True
                else:
                    self.log_status(
                        "Setup Neo4j Environment", "failed", "Docker not available"
                    )
                    return False
            except FileNotFoundError:
                self.log_status(
                    "Setup Neo4j Environment", "failed", "Docker not available"
                )
                return False

        except Exception as e:
            self.log_status("Setup Neo4j Environment", "failed", f"Error: {str(e)}")
            return False

    def create_neo4j_converter(self) -> bool:
        """Create basic AST to Neo4j converter"""
        try:
            self.log_status(
                "Create Neo4j Converter",
                "in_progress",
                "Creating AST to Neo4j converter",
            )

            converter_content = '''#!/usr/bin/env python3
"""
AST to Neo4j Converter
Convert filtered AST models to Neo4j graph database
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️  Neo4j driver not available. Install with: pip install neo4j")

@dataclass
class ConversionResult:
    """Result of AST to Neo4j conversion"""
    files_processed: int
    nodes_created: int
    relationships_created: int
    errors: List[str]
    duration: float

class ASTNeo4jConverter:
    """Convert AST models to Neo4j graph database"""

    def __init__(self, neo4j_uri: str = "bolt://localhost:7687",
                 username: str = "neo4j", password: str = "password"):
        self.neo4j_uri = neo4j_uri
        self.username = username
        self.password = password
        self.driver = None
        self.results = ConversionResult(0, 0, 0, [], 0.0)

    def connect(self) -> bool:
        """Connect to Neo4j database"""
        if not NEO4J_AVAILABLE:
            self.results.errors.append("Neo4j driver not available")
            return False

        try:
            self.driver = GraphDatabase.driver(self.neo4j_uri,
                                            auth=(self.username, self.password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            self.results.errors.append(f"Failed to connect to Neo4j: {str(e)}")
            return False

    def convert_ast_models(self, ast_file: str) -> ConversionResult:
        """Convert AST models to Neo4j"""
        start_time = datetime.now()

        try:
            # Load AST models
            with open(ast_file, "r") as f:
                ast_data = json.load(f)

            if not self.connect():
                return self.results

            with self.driver.session() as session:
                # Clear existing data
                session.run("MATCH (n) DETACH DELETE n")

                # Create file nodes
                for file_path, model in ast_data['file_models'].items():
                    try:
                        session.run("""
                            CREATE (f:File {
                                name: $name,
                                complexity_score: $complexity,
                                line_count: $lines,
                                file_type: $type,
                                function_count: $func_count,
                                class_count: $class_count,
                                import_count: $import_count
                            })
                        """, name=file_path,
                             complexity=model.get('complexity_score', 0),
                             lines=model.get('line_count', 0),
                             type=model.get('file_type', 'unknown'),
                             func_count=model.get('function_count', 0),
                             class_count=model.get('class_count', 0),
                             import_count=model.get('import_count', 0))

                        self.results.nodes_created += 1

                        # Create function nodes and relationships
                        if 'model_data' in model and 'functions' in model['model_data']:
                            for func in model['model_data']['functions']:
                                session.run("""
                                    MATCH (f:File {name: $file_name})
                                    CREATE (func:Function {name: $func_name})
                                    CREATE (f)-[:CONTAINS]->(func)
                                """, file_name=file_path, func_name=func.get('name', 'unknown'))

                                self.results.nodes_created += 1
                                self.results.relationships_created += 1

                        # Create class nodes and relationships
                        if 'model_data' in model and 'classes' in model['model_data']:
                            for cls in model['model_data']['classes']:
                                session.run("""
                                    MATCH (f:File {name: $file_name})
                                    CREATE (cls:Class {name: $class_name})
                                    CREATE (f)-[:CONTAINS]->(cls)
                                """, file_name=file_path, class_name=cls.get('name', 'unknown'))

                                self.results.nodes_created += 1
                                self.results.relationships_created += 1

                        # Create import relationships
                        if 'model_data' in model and 'imports' in model['model_data']:
                            for imp in model['model_data']['imports']:
                                session.run("""
                                    MATCH (f:File {name: $file_name})
                                    MERGE (imp:Import {name: $import_name})
                                    CREATE (f)-[:IMPORTS]->(imp)
                                """, file_name=file_path, import_name=imp)

                                self.results.nodes_created += 1
                                self.results.relationships_created += 1

                        self.results.files_processed += 1

                    except Exception as e:
                        self.results.errors.append(f"Error processing {file_path}: {str(e)}")

            self.results.duration = (datetime.now() - start_time).total_seconds()
            return self.results

        except Exception as e:
            self.results.errors.append(f"Conversion failed: {str(e)}")
            return self.results

    def create_sample_queries(self) -> List[str]:
        """Create sample Cypher queries for the converted data"""
        return [
            # Find high complexity files
            """
            MATCH (f:File)
            WHERE f.complexity_score > 50
            RETURN f.name, f.complexity_score, f.line_count
            ORDER BY f.complexity_score DESC
            LIMIT 10
            """,

            # Find files with many functions
            """
            MATCH (f:File)-[:CONTAINS]->(func:Function)
            WITH f, count(func) as func_count
            WHERE func_count > 5
            RETURN f.name, func_count
            ORDER BY func_count DESC
            """,

            # Find import dependencies
            """
            MATCH (f:File)-[:IMPORTS]->(imp:Import)
            RETURN f.name, imp.name
            LIMIT 20
            """,

            # Find files by type
            """
            MATCH (f:File)
            WHERE f.file_type = 'python'
            RETURN f.name, f.complexity_score
            ORDER BY f.complexity_score DESC
            """,

            # Find complex classes
            """
            MATCH (f:File)-[:CONTAINS]->(cls:Class)
            WHERE f.complexity_score > 30
            RETURN f.name, cls.name, f.complexity_score
            ORDER BY f.complexity_score DESC
            """
        ]

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

def main():
    """Main conversion function"""
    if len(sys.argv) != 2:
        print("Usage: python ast_to_neo4j_converter.py <ast_file>")
        sys.exit(1)

    ast_file = sys.argv[1]

    if not Path(ast_file).exists():
        print(f"Error: AST file {ast_file} not found")
        sys.exit(1)

    converter = ASTNeo4jConverter()
    results = converter.convert_ast_models(ast_file)

    print("🎯 **AST to Neo4j Conversion Results:**")
    print(f"Files processed: {results.files_processed}")
    print(f"Nodes created: {results.nodes_created}")
    print(f"Relationships created: {results.relationships_created}")
    print(f"Duration: {results.duration:.2f} seconds")

    if results.errors:
        print(f"Errors: {len(results.errors)}")
        for error in results.errors:
            print(f"  - {error}")

    print("\n📋 **Sample Queries:**")
    queries = converter.create_sample_queries()
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}:")
        print(query.strip())

    converter.close()

if __name__ == "__main__":
    main()
'''

            with open(self.neo4j_converter_file, "w") as f:
                f.write(converter_content)

            # Make it executable
            Path(self.neo4j_converter_file).chmod(0o755)

            self.log_status(
                "Create Neo4j Converter",
                "completed",
                f"Created {self.neo4j_converter_file} with comprehensive conversion logic",
            )
            return True

        except Exception as e:
            self.log_status("Create Neo4j Converter", "failed", f"Error: {str(e)}")
            return False

    def implement_data_validation(self) -> bool:
        """Implement basic data validation framework"""
        try:
            self.log_status(
                "Implement Data Validation",
                "in_progress",
                "Creating validation framework",
            )

            validation_content = '''#!/usr/bin/env python3
"""
AST Data Validation Framework
Validate AST models and conversion results
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    """Result of data validation"""
    passed: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]

class ASTDataValidator:
    """Validate AST models and conversion data"""

    def __init__(self):
        self.results = ValidationResult(True, [], [], {})

    def validate_ast_file(self, ast_file: str) -> ValidationResult:
        """Validate AST model file"""
        try:
            with open(ast_file, "r") as f:
                ast_data = json.load(f)

            # Check required fields
            required_fields = ['file_models', 'metadata', 'summary']
            for field in required_fields:
                if field not in ast_data:
                    self.results.errors.append(f"Missing required field: {field}")
                    self.results.passed = False

            # Check file models
            if 'file_models' in ast_data:
                file_count = len(ast_data['file_models'])
                self.results.details['file_count'] = file_count

                # Check for mypy cache files
                mypy_cache_count = sum(1 for path in ast_data['file_models'].keys()
                                     if '.mypy_cache' in path)
                if mypy_cache_count > 0:
                    self.results.warnings.append(f"Found {mypy_cache_count} mypy cache files")

                # Validate individual models
                for file_path, model in ast_data['file_models'].items():
                    self._validate_model(file_path, model)

            return self.results

        except Exception as e:
            self.results.errors.append(f"Validation failed: {str(e)}")
            self.results.passed = False
            return self.results

    def _validate_model(self, file_path: str, model: Dict[str, Any]):
        """Validate individual AST model"""
        required_model_fields = ['file_path', 'file_type', 'model_type', 'complexity_score']

        for field in required_model_fields:
            if field not in model:
                self.results.errors.append(f"Missing field '{field}' in {file_path}")
                self.results.passed = False

        # Validate complexity score
        if 'complexity_score' in model:
            complexity = model['complexity_score']
            if not isinstance(complexity, (int, float)) or complexity < 0:
                self.results.errors.append(f"Invalid complexity score in {file_path}: {complexity}")
                self.results.passed = False

        # Validate model data
        if 'model_data' in model:
            model_data = model['model_data']
            if not isinstance(model_data, dict):
                self.results.errors.append(f"Invalid model_data in {file_path}")
                self.results.passed = False

    def validate_conversion_results(self, results_file: str) -> ValidationResult:
        """Validate Neo4j conversion results"""
        try:
            with open(results_file, "r") as f:
                results = json.load(f)

            # Check required fields
            required_fields = ['files_processed', 'nodes_created', 'relationships_created']
            for field in required_fields:
                if field not in results:
                    self.results.errors.append(f"Missing required field: {field}")
                    self.results.passed = False

            # Validate counts
            if 'files_processed' in results and 'nodes_created' in results:
                if results['nodes_created'] < results['files_processed']:
                    self.results.warnings.append("Node count should be >= file count")

            return self.results

        except Exception as e:
            self.results.errors.append(f"Conversion validation failed: {str(e)}")
            self.results.passed = False
            return self.results

def main():
    """Run validation on AST files"""
    validator = ASTDataValidator()

    # Validate filtered AST file
    if Path("ast_models_filtered.json").exists():
        print("🔍 Validating filtered AST file...")
        result = validator.validate_ast_file("ast_models_filtered.json")

        if result.passed:
            print("✅ Validation passed")
        else:
            print("❌ Validation failed")

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

        if result.details:
            print("\nDetails:")
            for key, value in result.details.items():
                print(f"  - {key}: {value}")
    else:
        print("⚠️  ast_models_filtered.json not found")

if __name__ == "__main__":
    main()
'''

            with open("ast_data_validator.py", "w") as f:
                f.write(validation_content)

            # Make it executable
            Path("ast_data_validator.py").chmod(0o755)

            self.log_status(
                "Implement Data Validation",
                "completed",
                "Created ast_data_validator.py with comprehensive validation framework",
            )
            return True

        except Exception as e:
            self.log_status("Implement Data Validation", "failed", f"Error: {str(e)}")
            return False

    def run_implementation(self) -> bool:
        """Run the complete implementation"""
        print("🚀 **AST GRAPH DATABASE IMPLEMENTATION** 🚀")
        print("=" * 60)

        steps = [
            ("Fix AST Modeler Exclusions", self.fix_ast_modeler_exclusions),
            ("Create Filtered AST Dataset", self.create_filtered_ast_dataset),
            ("Setup Neo4j Environment", self.setup_neo4j_environment),
            ("Create Neo4j Converter", self.create_neo4j_converter),
            ("Implement Data Validation", self.implement_data_validation),
        ]

        success_count = 0
        for step_name, step_func in steps:
            if step_func():
                success_count += 1

        # Print summary
        print("\n📊 **IMPLEMENTATION SUMMARY:**")
        print(f"Steps completed: {success_count}/{len(steps)}")

        if success_count == len(steps):
            print("🎉 **ALL STEPS COMPLETED SUCCESSFULLY!**")
            print("\n📋 **Next Steps:**")
            print("1. Start Neo4j: docker-compose up -d")
            print("2. Validate data: python ast_data_validator.py")
            print(
                "3. Convert to Neo4j: python ast_to_neo4j_converter.py ast_models_filtered.json"
            )
            print("4. Explore graph: http://localhost:7474")
            return True
        else:
            print("⚠️ **SOME STEPS FAILED - CHECK LOGS ABOVE**")
            return False


def main() -> None:
    """Main implementation function"""
    implementer = ASTGraphImplementer()
    success = implementer.run_implementation()

    if success:
        print("\n🎯 **READY FOR GRAPH DATABASE ANALYSIS!** 🎯")
    else:
        print("\n❌ **IMPLEMENTATION INCOMPLETE - MANUAL INTERVENTION REQUIRED** ❌")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
