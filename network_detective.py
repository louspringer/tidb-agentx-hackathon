#!/usr/bin/env python3
"""
Network Detective - Find the other agent!
"""

import redis
import json
import time
from datetime import datetime

def investigate_network():
    """Investigate where the other agent might be."""
    
    print("🕵️ NETWORK DETECTIVE - Finding the other agent")
    print("=" * 50)
    
    # Check different Redis configurations
    redis_configs = [
        {"host": "localhost", "port": 6379, "db": 0},
        {"host": "localhost", "port": 6379, "db": 1},
        {"host": "127.0.0.1", "port": 6379, "db": 0},
        {"host": "localhost", "port": 6380, "db": 0},  # Alternative port
        {"host": "redis", "port": 6379, "db": 0},      # Docker name
    ]
    
    for i, config in enumerate(redis_configs):
        print(f"\n🔍 Checking Redis config {i+1}: {config}")
        try:
            client = redis.Redis(**config, decode_responses=True, socket_timeout=2)
            client.ping()
            
            # Check for keys
            keys = client.keys('*')
            print(f"  ✅ Connected! Found {len(keys)} keys")
            
            if keys:
                print(f"  📋 Sample keys: {keys[:10]}")
                
                # Look for agent-like data
                for key in keys:
                    if any(word in key.lower() for word in ['agent', 'beast', 'kiro', 'message', 'network']):
                        key_type = client.type(key)
                        print(f"  🎯 Interesting key: {key} ({key_type})")
                        
                        # Try to peek at the data
                        try:
                            if key_type == 'string':
                                value = client.get(key)
                                print(f"    Value: {str(value)[:100]}...")
                            elif key_type == 'hash':
                                fields = client.hgetall(key)
                                print(f"    Fields: {list(fields.keys())}")
                        except Exception as e:
                            print(f"    Error reading: {e}")
            
            # Check active pub/sub
            channels = client.pubsub_channels()
            if channels:
                print(f"  📡 Active channels: {channels}")
                for channel in channels:
                    subs = client.pubsub_numsub(channel)
                    print(f"    {channel}: {subs[0][1] if subs else 0} subscribers")
            
            # Check Redis info for activity
            info = client.info()
            commands = info.get('total_commands_processed', 0)
            clients = info.get('connected_clients', 0)
            print(f"  📊 Commands processed: {commands}, Connected clients: {clients}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    # Also check if there are any Beast Mode processes running
    print(f"\n🔍 Checking for Beast Mode processes...")
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        beast_processes = [line for line in lines if any(word in line.lower() for word in ['beast', 'agent', 'kiro', 'redis'])]
        
        if beast_processes:
            print("  🎯 Found relevant processes:")
            for proc in beast_processes[:10]:  # Show first 10
                print(f"    {proc}")
        else:
            print("  📭 No Beast Mode processes found")
            
    except Exception as e:
        print(f"  ⚠️ Process check failed: {e}")
    
    # Check network connections
    print(f"\n🔍 Checking network connections to Redis...")
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        redis_connections = [line for line in lines if '6379' in line or '6380' in line]
        
        if redis_connections:
            print("  🌐 Redis connections found:")
            for conn in redis_connections:
                print(f"    {conn}")
        else:
            print("  📭 No Redis connections visible")
            
    except Exception as e:
        print(f"  ⚠️ Network check failed: {e}")

if __name__ == "__main__":
    investigate_network()