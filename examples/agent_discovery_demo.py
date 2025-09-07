#!/usr/bin/env python3
"""
Agent Discovery System Demonstration

This script demonstrates the core functionality of the Beast Mode Agent Network's
agent discovery and registry system, including:

- Agent registration and discovery
- Capability-based agent matching
- Trust score calculation and updates
- Availability monitoring
"""

import asyncio
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.beast_mode_network import (
    AgentCapabilities, DiscoveredAgent, AgentRegistry, AgentStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demonstrate_agent_discovery():
    """Demonstrate the agent discovery system functionality."""
    
    print("🚀 Beast Mode Agent Network - Discovery System Demo")
    print("=" * 60)
    
    # Create agent registry
    print("\n1. Creating Agent Registry...")
    registry = AgentRegistry(availability_timeout_minutes=2)
    await registry.start_monitoring()
    
    try:
        # Create sample agents with different capabilities
        print("\n2. Creating Sample Agents...")
        
        agents_data = [
            {
                "agent_id": "python_expert",
                "capabilities": ["python", "data_analysis", "machine_learning"],
                "specializations": ["pandas", "scikit-learn", "tensorflow"],
                "description": "Expert Python developer specializing in ML"
            },
            {
                "agent_id": "web_developer", 
                "capabilities": ["javascript", "web_development", "react"],
                "specializations": ["frontend", "ui_ux", "responsive_design"],
                "description": "Full-stack web developer"
            },
            {
                "agent_id": "data_scientist",
                "capabilities": ["python", "data_analysis", "statistics", "visualization"],
                "specializations": ["matplotlib", "seaborn", "jupyter"],
                "description": "Data scientist with visualization expertise"
            },
            {
                "agent_id": "devops_engineer",
                "capabilities": ["docker", "kubernetes", "ci_cd", "monitoring"],
                "specializations": ["aws", "terraform", "prometheus"],
                "description": "DevOps engineer with cloud expertise"
            }
        ]
        
        # Register all agents
        print("\n3. Registering Agents...")
        for agent_data in agents_data:
            capabilities = AgentCapabilities(**agent_data)
            result = await registry.register_agent(capabilities)
            print(f"   ✅ Registered {agent_data['agent_id']}: {result}")
        
        # Get registry statistics
        print("\n4. Registry Statistics...")
        stats = await registry.get_registry_stats()
        print(f"   📊 Total agents: {stats['total_agents']}")
        print(f"   🟢 Online agents: {stats['online_agents']}")
        print(f"   📈 Average trust score: {stats['average_trust_score']:.3f}")
        print(f"   🔧 Total capabilities: {stats['total_capabilities']}")
        
        # Demonstrate capability-based search
        print("\n5. Capability-Based Agent Discovery...")
        
        search_queries = [
            ["python"],
            ["python", "data_analysis"],
            ["web_development"],
            ["docker", "kubernetes"],
            ["nonexistent_capability"]
        ]
        
        for query in search_queries:
            agents = await registry.find_agents_by_capabilities(query)
            print(f"   🔍 Search for {query}:")
            if agents:
                for agent in agents:
                    match_score = agent.calculate_capability_match_score(query)
                    print(f"      - {agent.agent_id} (match: {match_score:.2f}, trust: {agent.trust_score:.3f})")
            else:
                print(f"      - No agents found")
        
        # Demonstrate trust score updates
        print("\n6. Trust Score Management...")
        
        # Simulate successful interactions
        print("   📈 Simulating successful interactions...")
        await registry.update_agent_trust("python_expert", success=True, response_time=2.5)
        await registry.update_agent_trust("python_expert", success=True, response_time=1.8)
        await registry.update_agent_trust("python_expert", success=True, response_time=3.2)
        
        # Simulate failed interaction
        await registry.update_agent_trust("web_developer", success=False, response_time=10.0)
        await registry.update_agent_trust("web_developer", success=True, response_time=4.0)
        
        # Show updated trust scores
        python_expert = await registry.get_agent("python_expert")
        web_developer = await registry.get_agent("web_developer")
        
        print(f"   🏆 python_expert trust score: {python_expert.trust_score:.3f} "
              f"(interactions: {python_expert.total_interactions}, "
              f"success rate: {python_expert.successful_interactions/python_expert.total_interactions:.1%})")
        
        print(f"   ⚠️  web_developer trust score: {web_developer.trust_score:.3f} "
              f"(interactions: {web_developer.total_interactions}, "
              f"success rate: {web_developer.successful_interactions/web_developer.total_interactions:.1%})")
        
        # Demonstrate availability management
        print("\n7. Availability Management...")
        
        # Set an agent as busy
        await registry.update_agent_availability("data_scientist", AgentStatus.BUSY)
        print("   🔄 Set data_scientist as BUSY")
        
        # Set an agent as offline
        await registry.update_agent_availability("devops_engineer", AgentStatus.OFFLINE)
        print("   🔴 Set devops_engineer as OFFLINE")
        
        # Show available agents
        available_agents = await registry.get_available_agents(include_offline=False)
        print(f"   🟢 Available agents ({len(available_agents)}):")
        for agent in available_agents:
            print(f"      - {agent.agent_id} ({agent.availability.value})")
        
        # Show all agents including offline
        all_agents = await registry.get_available_agents(include_offline=True)
        print(f"   📋 All agents ({len(all_agents)}):")
        for agent in all_agents:
            print(f"      - {agent.agent_id} ({agent.availability.value})")
        
        # Demonstrate agent details
        print("\n8. Agent Details...")
        agent = await registry.get_agent("python_expert")
        if agent:
            print(f"   🤖 Agent: {agent.agent_id}")
            print(f"      📋 Capabilities: {', '.join(agent.capabilities)}")
            print(f"      🎯 Specializations: {', '.join(agent.specializations)}")
            print(f"      🏆 Trust Score: {agent.trust_score:.3f}")
            print(f"      📊 Interactions: {agent.total_interactions}")
            print(f"      ⏱️  Avg Response Time: {agent.average_response_time:.2f}s")
            print(f"      🕐 Last Seen: {agent.last_seen.strftime('%H:%M:%S')}")
            print(f"      📝 Description: {agent.description}")
        
        # Final statistics
        print("\n9. Final Registry Statistics...")
        final_stats = await registry.get_registry_stats()
        print(f"   📊 Total agents: {final_stats['total_agents']}")
        print(f"   🟢 Online agents: {final_stats['online_agents']}")
        print(f"   🔴 Offline agents: {final_stats['offline_agents']}")
        print(f"   📈 Average trust score: {final_stats['average_trust_score']:.3f}")
        
        print(f"\n   🔧 Capability distribution:")
        for capability, count in final_stats['capability_distribution'].items():
            print(f"      - {capability}: {count} agents")
        
    finally:
        # Clean up
        await registry.stop_monitoring()
        print("\n✅ Demo completed successfully!")


async def demonstrate_individual_agent():
    """Demonstrate individual agent functionality."""
    
    print("\n" + "=" * 60)
    print("🤖 Individual Agent Functionality Demo")
    print("=" * 60)
    
    # Create an agent
    agent = DiscoveredAgent(
        agent_id="demo_agent",
        capabilities=["python", "machine_learning", "data_analysis"],
        specializations=["tensorflow", "pytorch"],
        description="Demo agent for testing",
        trust_score=0.7
    )
    
    print(f"\n1. Created agent: {agent.agent_id}")
    print(f"   Trust score: {agent.trust_score}")
    print(f"   Capabilities: {', '.join(agent.capabilities)}")
    
    # Test capability matching
    print("\n2. Capability Matching Tests:")
    test_queries = [
        ["python"],
        ["python", "machine_learning"],
        ["python", "web_development"],
        ["javascript"],
        []
    ]
    
    for query in test_queries:
        has_caps = agent.has_capabilities(query)
        match_score = agent.calculate_capability_match_score(query)
        print(f"   Query {query}: has_all={has_caps}, score={match_score:.3f}")
    
    # Test trust score updates
    print("\n3. Trust Score Updates:")
    print(f"   Initial trust score: {agent.trust_score:.3f}")
    
    # Simulate interactions
    interactions = [
        (True, 2.0),   # Success, 2s response
        (True, 1.5),   # Success, 1.5s response  
        (False, 8.0),  # Failure, 8s response
        (True, 3.0),   # Success, 3s response
        (True, 2.5),   # Success, 2.5s response
    ]
    
    for success, response_time in interactions:
        agent.update_trust_score(success, response_time)
        print(f"   After {'success' if success else 'failure'} ({response_time}s): "
              f"trust={agent.trust_score:.3f}, interactions={agent.total_interactions}")
    
    # Test availability
    print("\n4. Availability Testing:")
    print(f"   Is available (5min timeout): {agent.is_available(5)}")
    print(f"   Is available (0.1min timeout): {agent.is_available(0.1)}")
    
    # Test serialization
    print("\n5. Agent Serialization:")
    agent_dict = agent.to_dict()
    print(f"   Serialized keys: {list(agent_dict.keys())}")
    print(f"   Agent ID: {agent_dict['agent_id']}")
    print(f"   Trust score: {agent_dict['trust_score']}")


async def main():
    """Run all demonstrations."""
    try:
        await demonstrate_agent_discovery()
        await demonstrate_individual_agent()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())