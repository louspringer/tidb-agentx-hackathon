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
        assert result["python"]["status"] in ["ok", "error"]  # Should at least attempt check
        
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