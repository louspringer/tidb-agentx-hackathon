#!/usr/bin/env python3
"""
TiDB Development Fallback - SQLite for immediate development
Allows Day 1 progress while TiDB Serverless is being set up
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

class TiDBDevFallback:
    """SQLite fallback that mimics TiDB interface for development."""
    
    def __init__(self, db_path: str = "beast_mode_dev.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.setup_sqlite_database()
        
    def setup_sqlite_database(self):
        """Create SQLite database with TiDB-compatible schema."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create beast_messages table (SQLite compatible)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS beast_messages (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            source TEXT NOT NULL,
            target TEXT,
            payload TEXT NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            priority INTEGER NOT NULL DEFAULT 5
        )
        """)
        
        # Create agent_activity table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_activity (
            agent_id TEXT PRIMARY KEY,
            last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER NOT NULL DEFAULT 0,
            capabilities TEXT
        )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON beast_messages (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON beast_messages (source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON beast_messages (type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_seen ON agent_activity (last_seen)")
        
        conn.commit()
        conn.close()
        
        print("✅ SQLite development database created")
    
    def store_message(self, message_data: Dict[str, Any]) -> bool:
        """Store message in SQLite (TiDB-compatible interface)."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO beast_messages (id, type, source, target, payload, timestamp, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message_data['id'],
                message_data['type'],
                message_data['source'],
                message_data['target'],
                message_data['payload'],
                message_data['timestamp'],
                message_data['priority']
            ))
            
            # Update agent activity
            cursor.execute("""
            INSERT OR REPLACE INTO agent_activity (agent_id, last_seen, message_count)
            VALUES (?, ?, COALESCE((SELECT message_count FROM agent_activity WHERE agent_id = ?), 0) + 1)
            """, (message_data['source'], datetime.now(), message_data['source']))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Message stored in SQLite: {message_data['id']}")
            return True
            
        except Exception as e:
            print(f"❌ SQLite storage failed: {e}")
            return False
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages from SQLite."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, type, source, target, payload, timestamp, priority
            FROM beast_messages
            ORDER BY timestamp DESC
            LIMIT ?
            """, (limit,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'type': row[1],
                    'source': row[2],
                    'target': row[3],
                    'payload': json.loads(row[4]) if row[4] else {},
                    'timestamp': row[5],
                    'priority': row[6]
                })
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"❌ SQLite retrieval failed: {e}")
            return []
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics from SQLite."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT 
                COUNT(*) as total_agents,
                COUNT(CASE WHEN datetime(last_seen) > datetime('now', '-5 minutes') THEN 1 END) as active_agents,
                SUM(message_count) as total_messages,
                MAX(last_seen) as last_activity
            FROM agent_activity
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_agents': row[0] or 0,
                'active_agents': row[1] or 0,
                'total_messages': row[2] or 0,
                'last_activity': row[3]
            }
            
        except Exception as e:
            print(f"❌ SQLite stats failed: {e}")
            return {}

def test_dev_fallback():
    """Test SQLite fallback for Day 1 development."""
    
    print("🚀 Day 1: TiDB Development Fallback Test")
    print("=" * 50)
    
    # Initialize SQLite fallback
    db = TiDBDevFallback()
    
    # Test message storage
    print("\n💾 Testing message storage...")
    test_message = {
        'id': 'dev-test-001',
        'type': 'status_update',
        'source': 'dev_test_agent',
        'target': None,
        'payload': json.dumps({
            'message': 'SQLite fallback test successful!',
            'test_timestamp': datetime.now().isoformat()
        }),
        'timestamp': datetime.now(),
        'priority': 5
    }
    
    if not db.store_message(test_message):
        print("❌ CRITICAL: SQLite storage failed!")
        return False
    
    # Test message retrieval
    print("\n📊 Testing message retrieval...")
    messages = db.get_recent_messages(5)
    if not messages:
        print("❌ WARNING: No messages retrieved!")
    else:
        print(f"✅ Retrieved {len(messages)} messages")
        for msg in messages:
            print(f"   - {msg['source']}: {msg['type']} at {msg['timestamp']}")
    
    # Test analytics
    print("\n📈 Testing analytics...")
    stats = db.get_agent_stats()
    if stats:
        print(f"✅ Agent Stats: {stats}")
    else:
        print("❌ WARNING: Stats retrieval failed!")
    
    print("\n" + "=" * 50)
    print("🎉 SQLite Development Fallback: SUCCESS!")
    print("✅ Can proceed with Day 1 development")
    print("✅ Ready to integrate with Beast Mode Network")
    print("✅ Will migrate to TiDB when connection is ready")
    
    return True

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run development fallback test
    success = test_dev_fallback()
    
    if success:
        print("\n🚀 DEVELOPMENT READY:")
        print("1. SQLite fallback operational")
        print("2. Can proceed with Beast Mode integration")
        print("3. Easy migration to TiDB when ready")
        print("4. Day 1 progress unblocked!")
    else:
        print("\n❌ Development fallback failed!")