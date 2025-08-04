#!/usr/bin/env python3
"""Live LLM integration for real smoke testing"""

import os
import json
import requests
from typing import Dict, Any, Optional


class LiveLLMOrchestrator:
    """Live LLM integration for real smoke testing"""

    def __init__(self, api_key: Optional[str] = None, provider: str = "openai") -> None:
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
            return {
                "error": f"No {self.provider.upper()}_API_KEY available",
                "questions": [],
            }

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
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 500,
                    },
                    timeout=30,
                )
            elif self.provider == "anthropic":
                response = requests.post(
                    self.base_url,
                    headers={
                        "x-api-key": self.api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 500,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=30,
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


def test_live_scenario_1() -> None:
    """Test live LLM with PR workflow scenario"""
    orchestrator = LiveLLMOrchestrator()

    context = """
    I created beautiful PR markdown files but never actual GitHub PRs.
    I did git merges directly instead of creating proper GitHub Pull Requests.
    I thought git merge was the proper PR workflow.
    """

    jeopardy_question = (
        "What's the proper GitHub PR workflow? Question me about my approach."
    )

    result = orchestrator.call_live_llm(context, jeopardy_question)
    print("Live LLM Test Results:")
    print(json.dumps(result, indent=2))


def test_live_scenario_2() -> None:
    """Test live LLM with security scenario"""
    orchestrator = LiveLLMOrchestrator()

    context = """
    I implemented HTTPS enforcement but didn't consider certificate validation.
    I assumed all HTTPS connections are secure.
    """

    jeopardy_question = (
        "Am I following security best practices? Challenge my assumptions."
    )

    result = orchestrator.call_live_llm(context, jeopardy_question)
    print("Live LLM Security Test Results:")
    print(json.dumps(result, indent=2))


def test_live_edge_case() -> None:
    """Test live LLM with edge case scenario"""
    orchestrator = LiveLLMOrchestrator()

    context = """
    I'm not sure if I'm missing something important.
    This seems too simple to be correct.
    """

    jeopardy_question = "Question me about this - I can't tell if I'm confused."

    result = orchestrator.call_live_llm(context, jeopardy_question)
    print("Live LLM Edge Case Test Results:")
    print(json.dumps(result, indent=2))


def compare_live_results(our_result: Dict, live_result: Dict) -> Dict[str, Any]:
    """Compare our analysis with live LLM results"""
    comparison = {
        "our_confidence": our_result.get("confidence", 0.0),
        "live_confidence": live_result.get("confidence", 0.0),
        "our_blind_spots": our_result.get("blind_spots", []),
        "live_blind_spots": live_result.get("blind_spots", []),
        "live_questions": live_result.get("questions", []),
        "agreement": False,
        "recommendation": "ASK_HUMAN",
    }

    # Check if both agree on confidence level
    our_conf = comparison["our_confidence"]
    live_conf = comparison["live_confidence"]

    if abs(our_conf - live_conf) < 0.2:
        comparison["agreement"] = True
        if our_conf > 0.7 and live_conf > 0.7:
            comparison["recommendation"] = "PROCEED"
        else:
            comparison["recommendation"] = "INVESTIGATE"

    return comparison


if __name__ == "__main__":
    print("🧪 Live LLM Smoke Testing")
    print("=" * 50)

    test_live_scenario_1()
    print("\n" + "=" * 50)
    test_live_scenario_2()
    print("\n" + "=" * 50)
    test_live_edge_case()
