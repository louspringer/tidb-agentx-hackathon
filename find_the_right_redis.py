#!/usr/bin/env python3
"""
Find the RIGHT Redis instance where the other agent is
"""

import redis
import socket
import subprocess
import json

def scan_all_redis_possibilities():
    """Scan every possible Redis configuration."""
    
    print("🔍 FINDING THE RIGHT REDIS INSTANCE")
    print("=" * 50)
    
    # Check what Redis processes are running
    print("1️⃣ Checking running Redis processes...")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        redis_processes = [line for line in result.stdout.split('\n') if 'redis' in line.lower()]
        
        for proc in redis_processes:
            print(f"  📍 {proc}")
            
            # Extract port from process if visible
            if ':' in proc:
                parts = proc.split()
                for part in parts:
                    if ':' in part and any(char.isdigit() for char in part):
                        print(f"    🎯 Possible connection: {part}")
                        
    except Exception as e:
        print(f"  ❌ Process check failed: {e}")
    
    # Check common Redis ports
    print("\n2️⃣ Scanning common Redis ports...")
    common_ports = [6379, 6380, 6381, 6382, 7000, 7001, 7002]
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"  ✅ Port {port} is open")
                
                # Try to connect to Redis on this port
                try:
                    client = redis.Redis(host='localhost', port=port, decode_responses=True, socket_timeout=2)
                    client.ping()
                    
                    # Check for activity
                    info = client.info()
                    keys = client.keys('*')
                    channels = client.pubsub_channels()
                    
                    print(f"    📊 Redis on port {port}:")
                    print(f"      Keys: {len(keys)}")
                    print(f"      Channels: {channels}")
                    print(f"      Connected clients: {info.get('connected_clients', 0)}")
                    print(f"      Commands processed: {info.get('total_commands_processed', 0)}")
                    
                    # Check each database
                    for db in range(16):  # Redis typically has 16 databases
                        try:
                            db_client = redis.Redis(host='localhost', port=port, db=db, decode_responses=True, socket_timeout=1)
                            db_keys = db_client.keys('*')
                            db_channels = db_client.pubsub_channels()
                            
                            if db_keys or db_channels:
                                print(f"      DB {db}: {len(db_keys)} keys, channels: {db_channels}")
                                
                                # Look for Beast Mode specific data
                                beast_keys = [k for k in db_keys if any(word in k.lower() for word in ['beast', 'agent', 'kiro'])]
                                if beast_keys:
                                    print(f"        🎯 Beast Mode keys: {beast_keys}")
                                
                        except:
                            pass  # DB doesn't exist or not accessible
                            
                except Exception as e:
                    print(f"    ❌ Redis connection failed: {e}")
            else:
                print(f"  ❌ Port {port} is closed")
                
        except Exception as e:
            print(f"  ⚠️ Error checking port {port}: {e}")
    
    # Check environment variables that might point to Redis
    print("\n3️⃣ Checking environment variables...")
    redis_env_vars = ['REDIS_URL', 'REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD']
    
    for var in redis_env_vars:
        import os
        value = os.environ.get(var)
        if value:
            print(f"  🔧 {var}={value}")
    
    # Check Docker containers
    print("\n4️⃣ Checking Docker containers...")
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'redis' in result.stdout.lower():
            print("  🐳 Found Redis in Docker:")
            for line in result.stdout.split('\n'):
                if 'redis' in line.lower():
                    print(f"    {line}")
        else:
            print("  📭 No Redis containers found")
    except:
        print("  ⚠️ Docker not available or no containers")
    
    # Check network connections more thoroughly
    print("\n5️⃣ Checking active network connections...")
    try:
        result = subprocess.run(['lsof', '-i', ':6379'], capture_output=True, text=True)
        if result.stdout:
            print("  🌐 Active connections to port 6379:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"    {line}")
    except:
        print("  ⚠️ lsof not available")

if __name__ == "__main__":
    scan_all_redis_possibilities()