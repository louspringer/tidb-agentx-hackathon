#!/usr/bin/env python3
"""
TiDB Client for Beast Mode Network
Handles TiDB integration with fallback to SQLite for development
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import logging
from dataclasses import dataclass, asdict

try:
    import pymysql
    import sqlalchemy
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    TIDB_AVAILABLE = True
except ImportError:
    TIDB_AVAILABLE = False

@dataclass
class BeastModeMessage:
    """Enhanced message model for TiDB storage."""
    id: str
    type: str
    source: str
    target: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5
    correlation_id: Optional[str] = None
    
    def to_storage_dict(self) -> Dict[str, Any]:
        """Convert to storage format."""
        return {
            'id': self.id,
            'type': self.type,
            'source': self.source,
            'target': self.target,
            'payload': json.dumps(self.payload),
            'timestamp': self.timestamp,
            'priority': self.priority,
            'correlation_id': self.correlation_id
        }

@dataclass
class AgentAnalytics:
    """Agent analytics data model."""
    agent_id: str
    last_seen: datetime
    message_count: int = 0
    capabilities: List[str] = None
    trust_score: float = 0.5
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

class TiDBClient:
    """TiDB client with SQLite fallback for development."""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.connection_string = connection_string or os.getenv('TIDB_CONNECTION_STRING')
        self.engine = None
        self.session_maker = None
        self.sqlite_path = "beast_mode_dev.db"
        self.use_sqlite = False
        
        # Try TiDB first, fallback to SQLite
        if not self._setup_tidb_connection():
            self._setup_sqlite_fallback()
    
    def _setup_tidb_connection(self) -> bool:
        """Set up TiDB connection."""
        if not TIDB_AVAILABLE:
            self.logger.warning("TiDB dependencies not available, using SQLite fallback")
            return False
            
        if not self.connection_string:
            self.logger.warning("No TiDB connection string provided, using SQLite fallback")
            return False
        
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # Set to True for debugging
            )
            
            self.session_maker = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                result.fetchone()
                
            self.logger.info("✅ TiDB connection successful")
            self._create_tidb_schema()
            return True
            
        except Exception as e:
            self.logger.error(f"TiDB connection failed: {e}")
            return False
    
    def _setup_sqlite_fallback(self):
        """Set up SQLite fallback."""
        self.use_sqlite = True
        self.logger.info("Using SQLite fallback for development")
        self._create_sqlite_schema()
    
    def _create_tidb_schema(self):
        """Create TiDB schema optimized for hackathon demo."""
        
        schema_sql = """
        -- Primary message storage with JSON payload
        CREATE TABLE IF NOT EXISTS beast_messages (
            id VARCHAR(36) PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            source VARCHAR(100) NOT NULL,
            target VARCHAR(100),
            payload JSON NOT NULL,
            timestamp TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            priority INT NOT NULL DEFAULT 5,
            correlation_id VARCHAR(36),
            
            -- Indexes for demo queries
            INDEX idx_timestamp (timestamp),
            INDEX idx_source_type (source, type),
            INDEX idx_target (target),
            INDEX idx_correlation (correlation_id)
        ) SHARD_ROW_ID_BITS = 4;
        
        -- Agent activity tracking for analytics
        CREATE TABLE IF NOT EXISTS agent_activity (
            agent_id VARCHAR(100) PRIMARY KEY,
            agent_name VARCHAR(200),
            capabilities JSON,
            last_seen TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            message_count INT NOT NULL DEFAULT 0,
            help_requests_sent INT NOT NULL DEFAULT 0,
            help_requests_received INT NOT NULL DEFAULT 0,
            trust_score DECIMAL(3,2) DEFAULT 0.50,
            status ENUM('online', 'offline', 'busy') DEFAULT 'online',
            
            INDEX idx_last_seen (last_seen),
            INDEX idx_status (status),
            INDEX idx_trust_score (trust_score)
        );
        
        -- Agent collaboration network for demo analytics
        CREATE TABLE IF NOT EXISTS agent_collaborations (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            requester_id VARCHAR(100) NOT NULL,
            helper_id VARCHAR(100) NOT NULL,
            collaboration_type VARCHAR(50) NOT NULL,
            started_at TIMESTAMP(6) NOT NULL,
            completed_at TIMESTAMP(6),
            success BOOLEAN,
            
            INDEX idx_requester (requester_id),
            INDEX idx_helper (helper_id),
            INDEX idx_type_time (collaboration_type, started_at)
        );
        """
        
        try:
            with self.engine.connect() as conn:
                # Execute schema creation
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                        
                conn.commit()
                self.logger.info("✅ TiDB schema created successfully")
                
        except Exception as e:
            self.logger.error(f"TiDB schema creation failed: {e}")
            raise
    
    def _create_sqlite_schema(self):
        """Create SQLite schema compatible with TiDB."""
        
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Drop existing tables to recreate with correct schema
        cursor.execute("DROP TABLE IF EXISTS beast_messages")
        cursor.execute("DROP TABLE IF EXISTS agent_activity")
        cursor.execute("DROP TABLE IF EXISTS agent_collaborations")
        
        # Create beast_messages table (SQLite compatible)
        cursor.execute("""
        CREATE TABLE beast_messages (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            source TEXT NOT NULL,
            target TEXT,
            payload TEXT NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            priority INTEGER NOT NULL DEFAULT 5,
            correlation_id TEXT
        )
        """)
        
        # Create agent_activity table
        cursor.execute("""
        CREATE TABLE agent_activity (
            agent_id TEXT PRIMARY KEY,
            agent_name TEXT,
            capabilities TEXT,
            last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER NOT NULL DEFAULT 0,
            help_requests_sent INTEGER NOT NULL DEFAULT 0,
            help_requests_received INTEGER NOT NULL DEFAULT 0,
            trust_score REAL DEFAULT 0.50,
            status TEXT DEFAULT 'online'
        )
        """)
        
        # Create agent_collaborations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_collaborations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_id TEXT NOT NULL,
            helper_id TEXT NOT NULL,
            collaboration_type TEXT NOT NULL,
            started_at DATETIME NOT NULL,
            completed_at DATETIME,
            success BOOLEAN
        )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON beast_messages (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_type ON beast_messages (source, type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_target ON beast_messages (target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_seen ON agent_activity (last_seen)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_requester ON agent_collaborations (requester_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_helper ON agent_collaborations (helper_id)")
        
        conn.commit()
        conn.close()
        
        self.logger.info("✅ SQLite schema created successfully")
    
    async def store_message(self, message: Union[BeastModeMessage, Dict[str, Any]]) -> bool:
        """Store message in TiDB or SQLite."""
        
        if isinstance(message, dict):
            # Convert dict to BeastModeMessage
            message = BeastModeMessage(**message)
        
        try:
            if self.use_sqlite:
                return self._store_message_sqlite(message)
            else:
                return self._store_message_tidb(message)
                
        except Exception as e:
            self.logger.error(f"Message storage failed: {e}")
            return False
    
    def _store_message_tidb(self, message: BeastModeMessage) -> bool:
        """Store message in TiDB."""
        
        insert_sql = """
        INSERT INTO beast_messages (id, type, source, target, payload, timestamp, priority, correlation_id)
        VALUES (:id, :type, :source, :target, :payload, :timestamp, :priority, :correlation_id)
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(insert_sql), message.to_storage_dict())
                conn.commit()
                
                # Update agent activity
                self._update_agent_activity_tidb(message.source)
                
                self.logger.debug(f"Message stored in TiDB: {message.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"TiDB message storage failed: {e}")
            return False
    
    def _store_message_sqlite(self, message: BeastModeMessage) -> bool:
        """Store message in SQLite."""
        
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            storage_dict = message.to_storage_dict()
            cursor.execute("""
            INSERT INTO beast_messages (id, type, source, target, payload, timestamp, priority, correlation_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                storage_dict['id'],
                storage_dict['type'],
                storage_dict['source'],
                storage_dict['target'],
                storage_dict['payload'],
                storage_dict['timestamp'],
                storage_dict['priority'],
                storage_dict['correlation_id']
            ))
            
            # Update agent activity
            cursor.execute("""
            INSERT OR REPLACE INTO agent_activity (agent_id, last_seen, message_count)
            VALUES (?, ?, COALESCE((SELECT message_count FROM agent_activity WHERE agent_id = ?), 0) + 1)
            """, (message.source, datetime.now(), message.source))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Message stored in SQLite: {message.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"SQLite message storage failed: {e}")
            return False
    
    def _update_agent_activity_tidb(self, agent_id: str):
        """Update agent activity in TiDB."""
        
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
            self.logger.warning(f"Agent activity update failed: {e}")
    
    async def get_recent_messages(self, limit: int = 10, agent_id: Optional[str] = None) -> List[BeastModeMessage]:
        """Get recent messages from storage."""
        
        try:
            if self.use_sqlite:
                return self._get_recent_messages_sqlite(limit, agent_id)
            else:
                return self._get_recent_messages_tidb(limit, agent_id)
                
        except Exception as e:
            self.logger.error(f"Message retrieval failed: {e}")
            return []
    
    def _get_recent_messages_tidb(self, limit: int, agent_id: Optional[str]) -> List[BeastModeMessage]:
        """Get recent messages from TiDB."""
        
        if agent_id:
            query_sql = """
            SELECT id, type, source, target, payload, timestamp, priority, correlation_id
            FROM beast_messages
            WHERE source = :agent_id OR target = :agent_id
            ORDER BY timestamp DESC
            LIMIT :limit
            """
            params = {'agent_id': agent_id, 'limit': limit}
        else:
            query_sql = """
            SELECT id, type, source, target, payload, timestamp, priority, correlation_id
            FROM beast_messages
            ORDER BY timestamp DESC
            LIMIT :limit
            """
            params = {'limit': limit}
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query_sql), params)
                
                messages = []
                for row in result:
                    messages.append(BeastModeMessage(
                        id=row.id,
                        type=row.type,
                        source=row.source,
                        target=row.target,
                        payload=json.loads(row.payload) if row.payload else {},
                        timestamp=row.timestamp,
                        priority=row.priority,
                        correlation_id=row.correlation_id
                    ))
                
                return messages
                
        except Exception as e:
            self.logger.error(f"TiDB message retrieval failed: {e}")
            return []
    
    def _get_recent_messages_sqlite(self, limit: int, agent_id: Optional[str]) -> List[BeastModeMessage]:
        """Get recent messages from SQLite."""
        
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            if agent_id:
                cursor.execute("""
                SELECT id, type, source, target, payload, timestamp, priority, correlation_id
                FROM beast_messages
                WHERE source = ? OR target = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """, (agent_id, agent_id, limit))
            else:
                cursor.execute("""
                SELECT id, type, source, target, payload, timestamp, priority, correlation_id
                FROM beast_messages
                ORDER BY timestamp DESC
                LIMIT ?
                """, (limit,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append(BeastModeMessage(
                    id=row[0],
                    type=row[1],
                    source=row[2],
                    target=row[3],
                    payload=json.loads(row[4]) if row[4] else {},
                    timestamp=datetime.fromisoformat(row[5]) if isinstance(row[5], str) else row[5],
                    priority=row[6],
                    correlation_id=row[7]
                ))
            
            conn.close()
            return messages
            
        except Exception as e:
            self.logger.error(f"SQLite message retrieval failed: {e}")
            return []
    
    async def get_network_analytics(self) -> Dict[str, Any]:
        """Get network analytics for demo dashboard."""
        
        try:
            if self.use_sqlite:
                return self._get_network_analytics_sqlite()
            else:
                return self._get_network_analytics_tidb()
                
        except Exception as e:
            self.logger.error(f"Analytics retrieval failed: {e}")
            return {}
    
    def _get_network_analytics_tidb(self) -> Dict[str, Any]:
        """Get network analytics from TiDB."""
        
        stats_sql = """
        SELECT 
            COUNT(*) as total_agents,
            COUNT(CASE WHEN last_seen > NOW() - INTERVAL 5 MINUTE THEN 1 END) as active_agents,
            SUM(message_count) as total_messages,
            AVG(trust_score) as avg_trust_score,
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
                    'avg_trust_score': float(row.avg_trust_score) if row.avg_trust_score else 0.5,
                    'last_activity': row.last_activity.isoformat() if row.last_activity else None,
                    'storage_type': 'TiDB'
                }
                
        except Exception as e:
            self.logger.error(f"TiDB analytics failed: {e}")
            return {}
    
    def _get_network_analytics_sqlite(self) -> Dict[str, Any]:
        """Get network analytics from SQLite."""
        
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT 
                COUNT(*) as total_agents,
                COUNT(CASE WHEN datetime(last_seen) > datetime('now', '-5 minutes') THEN 1 END) as active_agents,
                SUM(message_count) as total_messages,
                AVG(trust_score) as avg_trust_score,
                MAX(last_seen) as last_activity
            FROM agent_activity
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_agents': row[0] or 0,
                'active_agents': row[1] or 0,
                'total_messages': row[2] or 0,
                'avg_trust_score': row[3] or 0.5,
                'last_activity': row[4],
                'storage_type': 'SQLite (Development)'
            }
            
        except Exception as e:
            self.logger.error(f"SQLite analytics failed: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health."""
        
        try:
            if self.use_sqlite:
                # Test SQLite connection
                conn = sqlite3.connect(self.sqlite_path)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                conn.close()
                
                return {
                    'status': 'healthy',
                    'storage_type': 'SQLite (Development)',
                    'connection': 'ok'
                }
            else:
                # Test TiDB connection
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                
                return {
                    'status': 'healthy',
                    'storage_type': 'TiDB',
                    'connection': 'ok'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'storage_type': 'SQLite' if self.use_sqlite else 'TiDB'
            }

# Global client instance
_tidb_client = None

def get_tidb_client() -> TiDBClient:
    """Get global TiDB client instance."""
    global _tidb_client
    if _tidb_client is None:
        _tidb_client = TiDBClient()
    return _tidb_client