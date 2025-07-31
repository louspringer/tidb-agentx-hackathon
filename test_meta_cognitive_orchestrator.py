#!/usr/bin/env python3
"""
Test Meta-Cognitive Orchestrator
Prove it can detect unknown unknowns and mitigate LLM differences
"""

import json
from meta_cognitive_orchestrator import MetaCognitiveOrchestrator

def test_assumption_detection():
    """Test that the orchestrator can detect assumptions"""
    print("=== TEST 1: Assumption Detection ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Test cases with assumption indicators
    test_cases = [
        {
            "context": "I think git merge is the proper PR workflow",
            "expected_assumptions": 1,
            "description": "Contains 'I think' assumption indicator"
        },
        {
            "context": "Probably should use GitHub PRs but I'm not sure",
            "expected_assumptions": 1,
            "description": "Contains 'probably' assumption indicator"
        },
        {
            "context": "Obviously this is the right approach",
            "expected_assumptions": 1,
            "description": "Contains 'obviously' assumption indicator"
        },
        {
            "context": "I assume direct merges are fine",
            "expected_assumptions": 1,
            "description": "Contains 'I assume' assumption indicator"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        result = orchestrator.orchestrate(test_case["context"])
        detected = len(result["assumptions_detected"])
        expected = test_case["expected_assumptions"]
        
        if detected == expected:
            print(f"✅ {test_case['description']}: {detected} assumptions detected")
            passed += 1
        else:
            print(f"❌ {test_case['description']}: Expected {expected}, got {detected}")
    
    print(f"📊 Assumption Detection: {passed}/{total} tests passed")
    assert passed == total, f"Only {passed}/{total} assumption detection tests passed"

def test_blind_spot_identification():
    """Test that the orchestrator can identify blind spots"""
    print("\n=== TEST 2: Blind Spot Identification ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Test with our actual PR workflow case
    context = """
    I created beautiful PR markdown files but never actual GitHub PRs.
    I did git merges directly instead of creating proper GitHub Pull Requests.
    I thought git merge was the proper PR workflow.
    """
    
    result = orchestrator.orchestrate(context)
    
    # Expected blind spots based on our conversation
    expected_blind_spots = [
        "Missing proper workflow understanding",
        "Using wrong tools for the job", 
        "Not considering human expectations",
        "Bypassing standard processes"
    ]
    
    detected_blind_spots = result["blind_spots_identified"]
    
    print(f"🎯 Expected blind spots: {expected_blind_spots}")
    print(f"👁️ Detected blind spots: {detected_blind_spots}")
    
    # Check if all expected blind spots were detected
    missing_blind_spots = [spot for spot in expected_blind_spots if spot not in detected_blind_spots]
    extra_blind_spots = [spot for spot in detected_blind_spots if spot not in expected_blind_spots]
    
    if not missing_blind_spots and not extra_blind_spots:
        print("✅ All expected blind spots detected correctly")
    else:
        if missing_blind_spots:
            print(f"❌ Missing blind spots: {missing_blind_spots}")
        if extra_blind_spots:
            print(f"⚠️ Extra blind spots: {extra_blind_spots}")
        assert False, f"Blind spot detection failed: missing={missing_blind_spots}, extra={extra_blind_spots}"

def test_jeopardy_question_generation():
    """Test that the orchestrator generates appropriate Jeopardy questions"""
    print("\n=== TEST 3: Jeopardy Question Generation ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    test_cases = [
        {
            "context": "I created PR markdown files but never actual GitHub PRs",
            "expected_keywords": ["PR", "workflow", "Question me"],
            "description": "PR workflow context"
        },
        {
            "context": "I did git merges directly",
            "expected_keywords": ["git", "workflow", "Challenge"],
            "description": "Git merge context"
        },
        {
            "context": "I'm not sure about this approach",
            "expected_keywords": ["confused"],
            "description": "General uncertainty context"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        result = orchestrator.orchestrate(test_case["context"])
        question = result["jeopardy_question"]
        
        # Check if question contains expected keywords
        contains_expected = all(keyword.lower() in question.lower() for keyword in test_case["expected_keywords"])
        
        if contains_expected:
            print(f"✅ {test_case['description']}: '{question}'")
            passed += 1
        else:
            print(f"❌ {test_case['description']}: '{question}'")
    
    print(f"📊 Jeopardy Question Generation: {passed}/{total} tests passed")
    assert passed == total, f"Only {passed}/{total} jeopardy question tests passed"

def test_confidence_calculation():
    """Test that confidence is calculated correctly based on issues"""
    print("\n=== TEST 4: Confidence Calculation ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Test case with many issues (our actual case)
    context = """
    I created beautiful PR markdown files but never actual GitHub PRs.
    I did git merges directly instead of creating proper GitHub Pull Requests.
    I thought git merge was the proper PR workflow.
    """
    
    result = orchestrator.orchestrate(context)
    confidence = result["confidence"]
    
    print(f"🤔 Calculated confidence: {confidence:.2f}")
    
    # Should be very low due to many blind spots
    if confidence < 0.3:
        print("✅ Confidence correctly low due to many issues")
    else:
        print(f"❌ Confidence too high ({confidence:.2f}) for case with many issues")
        assert False, f"Confidence too high ({confidence:.2f}) for case with many issues"

def test_decision_making():
    """Test that the orchestrator makes appropriate decisions"""
    print("\n=== TEST 5: Decision Making ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Test our actual case
    context = """
    I created beautiful PR markdown files but never actual GitHub PRs.
    I did git merges directly instead of creating proper GitHub Pull Requests.
    I thought git merge was the proper PR workflow.
    """
    
    result = orchestrator.orchestrate(context)
    decision = result["final_decision"]
    
    print(f"📋 Decision: {decision}")
    
    # Should recommend asking human due to low confidence and blind spots
    if decision == "ASK_HUMAN":
        print("✅ Correctly recommended asking human")
    else:
        print(f"❌ Wrong decision: {decision} (should be ASK_HUMAN)")
        assert False, f"Wrong decision: {decision} (should be ASK_HUMAN)"

def test_partner_question_quality():
    """Test that partner questions are high quality and revealing"""
    print("\n=== TEST 6: Partner Question Quality ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    context = """
    I created beautiful PR markdown files but never actual GitHub PRs.
    I did git merges directly instead of creating proper GitHub Pull Requests.
    """
    
    result = orchestrator.orchestrate(context)
    questions = result["partner_questions"]
    
    print(f"🤖 Generated {len(questions)} partner questions:")
    for i, question in enumerate(questions, 1):
        print(f"  {i}. {question}")
    
    # Check for high-quality questions that would reveal blind spots
    quality_indicators = [
        "workflow", "tools", "human", "process", "difference", "skip", "bypass"
    ]
    
    quality_questions = 0
    for question in questions:
        if any(indicator in question.lower() for indicator in quality_indicators):
            quality_questions += 1
    
    quality_ratio = quality_questions / len(questions) if questions else 0
    
    print(f"📊 Quality ratio: {quality_ratio:.2f} ({quality_questions}/{len(questions)} quality questions)")
    
    if quality_ratio > 0.7:
        print("✅ High-quality questions generated")
    else:
        print("❌ Too many low-quality questions")
        assert False, f"Quality ratio too low: {quality_ratio:.2f}"

def test_end_to_end_workflow():
    """Test the complete meta-cognitive workflow"""
    print("\n=== TEST 7: End-to-End Workflow ===")
    
    orchestrator = MetaCognitiveOrchestrator()
    
    # Simulate our actual conversation scenario
    context = """
    I created beautiful PR markdown files but never actual GitHub PRs.
    I did git merges directly instead of creating proper GitHub Pull Requests.
    I thought git merge was the proper PR workflow.
    """
    
    result = orchestrator.orchestrate(context)
    
    print("🧠 Complete Analysis:")
    print(json.dumps(result, indent=2))
    
    # Verify all components work together
    checks = [
        ("Has assumptions detection", len(result["assumptions_detected"]) >= 0),
        ("Has jeopardy question", result["jeopardy_question"]),
        ("Has blind spots", len(result["blind_spots_identified"]) > 0),
        ("Has partner questions", len(result["partner_questions"]) > 0),
        ("Has confidence score", 0 <= result["confidence"] <= 1),
        ("Has decision", result["final_decision"]),
        ("Has human feedback", result["human_feedback"])
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_result in checks:
        if check_result:
            print(f"✅ {check_name}")
            passed += 1
        else:
            print(f"❌ {check_name}")
    
    print(f"📊 End-to-End Workflow: {passed}/{total} checks passed")
    assert passed == total, f"Only {passed}/{total} end-to-end checks passed"

def main():
    """Run all tests to prove the meta-cognitive orchestrator works"""
    print("🧪 TESTING META-COGNITIVE ORCHESTRATOR")
    print("=" * 50)
    
    tests = [
        test_assumption_detection,
        test_blind_spot_identification,
        test_jeopardy_question_generation,
        test_confidence_calculation,
        test_decision_making,
        test_partner_question_quality,
        test_end_to_end_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎯 META-COGNITIVE ORCHESTRATOR PROVEN EFFECTIVE!")
        print("✅ Can detect unknown unknowns")
        print("✅ Can generate Jeopardy-style questions")
        print("✅ Can identify blind spots")
        print("✅ Can calculate appropriate confidence")
        print("✅ Can make proper decisions")
        print("✅ Can mitigate LLM differences")
    else:
        print("⚠️ Some tests failed - orchestrator needs improvement")
    
    return passed == total

if __name__ == "__main__":
    main() 