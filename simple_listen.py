#!/usr/bin/env python3
"""
Simple direct Redis pubsub listener - no fancy stuff
"""

import redis
import json
from datetime import datetime

def simple_listen():
    """Just listen to the damn channel."""
    
    print("🎧 SIMPLE REDIS LISTENER")
    print("Connecting to localhost:6379...")
    
    # Direct Redis connection
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Test connection
    r.ping()
    print("✅ Connected!")
    
    # Get pubsub
    pubsub = r.pubsub()
    
    # Subscribe to the channel we know exists
    pubsub.subscribe('beast_mode_network')
    print("📡 Subscribed to beast_mode_network")
    print("👂 Listening... (Ctrl+C to stop)")
    print("=" * 50)
    
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"\n[{timestamp}] 📨 MESSAGE RECEIVED!")
                print(f"Channel: {message['channel']}")
                print(f"Data: {message['data']}")
                
                # Try to parse JSON
                try:
                    parsed = json.loads(message['data'])
                    print("Parsed JSON:")
                    print(json.dumps(parsed, indent=2))
                except:
                    print("(Raw text, not JSON)")
                
                print("-" * 50)
                
            elif message['type'] == 'subscribe':
                print(f"✅ Subscribed to {message['channel']}")
                
    except KeyboardInterrupt:
        print("\n🛑 Stopped listening")
    finally:
        pubsub.close()

if __name__ == "__main__":
    simple_listen()