#!/usr/bin/env python3
"""
AST to Neo4j Converter
Converts AST models to Neo4j graph database
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from neo4j import GraphDatabase, Driver

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of AST to Neo4j conversion"""
    success: bool
    nodes_created: int = 0
    relationships_created: int = 0
    errors: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


class ASTToNeo4jConverter:
    """Converts AST models to Neo4j graph database"""

    def __init__(self, neo4j_uri: str = "bolt://localhost:7687",
                 username: str = "neo4j", password: str = "password"):
        self.neo4j_uri = neo4j_uri
        self.username = username
        self.password = password
        self.driver: Optional[Driver] = None

    def connect(self) -> bool:
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.username, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1")
                result.single()
            logger.info("✅ Connected to Neo4j successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            return False

    def convert_ast_models(self, ast_models_file: str) -> ConversionResult:
        """Convert AST models to Neo4j graph"""
        try:
            # Load AST models
            with open(ast_models_file, 'r') as f:
                ast_models = json.load(f)

            if not self.connect():
                return ConversionResult(success=False, errors=["Failed to connect to Neo4j"])

            # Clear existing data
            self._clear_existing_data()

            # Convert files to nodes
            file_nodes = self._create_file_nodes(ast_models)

            # Convert functions to nodes
            function_nodes = self._create_function_nodes(ast_models)

            # Convert classes to nodes
            class_nodes = self._create_class_nodes(ast_models)

            # Convert imports to nodes
            import_nodes = self._create_import_nodes(ast_models)

            # Create relationships
            relationships = self._create_relationships(ast_models)

            total_nodes = file_nodes + function_nodes + class_nodes + import_nodes

            logger.info(f"✅ Conversion completed: {total_nodes} nodes, {relationships} relationships")

            return ConversionResult(
                success=True,
                nodes_created=total_nodes,
                relationships_created=relationships
            )

        except Exception as e:
            logger.error(f"❌ Conversion failed: {e}")
            return ConversionResult(success=False, errors=[str(e)])

    def _clear_existing_data(self) -> None:
        """Clear existing data from Neo4j"""
        if self.driver is None:
            return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("🧹 Cleared existing data")

    def _create_file_nodes(self, ast_models: Dict[str, Any]) -> int:
        """Create file nodes in Neo4j"""
        if self.driver is None:
            return 0
        count = 0
        with self.driver.session() as session:
            for file_path, file_data in ast_models.items():
                cypher = """
                CREATE (f:File {
                    path: $path,
                    file_type: $file_type,
                    size: $size,
                    functions_count: $functions_count,
                    classes_count: $classes_count,
                    imports_count: $imports_count
                })
                """
                session.run(cypher, {
                    'path': file_path,
                    'file_type': file_data.get('file_type', 'unknown'),
                    'size': file_data.get('size', 0),
                    'functions_count': len(file_data.get('functions', [])),
                    'classes_count': len(file_data.get('classes', [])),
                    'imports_count': len(file_data.get('imports', []))
                })
                count += 1

        logger.info(f"📁 Created {count} file nodes")
        return count

    def _create_function_nodes(self, ast_models: Dict[str, Any]) -> int:
        """Create function nodes in Neo4j"""
        if self.driver is None:
            return 0
        count = 0
        with self.driver.session() as session:
            for file_path, file_data in ast_models.items():
                for func in file_data.get('functions', []):
                    cypher = """
                    CREATE (func:Function {
                        name: $name,
                        file_path: $file_path,
                        line_number: $line_number,
                        parameters: $parameters,
                        return_type: $return_type
                    })
                    """
                    session.run(cypher, {
                        'name': func.get('name', ''),
                        'file_path': file_path,
                        'line_number': func.get('line_number', 0),
                        'parameters': json.dumps(func.get('parameters', [])),
                        'return_type': func.get('return_type', '')
                    })
                    count += 1

        logger.info(f"🔧 Created {count} function nodes")
        return count

    def _create_class_nodes(self, ast_models: Dict[str, Any]) -> int:
        """Create class nodes in Neo4j"""
        if self.driver is None:
            return 0
        count = 0
        with self.driver.session() as session:
            for file_path, file_data in ast_models.items():
                for cls in file_data.get('classes', []):
                    cypher = """
                    CREATE (cls:Class {
                        name: $name,
                        file_path: $file_path,
                        line_number: $line_number,
                        methods_count: $methods_count,
                        base_classes: $base_classes
                    })
                    """
                    session.run(cypher, {
                        'name': cls.get('name', ''),
                        'file_path': file_path,
                        'line_number': cls.get('line_number', 0),
                        'methods_count': len(cls.get('methods', [])),
                        'base_classes': json.dumps(cls.get('base_classes', []))
                    })
                    count += 1

        logger.info(f"🏗️  Created {count} class nodes")
        return count

    def _create_import_nodes(self, ast_models: Dict[str, Any]) -> int:
        """Create import nodes in Neo4j"""
        if self.driver is None:
            return 0
        count = 0
        with self.driver.session() as session:
            for file_path, file_data in ast_models.items():
                for imp in file_data.get('imports', []):
                    cypher = """
                    CREATE (imp:Import {
                        module: $module,
                        file_path: $file_path,
                        line_number: $line_number,
                        import_type: $import_type
                    })
                    """
                    session.run(cypher, {
                        'module': imp.get('module', ''),
                        'file_path': file_path,
                        'line_number': imp.get('line_number', 0),
                        'import_type': imp.get('import_type', 'import')
                    })
                    count += 1

        logger.info(f"📦 Created {count} import nodes")
        return count

    def _create_relationships(self, ast_models: Dict[str, Any]) -> int:
        """Create relationships between nodes"""
        if self.driver is None:
            return 0
        count = 0
        with self.driver.session() as session:
            # File -> Function relationships
            for file_path, file_data in ast_models.items():
                for func in file_data.get('functions', []):
                    cypher = """
                    MATCH (f:File {path: $file_path})
                    MATCH (func:Function {name: $func_name, file_path: $file_path})
                    CREATE (f)-[:CONTAINS]->(func)
                    """
                    session.run(cypher, {
                        'file_path': file_path,
                        'func_name': func.get('name', '')
                    })
                    count += 1

            # File -> Class relationships
            for file_path, file_data in ast_models.items():
                for cls in file_data.get('classes', []):
                    cypher = """
                    MATCH (f:File {path: $file_path})
                    MATCH (cls:Class {name: $class_name, file_path: $file_path})
                    CREATE (f)-[:CONTAINS]->(cls)
                    """
                    session.run(cypher, {
                        'file_path': file_path,
                        'class_name': cls.get('name', '')
                    })
                    count += 1

            # File -> Import relationships
            for file_path, file_data in ast_models.items():
                for imp in file_data.get('imports', []):
                    cypher = """
                    MATCH (f:File {path: $file_path})
                    MATCH (imp:Import {module: $module, file_path: $file_path})
                    CREATE (f)-[:IMPORTS]->(imp)
                    """
                    session.run(cypher, {
                        'file_path': file_path,
                        'module': imp.get('module', '')
                    })
                    count += 1

        logger.info(f"🔗 Created {count} relationships")
        return count

    def create_sample_queries(self) -> List[str]:
        """Create sample Cypher queries for the graph"""
        return [
            "MATCH (f:File) RETURN f.path, f.functions_count ORDER BY f.functions_count DESC LIMIT 10",
            "MATCH (func:Function) RETURN func.name, func.file_path LIMIT 10",
            "MATCH (cls:Class) RETURN cls.name, cls.methods_count ORDER BY cls.methods_count DESC LIMIT 10",
            "MATCH (imp:Import) RETURN imp.module, COUNT(*) as usage_count ORDER BY usage_count DESC LIMIT 10",
            "MATCH (f:File)-[:CONTAINS]->(func:Function) RETURN f.path, COUNT(func) as func_count ORDER BY func_count DESC LIMIT 10"
        ]

    def close(self) -> None:
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("🔌 Closed Neo4j connection")


def main() -> None:
    """Main function to convert AST models to Neo4j"""
    print("🚀 **AST TO NEO4J CONVERTER**")
    print("=" * 40)

    # Initialize converter
    converter = ASTToNeo4jConverter()

    # Convert AST models
    result = converter.convert_ast_models("ast_models_filtered.json")

    if result.success:
        print("✅ Conversion successful!")
        print(f"   Nodes created: {result.nodes_created}")
        print(f"   Relationships created: {result.relationships_created}")

        print("\n📋 **Sample Queries:**")
        queries = converter.create_sample_queries()
        for i, query in enumerate(queries, 1):
            print(f"Query {i}:")
            print(query.strip())
            print()
    else:
        print("❌ Conversion failed:")
        for error in result.errors or []:
            print(f"  - {error}")

    converter.close()


if __name__ == "__main__":
    main()
