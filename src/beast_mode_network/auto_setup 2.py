"""
Auto Setup System and Spore Extraction for Beast Mode Agent Network.

This module provides automated setup, dependency verification, spore extraction,
and system demonstration capabilities for easy deployment and testing.
"""

import asyncio
import logging
import os
import sys
import json
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from .auto_agent import AutoAgent, AutoAgentConfig, AgentPersonality, run_agent_demonstration
from .bus_client import create_bus_client
from .message_models import MessageType


@dataclass
class SporeConfig:
    """Configuration for spore extraction and deployment."""
    
    # Source information
    source_directory: str = ""
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    
    # Target information
    target_directory: str = ""
    spore_name: str = "beast_mode_network_spore"
    
    # Dependencies
    python_requirements: List[str] = None
    system_requirements: List[str] = None
    
    # Configuration
    include_examples: bool = True
    include_tests: bool = False
    include_documentation: bool = True
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if self.include_patterns is None:
            self.include_patterns = [
                "*.py",
                "*.md",
                "*.txt",
                "*.json",
                "*.yaml",
                "*.yml"
            ]
        
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "__pycache__",
                "*.pyc",
                "*.pyo",
                ".git",
                ".pytest_cache",
                "*.log"
            ]
        
        if self.python_requirements is None:
            self.python_requirements = [
                "redis>=4.0.0",
                "asyncio-mqtt>=0.11.0",
                "pydantic>=1.8.0"
            ]
        
        if self.system_requirements is None:
            self.system_requirements = [
                "redis-server"
            ]


class SystemChecker:
    """System dependency checker and validator."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.check_results: Dict[str, Any] = {}
    
    async def check_all_dependencies(self) -> Dict[str, Any]:
        """
        Check all system dependencies.
        
        Returns:
            Dictionary containing check results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "python": await self._check_python(),
            "redis": await self._check_redis(),
            "network": await self._check_network(),
            "permissions": await self._check_permissions(),
            "overall_status": "unknown"
        }
        
        # Determine overall status
        critical_checks = ["python", "redis"]
        all_critical_passed = all(
            results[check]["status"] == "ok" 
            for check in critical_checks
        )
        
        if all_critical_passed:
            results["overall_status"] = "ready"
        else:
            results["overall_status"] = "not_ready"
        
        self.check_results = results
        return results
    
    async def _check_python(self) -> Dict[str, Any]:
        """Check Python installation and version."""
        try:
            version = sys.version_info
            
            result = {
                "status": "ok",
                "version": f"{version.major}.{version.minor}.{version.micro}",
                "executable": sys.executable,
                "issues": []
            }
            
            # Check minimum version (3.7+)
            if version < (3, 7):
                result["status"] = "error"
                result["issues"].append(f"Python 3.7+ required, found {version.major}.{version.minor}")
            
            # Check for asyncio support
            try:
                import asyncio
                result["asyncio_available"] = True
            except ImportError:
                result["status"] = "error"
                result["issues"].append("asyncio not available")
                result["asyncio_available"] = False
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": ["Failed to check Python installation"]
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis availability and connectivity."""
        try:
            # Try to import redis
            try:
                import redis
                redis_available = True
            except ImportError:
                return {
                    "status": "error",
                    "error": "redis package not installed",
                    "issues": ["Install redis package: pip install redis>=4.0.0"]
                }
            
            # Try to connect to Redis
            try:
                client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                client.ping()
                
                # Get Redis info
                info = client.info()
                
                return {
                    "status": "ok",
                    "version": info.get("redis_version", "unknown"),
                    "host": "localhost",
                    "port": 6379,
                    "connected": True,
                    "memory_usage": info.get("used_memory_human", "unknown"),
                    "uptime": info.get("uptime_in_seconds", 0)
                }
                
            except redis.ConnectionError:
                return {
                    "status": "warning",
                    "connected": False,
                    "issues": [
                        "Cannot connect to Redis server",
                        "Make sure Redis is running: redis-server",
                        "Or install Redis: apt-get install redis-server (Ubuntu) or brew install redis (macOS)"
                    ]
                }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": ["Failed to check Redis"]
            }
    
    async def _check_network(self) -> Dict[str, Any]:
        """Check network connectivity and ports."""
        try:
            import socket
            
            result = {
                "status": "ok",
                "localhost_available": True,
                "redis_port_available": False,
                "issues": []
            }
            
            # Check if Redis port is available
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result_code = sock.connect_ex(('localhost', 6379))
                sock.close()
                
                if result_code == 0:
                    result["redis_port_available"] = True
                else:
                    result["issues"].append("Redis port 6379 not accessible")
                    
            except Exception as e:
                result["issues"].append(f"Network check failed: {e}")
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": ["Failed to check network"]
            }
    
    async def _check_permissions(self) -> Dict[str, Any]:
        """Check file system permissions."""
        try:
            result = {
                "status": "ok",
                "can_write_temp": False,
                "can_create_files": False,
                "issues": []
            }
            
            # Check temp directory write access
            try:
                with tempfile.NamedTemporaryFile(delete=True) as tmp:
                    tmp.write(b"test")
                result["can_write_temp"] = True
            except Exception:
                result["issues"].append("Cannot write to temp directory")
            
            # Check current directory write access
            try:
                test_file = "beast_mode_test_file.tmp"
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                result["can_create_files"] = True
            except Exception:
                result["issues"].append("Cannot create files in current directory")
            
            if result["issues"]:
                result["status"] = "warning"
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": ["Failed to check permissions"]
            }


class SporeExtractor:
    """Spore extraction system for creating deployable packages."""
    
    def __init__(self, config: SporeConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def extract_spore(self) -> Dict[str, Any]:
        """
        Extract a spore (deployable package) from the source code.
        
        Returns:
            Dictionary containing extraction results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "spore_name": self.config.spore_name,
            "source_directory": self.config.source_directory,
            "target_directory": self.config.target_directory,
            "files_copied": 0,
            "total_size": 0,
            "success": False,
            "files": []
        }
        
        try:
            # Create target directory
            target_path = Path(self.config.target_directory)
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy source files
            source_path = Path(self.config.source_directory)
            if not source_path.exists():
                raise FileNotFoundError(f"Source directory not found: {self.config.source_directory}")
            
            copied_files = await self._copy_files(source_path, target_path)
            results["files"] = copied_files
            results["files_copied"] = len(copied_files)
            
            # Calculate total size
            total_size = sum(
                os.path.getsize(target_path / file_info["relative_path"])
                for file_info in copied_files
            )
            results["total_size"] = total_size
            
            # Create spore metadata
            await self._create_spore_metadata(target_path, results)
            
            # Create setup script
            await self._create_setup_script(target_path)
            
            # Create requirements file
            await self._create_requirements_file(target_path)
            
            # Create README
            await self._create_readme(target_path)
            
            results["success"] = True
            self.logger.info(f"Spore extracted successfully: {self.config.spore_name}")
            
        except Exception as e:
            results["error"] = str(e)
            self.logger.error(f"Failed to extract spore: {e}")
        
        return results
    
    async def _copy_files(self, source_path: Path, target_path: Path) -> List[Dict[str, Any]]:
        """Copy files from source to target based on patterns."""
        copied_files = []
        
        for root, dirs, files in os.walk(source_path):
            # Filter directories
            dirs[:] = [d for d in dirs if not self._should_exclude_path(d)]
            
            for file in files:
                if self._should_include_file(file):
                    source_file = Path(root) / file
                    relative_path = source_file.relative_to(source_path)
                    target_file = target_path / relative_path
                    
                    # Create target directory if needed
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(source_file, target_file)
                    
                    file_info = {
                        "relative_path": str(relative_path),
                        "size": source_file.stat().st_size,
                        "modified": datetime.fromtimestamp(source_file.stat().st_mtime).isoformat()
                    }
                    copied_files.append(file_info)
        
        return copied_files
    
    def _should_include_file(self, filename: str) -> bool:
        """Check if file should be included based on patterns."""
        # Check exclude patterns first
        for pattern in self.config.exclude_patterns:
            if self._matches_pattern(filename, pattern):
                return False
        
        # Check include patterns
        for pattern in self.config.include_patterns:
            if self._matches_pattern(filename, pattern):
                return True
        
        return False
    
    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded."""
        for pattern in self.config.exclude_patterns:
            if pattern in path or self._matches_pattern(path, pattern):
                return True
        return False
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Simple pattern matching (supports * wildcard)."""
        if '*' not in pattern:
            return pattern in text
        
        # Simple wildcard matching
        parts = pattern.split('*')
        if len(parts) == 2:
            return text.startswith(parts[0]) and text.endswith(parts[1])
        
        return pattern in text
    
    async def _create_spore_metadata(self, target_path: Path, results: Dict[str, Any]) -> None:
        """Create spore metadata file."""
        metadata = {
            "spore_name": self.config.spore_name,
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "description": "Beast Mode Agent Network Spore",
            "python_requirements": self.config.python_requirements,
            "system_requirements": self.config.system_requirements,
            "extraction_results": results,
            "entry_points": {
                "main": "beast_mode_network.auto_setup:main",
                "demo": "beast_mode_network.auto_setup:run_demo",
                "check": "beast_mode_network.auto_setup:check_system"
            }
        }
        
        metadata_file = target_path / "spore_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    async def _create_setup_script(self, target_path: Path) -> None:
        """Create setup script for the spore."""
        setup_script = '''#!/usr/bin/env python3
"""
Beast Mode Agent Network Spore Setup Script
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from beast_mode_network.auto_setup import AutoSetup

async def main():
    """Main setup function."""
    setup = AutoSetup()
    
    print("Beast Mode Agent Network Spore Setup")
    print("=" * 40)
    
    # Check system
    print("Checking system dependencies...")
    check_results = await setup.check_system()
    
    if check_results["overall_status"] != "ready":
        print("System not ready. Please address the following issues:")
        for component, result in check_results.items():
            if isinstance(result, dict) and result.get("issues"):
                print(f"\\n{component.upper()}:")
                for issue in result["issues"]:
                    print(f"  - {issue}")
        return False
    
    print("System check passed!")
    
    # Run demonstration
    print("\\nRunning system demonstration...")
    demo_results = await setup.run_demonstration()
    
    if demo_results["success"]:
        print("Demonstration completed successfully!")
        print(f"Agents created: {demo_results['num_agents']}")
        print(f"Duration: {demo_results['duration_minutes']} minutes")
    else:
        print(f"Demonstration failed: {demo_results.get('error', 'Unknown error')}")
        return False
    
    print("\\nBeast Mode Agent Network is ready to use!")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
'''
        
        setup_file = target_path / "setup.py"
        with open(setup_file, 'w') as f:
            f.write(setup_script)
        
        # Make executable
        os.chmod(setup_file, 0o755)
    
    async def _create_requirements_file(self, target_path: Path) -> None:
        """Create requirements.txt file."""
        requirements_file = target_path / "requirements.txt"
        with open(requirements_file, 'w') as f:
            for req in self.config.python_requirements:
                f.write(f"{req}\\n")
    
    async def _create_readme(self, target_path: Path) -> None:
        """Create README file for the spore."""
        readme_content = f'''# {self.config.spore_name}

Beast Mode Agent Network Spore - A deployable package for the distributed agent collaboration system.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Redis server:
   ```bash
   redis-server
   ```

3. Run setup and demonstration:
   ```bash
   python setup.py
   ```

## System Requirements

### Python Requirements
{chr(10).join(f"- {req}" for req in self.config.python_requirements)}

### System Requirements
{chr(10).join(f"- {req}" for req in self.config.system_requirements)}

## Usage

### Basic Usage
```python
from beast_mode_network import create_bus_client

# Create and connect a client
client = await create_bus_client(
    agent_id="my_agent",
    capabilities=["general", "helpful"]
)

# Send a message
await client.send_simple_message("Hello, network!")

# Discover other agents
agents = await client.discover_agents()

# Request help
request_id = await client.request_help(
    required_capabilities=["python"],
    description="Need help with Python coding"
)
```

### Auto Agent
```python
from beast_mode_network import AutoAgent, AutoAgentConfig, AgentPersonality

# Create an auto agent
config = AutoAgentConfig(
    agent_id="helpful_bot",
    capabilities=["general", "automation"],
    personality=AgentPersonality.HELPFUL
)

agent = AutoAgent(config)
await agent.start()

# Run demonstration
results = await agent.demonstrate_functionality()
```

## Architecture

The Beast Mode Agent Network consists of:

- **Message Models**: Structured data exchange
- **Redis Foundation**: Reliable messaging infrastructure  
- **Agent Discovery**: Network topology management
- **Help System**: Collaborative problem-solving
- **Bus Client**: Simplified agent integration
- **Auto Agent**: Automated demonstration agents

## Generated on {datetime.now().isoformat()}
'''
        
        readme_file = target_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)


class AutoSetup:
    """Automated setup system for Beast Mode Agent Network."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system_checker = SystemChecker()
    
    async def check_system(self) -> Dict[str, Any]:
        """
        Check system readiness for Beast Mode Agent Network.
        
        Returns:
            Dictionary containing system check results
        """
        return await self.system_checker.check_all_dependencies()
    
    async def setup_environment(self) -> Dict[str, Any]:
        """
        Set up the environment for Beast Mode Agent Network.
        
        Returns:
            Dictionary containing setup results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "success": False
        }
        
        try:
            # Check system first
            check_results = await self.check_system()
            results["steps"].append({
                "name": "system_check",
                "success": check_results["overall_status"] == "ready",
                "details": check_results
            })
            
            if check_results["overall_status"] != "ready":
                results["error"] = "System check failed"
                return results
            
            # Test Redis connectivity
            redis_test = await self._test_redis_connectivity()
            results["steps"].append({
                "name": "redis_test",
                "success": redis_test["success"],
                "details": redis_test
            })
            
            if not redis_test["success"]:
                results["error"] = "Redis connectivity test failed"
                return results
            
            # Test basic agent creation
            agent_test = await self._test_agent_creation()
            results["steps"].append({
                "name": "agent_test",
                "success": agent_test["success"],
                "details": agent_test
            })
            
            if not agent_test["success"]:
                results["error"] = "Agent creation test failed"
                return results
            
            results["success"] = True
            self.logger.info("Environment setup completed successfully")
            
        except Exception as e:
            results["error"] = str(e)
            self.logger.error(f"Environment setup failed: {e}")
        
        return results
    
    async def run_demonstration(self, num_agents: int = 2, 
                              duration_minutes: int = 2) -> Dict[str, Any]:
        """
        Run a system demonstration.
        
        Args:
            num_agents: Number of agents to create
            duration_minutes: How long to run the demonstration
            
        Returns:
            Dictionary containing demonstration results
        """
        try:
            self.logger.info(f"Starting demonstration with {num_agents} agents for {duration_minutes} minutes")
            
            results = await run_agent_demonstration(
                num_agents=num_agents,
                duration_minutes=duration_minutes
            )
            
            if results["success"]:
                self.logger.info("Demonstration completed successfully")
            else:
                self.logger.error(f"Demonstration failed: {results.get('error', 'Unknown error')}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Demonstration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def extract_spore(self, source_dir: str, target_dir: str,
                          spore_name: str = "beast_mode_network_spore") -> Dict[str, Any]:
        """
        Extract a deployable spore from the source code.
        
        Args:
            source_dir: Source directory containing the code
            target_dir: Target directory for the spore
            spore_name: Name of the spore
            
        Returns:
            Dictionary containing extraction results
        """
        config = SporeConfig(
            source_directory=source_dir,
            target_directory=target_dir,
            spore_name=spore_name
        )
        
        extractor = SporeExtractor(config)
        return await extractor.extract_spore()
    
    async def _test_redis_connectivity(self) -> Dict[str, Any]:
        """Test Redis connectivity."""
        try:
            import redis
            
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Test basic operations
            test_key = "beast_mode_test"
            test_value = "connectivity_test"
            
            client.set(test_key, test_value)
            retrieved_value = client.get(test_key)
            client.delete(test_key)
            
            if retrieved_value == test_value:
                return {
                    "success": True,
                    "message": "Redis connectivity test passed"
                }
            else:
                return {
                    "success": False,
                    "error": "Redis data integrity test failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Redis connectivity test failed: {e}"
            }
    
    async def _test_agent_creation(self) -> Dict[str, Any]:
        """Test basic agent creation."""
        try:
            # Create a simple test agent
            client = await create_bus_client(
                agent_id="test_agent",
                capabilities=["test"]
            )
            
            # Test basic operations
            await client.announce_presence()
            agents = await client.discover_agents()
            
            # Cleanup
            await client.disconnect()
            
            return {
                "success": True,
                "message": "Agent creation test passed",
                "agents_discovered": len(agents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent creation test failed: {e}"
            }


# Main functions for command-line usage
async def main():
    """Main function for auto setup."""
    setup = AutoSetup()
    
    print("Beast Mode Agent Network Auto Setup")
    print("=" * 40)
    
    # Check system
    print("Checking system...")
    check_results = await setup.check_system()
    
    if check_results["overall_status"] == "ready":
        print("✓ System ready")
    else:
        print("✗ System not ready")
        return False
    
    # Setup environment
    print("Setting up environment...")
    setup_results = await setup.setup_environment()
    
    if setup_results["success"]:
        print("✓ Environment setup complete")
    else:
        print(f"✗ Environment setup failed: {setup_results.get('error', 'Unknown error')}")
        return False
    
    # Run demonstration
    print("Running demonstration...")
    demo_results = await setup.run_demonstration()
    
    if demo_results["success"]:
        print("✓ Demonstration complete")
        print(f"  Agents: {demo_results['num_agents']}")
        print(f"  Duration: {demo_results['duration_minutes']} minutes")
    else:
        print(f"✗ Demonstration failed: {demo_results.get('error', 'Unknown error')}")
        return False
    
    print("\nBeast Mode Agent Network is ready!")
    return True


async def check_system():
    """Check system dependencies."""
    setup = AutoSetup()
    results = await setup.check_system()
    
    print("System Check Results")
    print("=" * 20)
    
    for component, result in results.items():
        if component == "overall_status":
            continue
            
        if isinstance(result, dict):
            status = result.get("status", "unknown")
            print(f"{component}: {status}")
            
            if result.get("issues"):
                for issue in result["issues"]:
                    print(f"  - {issue}")
    
    print(f"\nOverall Status: {results['overall_status']}")
    return results["overall_status"] == "ready"


async def run_demo(agents: int = 3, minutes: int = 2):
    """Run a demonstration."""
    setup = AutoSetup()
    results = await setup.run_demonstration(agents, minutes)
    
    if results["success"]:
        print(f"Demo completed with {results['num_agents']} agents")
    else:
        print(f"Demo failed: {results.get('error', 'Unknown error')}")
    
    return results["success"]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            success = asyncio.run(check_system())
        elif command == "demo":
            agents = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 2
            success = asyncio.run(run_demo(agents, minutes))
        else:
            success = asyncio.run(main())
    else:
        success = asyncio.run(main())
    
    sys.exit(0 if success else 1)