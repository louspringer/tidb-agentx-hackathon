#!/usr/bin/env python3
"""Meta-Cognitive Orchestrator for LLM self-awareness"""

from typing import List, Dict, Any


class MetaCognitiveOrchestrator:
    """Orchestrates meta-cognitive awareness through partner LLM questioning"""

    def __init__(self, confidence_threshold: float = 0.7) -> None:
        self.confidence_threshold = confidence_threshold
        self.uncertainty_indicators = [
            "I think",
            "probably",
            "should be",
            "obviously",
            "I assume",
            "I guess",
            "maybe",
            "I believe",
        ]

    def detect_assumptions(self, context: str) -> List[str]:
        """Detect when I'm making assumptions or missing information"""
        detected_assumptions = []
        for indicator in self.uncertainty_indicators:
            if indicator.lower() in context.lower():
                detected_assumptions.append(
                    f"Using assumption indicator: '{indicator}'"
                )
        return detected_assumptions

    def generate_jeopardy_question(self, context: str) -> str:
        """Generate Jeopardy-style question for partner LLM"""
        if "PR" in context or "pull request" in context:
            return (
                "What's the proper GitHub PR workflow? Question me about my approach."
            )
        elif "git" in context or "merge" in context:
            return "Am I following standard git workflow? Challenge my assumptions."
        else:
            return "Question me about this - I can't tell if I'm confused."

    def simulate_partner_investigation(self, context: str) -> List[str]:
        """Simulate partner LLM investigation with Jeopardy-style questions"""
        partner_questions = []

        if "PR" in context:
            partner_questions.extend(
                [
                    "What workflow were you following?",
                    "Did you create actual GitHub PRs or just merge directly?",
                    "What tools did you use for this task?",
                    "What would a human expect you to do?",
                    "What's the standard process here?",
                ]
            )

        if "git merge" in context:
            partner_questions.extend(
                [
                    "What's the difference between git merge and GitHub PR?",
                    "Why did you skip the PR creation step?",
                    "What review process did you bypass?",
                    "What would a human expect for this workflow?",
                ]
            )

        return partner_questions

    def identify_blind_spots(self, partner_questions: List[str]) -> List[str]:
        """Analyze partner LLM feedback and identify blind spots"""
        blind_spots = []

        for question in partner_questions:
            if "workflow" in question.lower():
                blind_spots.append("Missing proper workflow understanding")
            if "tools" in question.lower():
                blind_spots.append("Using wrong tools for the job")
            if "human" in question.lower():
                blind_spots.append("Not considering human expectations")
            if "process" in question.lower():
                blind_spots.append("Bypassing standard processes")

        return blind_spots

    def calculate_confidence(
        self, assumptions: List[str], blind_spots: List[str]
    ) -> float:
        """Calculate confidence based on detected issues"""
        confidence = 1.0
        confidence -= len(assumptions) * 0.2
        confidence -= len(blind_spots) * 0.3

        return max(0.0, confidence)

    def make_decision(self, confidence: float, blind_spots: List[str]) -> str:
        """Make final decision based on confidence and blind spots"""
        if confidence < self.confidence_threshold or blind_spots:
            return "ASK_HUMAN"
        elif blind_spots:
            return "INVESTIGATE_BLIND_SPOTS"
        else:
            return "PROCEED_WITH_CAUTION"

    def orchestrate(self, context: str) -> Dict[str, Any]:
        """Orchestrate meta-cognitive awareness for a given context"""
        # Detect assumptions
        assumptions = self.detect_assumptions(context)

        # Generate Jeopardy question
        jeopardy_question = self.generate_jeopardy_question(context)

        # Simulate partner investigation
        partner_questions = self.simulate_partner_investigation(context)

        # Identify blind spots
        blind_spots = self.identify_blind_spots(partner_questions)

        # Calculate confidence
        confidence = self.calculate_confidence(assumptions, blind_spots)

        # Make decision
        final_decision = self.make_decision(confidence, blind_spots)

        return {
            "assumptions": assumptions,
            "jeopardy_question": jeopardy_question,
            "partner_questions": partner_questions,
            "blind_spots": blind_spots,
            "confidence": confidence,
            "decision": final_decision,
        }


def test_meta_cognitive_orchestrator() -> None:
    """Test the meta-cognitive orchestrator"""
    orchestrator = MetaCognitiveOrchestrator()

    # Test with different contexts
    test_contexts = [
        "I think I should create a PR for this change",
        "I'll just merge directly to main",
        "This should be obvious to implement",
    ]

    for context in test_contexts:
        print(f"\nContext: {context}")
        result = orchestrator.orchestrate(context)
        print(f"Decision: {result['decision']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Assumptions: {result['assumptions']}")
        print(f"Blind spots: {result['blind_spots']}")


if __name__ == "__main__":
    test_meta_cognitive_orchestrator()
