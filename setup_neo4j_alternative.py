#!/usr/bin/env python3
"""
Alternative Neo4j Setup
Provide multiple options for Neo4j installation
"""

import subprocess
import sys
from pathlib import Path

def check_command(command: str) -> bool:
    """Check if a command is available"""
    try:
        result = subprocess.run([command, "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_neo4j_python_driver():
    """Install Neo4j Python driver"""
    print("📦 Installing Neo4j Python driver...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "neo4j"], check=True)
        print("✅ Neo4j Python driver installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Neo4j driver: {e}")
        return False

def create_neo4j_instructions():
    """Create instructions for Neo4j setup"""
    instructions = """
# 🎯 NEO4J SETUP INSTRUCTIONS

## Option 1: Docker (Recommended)
```bash
# Install Docker if not available
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Start Neo4j
docker-compose up -d
```

## Option 2: Direct Installation
```bash
# Add Neo4j repository
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list

# Install Neo4j
sudo apt-get update
sudo apt-get install neo4j

# Start Neo4j
sudo systemctl start neo4j
```

## Option 3: Manual Download
```bash
# Download Neo4j Community Edition
wget https://dist.neo4j.org/neo4j-community-5.15.0-unix.tar.gz
tar -xf neo4j-community-5.15.0-unix.tar.gz
cd neo4j-community-5.15.0

# Configure and start
./bin/neo4j start
```

## Option 4: Cloud Neo4j (Free Tier)
1. Go to https://neo4j.com/cloud/platform/aura-graph-database/
2. Create free account
3. Create new database
4. Use provided connection string

## Connection Details
- URL: bolt://localhost:7687 (local) or your cloud URL
- Username: neo4j
- Password: password (local) or your cloud password

## Test Connection
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    result = session.run("RETURN 1 as test")
    print("✅ Neo4j connection successful!")
driver.close()
```

## Next Steps After Setup
1. Run: python ast_data_validator.py
2. Run: python ast_to_neo4j_converter.py ast_models_filtered.json
3. Open: http://localhost:7474 (Neo4j Browser)
"""
    
    with open("NEO4J_SETUP_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("📋 Created NEO4J_SETUP_INSTRUCTIONS.md with detailed setup options")

def create_test_script():
    """Create a test script for Neo4j connection"""
    test_script = '''#!/usr/bin/env python3
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
'''
    
    with open("test_neo4j_connection.py", "w") as f:
        f.write(test_script)
    
    Path("test_neo4j_connection.py").chmod(0o755)
    print("📋 Created test_neo4j_connection.py")

def main():
    """Main setup function"""
    print("🔧 **ALTERNATIVE NEO4J SETUP** 🔧")
    print("=" * 50)
    
    # Check current status
    print("📊 **Current Status:**")
    print(f"Docker available: {check_command('docker')}")
    print(f"Docker Compose available: {check_command('docker-compose')}")
    print(f"Neo4j available: {check_command('neo4j')}")
    
    # Install Python driver
    print("\n📦 **Installing Neo4j Python Driver:**")
    if install_neo4j_python_driver():
        print("✅ Python driver ready")
    else:
        print("⚠️  Manual installation required")
    
    # Create instructions
    print("\n📋 **Creating Setup Instructions:**")
    create_neo4j_instructions()
    create_test_script()
    
    print("\n🎯 **NEXT STEPS:**")
    print("1. Choose a Neo4j setup option from NEO4J_SETUP_INSTRUCTIONS.md")
    print("2. Follow the instructions to install and start Neo4j")
    print("3. Test connection: python test_neo4j_connection.py")
    print("4. Run conversion: python ast_to_neo4j_converter.py ast_models_filtered.json")
    print("5. Explore graph: http://localhost:7474")
    
    print("\n💡 **Quick Start (if you have Docker):**")
    print("docker-compose up -d")
    print("python test_neo4j_connection.py")

if __name__ == "__main__":
    main() 