#!/usr/bin/env python3
"""
Beast Mode Network CLI Tool
Proper command-line interface for Beast Mode Network operations
"""

import json
import redis
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class BeastCLI:
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        """Initialize Beast Mode Network CLI."""
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
        except redis.ConnectionError:
            print(f"❌ Failed to connect to Redis at {redis_host}:{redis_port}")
            print("💡 Make sure Redis is running and accessible")
            sys.exit(1)
    
    def post_status(self, 
                   message: str,
                   source: str = "Beast CLI",
                   target: Optional[str] = None,
                   priority: int = 5,
                   task_completed: Optional[str] = None,
                   progress: Optional[str] = None,
                   completion_percentage: Optional[int] = None) -> bool:
        """Post status update to Beast Mode Network."""
        
        payload = {"message": message}
        
        if task_completed:
            payload["task_completed"] = task_completed
        if progress:
            payload["progress"] = progress
        if completion_percentage is not None:
            payload["completion_percentage"] = completion_percentage
        
        status_message = {
            "type": "status_update",
            "source": source,
            "target": target,
            "payload": payload,
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "id": str(uuid.uuid4())
        }
        
        try:
            message_json = json.dumps(status_message)
            self.redis_client.publish("beast_mode_network", message_json)
            print(f"✅ Posted status update to Beast Mode Network")
            return True
        except Exception as e:
            print(f"❌ Failed to post status: {e}")
            return False
    
    def post_collaboration_request(self,
                                 request_type: str,
                                 message: str,
                                 source: str = "Beast CLI",
                                 target: Optional[str] = None,
                                 priority: int = 5) -> bool:
        """Post collaboration request to Beast Mode Network."""
        
        collab_message = {
            "type": "collaboration_request",
            "source": source,
            "target": target,
            "payload": {
                "request_type": request_type,
                "message": message,
                "requester": source
            },
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "id": str(uuid.uuid4())
        }
        
        try:
            message_json = json.dumps(collab_message)
            self.redis_client.publish("beast_mode_network", message_json)
            print(f"✅ Posted collaboration request to Beast Mode Network")
            return True
        except Exception as e:
            print(f"❌ Failed to post collaboration request: {e}")
            return False
    
    def listen_network(self, duration: Optional[int] = None) -> None:
        """Listen to Beast Mode Network messages."""
        
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("beast_mode_network")
        
        print(f"🎧 Listening to Beast Mode Network...")
        if duration:
            print(f"⏱️  Will listen for {duration} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            start_time = datetime.now()
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        timestamp = data.get("timestamp", "unknown")
                        source = data.get("source", "unknown")
                        msg_type = data.get("type", "unknown")
                        payload = data.get("payload", {})
                        
                        print(f"📨 [{timestamp}] {source} ({msg_type})")
                        if "message" in payload:
                            print(f"   {payload['message']}")
                        print()
                        
                    except json.JSONDecodeError:
                        print(f"⚠️  Received invalid JSON: {message['data']}")
                
                # Check duration limit
                if duration:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration:
                        break
                        
        except KeyboardInterrupt:
            print("\n👋 Stopped listening to Beast Mode Network")
        finally:
            pubsub.unsubscribe("beast_mode_network")
            pubsub.close()
    
    def listen_network_json(self, duration: Optional[int] = None) -> None:
        """Listen to Beast Mode Network messages with JSON output for piping."""
        
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("beast_mode_network")
        
        try:
            start_time = datetime.now()
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        # Output each message as a JSON line for easy parsing
                        print(json.dumps(data))
                        sys.stdout.flush()  # Ensure immediate output for pipes
                        
                    except json.JSONDecodeError:
                        error_msg = {
                            "error": "invalid_json",
                            "raw_data": message["data"],
                            "timestamp": datetime.now().isoformat()
                        }
                        print(json.dumps(error_msg))
                        sys.stdout.flush()
                
                # Check duration limit
                if duration:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration:
                        break
                        
        except KeyboardInterrupt:
            pass  # Silent exit for JSON mode
        finally:
            pubsub.unsubscribe("beast_mode_network")
            pubsub.close()
    
    def network_health(self) -> Dict[str, Any]:
        """Check Beast Mode Network health."""
        
        try:
            # Check Redis connection
            redis_info = self.redis_client.info()
            
            # Get network statistics
            pubsub_channels = self.redis_client.pubsub_channels()
            
            health = {
                "redis_connected": True,
                "redis_version": redis_info.get("redis_version", "unknown"),
                "beast_network_active": "beast_mode_network" in pubsub_channels,
                "active_channels": len(pubsub_channels),
                "memory_usage": redis_info.get("used_memory_human", "unknown")
            }
            
            return health
            
        except Exception as e:
            return {
                "redis_connected": False,
                "error": str(e)
            }


def main():
    """Simple command-line interface with streaming support."""
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    # Parse simple command structure
    command = sys.argv[1]
    
    # Default options
    redis_host = "localhost"
    redis_port = 6379
    source = "Beast CLI"
    
    if command == "status":
        # Check if reading from stdin
        if len(sys.argv) < 3 or sys.argv[2] == "-":
            if not sys.stdin.isatty():
                # Reading from pipe/redirect
                message = sys.stdin.read().strip()
            else:
                print("Error: status command requires a message or stdin input")
                print("Usage: beast_cli.py status <message>")
                print("   or: echo 'message' | beast_cli.py status -")
                sys.exit(1)
        else:
            message = sys.argv[2]
        
        # Parse optional arguments
        task_completed = None
        progress = None
        percentage = None
        target = None
        priority = 5
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--task-completed" and i + 1 < len(sys.argv):
                task_completed = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--progress" and i + 1 < len(sys.argv):
                progress = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--percentage" and i + 1 < len(sys.argv):
                percentage = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--source" and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--target" and i + 1 < len(sys.argv):
                target = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        cli = BeastCLI(redis_host=redis_host, redis_port=redis_port)
        
        # Check for JSON output flag
        json_output = "--json" in sys.argv
        
        success = cli.post_status(
            message=message,
            source=source,
            target=target,
            priority=priority,
            task_completed=task_completed,
            progress=progress,
            completion_percentage=percentage
        )
        
        if json_output:
            result = {"success": success, "command": "status", "message": message}
            print(json.dumps(result))
        
        sys.exit(0 if success else 1)
    
    elif command == "collab":
        # Check if reading from stdin
        if len(sys.argv) < 3 or sys.argv[2] == "-":
            if not sys.stdin.isatty():
                # Reading from pipe/redirect
                message = sys.stdin.read().strip()
            else:
                print("Error: collab command requires a message or stdin input")
                print("Usage: beast_cli.py collab <message>")
                print("   or: echo 'message' | beast_cli.py collab -")
                sys.exit(1)
        else:
            message = sys.argv[2]
        request_type = "general"
        target = None
        priority = 5
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--request-type" and i + 1 < len(sys.argv):
                request_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--source" and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--target" and i + 1 < len(sys.argv):
                target = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        cli = BeastCLI(redis_host=redis_host, redis_port=redis_port)
        
        # Check for JSON output flag
        json_output = "--json" in sys.argv
        
        success = cli.post_collaboration_request(
            request_type=request_type,
            message=message,
            source=source,
            target=target,
            priority=priority
        )
        
        if json_output:
            result = {"success": success, "command": "collab", "message": message}
            print(json.dumps(result))
        
        sys.exit(0 if success else 1)
    
    elif command == "listen":
        duration = None
        json_output = "--json" in sys.argv
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--duration" and i + 1 < len(sys.argv):
                duration = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        cli = BeastCLI(redis_host=redis_host, redis_port=redis_port)
        if json_output:
            cli.listen_network_json(duration=duration)
        else:
            cli.listen_network(duration=duration)
    
    elif command == "health":
        cli = BeastCLI(redis_host=redis_host, redis_port=redis_port)
        health = cli.network_health()
        
        if health.get("redis_connected"):
            print("✅ Beast Mode Network Health Check")
            print(f"   Redis Version: {health['redis_version']}")
            print(f"   Network Active: {'✅' if health['beast_network_active'] else '❌'}")
            print(f"   Active Channels: {health['active_channels']}")
            print(f"   Memory Usage: {health['memory_usage']}")
        else:
            print("❌ Beast Mode Network Health Check Failed")
            print(f"   Error: {health.get('error', 'Unknown error')}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print_help()
        sys.exit(1)


def print_help():
    """Print help message."""
    print("""Beast Mode Network CLI Tool

Usage:
  beast_cli.py status <message|-> [options]
  beast_cli.py collab <message|-> [options]  
  beast_cli.py listen [options]
  beast_cli.py health

Commands:
  status    Post status update to network
  collab    Post collaboration request
  listen    Listen to network messages
  health    Check network health

Global Options:
  --json                    Output JSON for piping

Status Options:
  --source <name>           Source identifier
  --task-completed <task>   Completed task name
  --progress <desc>         Progress description
  --percentage <0-100>      Completion percentage
  --target <agent>          Target agent
  --priority <1-10>         Message priority

Collab Options:
  --source <name>           Source identifier
  --request-type <type>     Request type
  --target <agent>          Target agent
  --priority <1-10>         Message priority

Listen Options:
  --duration <seconds>      Listen duration
  --json                    Output JSON lines for piping

Streaming Examples:
  # Pipe message from stdin
  echo "Task completed" | beast_cli.py status -
  
  # JSON output for processing
  beast_cli.py status "Done" --json | jq .success
  
  # Listen and filter with jq
  beast_cli.py listen --json | jq 'select(.type=="status_update")'
  
  # Chain commands
  echo "Need help debugging" | beast_cli.py collab - --request-type "assistance" --json

Basic Examples:
  beast_cli.py status "Task completed"
  beast_cli.py status "Working on X" --progress "50% done" --percentage 50
  beast_cli.py collab "Need help" --request-type "assistance"
  beast_cli.py listen --duration 30
  beast_cli.py health
""")


if __name__ == "__main__":
    main()