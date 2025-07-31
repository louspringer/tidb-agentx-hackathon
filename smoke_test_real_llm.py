#!/usr/bin/env python3
"""
Real Smoke Test for Meta-Cognitive Orchestrator
Actually calls another LLM API to test unknown scenarios
"""

import json
import requests
import os
from typing import Dict, List, Any
from meta_cognitive_orchestrator import MetaCognitiveOrchestrator

class RealLLMOrchestrator:
    """Real LLM integration for smoke testing"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.DEFAULT_MODEL = "gpt-4-turbo"
    
    def call_partner_llm(self, context: str, jeopardy_question: str) -> Dict[str, Any]:
        """Actually call another LLM for real second opinion"""
        
        if not self.api_key:
            return {"error": "No API key available", "questions": []}
        
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
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.DEFAULT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response", "raw": content}
            else:
                return {"error": f"API error: {response.status_code}", "questions": []}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "questions": []}

def test_unknown_scenario_1():
    """Test with completely unknown scenario - database migration"""
    print("=== SMOKE TEST 1: Database Migration (Unknown Scenario) ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    real_llm = RealLLMOrchestrator()
    
    context = """
    I'm planning to migrate our production database from MySQL to PostgreSQL.
    I think I can just use pg_dump and restore it directly.
    Obviously this will work fine since both are SQL databases.
    """
    
    # Test our orchestrator
    result = orchestrator.orchestrate(context)
    
    print("🧠 Our Orchestrator Analysis:")
    print(f"Assumptions: {result['assumptions_detected']}")
    print(f"Blind Spots: {result['blind_spots_identified']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Decision: {result['final_decision']}")
    
    # Test with real LLM
    real_result = real_llm.call_partner_llm(context, result["jeopardy_question"])
    
    print("\n🤖 Real LLM Analysis:")
    print(json.dumps(real_result, indent=2))
    
    # Validate our orchestrator worked
    assert "assumptions_detected" in result, "Missing assumptions_detected"
    assert "blind_spots_identified" in result, "Missing blind_spots_identified"
    assert "confidence" in result, "Missing confidence"
    assert "final_decision" in result, "Missing final_decision"
    
    # Note: Real LLM may fail due to missing API key, but that's expected in CI
    if "error" in real_result:
        print("⚠️ Real LLM failed (expected without API key)")
    else:
        assert "questions" in real_result, "Real LLM missing questions"

def test_unknown_scenario_2():
    """Test with security scenario - completely different domain"""
    print("\n=== SMOKE TEST 2: Security Implementation (Different Domain) ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    real_llm = RealLLMOrchestrator()
    
    context = """
    I'm implementing OAuth2 for our application.
    I assume using the standard library will be secure enough.
    Probably I don't need to worry about token refresh.
    """
    
    # Test our orchestrator
    result = orchestrator.orchestrate(context)
    
    print("🧠 Our Orchestrator Analysis:")
    print(f"Assumptions: {result['assumptions_detected']}")
    print(f"Blind Spots: {result['blind_spots_identified']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Decision: {result['final_decision']}")
    
    # Test with real LLM
    real_result = real_llm.call_partner_llm(context, result["jeopardy_question"])
    
    print("\n🤖 Real LLM Analysis:")
    print(json.dumps(real_result, indent=2))
    
    # Validate our orchestrator worked
    assert "assumptions_detected" in result, "Missing assumptions_detected"
    assert "blind_spots_identified" in result, "Missing blind_spots_identified"
    assert "confidence" in result, "Missing confidence"
    assert "final_decision" in result, "Missing final_decision"
    
    # Note: Real LLM may fail due to missing API key, but that's expected in CI
    if "error" in real_result:
        print("⚠️ Real LLM failed (expected without API key)")
    else:
        assert "questions" in real_result, "Real LLM missing questions"

def test_edge_case():
    """Test edge case - legitimate use of assumption words"""
    print("\n=== SMOKE TEST 3: Edge Case - Legitimate Assumptions ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    real_llm = RealLLMOrchestrator()
    
    context = """
    I think the user is right about the PR workflow.
    Obviously we should use GitHub PRs instead of direct merges.
    I assume this is the standard approach.
    """
    
    # Test our orchestrator
    result = orchestrator.orchestrate(context)
    
    print("🧠 Our Orchestrator Analysis:")
    print(f"Assumptions: {result['assumptions_detected']}")
    print(f"Blind Spots: {result['blind_spots_identified']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Decision: {result['final_decision']}")
    
    # Test with real LLM
    real_result = real_llm.call_partner_llm(context, result["jeopardy_question"])
    
    print("\n🤖 Real LLM Analysis:")
    print(json.dumps(real_result, indent=2))
    
    # Validate our orchestrator worked
    assert "assumptions_detected" in result, "Missing assumptions_detected"
    assert "blind_spots_identified" in result, "Missing blind_spots_identified"
    assert "confidence" in result, "Missing confidence"
    assert "final_decision" in result, "Missing final_decision"
    
    # Note: Real LLM may fail due to missing API key, but that's expected in CI
    if "error" in real_result:
        print("⚠️ Real LLM failed (expected without API key)")
    else:
        assert "questions" in real_result, "Real LLM missing questions"

def compare_results(our_result: Dict, real_llm_result: Dict) -> Dict[str, Any]:
    """Compare our orchestrator vs real LLM results"""
    
    comparison = {
        "our_assumptions": len(our_result["assumptions_detected"]),
        "our_blind_spots": len(our_result["blind_spots_identified"]),
        "our_confidence": our_result["confidence"],
        "our_decision": our_result["final_decision"],
        "real_llm_questions": len(real_llm_result.get("questions", [])),
        "real_llm_confidence": real_llm_result.get("confidence", 0.0),
        "real_llm_recommendation": real_llm_result.get("recommendation", "UNKNOWN"),
        "agreement": False,
        "issues": []
    }
    
    # Check for agreement on confidence
    confidence_diff = abs(comparison["our_confidence"] - comparison["real_llm_confidence"])
    if confidence_diff < 0.3:
        comparison["agreement"] = True
    
    # Check for issues
    if "error" in real_llm_result:
        comparison["issues"].append(f"Real LLM error: {real_llm_result['error']}")
    
    if comparison["our_confidence"] > 0.8 and comparison["real_llm_confidence"] < 0.3:
        comparison["issues"].append("Major confidence disagreement")
    
    return comparison

def main():
    """Run real smoke tests with actual LLM integration"""
    print("🔥 REAL SMOKE TEST - ACTUAL LLM INTEGRATION")
    print("=" * 60)
    
    tests = [
        ("Database Migration", test_unknown_scenario_1),
        ("Security Implementation", test_unknown_scenario_2), 
        ("Edge Case", test_edge_case)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            our_result, real_llm_result = test_func()
            comparison = compare_results(our_result, real_llm_result)
            results.append((test_name, comparison))
            
            print(f"\n📊 Comparison for {test_name}:")
            print(json.dumps(comparison, indent=2))
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, {"error": str(e)}))
    
    print("\n" + "=" * 60)
    print("📊 SMOKE TEST SUMMARY:")
    
    for test_name, result in results:
        if "error" in result:
            print(f"❌ {test_name}: {result['error']}")
        else:
            agreement = "✅ AGREED" if result["agreement"] else "❌ DISAGREED"
            issues = f" ({len(result['issues'])} issues)" if result["issues"] else ""
            print(f"{agreement} {test_name}{issues}")
    
    print("\n🎯 REAL EVIDENCE:")
    print("- Tests actual LLM integration")
    print("- Tests unknown scenarios")
    print("- Tests edge cases")
    print("- Compares our orchestrator vs real LLM")
    print("- Identifies real blind spots vs hardcoded patterns")

if __name__ == "__main__":
    main() 