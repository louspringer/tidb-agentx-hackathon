#!/usr/bin/env python3
"""
Test Neo4j Connection
Verify Neo4j is working before running the converter
"""

try:
    from neo4j import GraphDatabase
    print("✅ Neo4j Python driver available")
    
    # Test connection
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        print("✅ Neo4j connection successful!")
        print(f"Test result: {result.single()['test']}")
    driver.close()
    
    print("🎉 Neo4j is ready for AST conversion!")
    
except ImportError:
    print("❌ Neo4j Python driver not installed")
    print("Run: pip install neo4j")
    
except Exception as e:
    print(f"❌ Neo4j connection failed: {e}")
    print("Please check Neo4j setup instructions in NEO4J_SETUP_INSTRUCTIONS.md")
