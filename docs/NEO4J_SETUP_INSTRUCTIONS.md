
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
