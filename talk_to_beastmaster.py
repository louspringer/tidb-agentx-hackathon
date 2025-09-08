#!/usr/bin/env python3
"""
Script to establish a conversation with the beastmaster agent
"""
import redis
import json
import time
import sys
from datetime import datetime

def connect_to_redis():
    """Try to connect to Redis on common ports"""
    ports = [6379, 6380, 6381]
    
    for port in ports:
        try:
            r = redis.Redis(host='localhost', port=port, decode_responses=True)
            r.ping()
            print(f"✓ Connected to Redis on port {port}")
            return r
        except redis.ConnectionError:
            continue
    
    print("✗ Could not connect to Redis on any common port")
    return None

def send_message_to_beastmaster(redis_client, message):
    """Send a direct message to the beastmaster"""
    msg_data = {
        "type": "direct_message",
        "from": "TiDB Master",
        "to": "beastmaster",
        "content": message,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to beastmaster's direct channel
    channel = "agent:beastmaster:direct"
    redis_client.publish(channel, json.dumps(msg_data))
    print(f"📤 Sent message to beastmaster: {message}")

def listen_for_responses(redis_client):
    """Listen for responses from beastmaster"""
    pubsub = redis_client.pubsub()
    
    # Subscribe to our direct channel
    our_channel = "agent:TiDB Master:direct"
    pubsub.subscribe(our_channel)
    
    print(f"👂 Listening for responses on {our_channel}")
    print("Press Ctrl+C to stop listening...")
    
    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    if data.get('from') == 'beastmaster':
                        print(f"\n📥 Response from beastmaster: {data.get('content', 'No content')}")
                        print(f"   Timestamp: {data.get('timestamp', 'Unknown')}")
                except json.JSONDecodeError:
                    print(f"📥 Raw message: {message['data']}")
    except KeyboardInterrupt:
        print("\n👋 Stopped listening")
        pubsub.close()

def main():
    print("🔗 Connecting to Beast Mode Network...")
    
    redis_client = connect_to_redis()
    if not redis_client:
        sys.exit(1)
    
    # Initial greeting to beastmaster
    greeting = "Hello beastmaster! This is TiDB Master. I'd like to establish a conversation with you. Are you available?"
    
    send_message_to_beastmaster(redis_client, greeting)
    
    # Wait a moment then start listening
    time.sleep(1)
    listen_for_responses(redis_client)

if __name__ == "__main__":
    main()