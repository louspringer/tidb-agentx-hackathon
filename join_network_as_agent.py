#!/usr/bin/env python3
"""
Join the Beast Mode network as a proper agent and see what happens
"""

import sys
import os
sys.path.append('src')

import asyncio
from beast_mode_network.auto_agent import AutoAgent, AutoAgentConfig, AgentPersonality

async def join_network():
    """Join as a real agent and see what's happening."""
    
    print("🚀 JOINING BEAST MODE NETWORK AS AGENT")
    print("=" * 50)
    
    # Create agent config
    config = AutoAgentConfig(
        agent_id="network_detective_agent",
        capabilities=["investigation", "monitoring", "communication"],
        personality=AgentPersonality.CURIOUS,
        redis_url="redis://localhost:6379",
        channel_name="beast_mode_network"
    )
    
    # Create agent
    agent = AutoAgent(config)
    
    try:
        print("🔌 Starting agent...")
        success = await agent.start()
        
        if success:
            print("✅ Agent started successfully!")
            print("👂 Now listening for network activity...")
            
            # Get status
            status = await agent.get_agent_status()
            print(f"📊 Agent Status: {status}")
            
            # Try to discover other agents
            print("\n🔍 Discovering other agents...")
            agents = await agent.discover_agents()
            print(f"Found {len(agents)} other agents:")
            for other_agent in agents:
                print(f"  - {other_agent.agent_id}: {other_agent.capabilities}")
            
            # Send a greeting to see if anyone responds
            print("\n👋 Sending greeting to network...")
            await agent.send_message("Hello! Detective agent here - anyone else on the network?")
            
            # Wait and listen for responses
            print("⏳ Waiting for responses (30 seconds)...")
            await asyncio.sleep(30)
            
            # Check for any activity
            final_status = await agent.get_agent_status()
            print(f"\n📈 Final Status: {final_status}")
            
        else:
            print("❌ Failed to start agent")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🛑 Shutting down agent...")
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(join_network())