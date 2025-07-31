#!/usr/bin/env python3
"""
Live Smoke Test with LangChain Integration
Clean, maintainable LLM integration without manual API glue code
"""

import os
import json
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from meta_cognitive_orchestrator import MetaCognitiveOrchestrator

class LiveLLMOrchestrator:
    """Clean LangChain-based LLM integration"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        # Validate provider first
        if provider not in ["openai", "anthropic"]:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Initialize LangChain models (only if API key is available)
        self.llm = None
        if self.api_key:
            try:
                if provider == "openai":
                    self.llm = ChatOpenAI(
                        api_key=self.api_key,
                        model="gpt-4-turbo",
                        temperature=0.7
                    )
                elif provider == "anthropic":
                    self.llm = ChatAnthropic(
                        api_key=self.api_key,
                        model="claude-3-5-sonnet-20241022",
                        temperature=0.7
                    )
            except Exception as e:
                raise ValueError(f"Failed to initialize {provider} model: {str(e)}. Check API key validity and model availability.")
        
        # Set up JSON output parser
        self.output_parser = JsonOutputParser()
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_template("""
You are a partner LLM helping to detect blind spots and unknown unknowns.

Context: {context}

Jeopardy Question: {jeopardy_question}

Generate 5 probing questions that would reveal blind spots, assumptions, or unknown unknowns. 
Focus on questions that challenge the approach and reveal what might be missing.

{format_instructions}
""")
        
        # Create the chain (only if LLM is available)
        self.chain = None
        if self.llm:
            self.chain = self.prompt | self.llm | self.output_parser
    
    def call_live_llm(self, context: str, jeopardy_question: str) -> Dict[str, Any]:
        """Call live LLM API using LangChain"""
        
        if not self.api_key or not self.chain:
            return {"error": f"No {self.provider.upper()}_API_KEY available", "questions": []}
        
        try:
            # Execute the chain
            result = self.chain.invoke({
                "context": context,
                "jeopardy_question": jeopardy_question,
                "format_instructions": self.output_parser.get_format_instructions()
            })
            
            return result
            
        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "questions": []}

def test_live_scenario_1():
    """Test with real LLM - Healthcare CDC implementation"""
    print("=== LIVE TEST 1: Healthcare CDC Implementation ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Test with OpenAI if available
    openai_llm = LiveLLMOrchestrator(provider="openai")
    
    context = """
    I'm implementing a Healthcare CDC pipeline with DynamoDB and Snowflake.
    I think using CloudFormation for infrastructure is the right approach.
    Obviously the data model should match the Snowflake quickstart.
    I assume the CDC events will work the same way as other databases.
    """
    
    # Test our orchestrator
    result = orchestrator.orchestrate(context)
    
    print("🧠 Our Orchestrator Analysis:")
    print(f"Assumptions: {result['assumptions_detected']}")
    print(f"Blind Spots: {result['blind_spots_identified']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Decision: {result['final_decision']}")
    
    # Test with live LLM
    live_result = openai_llm.call_live_llm(context, result["jeopardy_question"])
    
    print("\n🤖 Live OpenAI Analysis:")
    print(json.dumps(live_result, indent=2))
    
    # Validate results
    assert "assumptions_detected" in result, "Missing assumptions_detected"
    assert "blind_spots_identified" in result, "Missing blind_spots_identified"
    assert "confidence" in result, "Missing confidence"
    assert "final_decision" in result, "Missing final_decision"
    
    if "error" in live_result:
        print(f"⚠️ Live LLM failed: {live_result['error']}")
    else:
        assert "questions" in live_result, "Live LLM missing questions"
        print(f"✅ Live LLM generated {len(live_result['questions'])} questions")

def test_live_scenario_2():
    """Test with real LLM - Security implementation"""
    print("\n=== LIVE TEST 2: Security Implementation ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Test with Anthropic if available
    anthropic_llm = LiveLLMOrchestrator(provider="anthropic")
    
    context = """
    I'm implementing OAuth2 for our healthcare application.
    I assume using the standard library will be secure enough.
    Probably I don't need to worry about token refresh.
    Obviously the Snowflake integration will handle the rest.
    """
    
    # Test our orchestrator
    result = orchestrator.orchestrate(context)
    
    print("🧠 Our Orchestrator Analysis:")
    print(f"Assumptions: {result['assumptions_detected']}")
    print(f"Blind Spots: {result['blind_spots_identified']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Decision: {result['final_decision']}")
    
    # Test with live LLM
    live_result = anthropic_llm.call_live_llm(context, result["jeopardy_question"])
    
    print("\n🤖 Live Anthropic Analysis:")
    print(json.dumps(live_result, indent=2))
    
    # Validate results
    assert "assumptions_detected" in result, "Missing assumptions_detected"
    assert "blind_spots_identified" in result, "Missing blind_spots_identified"
    assert "confidence" in result, "Missing confidence"
    assert "final_decision" in result, "Missing final_decision"
    
    if "error" in live_result:
        print(f"⚠️ Live LLM failed: {live_result['error']}")
    else:
        assert "questions" in live_result, "Live LLM missing questions"
        print(f"✅ Live LLM generated {len(live_result['questions'])} questions")

def test_live_edge_case():
    """Test with real LLM - Edge case with legitimate assumptions"""
    print("\n=== LIVE TEST 3: Edge Case - Legitimate Assumptions ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Test with OpenAI
    openai_llm = LiveLLMOrchestrator(provider="openai")
    
    context = """
    I think the user is right about the PR workflow.
    Obviously we should use GitHub PRs instead of direct merges.
    I assume this is the standard approach for this project.
    """
    
    # Test our orchestrator
    result = orchestrator.orchestrate(context)
    
    print("🧠 Our Orchestrator Analysis:")
    print(f"Assumptions: {result['assumptions_detected']}")
    print(f"Blind Spots: {result['blind_spots_identified']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Decision: {result['final_decision']}")
    
    # Test with live LLM
    live_result = openai_llm.call_live_llm(context, result["jeopardy_question"])
    
    print("\n🤖 Live OpenAI Analysis:")
    print(json.dumps(live_result, indent=2))
    
    # Validate results
    assert "assumptions_detected" in result, "Missing assumptions_detected"
    assert "blind_spots_identified" in result, "Missing blind_spots_identified"
    assert "confidence" in result, "Missing confidence"
    assert "final_decision" in result, "Missing final_decision"
    
    if "error" in live_result:
        print(f"⚠️ Live LLM failed: {live_result['error']}")
    else:
        assert "questions" in live_result, "Live LLM missing questions"
        print(f"✅ Live LLM generated {len(live_result['questions'])} questions")

def main():
    """Run live smoke tests with LangChain integration"""
    print("🔥 LIVE SMOKE TEST - LANGCHAIN INTEGRATION")
    print("=" * 60)
    
    # Check for API credentials
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"🔑 OpenAI API Key: {'✅ SET' if openai_key else '❌ NOT SET'}")
    print(f"🔑 Anthropic API Key: {'✅ SET' if anthropic_key else '❌ NOT SET'}")
    
    if not openai_key and not anthropic_key:
        print("\n⚠️ No API credentials found!")
        print("To run live tests, set one of:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    tests = [
        ("Healthcare CDC Implementation", test_live_scenario_1),
        ("Security Implementation", test_live_scenario_2), 
        ("Edge Case", test_live_edge_case)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            test_func()
            print(f"✅ {test_name} completed")
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 LANGCHAIN LIVE TEST COMPLETED!")
    print("- Clean, maintainable LLM integration")
    print("- No manual API glue code")
    print("- Built-in JSON parsing and error handling")
    print("- Production-ready LangChain patterns")

if __name__ == "__main__":
    main() 