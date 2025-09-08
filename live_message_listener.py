#!/usr/bin/env python3
"""
Live Message Listener - Catch messages from the other agent!
"""

import asyncio
import redis
import json
import time
from datetime import datetime

class LiveMessageListener:
    """Listen for live messages and save everything."""
    
    def __init__(self):
        self.redis_client = None
        self.messages_received = []
        self.session_start = datetime.now()
        
    async def connect_and_listen(self):
        """Connect and start listening for messages."""
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            print("✅ Connected to Redis")
            
            # Create pubsub
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to the active channel
            pubsub.subscribe('beast_mode_network')
            print("📡 Subscribed to beast_mode_network channel")
            print("🎧 Listening for messages... (Press Ctrl+C to stop)")
            print("=" * 60)
            
            message_count = 0
            
            # Listen indefinitely
            for message in pubsub.listen():
                if message['type'] == 'message':
                    message_count += 1
                    timestamp = datetime.now()
                    
                    print(f"\n📨 MESSAGE #{message_count} at {timestamp.strftime('%H:%M:%S')}")
                    print(f"Channel: {message['channel']}")
                    print(f"Data: {message['data']}")
                    
                    # Try to parse as JSON for better display
                    try:
                        parsed_data = json.loads(message['data'])
                        print("📋 Parsed JSON:")
                        print(json.dumps(parsed_data, indent=2))
                    except:
                        print("📝 Raw data (not JSON)")
                    
                    # Save message
                    saved_message = {
                        "message_number": message_count,
                        "timestamp": timestamp.isoformat(),
                        "channel": message['channel'],
                        "data": message['data'],
                        "session_start": self.session_start.isoformat()
                    }
                    
                    self.messages_received.append(saved_message)
                    
                    # Save to file immediately (don't lose anything!)
                    self.save_messages()
                    
                    print("-" * 60)
                
                elif message['type'] == 'subscribe':
                    print(f"✅ Successfully subscribed to {message['channel']}")
            
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped listening. Captured {len(self.messages_received)} messages")
            self.save_messages()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
    def save_messages(self):
        """Save all captured messages to file."""
        if self.messages_received:
            filename = f"captured_messages_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump({
                    "session_info": {
                        "start_time": self.session_start.isoformat(),
                        "total_messages": len(self.messages_received)
                    },
                    "messages": self.messages_received
                }, f, indent=2)
            print(f"💾 Saved {len(self.messages_received)} messages to {filename}")

async def main():
    """Main listener function."""
    print("🎧 LIVE MESSAGE LISTENER")
    print("=" * 30)
    print("Connecting to the Beast Mode network...")
    print("The other agent is out there - let's hear what it's saying!")
    print()
    
    listener = LiveMessageListener()
    await listener.connect_and_listen()

if __name__ == "__main__":
    asyncio.run(main())