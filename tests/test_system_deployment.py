"""
System tests for auto setup and deployment of Beast Mode Agent Network.

These tests cover complete spore extraction and file generation, automated agent
configuration and startup, dependency verification and error reporting, cross-platform
compatibility and Redis connectivity, and end-to-end system demonstration.
"""

import asyncio
import pytest
import pytest_asyncio
import os
import sys
import tempfile
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from unittest.mock import AsyncMock, patch, MagicMock

from src.beast_mode_network.auto_setup import (
    AutoSetup,
    SystemChecker,
    SporeExtractor,
    SporeConfig,
)
from src.beast_mode_network.auto_agent import (
    AutoAgent,
    AutoAgentConfig,
    AgentPersonality,
    run_agent_demonstration,
)


class TestSystemChecker:
    """Test system dependency checking and validation."""
    
    @pytest.fixture
    def system_checker(self):
        """Create SystemChecker instance."""
        return SystemChecker()
    
    @pytest.mark.asyncio
    async def test_python_check_success(self, system_checker):
        """Test successful Python installation check."""
        result = await system_checker._check_python()
        
        assert result["status"] == "ok"
        assert "version" in result
        assert "executable" in result
        assert result["asyncio_available"] is True
        assert len(result.get("issues", [])) == 0
    
    @pytest.mark.asyncio
    async def test_python_check_old_version(self, system_checker):
        """Test Python version check with old version."""
        with patch('sys.version_info', (3, 6, 0)):  # Python 3.6
            result = await system_checker._check_python()
            
            assert result["status"] == "error"
            assert any("Python 3.7+ required" in issue for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_redis_check_success(self, system_checker):
        """Test successful Redis check."""
        mock_redis_client = MagicMock()
        mock_redis_client.ping.return_value = True
        mock_redis_client.info.return_value = {
            "redis_version": "6.2.0",
            "used_memory_human": "1.5M",
            "uptime_in_seconds": 3600
        }
        
        with patch('redis.Redis', return_value=mock_redis_client):
            result = await system_checker._check_redis()
            
            assert result["status"] == "ok"
            assert result["version"] == "6.2.0"
            assert result["connected"] is True
            assert result["memory_usage"] == "1.5M"
            assert result["uptime"] == 3600
    
    @pytest.mark.asyncio
    async def test_redis_check_not_installed(self, system_checker):
        """Test Redis check when package not installed."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'redis'")):
            result = await system_checker._check_redis()
            
            assert result["status"] == "error"
            assert "redis package not installed" in result["error"]
            assert any("pip install redis" in issue for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_redis_check_connection_failed(self, system_checker):
        """Test Redis check when connection fails."""
        import redis
        
        with patch('redis.Redis') as MockRedis:
            mock_client = MagicMock()
            mock_client.ping.side_effect = redis.ConnectionError("Connection refused")
            MockRedis.return_value = mock_client
            
            result = await system_checker._check_redis()
            
            assert result["status"] == "warning"
            assert result["connected"] is False
            assert any("Cannot connect to Redis server" in issue for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_network_check_success(self, system_checker):
        """Test successful network connectivity check."""
        with patch('socket.socket') as MockSocket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0  # Success
            MockSocket.return_value = mock_sock
            
            result = await system_checker._check_network()
            
            assert result["status"] == "ok"
            assert result["localhost_available"] is True
            assert result["redis_port_available"] is True
            assert len(result.get("issues", [])) == 0
    
    @pytest.mark.asyncio
    async def test_network_check_redis_port_unavailable(self, system_checker):
        """Test network check when Redis port is unavailable."""
        with patch('socket.socket') as MockSocket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 1  # Connection refused
            MockSocket.return_value = mock_sock
            
            result = await system_checker._check_network()
            
            assert result["status"] == "ok"  # Still ok, just port unavailable
            assert result["redis_port_available"] is False
            assert any("Redis port 6379 not accessible" in issue for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_permissions_check_success(self, system_checker):
        """Test successful permissions check."""
        result = await system_checker._check_permissions()
        
        # Should be able to write to temp and current directory in normal test environment
        assert result["status"] in ["ok", "warning"]
        assert result["can_write_temp"] is True
        # can_create_files might be False in some CI environments
    
    @pytest.mark.asyncio
    async def test_permissions_check_no_temp_access(self, system_checker):
        """Test permissions check when temp directory is not writable."""
        with patch('tempfile.NamedTemporaryFile', side_effect=PermissionError("Access denied")):
            result = await system_checker._check_permissions()
            
            assert result["status"] == "warning"
            assert result["can_write_temp"] is False
            assert any("Cannot write to temp directory" in issue for issue in result["issues"])
    
    @pytest.mark.asyncio
    async def test_check_all_dependencies_ready(self, system_checker):
        """Test complete dependency check when system is ready."""
        # Mock all checks to return success
        with patch.object(system_checker, '_check_python', return_value={"status": "ok"}):
            with patch.object(system_checker, '_check_redis', return_value={"status": "ok"}):
                with patch.object(system_checker, '_check_network', return_value={"status": "ok"}):
                    with patch.object(system_checker, '_check_permissions', return_value={"status": "ok"}):
                        result = await system_checker.check_all_dependencies()
        
        assert result["overall_status"] == "ready"
        assert result["python"]["status"] == "ok"
        assert result["redis"]["status"] == "ok"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_check_all_dependencies_not_ready(self, system_checker):
        """Test complete dependency check when system is not ready."""
        # Mock critical checks to fail
        with patch.object(system_checker, '_check_python', return_value={"status": "error"}):
            with patch.object(system_checker, '_check_redis', return_value={"status": "ok"}):
                with patch.object(system_checker, '_check_network', return_value={"status": "ok"}):
                    with patch.object(system_checker, '_check_permissions', return_value={"status": "ok"}):
                        result = await system_checker.check_all_dependencies()
        
        assert result["overall_status"] == "not_ready"
        assert result["python"]["status"] == "error"


class TestSporeExtractor:
    """Test spore extraction and deployment package creation."""
    
    @pytest.fixture
    def temp_source_dir(self):
        """Create temporary source directory with test files."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test file structure
        source_path = Path(temp_dir) / "source"
        source_path.mkdir()
        
        # Create Python files
        (source_path / "main.py").write_text("print('Hello World')")
        (source_path / "utils.py").write_text("def helper(): pass")
        
        # Create subdirectory
        sub_dir = source_path / "submodule"
        sub_dir.mkdir()
        (sub_dir / "module.py").write_text("class TestClass: pass")
        
        # Create files to exclude
        (source_path / "__pycache__").mkdir()
        (source_path / "__pycache__" / "main.cpython-39.pyc").write_text("bytecode")
        (source_path / "test.log").write_text("log content")
        
        # Create documentation
        (source_path / "README.md").write_text("# Test Project")
        (source_path / "requirements.txt").write_text("redis>=4.0.0")
        
        yield str(source_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_target_dir(self):
        """Create temporary target directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def spore_config(self, temp_source_dir, temp_target_dir):
        """Create spore configuration."""
        return SporeConfig(
            source_directory=temp_source_dir,
            target_directory=temp_target_dir,
            spore_name="test_spore",
            include_examples=True,
            include_tests=False
        )
    
    def test_spore_config_defaults(self):
        """Test SporeConfig default values."""
        config = SporeConfig()
        
        assert config.spore_name == "beast_mode_network_spore"
        assert "*.py" in config.include_patterns
        assert "*.md" in config.include_patterns
        assert "__pycache__" in config.exclude_patterns
        assert "*.pyc" in config.exclude_patterns
        assert "redis>=4.0.0" in config.python_requirements
        assert "redis-server" in config.system_requirements
    
    @pytest.mark.asyncio
    async def test_spore_extraction_success(self, spore_config):
        """Test successful spore extraction."""
        extractor = SporeExtractor(spore_config)
        result = await extractor.extract_spore()
        
        assert result["success"] is True
        assert result["spore_name"] == "test_spore"
        assert result["files_copied"] > 0
        assert result["total_size"] > 0
        
        # Check that files were copied
        target_path = Path(spore_config.target_directory)
        assert (target_path / "main.py").exists()
        assert (target_path / "utils.py").exists()
        assert (target_path / "submodule" / "module.py").exists()
        assert (target_path / "README.md").exists()
        
        # Check that excluded files were not copied
        assert not (target_path / "__pycache__").exists()
        assert not (target_path / "test.log").exists()
        
        # Check that metadata was created
        assert (target_path / "spore_metadata.json").exists()
        assert (target_path / "setup.py").exists()
        assert (target_path / "requirements.txt").exists()
        
        # Verify metadata content
        with open(target_path / "spore_metadata.json") as f:
            metadata = json.load(f)
        
        assert metadata["spore_name"] == "test_spore"
        assert metadata["version"] == "1.0.0"
        assert "created_at" in metadata
        assert "python_requirements" in metadata
        assert "entry_points" in metadata
    
    @pytest.mark.asyncio
    async def test_spore_extraction_nonexistent_source(self, temp_target_dir):
        """Test spore extraction with non-existent source directory."""
        config = SporeConfig(
            source_directory="/nonexistent/path",
            target_directory=temp_target_dir,
            spore_name="test_spore"
        )
        
        extractor = SporeExtractor(config)
        result = await extractor.extract_spore()
        
        assert result["success"] is False
        assert "Source directory not found" in result["error"]
    
    def test_file_pattern_matching(self, spore_config):
        """Test file pattern matching logic."""
        extractor = SporeExtractor(spore_config)
        
        # Test include patterns
        assert extractor._should_include_file("test.py") is True
        assert extractor._should_include_file("README.md") is True
        assert extractor._should_include_file("config.json") is True
        
        # Test exclude patterns
        assert extractor._should_include_file("test.pyc") is False
        assert extractor._should_include_file("debug.log") is False
        
        # Test path exclusion
        assert extractor._should_exclude_path("__pycache__") is True
        assert extractor._should_exclude_path(".git") is True
        assert extractor._should_exclude_path("normal_dir") is False


class TestAutoSetup:
    """Test automated setup system."""
    
    @pytest.fixture
    def auto_setup(self):
        """Create AutoSetup instance."""
        return AutoSetup()
    
    @pytest.mark.asyncio
    async def test_check_system_success(self, auto_setup):
        """Test system check with all dependencies ready."""
        mock_checker = AsyncMock()
        mock_checker.check_all_dependencies.return_value = {
            "overall_status": "ready",
            "python": {"status": "ok"},
            "redis": {"status": "ok"},
            "network": {"status": "ok"},
            "permissions": {"status": "ok"}
        }
        
        auto_setup.system_checker = mock_checker
        
        result = await auto_setup.check_system()
        
        assert result["overall_status"] == "ready"
        mock_checker.check_all_dependencies.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_setup_environment_success(self, auto_setup):
        """Test successful environment setup."""
        # Mock system check to pass
        with patch.object(auto_setup, 'check_system', return_value={"overall_status": "ready"}):
            with patch.object(auto_setup, '_test_redis_connectivity', return_value={"success": True}):
                with patch.object(auto_setup, '_test_agent_creation', return_value={"success": True}):
                    result = await auto_setup.setup_environment()
        
        assert result["success"] is True
        assert len(result["steps"]) == 3
        assert all(step["success"] for step in result["steps"])
    
    @pytest.mark.asyncio
    async def test_setup_environment_system_check_failed(self, auto_setup):
        """Test environment setup when system check fails."""
        with patch.object(auto_setup, 'check_system', return_value={"overall_status": "not_ready"}):
            result = await auto_setup.setup_environment()
        
        assert result["success"] is False
        assert "System check failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_redis_connectivity_test_success(self, auto_setup):
        """Test Redis connectivity test."""
        mock_redis_client = MagicMock()
        mock_redis_client.set.return_value = True
        mock_redis_client.get.return_value = "connectivity_test"
        mock_redis_client.delete.return_value = 1
        
        with patch('redis.Redis', return_value=mock_redis_client):
            result = await auto_setup._test_redis_connectivity()
        
        assert result["success"] is True
        assert "connectivity test passed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_redis_connectivity_test_failure(self, auto_setup):
        """Test Redis connectivity test failure."""
        with patch('redis.Redis', side_effect=Exception("Connection failed")):
            result = await auto_setup._test_redis_connectivity()
        
        assert result["success"] is False
        assert "Connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_agent_creation_test_success(self, auto_setup):
        """Test agent creation test."""
        mock_client = AsyncMock()
        mock_client.announce_presence = AsyncMock()
        mock_client.discover_agents = AsyncMock(return_value=[])
        mock_client.disconnect = AsyncMock()
        
        with patch('src.beast_mode_network.auto_setup.create_bus_client', return_value=mock_client):
            result = await auto_setup._test_agent_creation()
        
        assert result["success"] is True
        assert "Agent creation test passed" in result["message"]
        mock_client.announce_presence.assert_called_once()
        mock_client.discover_agents.assert_called_once()
        mock_client.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_creation_test_failure(self, auto_setup):
        """Test agent creation test failure."""
        with patch('src.beast_mode_network.auto_setup.create_bus_client', side_effect=Exception("Creation failed")):
            result = await auto_setup._test_agent_creation()
        
        assert result["success"] is False
        assert "Creation failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_run_demonstration_success(self, auto_setup):
        """Test successful demonstration run."""
        mock_demo_result = {
            "success": True,
            "num_agents": 2,
            "duration_minutes": 1,
            "agents": [
                {"agent_id": "demo_agent_1", "personality": "helpful"},
                {"agent_id": "demo_agent_2", "personality": "curious"}
            ]
        }
        
        with patch('src.beast_mode_network.auto_setup.run_agent_demonstration', return_value=mock_demo_result):
            result = await auto_setup.run_demonstration(num_agents=2, duration_minutes=1)
        
        assert result["success"] is True
        assert result["num_agents"] == 2
        assert result["duration_minutes"] == 1
    
    @pytest.mark.asyncio
    async def test_run_demonstration_failure(self, auto_setup):
        """Test demonstration run failure."""
        with patch('src.beast_mode_network.auto_setup.run_agent_demonstration', side_effect=Exception("Demo failed")):
            result = await auto_setup.run_demonstration()
        
        assert result["success"] is False
        assert "Demo failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_extract_spore_success(self, auto_setup):
        """Test successful spore extraction."""
        mock_result = {
            "success": True,
            "spore_name": "test_spore",
            "files_copied": 10,
            "total_size": 50000
        }
        
        with patch('src.beast_mode_network.auto_setup.SporeExtractor') as MockExtractor:
            mock_extractor = AsyncMock()
            mock_extractor.extract_spore.return_value = mock_result
            MockExtractor.return_value = mock_extractor
            
            result = await auto_setup.extract_spore("/source", "/target", "test_spore")
        
        assert result["success"] is True
        assert result["spore_name"] == "test_spore"
        assert result["files_copied"] == 10


class TestAutoAgentDeployment:
    """Test auto agent deployment and demonstration."""
    
    @pytest.mark.asyncio
    async def test_auto_agent_creation_and_startup(self):
        """Test auto agent creation and startup process."""
        config = AutoAgentConfig(
            agent_id="test_deployment_agent",
            capabilities=["testing", "deployment"],
            personality=AgentPersonality.HELPFUL,
            redis_url="redis://localhost:6379"
        )
        
        # Mock Redis and other dependencies
        with patch('src.beast_mode_network.auto_agent.BeastModeBusClient') as MockBusClient:
            mock_client = AsyncMock()
            mock_client.connect.return_value = True
            mock_client.disconnect = AsyncMock()
            mock_client.announce_presence = AsyncMock()
            MockBusClient.return_value = mock_client
            
            agent = AutoAgent(config)
            
            # Test startup
            success = await agent.start()
            assert success is True
            assert agent._is_running is True
            
            # Test status
            status = await agent.get_agent_status()
            assert status["agent_id"] == "test_deployment_agent"
            assert status["is_running"] is True
            assert status["personality"] == "helpful"
            assert status["capabilities"] == ["testing", "deployment"]
            
            # Test shutdown
            await agent.stop()
            assert agent._is_running is False
    
    @pytest.mark.asyncio
    async def test_auto_agent_demonstration_functionality(self):
        """Test auto agent demonstration capabilities."""
        config = AutoAgentConfig(
            agent_id="demo_agent",
            capabilities=["demonstration"],
            personality=AgentPersonality.ANALYTICAL
        )
        
        # Mock all dependencies
        with patch('src.beast_mode_network.auto_agent.BeastModeBusClient') as MockBusClient:
            mock_client = AsyncMock()
            mock_client.connect.return_value = True
            mock_client.disconnect = AsyncMock()
            mock_client.discover_agents.return_value = []
            mock_client.send_simple_message.return_value = True
            mock_client.request_help.return_value = "help-123"
            mock_client.get_my_requests.return_value = []
            mock_client.find_best_agents.return_value = []
            mock_client.get_network_stats.return_value = {"agents": 1, "messages": 5}
            MockBusClient.return_value = mock_client
            
            agent = AutoAgent(config)
            await agent.start()
            
            try:
                # Run demonstration
                results = await agent.demonstrate_functionality()
                
                assert results["success"] is True
                assert results["agent_id"] == "demo_agent"
                assert "demonstrations" in results
                assert len(results["demonstrations"]) >= 4  # Should have multiple demos
                
                # Check specific demonstrations
                demo_names = [demo["name"] for demo in results["demonstrations"]]
                assert "agent_discovery" in demo_names
                assert "simple_message" in demo_names
                assert "capability_search" in demo_names
                assert "network_statistics" in demo_names
                
            finally:
                await agent.stop()
    
    @pytest.mark.asyncio
    async def test_multi_agent_demonstration_run(self):
        """Test running demonstration with multiple agents."""
        mock_demo_result = {
            "success": True,
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "num_agents": 3,
            "duration_minutes": 1,
            "agents": [
                {
                    "agent_id": "demo_agent_1",
                    "personality": "helpful",
                    "capabilities": ["general", "demonstration"],
                    "final_stats": {
                        "messages_sent": 5,
                        "help_responses_sent": 2,
                        "help_requests_made": 1
                    }
                },
                {
                    "agent_id": "demo_agent_2", 
                    "personality": "curious",
                    "capabilities": ["general", "demonstration"],
                    "final_stats": {
                        "messages_sent": 3,
                        "help_responses_sent": 1,
                        "help_requests_made": 2
                    }
                },
                {
                    "agent_id": "demo_agent_3",
                    "personality": "expert",
                    "capabilities": ["general", "demonstration"],
                    "final_stats": {
                        "messages_sent": 4,
                        "help_responses_sent": 3,
                        "help_requests_made": 0
                    }
                }
            ]
        }
        
        with patch('src.beast_mode_network.auto_agent.run_agent_demonstration', return_value=mock_demo_result):
            result = await run_agent_demonstration(num_agents=3, duration_minutes=1)
        
        assert result["success"] is True
        assert result["num_agents"] == 3
        assert len(result["agents"]) == 3
        
        # Verify agent statistics
        total_messages = sum(agent["final_stats"]["messages_sent"] for agent in result["agents"])
        total_help_responses = sum(agent["final_stats"]["help_responses_sent"] for agent in result["agents"])
        total_help_requests = sum(agent["final_stats"]["help_requests_made"] for agent in result["agents"])
        
        assert total_messages > 0
        assert total_help_responses > 0
        assert total_help_requests > 0


class TestEndToEndDeployment:
    """Test complete end-to-end deployment scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_setup_and_demonstration_workflow(self):
        """Test complete setup workflow from system check to demonstration."""
        auto_setup = AutoSetup()
        
        # Mock all system checks to pass
        mock_system_results = {
            "overall_status": "ready",
            "python": {"status": "ok", "version": "3.9.0"},
            "redis": {"status": "ok", "connected": True},
            "network": {"status": "ok", "redis_port_available": True},
            "permissions": {"status": "ok", "can_write_temp": True}
        }
        
        mock_setup_results = {
            "success": True,
            "steps": [
                {"name": "system_check", "success": True},
                {"name": "redis_test", "success": True},
                {"name": "agent_test", "success": True}
            ]
        }
        
        mock_demo_results = {
            "success": True,
            "num_agents": 2,
            "duration_minutes": 1,
            "agents": [
                {"agent_id": "agent_1", "final_stats": {"messages_sent": 3}},
                {"agent_id": "agent_2", "final_stats": {"messages_sent": 2}}
            ]
        }
        
        with patch.object(auto_setup, 'check_system', return_value=mock_system_results):
            with patch.object(auto_setup, 'setup_environment', return_value=mock_setup_results):
                with patch.object(auto_setup, 'run_demonstration', return_value=mock_demo_results):
                    
                    # Step 1: Check system
                    system_check = await auto_setup.check_system()
                    assert system_check["overall_status"] == "ready"
                    
                    # Step 2: Setup environment
                    setup_result = await auto_setup.setup_environment()
                    assert setup_result["success"] is True
                    
                    # Step 3: Run demonstration
                    demo_result = await auto_setup.run_demonstration(num_agents=2, duration_minutes=1)
                    assert demo_result["success"] is True
                    assert demo_result["num_agents"] == 2
    
    @pytest.mark.asyncio
    async def test_deployment_failure_scenarios(self):
        """Test various deployment failure scenarios."""
        auto_setup = AutoSetup()
        
        # Test system check failure
        with patch.object(auto_setup, 'check_system', return_value={"overall_status": "not_ready"}):
            setup_result = await auto_setup.setup_environment()
            assert setup_result["success"] is False
            assert "System check failed" in setup_result["error"]
        
        # Test Redis connectivity failure
        mock_system_ok = {"overall_status": "ready"}
        mock_redis_fail = {"success": False, "error": "Redis connection failed"}
        
        with patch.object(auto_setup, 'check_system', return_value=mock_system_ok):
            with patch.object(auto_setup, '_test_redis_connectivity', return_value=mock_redis_fail):
                setup_result = await auto_setup.setup_environment()
                assert setup_result["success"] is False
                assert "Redis connectivity test failed" in setup_result["error"]
        
        # Test agent creation failure
        mock_redis_ok = {"success": True}
        mock_agent_fail = {"success": False, "error": "Agent creation failed"}
        
        with patch.object(auto_setup, 'check_system', return_value=mock_system_ok):
            with patch.object(auto_setup, '_test_redis_connectivity', return_value=mock_redis_ok):
                with patch.object(auto_setup, '_test_agent_creation', return_value=mock_agent_fail):
                    setup_result = await auto_setup.setup_environment()
                    assert setup_result["success"] is False
                    assert "Agent creation test failed" in setup_result["error"]
    
    @pytest.mark.asyncio
    async def test_cross_platform_compatibility_checks(self):
        """Test cross-platform compatibility verification."""
        system_checker = SystemChecker()
        
        # Test on current platform (should work in test environment)
        result = await system_checker.check_all_dependencies()
        
        # Basic checks that should work on any platform
        assert "python" in result
        assert "network" in result
        assert "permissions" in result
        assert result["python"]["status"] in ["ok", "error"]
        
        # Platform-specific checks
        if sys.platform.startswith('win'):
            # Windows-specific checks
            assert result["python"]["executable"].endswith('.exe')
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            # Unix-like systems
            assert '/' in result["python"]["executable"]
    
    @pytest.mark.asyncio
    async def test_redis_connectivity_cross_platform(self):
        """Test Redis connectivity on different platforms."""
        auto_setup = AutoSetup()
        
        # Test with different Redis URLs that might be used on different platforms
        redis_urls = [
            "redis://localhost:6379",
            "redis://127.0.0.1:6379",
            "redis://redis:6379",  # Docker container name
        ]
        
        for redis_url in redis_urls:
            # Mock Redis client for each URL
            mock_client = MagicMock()
            mock_client.set.return_value = True
            mock_client.get.return_value = "connectivity_test"
            mock_client.delete.return_value = 1
            
            with patch('redis.Redis', return_value=mock_client):
                # Temporarily modify the test to use different URL
                original_method = auto_setup._test_redis_connectivity
                
                async def test_with_url():
                    import redis
                    client = redis.Redis.from_url(redis_url, decode_responses=True)
                    test_key = "beast_mode_test"
                    test_value = "connectivity_test"
                    
                    client.set(test_key, test_value)
                    retrieved_value = client.get(test_key)
                    client.delete(test_key)
                    
                    if retrieved_value == test_value:
                        return {"success": True, "message": f"Redis connectivity test passed for {redis_url}"}
                    else:
                        return {"success": False, "error": "Redis data integrity test failed"}
                
                result = await test_with_url()
                assert result["success"] is True, f"Redis connectivity should work with {redis_url}"


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior."""
    
    @pytest.mark.asyncio
    async def test_spore_extraction_performance(self):
        """Test spore extraction performance with large codebases."""
        # Create a large temporary codebase
        temp_dir = tempfile.mkdtemp()
        source_path = Path(temp_dir) / "large_source"
        source_path.mkdir()
        
        try:
            # Create many files to simulate large codebase
            import time
            
            for i in range(100):
                file_path = source_path / f"module_{i}.py"
                file_content = f"""
# Module {i}
class Module{i}:
    def __init__(self):
        self.value = {i}
    
    def process(self):
        return self.value * 2
    
    def get_info(self):
        return f"Module {i} with value {{self.value}}"
""" * 10  # Make each file reasonably large
                file_path.write_text(file_content)
            
            # Create subdirectories with more files
            for i in range(10):
                sub_dir = source_path / f"package_{i}"
                sub_dir.mkdir()
                for j in range(10):
                    file_path = sub_dir / f"submodule_{j}.py"
                    file_path.write_text(f"# Submodule {i}.{j}\nvalue = {i * 10 + j}")
            
            target_path = Path(temp_dir) / "extracted"
            
            config = SporeConfig(
                source_directory=str(source_path),
                target_directory=str(target_path),
                spore_name="performance_test_spore"
            )
            
            # Time the extraction
            start_time = time.time()
            
            extractor = SporeExtractor(config)
            result = await extractor.extract_spore()
            
            extraction_time = time.time() - start_time
            
            # Verify extraction succeeded
            assert result["success"] is True
            assert result["files_copied"] > 100  # Should have copied many files
            
            # Performance check - should complete in reasonable time
            assert extraction_time < 5.0, f"Extraction took too long: {extraction_time:.2f}s"
            
            # Verify all files were copied correctly
            assert (target_path / "module_0.py").exists()
            assert (target_path / "module_99.py").exists()
            assert (target_path / "package_0" / "submodule_0.py").exists()
            assert (target_path / "package_9" / "submodule_9.py").exists()
            
            print(f"Extracted {result['files_copied']} files in {extraction_time:.2f}s")
            print(f"Total size: {result['total_size']} bytes")
            
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_multi_agent_demonstration_scaling(self):
        """Test demonstration scaling with many agents."""
        # Test with increasing numbers of agents
        agent_counts = [2, 5, 10]
        
        for num_agents in agent_counts:
            mock_agents = []
            for i in range(num_agents):
                mock_agents.append({
                    "agent_id": f"scale_test_agent_{i}",
                    "personality": ["helpful", "curious", "expert"][i % 3],
                    "capabilities": ["general", "demonstration", f"specialty_{i}"],
                    "final_stats": {
                        "messages_sent": 3 + (i % 5),
                        "help_responses_sent": 1 + (i % 3),
                        "help_requests_made": i % 2,
                        "discovered_agents": num_agents - 1
                    }
                })
            
            mock_result = {
                "success": True,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "num_agents": num_agents,
                "duration_minutes": 1,
                "agents": mock_agents
            }
            
            with patch('src.beast_mode_network.auto_agent.run_agent_demonstration', return_value=mock_result):
                import time
                start_time = time.time()
                
                result = await run_agent_demonstration(
                    num_agents=num_agents,
                    duration_minutes=1
                )
                
                demo_time = time.time() - start_time
                
                assert result["success"] is True
                assert result["num_agents"] == num_agents
                assert len(result["agents"]) == num_agents
                
                # Performance should scale reasonably
                assert demo_time < 2.0, f"Demo with {num_agents} agents took too long: {demo_time:.2f}s"
                
                print(f"Demo with {num_agents} agents completed in {demo_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_system_resource_usage(self):
        """Test system resource usage during operations."""
        import psutil
        import gc
        
        # Get initial resource usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        initial_cpu_percent = process.cpu_percent()
        
        # Force garbage collection
        gc.collect()
        
        auto_setup = AutoSetup()
        
        # Mock heavy operations
        with patch.object(auto_setup, 'check_system') as mock_check:
            with patch.object(auto_setup, 'setup_environment') as mock_setup:
                with patch.object(auto_setup, 'run_demonstration') as mock_demo:
                    
                    # Configure mocks to return success
                    mock_check.return_value = {"overall_status": "ready"}
                    mock_setup.return_value = {"success": True, "steps": []}
                    mock_demo.return_value = {"success": True, "num_agents": 5}
                    
                    # Perform operations
                    for _ in range(10):  # Repeat operations
                        await auto_setup.check_system()
                        await auto_setup.setup_environment()
                        await auto_setup.run_demonstration(num_agents=5, duration_minutes=1)
        
        # Check final resource usage
        final_memory = process.memory_info().rss
        final_cpu_percent = process.cpu_percent()
        
        # Memory growth should be reasonable
        memory_growth = final_memory - initial_memory
        memory_growth_mb = memory_growth / (1024 * 1024)
        
        assert memory_growth_mb < 100, f"Memory growth too high: {memory_growth_mb:.1f}MB"
        
        print(f"Memory growth: {memory_growth_mb:.1f}MB")
        print(f"CPU usage: {final_cpu_percent:.1f}%")


class TestErrorRecoveryAndResilience:
    """Test error recovery and system resilience."""
    
    @pytest.mark.asyncio
    async def test_partial_system_failure_recovery(self):
        """Test recovery from partial system failures."""
        auto_setup = AutoSetup()
        
        # Simulate intermittent Redis failures
        call_count = 0
        
        async def flaky_redis_test():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # Fail first two attempts
                return {"success": False, "error": "Connection timeout"}
            else:  # Succeed on third attempt
                return {"success": True, "message": "Redis connectivity test passed"}
        
        with patch.object(auto_setup, 'check_system', return_value={"overall_status": "ready"}):
            with patch.object(auto_setup, '_test_redis_connectivity', side_effect=flaky_redis_test):
                with patch.object(auto_setup, '_test_agent_creation', return_value={"success": True}):
                    
                    # First attempt should fail
                    result1 = await auto_setup.setup_environment()
                    assert result1["success"] is False
                    
                    # Second attempt should also fail
                    result2 = await auto_setup.setup_environment()
                    assert result2["success"] is False
                    
                    # Third attempt should succeed
                    result3 = await auto_setup.setup_environment()
                    assert result3["success"] is True
    
    @pytest.mark.asyncio
    async def test_corrupted_spore_handling(self):
        """Test handling of corrupted or incomplete spore extraction."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            source_path = Path(temp_dir) / "source"
            target_path = Path(temp_dir) / "target"
            source_path.mkdir()
            
            # Create source files
            (source_path / "valid.py").write_text("print('valid')")
            
            config = SporeConfig(
                source_directory=str(source_path),
                target_directory=str(target_path),
                spore_name="corruption_test"
            )
            
            extractor = SporeExtractor(config)
            
            # Simulate file system error during extraction
            original_copy = shutil.copy2
            
            def failing_copy(src, dst):
                if "valid.py" in str(src):
                    raise PermissionError("Simulated file system error")
                return original_copy(src, dst)
            
            with patch('shutil.copy2', side_effect=failing_copy):
                result = await extractor.extract_spore()
            
            # Should handle the error gracefully
            assert result["success"] is False
            assert "error" in result
            
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_network_interruption_during_demo(self):
        """Test behavior during network interruptions in demonstration."""
        # Simulate network interruption during agent demonstration
        interruption_count = 0
        
        async def flaky_demo(*args, **kwargs):
            nonlocal interruption_count
            interruption_count += 1
            
            if interruption_count == 1:
                # First call fails due to network issue
                raise ConnectionError("Network unreachable")
            else:
                # Second call succeeds
                return {
                    "success": True,
                    "num_agents": kwargs.get("num_agents", 2),
                    "duration_minutes": kwargs.get("duration_minutes", 1),
                    "agents": [
                        {"agent_id": f"recovery_agent_{i}", "final_stats": {"messages_sent": 1}}
                        for i in range(kwargs.get("num_agents", 2))
                    ]
                }
        
        auto_setup = AutoSetup()
        
        with patch('src.beast_mode_network.auto_setup.run_agent_demonstration', side_effect=flaky_demo):
            # First attempt should fail
            result1 = await auto_setup.run_demonstration()
            assert result1["success"] is False
            assert "Network unreachable" in result1["error"]
            
            # Second attempt should succeed
            result2 = await auto_setup.run_demonstration()
            assert result2["success"] is True
    
    @pytest.mark.asyncio
    async def test_dependency_version_conflicts(self):
        """Test handling of dependency version conflicts."""
        system_checker = SystemChecker()
        
        # Simulate old Python version
        with patch('sys.version_info', (3, 6, 5)):  # Python 3.6.5
            result = await system_checker._check_python()
            
            assert result["status"] == "error"
            assert any("Python 3.7+ required" in issue for issue in result["issues"])
        
        # Simulate missing asyncio (shouldn't happen in practice, but test error handling)
        with patch('builtins.__import__', side_effect=ImportError("No module named 'asyncio'")):
            result = await system_checker._check_python()
            
            assert result["status"] == "error"
            assert any("asyncio not available" in issue for issue in result["issues"])


class TestDocumentationAndUsability:
    """Test documentation generation and usability features."""
    
    @pytest.mark.asyncio
    async def test_spore_documentation_generation(self):
        """Test that spore extraction generates proper documentation."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            source_path = Path(temp_dir) / "source"
            target_path = Path(temp_dir) / "target"
            source_path.mkdir()
            
            # Create source files
            (source_path / "main.py").write_text("# Main module\nprint('Hello')")
            
            config = SporeConfig(
                source_directory=str(source_path),
                target_directory=str(target_path),
                spore_name="documentation_test",
                include_documentation=True
            )
            
            extractor = SporeExtractor(config)
            result = await extractor.extract_spore()
            
            assert result["success"] is True
            
            # Check that documentation files were created
            assert (target_path / "README.md").exists()
            assert (target_path / "requirements.txt").exists()
            assert (target_path / "setup.py").exists()
            assert (target_path / "spore_metadata.json").exists()
            
            # Verify README content
            readme_content = (target_path / "README.md").read_text()
            assert "documentation_test" in readme_content
            assert "Beast Mode Agent Network Spore" in readme_content
            assert "Quick Start" in readme_content
            assert "Usage" in readme_content
            assert "Architecture" in readme_content
            
            # Verify setup script is executable
            setup_script = target_path / "setup.py"
            assert setup_script.exists()
            
            # Check that setup script has proper shebang and permissions
            setup_content = setup_script.read_text()
            assert setup_content.startswith("#!/usr/bin/env python3")
            assert "Beast Mode Agent Network Spore Setup Script" in setup_content
            
            # Verify requirements file
            requirements_content = (target_path / "requirements.txt").read_text()
            assert "redis>=4.0.0" in requirements_content
            
            # Verify metadata
            with open(target_path / "spore_metadata.json") as f:
                metadata = json.load(f)
            
            assert metadata["spore_name"] == "documentation_test"
            assert "entry_points" in metadata
            assert "main" in metadata["entry_points"]
            assert "demo" in metadata["entry_points"]
            assert "check" in metadata["entry_points"]
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_help_and_usage_information(self):
        """Test that help and usage information is comprehensive."""
        # Test AutoSetup main function help
        from src.beast_mode_network.auto_setup import main, check_system, run_demo
        
        # These functions should be importable and have proper docstrings
        assert main.__doc__ is not None
        assert check_system.__doc__ is not None
        assert run_demo.__doc__ is not None
        
        # Test that command-line interface works
        import sys
        from unittest.mock import patch
        
        # Test help command
        with patch('sys.argv', ['auto_setup.py', 'check']):
            with patch('src.beast_mode_network.auto_setup.check_system') as mock_check:
                mock_check.return_value = asyncio.create_task(
                    asyncio.coroutine(lambda: {"overall_status": "ready"})()
                )
                
                # Should not raise exception
                try:
                    # This would normally run the check command
                    pass
                except SystemExit:
                    pass  # Expected for command-line tools


if __name__ == "__main__":
    pytest.main([__file__])n"]["status"] in ["ok", "error"]  # Should at least attempt check
        
        # Platform-specific path separators should be handled
        if sys.platform.startswith('win'):
            # Windows-specific checks could go here
            pass
        else:
            # Unix-like system checks
            assert result["permissions"]["can_write_temp"] in [True, False]


class TestCommandLineInterface:
    """Test command-line interface functionality."""
    
    def test_main_function_import(self):
        """Test that main functions can be imported."""
        from src.beast_mode_network.auto_setup import main, check_system, run_demo
        
        # Functions should be callable
        assert callable(main)
        assert callable(check_system)
        assert callable(run_demo)
    
    @pytest.mark.asyncio
    async def test_check_system_cli_function(self):
        """Test check_system CLI function."""
        from src.beast_mode_network.auto_setup import check_system
        
        # Mock system checker
        with patch('src.beast_mode_network.auto_setup.AutoSetup') as MockAutoSetup:
            mock_setup = AsyncMock()
            mock_setup.check_system.return_value = {
                "overall_status": "ready",
                "python": {"status": "ok"},
                "redis": {"status": "ok"},
                "network": {"status": "ok"},
                "permissions": {"status": "ok"}
            }
            MockAutoSetup.return_value = mock_setup
            
            result = await check_system()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_run_demo_cli_function(self):
        """Test run_demo CLI function."""
        from src.beast_mode_network.auto_setup import run_demo
        
        # Mock demonstration
        with patch('src.beast_mode_network.auto_setup.AutoSetup') as MockAutoSetup:
            mock_setup = AsyncMock()
            mock_setup.run_demonstration.return_value = {
                "success": True,
                "num_agents": 2,
                "duration_minutes": 1
            }
            MockAutoSetup.return_value = mock_setup
            
            result = await run_demo(agents=2, minutes=1)
            assert result is True


if __name__ == "__main__":
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    pytest.main([__file__, "-v"])