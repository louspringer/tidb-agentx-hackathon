#!/usr/bin/env python3
"""
Full Redis scan to see what's actually there
"""

import redis
import json
from datetime import datetime

def scan_redis():
    """Scan all Redis data to see what's there."""
    try:
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Connected to Redis")
        
        # Get ALL keys
        all_keys = client.keys('*')
        print(f"📊 Total keys in Redis: {len(all_keys)}")
        
        if not all_keys:
            print("📭 Redis is completely empty")
            return
        
        # Categorize keys
        categories = {}
        for key in all_keys:
            prefix = key.split(':')[0] if ':' in key else key.split('_')[0] if '_' in key else 'other'
            if prefix not in categories:
                categories[prefix] = []
            categories[prefix].append(key)
        
        print("\n📂 Keys by category:")
        for category, keys in categories.items():
            print(f"  {category}: {len(keys)} keys")
            for key in keys[:5]:  # Show first 5
                key_type = client.type(key)
                print(f"    - {key} ({key_type})")
            if len(keys) > 5:
                print(f"    ... and {len(keys) - 5} more")
        
        # Check for any message-like patterns
        message_patterns = ['*message*', '*queue*', '*channel*', '*agent*', '*beast*', '*kiro*']
        print("\n🔍 Searching for message-related keys:")
        
        found_any = False
        for pattern in message_patterns:
            matches = client.keys(pattern)
            if matches:
                found_any = True
                print(f"  Pattern '{pattern}': {matches}")
        
        if not found_any:
            print("  No message-related keys found")
        
        # Check Redis info
        info = client.info()
        print(f"\n📈 Redis Info:")
        print(f"  Version: {info.get('redis_version', 'unknown')}")
        print(f"  Connected clients: {info.get('connected_clients', 0)}")
        print(f"  Used memory: {info.get('used_memory_human', 'unknown')}")
        print(f"  Total commands processed: {info.get('total_commands_processed', 0)}")
        
        # Check active channels
        channels = client.pubsub_channels()
        print(f"\n📡 Active pub/sub channels: {len(channels)}")
        for channel in channels:
            subs = client.pubsub_numsub(channel)
            print(f"  {channel}: {subs[0][1] if subs else 0} subscribers")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    scan_redis()