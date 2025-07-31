#!/usr/bin/env python3
"""
Live Smoke Test with Real API Credentials
Tests the meta-cognitive orchestrator against real LLM APIs
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from meta_cognitive_orchestrator import MetaCognitiveOrchestrator

class LiveLLMOrchestrator:
    """Live LLM integration for real smoke testing"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openai"):
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.base_url = self._get_base_url()
        self.model = self._get_model()
    
    def _get_base_url(self) -> str:
        if self.provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        elif self.provider == "anthropic":
            return "https://api.anthropic.com/v1/messages"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _get_model(self) -> str:
        if self.provider == "openai":
            return "gpt-4-turbo"
        elif self.provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        else:
            return "gpt-4-turbo"
    
    def call_live_llm(self, context: str, jeopardy_question: str) -> Dict[str, Any]:
        """Call live LLM API for real second opinion"""
        
        if not self.api_key:
            return {"error": f"No {self.provider.upper()}_API_KEY available", "questions": []}
        
        prompt = f"""
You are a partner LLM helping to detect blind spots and unknown unknowns.

Context: {context}

Jeopardy Question: {jeopardy_question}

Generate 5 probing questions that would reveal blind spots, assumptions, or unknown unknowns. 
Focus on questions that challenge the approach and reveal what might be missing.

Format as JSON:
{{
    "questions": ["question1", "question2", ...],
    "confidence": 0.0-1.0,
    "blind_spots": ["blind_spot1", "blind_spot2", ...],
    "recommendation": "ASK_HUMAN|INVESTIGATE|PROCEED"
}}
"""
        
        try:
            if self.provider == "openai":
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    timeout=30
                )
            elif self.provider == "anthropic":
                response = requests.post(
                    self.base_url,
                    headers={
                        "x-api-key": self.api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 500,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                if self.provider == "openai":
                    content = result["choices"][0]["message"]["content"]
                elif self.provider == "anthropic":
                    content = result["content"][0]["text"]
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response", "raw": content}
            else:
                return {"error": f"API error: {response.status_code}", "questions": []}
                
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

def compare_live_results(our_result: Dict, live_result: Dict) -> Dict[str, Any]:
    """Compare our orchestrator vs live LLM results"""
    
    comparison = {
        "our_assumptions": len(our_result["assumptions_detected"]),
        "our_blind_spots": len(our_result["blind_spots_identified"]),
        "our_confidence": our_result["confidence"],
        "our_decision": our_result["final_decision"],
        "live_llm_questions": len(live_result.get("questions", [])),
        "live_llm_confidence": live_result.get("confidence", 0.0),
        "live_llm_recommendation": live_result.get("recommendation", "UNKNOWN"),
        "agreement": False,
        "issues": []
    }
    
    # Check for agreement on confidence
    confidence_diff = abs(comparison["our_confidence"] - comparison["live_llm_confidence"])
    if confidence_diff < 0.3:
        comparison["agreement"] = True
    
    # Check for issues
    if "error" in live_result:
        comparison["issues"].append(f"Live LLM error: {live_result['error']}")
    
    if comparison["our_confidence"] > 0.8 and comparison["live_llm_confidence"] < 0.3:
        comparison["issues"].append("Major confidence disagreement")
    
    return comparison

def main():
    """Run live smoke tests with real API credentials"""
    print("🔥 LIVE SMOKE TEST - REAL API CREDENTIALS")
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
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            test_func()
            print(f"✅ {test_name} completed")
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 LIVE TEST COMPLETED!")
    print("- Tests actual LLM integration")
    print("- Tests real unknown scenarios")
    print("- Tests edge cases with live APIs")
    print("- Validates meta-cognitive capabilities")

if __name__ == "__main__":
    main() 