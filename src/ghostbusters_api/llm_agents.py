#!/usr/bin/env python3
"""
LLM-Enhanced Ghostbusters Agents
Use LLMs to enhance the rule-based agents with AI-powered analysis
"""

import json
import logging
from typing import Any, Optional

import requests

from .agents import (
    ArchitectureExpert,
    BuildExpert,
    CodeQualityExpert,
    DelusionResult,
    ModelExpert,
    SecurityExpert,
    TestExpert,
)
from .secret_manager import get_anthropic_api_key, get_openai_api_key

logger = logging.getLogger(__name__)


class LLMEnhancedAgent:
    """Base class for LLM-enhanced agents"""

    def __init__(self, base_agent, llm_provider: str = "openai"):  # type: ignore
        self.base_agent = base_agent
        self.llm_provider = llm_provider
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> Optional[str]:
        """Get API key for the specified LLM provider"""
        if self.llm_provider == "openai":
            return get_openai_api_key()
        if self.llm_provider == "anthropic":
            return get_anthropic_api_key()
        logger.warning(f"Unknown LLM provider: {self.llm_provider}")
        return None

    def _call_llm(self, prompt: str, context: str) -> Optional[str]:
        """Call LLM with the given prompt and context"""
        if not self.api_key:
            logger.warning(f"No API key available for {self.llm_provider}")
            return None

        try:
            if self.llm_provider == "openai":
                return self._call_openai(prompt, context)
            if self.llm_provider == "anthropic":
                return self._call_anthropic(prompt, context)
            logger.warning(f"Unsupported LLM provider: {self.llm_provider}")
            return None
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None

    def _call_openai(self, prompt: str, context: str) -> Optional[str]:
        """Call OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code analyst. Analyze the provided code and context to identify potential issues, security vulnerabilities, and areas for improvement.",
                },
                {"role": "user", "content": f"Context: {context}\n\nPrompt: {prompt}"},
            ],
            "temperature": 0.3,
            "max_tokens": 1000,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]  # type: ignore

    def _call_anthropic(self, prompt: str, context: str) -> Optional[str]:
        """Call Anthropic API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": f"Context: {context}\n\nPrompt: {prompt}"},
            ],
        }

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()
        return result["content"][0]["text"]  # type: ignore

    async def detect_delusions(self, project_path) -> DelusionResult:  # type: ignore
        """Run base agent and enhance with LLM analysis"""
        # Run the base agent first
        base_result = await self.base_agent.detect_delusions(project_path)

        # If no LLM available, return base result
        if not self.api_key:
            logger.info("No LLM API key available, using base agent only")
            return base_result  # type: ignore

        # Enhance with LLM analysis
        try:
            llm_analysis = await self._enhance_with_llm(project_path, base_result)
            if llm_analysis:
                # Merge LLM findings with base findings
                enhanced_delusions = base_result.delusions + llm_analysis.get(
                    "delusions",
                    [],
                )
                enhanced_recommendations = (
                    base_result.recommendations
                    + llm_analysis.get("recommendations", [])
                )

                return DelusionResult(
                    delusions=enhanced_delusions,
                    confidence=max(
                        base_result.confidence,
                        llm_analysis.get("confidence", 0.0),
                    ),
                    recommendations=enhanced_recommendations,
                )
        except Exception as e:
            logger.error(f"Error enhancing with LLM: {e}")

        return base_result  # type: ignore

    async def _enhance_with_llm(  # type: ignore
        self,
        project_path,
        base_result: DelusionResult,
    ) -> Optional[dict[str, Any]]:
        """Enhance base results with LLM analysis"""
        # Create context from base results
        context = f"""
Project Path: {project_path}
Base Findings: {len(base_result.delusions)} delusions found
Base Recommendations: {base_result.recommendations}
Base Confidence: {base_result.confidence}
        """

        # Create prompt for LLM
        prompt = f"""
You are an expert code analyst. The base analysis found {len(base_result.delusions)} issues.

Please provide additional analysis focusing on:
1. Edge cases and scenarios the base analysis might have missed
2. Advanced security vulnerabilities
3. Performance and scalability issues
4. Architectural concerns
5. Best practices and modern patterns

Return your analysis in JSON format:
{{
    "delusions": [
        {{
            "type": "llm_enhanced",
            "description": "Description of the issue",
            "priority": "high|medium|low",
            "file": "affected_file.py",
            "agent": "llm_enhanced"
        }}
    ],
    "recommendations": [
        "Specific actionable recommendations"
    ],
    "confidence": 0.85
}}
        """

        # Call LLM
        llm_response = self._call_llm(prompt, context)
        if not llm_response:
            return None

        try:
            # Parse LLM response
            return json.loads(llm_response)
        except json.JSONDecodeError:
            logger.warning("LLM response was not valid JSON")
            return None


# Create LLM-enhanced versions of all agents
class LLMEnhancedSecurityExpert(LLMEnhancedAgent):
    def __init__(self, llm_provider: str = "openai"):
        super().__init__(SecurityExpert(), llm_provider)


class LLMEnhancedCodeQualityExpert(LLMEnhancedAgent):
    def __init__(self, llm_provider: str = "openai"):
        super().__init__(CodeQualityExpert(), llm_provider)


class LLMEnhancedTestExpert(LLMEnhancedAgent):
    def __init__(self, llm_provider: str = "openai"):
        super().__init__(TestExpert(), llm_provider)


class LLMEnhancedBuildExpert(LLMEnhancedAgent):
    def __init__(self, llm_provider: str = "openai"):
        super().__init__(BuildExpert(), llm_provider)


class LLMEnhancedArchitectureExpert(LLMEnhancedAgent):
    def __init__(self, llm_provider: str = "openai"):
        super().__init__(ArchitectureExpert(), llm_provider)


class LLMEnhancedModelExpert(LLMEnhancedAgent):
    def __init__(self, llm_provider: str = "openai"):
        super().__init__(ModelExpert(), llm_provider)


# Agent factory
def create_agent(
    agent_name: str,
    use_llm: bool = True,
    llm_provider: str = "openai",
) -> None:
    """Create an agent with optional LLM enhancement"""
    if use_llm:
        # Check if LLM is available
        if llm_provider == "openai" and get_openai_api_key():
            agent_map = {
                "security": LLMEnhancedSecurityExpert,
                "code_quality": LLMEnhancedCodeQualityExpert,
                "test": LLMEnhancedTestExpert,
                "build": LLMEnhancedBuildExpert,
                "architecture": LLMEnhancedArchitectureExpert,
                "model": LLMEnhancedModelExpert,
            }
            agent_class = agent_map.get(agent_name)
            if agent_class:
                return agent_class(llm_provider)  # type: ignore
        elif llm_provider == "anthropic" and get_anthropic_api_key():
            # Same mapping for Anthropic
            agent_map = {
                "security": LLMEnhancedSecurityExpert,
                "code_quality": LLMEnhancedCodeQualityExpert,
                "test": LLMEnhancedTestExpert,
                "build": LLMEnhancedBuildExpert,
                "architecture": LLMEnhancedArchitectureExpert,
                "model": LLMEnhancedModelExpert,
            }
            agent_class = agent_map.get(agent_name)
            if agent_class:
                return agent_class(llm_provider)  # type: ignore

    # Fall back to base agents
    base_agent_map = {
        "security": SecurityExpert,
        "code_quality": CodeQualityExpert,
        "test": TestExpert,
        "build": BuildExpert,
        "architecture": ArchitectureExpert,
        "model": ModelExpert,
    }

    agent_class = base_agent_map.get(agent_name)  # type: ignore
    if agent_class:
        return agent_class()  # type: ignore

    msg = f"Unknown agent: {agent_name}"
    raise ValueError(msg)


if __name__ == "__main__":
    # Test the LLM-enhanced agents
    print("🤖 Testing LLM-Enhanced Ghostbusters Agents")
    print("=" * 50)

    # Check API key availability
    from .secret_manager import check_api_keys_availability

    availability = check_api_keys_availability()

    print("\n📋 API Key Availability:")
    for provider, available in availability.items():
        status = "✅ AVAILABLE" if available else "❌ NOT AVAILABLE"
        print(f"  {provider}: {status}")

    print("\n🔧 To add API keys to GCP Secret Manager:")
    print("  ./scripts/deploy-api-keys-to-gcp.sh")
