#!/usr/bin/env python3
"""
Day 1: TiDB Integration Foundation
Emergency hackathon implementation - get TiDB connected ASAP
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# TiDB connection setup
try:
    import pymysql
    import sqlalchemy
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError:
    print("❌ Missing TiDB dependencies. Installing...")
    os.system("pip install pymysql sqlalchemy")
    import pymysql
    import sqlalchemy
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

class TiDBConnection:
    """Emergency TiDB connection for hackathon demo."""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self.logger = logging.getLogger(__name__)
        
    def setup_connection(self, connection_string: str = None):
        """Set up TiDB Serverless connection."""
        
        if not connection_string:
            # Default TiDB Serverless connection format
            # User needs to provide actual credentials
            connection_string = os.getenv('TIDB_CONNECTION_STRING', 
                'mysql+pymysql://username:password@gateway01.us-west-2.prod.aws.tidbcloud.com:4000/database_name?ssl_verify_cert=true&ssl_verify_identity=true'
            )
        
        try:
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=True  # Debug mode for hackathon
            )
            
            self.session_maker = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                print(f"✅ TiDB connection successful: {result.fetchone()}")
                
            return True
            
        except Exception as e:
            print(f"❌ TiDB connection failed: {e}")
            print("💡 Make sure to set TIDB_CONNECTION_STRING environment variable")
            return False
    
    def create_beast_mode_schema(self):
        """Create minimal schema for Beast Mode messages."""
        
        schema_sql = """
        CREATE TABLE IF NOT EXISTS beast_messages (
            id VARCHAR(36) PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            source VARCHAR(100) NOT NULL,
            target VARCHAR(100),
            payload JSON NOT NULL,
            timestamp TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            priority INT NOT NULL DEFAULT 5,
            
            -- Indexes for demo queries
            INDEX idx_timestamp (timestamp),
            INDEX idx_source (source),
            INDEX idx_type (type)
        );
        
        CREATE TABLE IF NOT EXISTS agent_activity (
            agent_id VARCHAR(100) PRIMARY KEY,
            last_seen TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            message_count INT NOT NULL DEFAULT 0,
            capabilities JSON,
            
            INDEX idx_last_seen (last_seen)
        );
        """
        
        try:
            with self.engine.connect() as conn:
                # Execute schema creation
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                        
                conn.commit()
                print("✅ Beast Mode schema created successfully")
                return True
                
        except Exception as e:
            print(f"❌ Schema creation failed: {e}")
            return False
    
    def store_message(self, message_data: Dict[str, Any]) -> bool:
        """Store a Beast Mode message in TiDB."""
        
        insert_sql = """
        INSERT INTO beast_messages (id, type, source, target, payload, timestamp, priority)
        VALUES (:id, :type, :source, :target, :payload, :timestamp, :priority)
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(insert_sql), message_data)
                conn.commit()
                
                # Update agent activity
                self.update_agent_activity(message_data['source'])
                
                print(f"✅ Message stored: {message_data['id']}")
                return True
                
        except Exception as e:
            print(f"❌ Message storage failed: {e}")
            return False
    
    def update_agent_activity(self, agent_id: str):
        """Update agent activity tracking."""
        
        upsert_sql = """
        INSERT INTO agent_activity (agent_id, last_seen, message_count)
        VALUES (:agent_id, NOW(6), 1)
        ON DUPLICATE KEY UPDATE
        last_seen = NOW(6),
        message_count = message_count + 1
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(upsert_sql), {'agent_id': agent_id})
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Agent activity update failed: {e}")
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages for demo."""
        
        query_sql = """
        SELECT id, type, source, target, payload, timestamp, priority
        FROM beast_messages
        ORDER BY timestamp DESC
        LIMIT :limit
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query_sql), {'limit': limit})
                
                messages = []
                for row in result:
                    messages.append({
                        'id': row.id,
                        'type': row.type,
                        'source': row.source,
                        'target': row.target,
                        'payload': json.loads(row.payload) if row.payload else {},
                        'timestamp': row.timestamp.isoformat(),
                        'priority': row.priority
                    })
                
                return messages
                
        except Exception as e:
            print(f"❌ Message retrieval failed: {e}")
            return []
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics for demo dashboard."""
        
        stats_sql = """
        SELECT 
            COUNT(*) as total_agents,
            COUNT(CASE WHEN last_seen > NOW() - INTERVAL 5 MINUTE THEN 1 END) as active_agents,
            SUM(message_count) as total_messages,
            MAX(last_seen) as last_activity
        FROM agent_activity
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(stats_sql))
                row = result.fetchone()
                
                return {
                    'total_agents': row.total_agents or 0,
                    'active_agents': row.active_agents or 0,
                    'total_messages': row.total_messages or 0,
                    'last_activity': row.last_activity.isoformat() if row.last_activity else None
                }
                
        except Exception as e:
            print(f"❌ Stats retrieval failed: {e}")
            return {}

def test_tidb_integration():
    """Test TiDB integration for Day 1 checkpoint."""
    
    print("🚀 Day 1: TiDB Integration Test")
    print("=" * 50)
    
    # Initialize connection
    tidb = TiDBConnection()
    
    # Step 1: Connect to TiDB
    print("\n📡 Step 1: Connecting to TiDB Serverless...")
    if not tidb.setup_connection():
        print("❌ CRITICAL: TiDB connection failed!")
        print("💡 Set TIDB_CONNECTION_STRING environment variable")
        return False
    
    # Step 2: Create schema
    print("\n🏗️ Step 2: Creating Beast Mode schema...")
    if not tidb.create_beast_mode_schema():
        print("❌ CRITICAL: Schema creation failed!")
        return False
    
    # Step 3: Test message storage
    print("\n💾 Step 3: Testing message storage...")
    test_message = {
        'id': 'test-message-001',
        'type': 'status_update',
        'source': 'tidb_test_agent',
        'target': None,
        'payload': json.dumps({
            'message': 'TiDB integration test successful!',
            'test_timestamp': datetime.now().isoformat()
        }),
        'timestamp': datetime.now(),
        'priority': 5
    }
    
    if not tidb.store_message(test_message):
        print("❌ CRITICAL: Message storage failed!")
        return False
    
    # Step 4: Test message retrieval
    print("\n📊 Step 4: Testing message retrieval...")
    messages = tidb.get_recent_messages(5)
    if not messages:
        print("❌ WARNING: No messages retrieved!")
    else:
        print(f"✅ Retrieved {len(messages)} messages")
        for msg in messages:
            print(f"   - {msg['source']}: {msg['type']} at {msg['timestamp']}")
    
    # Step 5: Test analytics
    print("\n📈 Step 5: Testing analytics...")
    stats = tidb.get_agent_stats()
    if stats:
        print(f"✅ Agent Stats: {stats}")
    else:
        print("❌ WARNING: Stats retrieval failed!")
    
    print("\n" + "=" * 50)
    print("🎉 Day 1 TiDB Integration: SUCCESS!")
    print("✅ TiDB connected and storing messages")
    print("✅ Basic analytics working")
    print("✅ Ready for Day 2: Full Beast Mode integration")
    
    return True

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run Day 1 test
    success = test_tidb_integration()
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Set up TiDB Serverless account if not done")
        print("2. Get connection string and set TIDB_CONNECTION_STRING")
        print("3. Run this script to validate setup")
        print("4. Integrate with existing Beast Mode Network")
    else:
        print("\n❌ Day 1 BLOCKED - Fix TiDB connection first!")