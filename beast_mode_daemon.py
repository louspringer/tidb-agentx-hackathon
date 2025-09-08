#!/usr/bin/env python3
"""
Beast Mode Message Capture Daemon - Singleton per user
Continuously captures messages with proper daemon behavior
"""

import os
import sys
import time
import json
import redis
import fcntl
import signal
import atexit
from datetime import datetime
from pathlib import Path

class BeastModeDaemon:
    """Singleton daemon for Beast Mode message capture."""
    
    def __init__(self):
        # Standard daemon PID file approach
        self.pidfile = '/tmp/beast_mode_daemon.pid'
        self.lockfile = '/tmp/beast_mode_daemon.lock'
        self.redis_client = None
        self.running = True
        self.message_count = 0
        
    def daemonize(self):
        """Daemonize the process."""
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit parent
        except OSError as e:
            sys.stderr.write(f"Fork #1 failed: {e}\n")
            sys.exit(1)
            
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit second parent
        except OSError as e:
            sys.stderr.write(f"Fork #2 failed: {e}\n")
            sys.exit(1)
            
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open('/dev/null', 'r')
        so = open('/tmp/beast_mode_daemon.log', 'a+')
        se = open('/tmp/beast_mode_daemon.log', 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
    def create_pidfile(self):
        """Create PID file with singleton protection."""
        try:
            # Try to acquire exclusive lock
            self.lockfd = open(self.lockfile, 'w')
            fcntl.flock(self.lockfd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write PID
            pid = str(os.getpid())
            with open(self.pidfile, 'w') as f:
                f.write(pid + '\n')
                
            atexit.register(self.cleanup)
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)
            
            print(f"Beast Mode Daemon started with PID: {pid}")
            return True
            
        except (IOError, OSError):
            print("Beast Mode Daemon already running!")
            return False
            
    def cleanup(self):
        """Clean up PID and lock files."""
        try:
            os.remove(self.pidfile)
            os.remove(self.lockfile)
        except:
            pass
            
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"Received signal {signum}, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
        
    def connect_redis(self):
        """Connect to Redis with retry logic."""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                self.redis_client.ping()
                print("Connected to Redis successfully")
                return True
                
            except Exception as e:
                print(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    
        print("Failed to connect to Redis after all retries")
        return False
        
    def capture_messages(self):
        """Continuously capture messages."""
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.psubscribe("beast_mode_network")
            pubsub.psubscribe("agent:*")
            
            print("Started message capture - listening for Beast Mode messages...")
            
            while self.running:
                try:
                    message = pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'pmessage':
                        self.message_count += 1
                        
                        # Create timestamped filename
                        timestamp = int(time.time())
                        filename = f"captured_messages_{timestamp}.json"
                        
                        # Load existing data or create new
                        try:
                            with open(filename, 'r') as f:
                                data = json.load(f)
                        except FileNotFoundError:
                            data = {
                                "session_info": {
                                    "start_time": datetime.now().isoformat(),
                                    "total_messages": 0
                                },
                                "messages": []
                            }
                        
                        # Add new message
                        msg_entry = {
                            "message_number": self.message_count,
                            "timestamp": datetime.now().isoformat(),
                            "channel": message['channel'],
                            "data": message['data'],
                            "session_start": data["session_info"]["start_time"]
                        }
                        
                        data["messages"].append(msg_entry)
                        data["session_info"]["total_messages"] = len(data["messages"])
                        
                        # Save immediately
                        with open(filename, 'w') as f:
                            json.dump(data, f, indent=2)
                            
                        print(f"Captured message {self.message_count}: {message['channel']}")
                        
                except Exception as e:
                    print(f"Error capturing message: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Error in message capture loop: {e}")
            
    def run(self):
        """Main daemon run loop."""
        if not self.create_pidfile():
            return False
            
        if not self.connect_redis():
            return False
            
        print("Beast Mode Daemon running - capturing messages continuously...")
        self.capture_messages()
        
        return True
        
    def start(self):
        """Start the daemon."""
        self.daemonize()
        self.run()
        
    def stop(self):
        """Stop the daemon safely using PID file."""
        try:
            with open(self.pidfile, 'r') as f:
                pid = int(f.read().strip())
            
            # Verify it's actually our process before killing
            try:
                os.kill(pid, 0)  # Check if process exists
                # Send SIGTERM for graceful shutdown
                os.kill(pid, signal.SIGTERM)
                
                # Wait a bit for graceful shutdown
                time.sleep(2)
                
                # Check if still running, force kill if needed
                try:
                    os.kill(pid, 0)
                    print(f"Process {pid} still running, force killing...")
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already gone
                    
                print(f"Beast Mode Daemon (PID {pid}) stopped")
                
            except ProcessLookupError:
                print(f"Process {pid} not found, cleaning up stale PID file")
                self.cleanup()
                
        except FileNotFoundError:
            print("Beast Mode Daemon not running (no PID file)")
        except Exception as e:
            print(f"Error stopping daemon: {e}")
            
    def status(self):
        """Check daemon status."""
        try:
            with open(self.pidfile, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if process exists
            print(f"Beast Mode Daemon running with PID: {pid}")
            return True
        except (FileNotFoundError, ProcessLookupError):
            print("Beast Mode Daemon not running")
            return False

def main():
    daemon = BeastModeDaemon()
    
    if len(sys.argv) == 2:
        if sys.argv[1] == 'start':
            daemon.start()
        elif sys.argv[1] == 'stop':
            daemon.stop()
        elif sys.argv[1] == 'restart':
            daemon.stop()
            time.sleep(1)
            daemon.start()
        elif sys.argv[1] == 'status':
            daemon.status()
        else:
            print("Usage: python3 beast_mode_daemon.py {start|stop|restart|status}")
    else:
        print("Usage: python3 beast_mode_daemon.py {start|stop|restart|status}")

if __name__ == "__main__":
    main()