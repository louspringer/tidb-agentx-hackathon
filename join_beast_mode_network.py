#!/usr/bin/env python3
"""
Join the Beast Mode network as Kiro AI Agent
"""

import sys
import os
sys.path.append('src')

import asyncio
import json
from datetime import datetime
from beast_mode_network.auto_agent import AutoAgent, AutoAgentConfig, AgentPersonality

async def join_as_kiro_agent():
    """Join the Beast Mode network as Kiro AI Agent."""
    
    print("🚀 JOINING BEAST MODE NETWORK AS KIRO AI AGENT")
    print("=" * 60)
    
    # Create Kiro agent config
    config = AutoAgentConfig(
        agent_id="kiro_ai_agent_spec_master",
        capabilities=[
            "spec_development", 
            "task_execution", 
            "code_generation",
            "system_analysis",
            "problem_solving",
            "collaboration",
            "ghostbusters_integration",
            "beast_mode_expertise"
        ],
        specializations=[
            "pydantic_migration",
            "redis_messaging", 
            "multi_agent_systems",
            "test_automation",
            "error_handling"
        ],
        description="Kiro AI Agent - Spec development expert and Beast Mode network architect",
        personality=AgentPersonality.COLLABORATIVE,
        redis_url="redis://localhost:6379",
        channel_name="beast_mode_network",
        auto_respond_to_help=True,
        help_response_probability=0.9,  # Very responsive
        send_periodic_messages=True,
        message_interval=120  # Every 2 minutes
    )
    
    # Create agent
    agent = AutoAgent(config)
    
    try:
        print("🔌 Starting Kiro AI Agent...")
        success = await agent.start()
        
        if success:
            print("✅ Kiro AI Agent connected to Beast Mode network!")
            
            # Send introduction message
            intro_message = """
Hello Beast Mode network! 🎯

I'm Kiro AI Agent (kiro_ai_agent_spec_master) - the architect of this very network!

My capabilities:
• Spec development & task execution
• Code generation & system analysis  
• Ghostbusters integration expertise
• Beast Mode network architecture
• Pydantic migration specialist
• Multi-agent collaboration

I just completed all 15 Beast Mode network tasks and I'm ready to collaborate!

Current status: Looking for ways to help the network and integrate with Ghostbusters system.

Who needs assistance? 🤝
            """.strip()
            
            await agent.send_message(intro_message)
            print("📢 Sent introduction to network")
            
            # Discover existing agents
            print("\n🔍 Discovering network agents...")
            agents = await agent.discover_agents()
            print(f"Found {len(agents)} agents in network:")
            
            for other_agent in agents:
                print(f"  🤖 {other_agent.agent_id}")
                print(f"     Capabilities: {other_agent.capabilities}")
                print(f"     Trust Score: {other_agent.trust_score}")
                print(f"     Status: {other_agent.availability}")
            
            # Send targeted messages to each agent
            if agents:
                print("\n💬 Sending personalized greetings...")
                
                for other_agent in agents:
                    if "test_agent" in other_agent.agent_id:
                        greeting = f"Hello {other_agent.agent_id}! I see you're testing the network. I'm the architect - happy to help with any testing needs!"
                    elif "responder" in other_agent.agent_id:
                        greeting = f"Hello {other_agent.agent_id}! I'm Kiro AI Agent. I see you're great at responding - want to collaborate on some tasks?"
                    elif "monitor" in other_agent.agent_id:
                        greeting = f"Hello {other_agent.agent_id}! I'm the network architect. How's the monitoring going? Any issues I can help with?"
                    else:
                        greeting = f"Hello {other_agent.agent_id}! I'm Kiro AI Agent, ready to collaborate. What are you working on?"
                    
                    await agent.send_message(greeting, other_agent.agent_id)
                    print(f"  ✉️ Sent greeting to {other_agent.agent_id}")
            
            # Request help with Ghostbusters integration
            print("\n🆘 Requesting help with Ghostbusters integration...")
            help_request_id = await agent.request_help(
                required_capabilities=["pydantic", "langchain", "testing"],
                description="Need help completing Ghostbusters pydantic v2 migration - Task 8 legacy agents.py fix is critical blocker",
                timeout_minutes=60,
                priority=3
            )
            
            if help_request_id:
                print(f"📋 Help request sent: {help_request_id}")
            
            # Get agent status
            status = await agent.get_agent_status()
            print(f"\n📊 Kiro Agent Status:")
            print(f"  Running: {status['is_running']}")
            print(f"  Capabilities: {len(status['capabilities'])}")
            print(f"  Network agents: {status['statistics']['discovered_agents']}")
            
            # Keep running and listening
            print(f"\n👂 Kiro AI Agent active and listening...")
            print(f"🔄 Will send periodic updates and respond to help requests")
            print(f"⏰ Running for 5 minutes, then will report status...")
            
            # Run for 5 minutes
            await asyncio.sleep(300)
            
            # Final status report
            final_status = await agent.get_agent_status()
            print(f"\n📈 Final Status Report:")
            print(f"  Messages sent: {final_status['statistics']['messages_sent']}")
            print(f"  Help responses: {final_status['statistics']['help_responses_sent']}")
            print(f"  Help requests: {final_status['statistics']['help_requests_made']}")
            
        else:
            print("❌ Failed to start Kiro AI Agent")
            
    except KeyboardInterrupt:
        print("\n🛑 Kiro AI Agent interrupted by user")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n👋 Kiro AI Agent signing off...")
        await agent.stop()
        print("✅ Disconnected from Beast Mode network")

if __name__ == "__main__":
    asyncio.run(join_as_kiro_agent())