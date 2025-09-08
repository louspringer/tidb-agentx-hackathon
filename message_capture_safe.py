#!/usr/bin/env python3
"""
SAFE Message Capture for Live Beast Mode Agent Network
- Captures ALL messages without consuming/deleting them
- Saves everything to persistent storage
- Non-destructive monitoring only
"""

import asyncio
import json
import redis
import time
from datetime import datetime
from pathlib import Path

# Create safe storage directory
STORAGE_DIR = Path("captured_messages")
STORAGE_DIR.mkdir(exist_ok=True)

class SafeMessageCapture:
    """Safe, non-destructive message capture system."""
    
    def __init__(self):
        self.redis_client = None
        self.captured_messages = []
        self.session_id = f"capture_{int(time.time())}"
        
    async def connect_safely(self):
        """Connect to Redis in read-only monitoring mode."""
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            print("✅ Connected to Redis safely")
            return True
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return False
    
    async def capture_existing_messages(self):
        """Capture any existing messages in queues/channels."""
        print("🔍 Scanning for existing messages...")
        
        # Check for Beast Mode channels
        channels_to_check = [
            "beast_mode_network",
            "beast_mode_network_*",
            "agent_*",
            "help_*"
        ]
        
        existing_data = {}
        
        try:
            # Get all keys matching patterns
            for pattern in ["beast_mode*", "agent*", "help*", "message*"]:
                keys = self.redis_client.keys(pattern)
                for key in keys:
                    try:
                        key_type = self.redis_client.type(key)
                        if key_type == 'string':
                            value = self.redis_client.get(key)
                        elif key_type == 'list':
                            value = self.redis_client.lrange(key, 0, -1)
                        elif key_type == 'hash':
                            value = self.redis_client.hgetall(key)
                        elif key_type == 'set':
                            value = list(self.redis_client.smembers(key))
                        else:
                            value = f"Type: {key_type}"
                        
                        existing_data[key] = {
                            "type": key_type,
                            "value": value,
                            "captured_at": datetime.now().isoformat()
                        }
                        
                    except Exception as e:
                        existing_data[key] = {"error": str(e)}
            
            # Save existing data
            if existing_data:
                filename = STORAGE_DIR / f"existing_data_{self.session_id}.json"
                with open(filename, 'w') as f:
                    json.dump(existing_data, f, indent=2, default=str)
                print(f"💾 Saved {len(existing_data)} existing keys to {filename}")
            else:
                print("📭 No existing Beast Mode data found")
                
        except Exception as e:
            print(f"⚠️ Error scanning existing data: {e}")
    
    async def start_live_monitoring(self, duration_seconds=30):
        """Start live message monitoring without consuming."""
        print(f"🎧 Starting live monitoring for {duration_seconds} seconds...")
        
        try:
            # Create pubsub for monitoring
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to Beast Mode channels
            channels = ["beast_mode_network", "beast_mode_*"]
            for channel in channels:
                try:
                    pubsub.psubscribe(channel)
                    print(f"📡 Monitoring channel: {channel}")
                except Exception as e:
                    print(f"⚠️ Could not subscribe to {channel}: {e}")
            
            # Monitor for specified duration
            start_time = time.time()
            message_count = 0
            
            while (time.time() - start_time) < duration_seconds:
                try:
                    message = pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'pmessage':
                        message_count += 1
                        
                        # Safe message capture
                        captured_msg = {
                            "message_id": message_count,
                            "channel": message['channel'],
                            "pattern": message['pattern'],
                            "data": message['data'],
                            "captured_at": datetime.now().isoformat(),
                            "session_id": self.session_id
                        }
                        
                        self.captured_messages.append(captured_msg)
                        print(f"📨 Message {message_count}: {message['channel']} -> {str(message['data'])[:100]}...")
                        
                        # Save immediately (don't lose anything!)
                        self.save_messages()
                        
                except Exception as e:
                    print(f"⚠️ Error receiving message: {e}")
                    continue
            
            pubsub.close()
            print(f"✅ Monitoring complete. Captured {message_count} messages")
            
        except Exception as e:
            print(f"❌ Error in live monitoring: {e}")
    
    def save_messages(self):
        """Save captured messages immediately."""
        if self.captured_messages:
            filename = STORAGE_DIR / f"live_messages_{self.session_id}.json"
            with open(filename, 'w') as f:
                json.dump(self.captured_messages, f, indent=2, default=str)
    
    def get_summary(self):
        """Get summary of captured data."""
        return {
            "session_id": self.session_id,
            "total_messages": len(self.captured_messages),
            "storage_directory": str(STORAGE_DIR),
            "files_created": list(STORAGE_DIR.glob(f"*{self.session_id}*"))
        }

async def main():
    """Main safe capture function."""
    print("🚨 SAFE MESSAGE CAPTURE - LIVE SYSTEM")
    print("=" * 50)
    print("⚠️  NON-DESTRUCTIVE MONITORING ONLY")
    print("💾 ALL MESSAGES WILL BE SAVED")
    print("=" * 50)
    
    capture = SafeMessageCapture()
    
    # Step 1: Connect safely
    if not await capture.connect_safely():
        print("❌ Cannot connect to Redis - system may not be running")
        return
    
    # Step 2: Capture existing data
    await capture.capture_existing_messages()
    
    # Step 3: Monitor live messages
    await capture.start_live_monitoring(duration_seconds=30)
    
    # Step 4: Final save and summary
    capture.save_messages()
    summary = capture.get_summary()
    
    print("\n📊 CAPTURE SUMMARY:")
    print(f"Session ID: {summary['session_id']}")
    print(f"Messages captured: {summary['total_messages']}")
    print(f"Storage: {summary['storage_directory']}")
    print(f"Files: {[f.name for f in summary['files_created']]}")
    
    return summary

if __name__ == "__main__":
    asyncio.run(main())