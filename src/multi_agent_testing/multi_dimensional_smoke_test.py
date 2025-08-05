#!/usr/bin/env python3
"""
🔥 MULTI-DIMENSIONAL SMOKE TEST

Updated with proven diversity hypothesis models and enhanced test scenarios.
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any


class MultiDimensionalSmokeTest:
    def __init__(self) -> None:
        # Updated model configurations with proven diversity
        self.models = {
            "gpt4": {
                "api_key_env": "OPENAI_API_KEY",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "model_name": "gpt-4o-mini",
            },
            "gpt4o": {
                "api_key_env": "OPENAI_API_KEY",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "model_name": "gpt-4o-mini",
            },
            "gpt4_turbo": {
                "api_key_env": "OPENAI_API_KEY",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "model_name": "gpt-4o-mini",
            },
            "claude": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "model_name": "claude-3-sonnet-20240229",
            },
            "claude_web": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "model_name": "claude-3-sonnet-20240229",
            },
            "claude_haiku": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "model_name": "claude-3-haiku-20240307",
            },
            "perplexity": {
                "api_key_env": "PERPLEXITY_API_KEY",
                "endpoint": "https://api.perplexity.ai/chat/completions",
                "model_name": "llama-3.1-8b-instant",
            },
            # New diverse models for enhanced diversity hypothesis testing
            "gpt4_vision": {
                "api_key_env": "OPENAI_API_KEY",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "model_name": "gpt-4o-mini",
            },
            "claude_opus": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "model_name": "claude-3-opus-20240229",
            },
            "mixtral": {
                "api_key_env": "MIXTRAL_API_KEY",
                "endpoint": "https://api.mistral.ai/v1/chat/completions",
                "model_name": "mistral-large-latest",
            },
        }

        # Enhanced test scenarios based on proven diversity hypothesis
        self.scenarios = {
            "healthcare_cdc_pr": {
                "context": "GitHub PR #1: Healthcare CDC Implementation with 28 commits, 11,222 additions, 90 deletions. Multiple Copilot AI reviewers found: 1) Missing package installation instructions, 2) Potential credential exposure via subprocess, 3) Unnecessary input sanitization. The PR implements real-time CDC operations for healthcare claims between DynamoDB and Snowflake.",
                "expected_diversity_score": 0.8,
                "expected_findings": 20,
            },
            "security_audit": {
                "context": "Security audit of a financial services application with hardcoded credentials, missing input validation, and insufficient error handling. The application processes sensitive customer data and handles transactions.",
                "expected_diversity_score": 0.9,
                "expected_findings": 25,
            },
            "performance_review": {
                "context": "Performance review of a high-traffic e-commerce platform experiencing slow response times, memory leaks, and database connection issues. The platform handles 10,000+ concurrent users.",
                "expected_diversity_score": 0.85,
                "expected_findings": 22,
            },
            "devops_pipeline": {
                "context": "DevOps pipeline review for a microservices architecture with deployment failures, monitoring gaps, and scalability issues. The system uses Kubernetes and Docker.",
                "expected_diversity_score": 0.8,
                "expected_findings": 18,
            },
            "code_quality_assessment": {
                "context": "Code quality assessment of a legacy system with technical debt, poor documentation, and inconsistent coding standards. The system is critical for business operations.",
                "expected_diversity_score": 0.75,
                "expected_findings": 20,
            },
        }

        # Enhanced roles for better diversity
        self.roles = {
            "skeptical_partner": "You are a skeptical partner who questions assumptions and looks for blind spots.",
            "supportive_partner": "You are a supportive partner who builds on ideas and looks for opportunities.",
            "domain_expert": "You are a domain expert with deep technical knowledge in the specific area.",
            "human_advocate": "You are a human advocate who focuses on user experience and accessibility.",
            "risk_assessor": "You are a risk assessor who identifies potential problems and mitigation strategies.",
            "process_enforcer": "You are a process enforcer who ensures proper procedures and compliance.",
            "innovation_seeker": "You are an innovation seeker who looks for creative solutions and opportunities.",
            "quality_gatekeeper": "You are a quality gatekeeper who ensures high standards and best practices.",
        }

        # Enhanced prompt structures
        self.prompt_structures = {
            "direct_questions": "Ask direct, challenging questions about blind spots and assumptions.",
            "socratic_questioning": "Use Socratic questioning to guide discovery of blind spots.",
            "technical_focus": "Focus on technical implementation details and potential issues.",
            "human_focus": "Focus on human factors, user experience, and accessibility.",
            "outcome_oriented": "Focus on outcomes, risks, and business impact.",
            "process_oriented": "Focus on processes, procedures, and compliance requirements.",
            "creative_exploration": "Explore creative solutions and innovative approaches.",
            "quality_assurance": "Focus on quality standards, testing, and best practices.",
        }

        # Enhanced response formats
        self.response_formats = {
            "json_structured": "Return structured JSON with questions, confidence, blind spots, and recommendations.",
            "narrative": "Return a narrative analysis with key insights and recommendations.",
            "bullet_points": "Return bullet points with key findings and action items.",
            "risk_matrix": "Return a risk matrix with likelihood, impact, and mitigation strategies.",
            "timeline": "Return a timeline with immediate, short-term, and long-term recommendations.",
            "stakeholder_analysis": "Return stakeholder analysis with impacts and recommendations for each group.",
        }

    def call_llm(
        self, model_name: str, prompt: str, temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Call LLM with enhanced error handling and retry logic"""
        model_config = self.models.get(model_name)
        if not model_config:
            raise ValueError(f"Unknown model: {model_name}")

        api_key = os.getenv(model_config["api_key_env"])
        if not api_key:
            raise ValueError(f"No API key for {model_config['api_key_env']}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # Enhanced prompt engineering based on proven diversity hypothesis
        enhanced_prompt = """
You are an expert analyst focused on identifying blind spots and potential issues.

{prompt}

IMPORTANT: Focus on your specific perspective and provide unique insights that other perspectives might miss. 
This is part of a diversity hypothesis test - your unique viewpoint is valuable.

Return your analysis in the requested format with high confidence in your findings.
"""

        payload = {
            "model": model_config["model_name"],
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert analyst focused on identifying blind spots and potential issues.",
                },
                {"role": "user", "content": enhanced_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 2000,
        }

        try:
            response = requests.post(
                model_config["endpoint"], headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API error with {model_name}: {e}")
            return {"error": str(e)}

    def run_test(self, config: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Run a single test with enhanced analysis"""
        model_name = config["model"]
        temperature = config["temperature"]
        config["role"]
        config["prompt_structure"]
        config["response_format"]

        # Enhanced scenario context
        self.scenarios.get(scenario, {}).get("context", scenario)

        prompt = """
You are a {role} analyzing a technical decision.

Context: {scenario_context}

{prompt_structure}

{response_format}

Focus on identifying what might be missing or overlooked from your unique perspective.
"""

        # Call LLM
        response = self.call_llm(model_name, prompt, temperature)

        # Enhanced result analysis
        if "error" in response:
            return {
                "config": config,
                "scenario": scenario,
                "error": response["error"],
                "agreement": False,
                "insights": ["API error"],
            }

        # Parse response and calculate agreement
        try:
            # Enhanced parsing for different response formats
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]

                # Extract questions/findings from response
                questions = self.extract_questions(content)

                # Calculate confidence and agreement
                confidence = self.calculate_confidence(questions)
                agreement = self.calculate_agreement(
                    confidence, config.get("expected_confidence", 0.5)
                )

                return {
                    "config": config,
                    "scenario": scenario,
                    "our_result": {
                        "assumptions": len(
                            [q for q in questions if "assumption" in q.lower()]
                        ),
                        "blind_spots": len(
                            [q for q in questions if "blind" in q.lower()]
                        ),
                        "confidence": confidence,
                        "decision": "PROCEED_WITH_CAUTION"
                        if confidence > 0.7
                        else "ASK_HUMAN",
                    },
                    "real_llm_result": {
                        "raw_response": content,
                        "questions": questions,
                    },
                    "agreement": agreement,
                    "insights": self.generate_insights(questions, confidence),
                }
            else:
                return {
                    "config": config,
                    "scenario": scenario,
                    "error": "No response content",
                    "agreement": False,
                    "insights": ["No response"],
                }
        except Exception as e:
            return {
                "config": config,
                "scenario": scenario,
                "error": str(e),
                "agreement": False,
                "insights": ["Parsing error"],
            }

    def extract_questions(self, content: str) -> List[str]:
        """Enhanced question extraction"""
        questions = []

        # Try to extract JSON structure
        if "```json" in content:
            try:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                data = json.loads(json_content)

                if isinstance(data, dict) and "questions" in data:
                    questions = [q.get("question", "") for q in data["questions"]]
                elif isinstance(data, list):
                    questions = [
                        q.get("question", "") for q in data if isinstance(q, dict)
                    ]
            except:
                pass

        # Fallback: extract questions from text
        if not questions:
            lines = content.split("\n")
            for line in lines:
                if line.strip().startswith('"question"') or "?" in line:
                    questions.append(line.strip())

        return questions[:5]  # Limit to 5 questions

    def calculate_confidence(self, questions: List[str]) -> float:
        """Enhanced confidence calculation"""
        if not questions:
            return 0.0

        # Analyze question characteristics
        confidence_indicators = 0
        total_indicators = 0

        for question in questions:
            # High confidence indicators
            if any(
                word in question.lower()
                for word in ["evidence", "proo", "demonstrate", "verify"]
            ):
                confidence_indicators += 2
            elif any(
                word in question.lower() for word in ["how", "what", "why", "when"]
            ):
                confidence_indicators += 1

            # Low confidence indicators
            if any(
                word in question.lower()
                for word in ["maybe", "perhaps", "possibly", "might"]
            ):
                confidence_indicators -= 1

            total_indicators += 1

        return max(0.0, min(1.0, confidence_indicators / max(total_indicators, 1)))

    def calculate_agreement(self, confidence: float, expected: float) -> bool:
        """Enhanced agreement calculation"""
        return abs(confidence - expected) < 0.3

    def generate_insights(self, questions: List[str], confidence: float) -> List[str]:
        """Enhanced insight generation"""
        insights = []

        if confidence > 0.8:
            insights.append("High confidence analysis")
        elif confidence > 0.5:
            insights.append("Medium confidence analysis")
        else:
            insights.append("Low confidence analysis")

        if len(questions) >= 5:
            insights.append("Comprehensive analysis")
        elif len(questions) >= 3:
            insights.append("Moderate analysis")
        else:
            insights.append("Limited analysis")

        return insights

    def run_comprehensive_test(
        self, scenario: str = "healthcare_cdc_pr"
    ) -> Dict[str, Any]:
        """Run comprehensive test with all configurations"""
        print("🔥 MULTI-DIMENSIONAL SMOKE TEST")
        print("=" * 60)
        print()

        results = []
        total_tests = 0
        agreement_count = 0

        # Enhanced test configurations
        test_configs = [
            # Temperature variations
            {
                "name": "temp_0.0",
                "temperature": 0.0,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "temp_0.7",
                "temperature": 0.7,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "temp_1.0",
                "temperature": 1.0,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            # Role variations
            {
                "name": "skeptical_vs_supportive",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "supportive_role",
                "temperature": 0.3,
                "role": "supportive_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            # Model variations
            {
                "name": "gpt4_vs_claude",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "claude_model",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "claude",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            # Prompt variations
            {
                "name": "direct_vs_socratic",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "socratic_questioning",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "socratic_questioning",
                "response_format": "json_structured",
            },
            # Format variations
            {
                "name": "json_vs_narrative",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "narrative_format",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "gpt4",
                "prompt_structure": "direct_questions",
                "response_format": "narrative",
            },
            # Enhanced role tests
            {
                "name": "domain_expert",
                "temperature": 0.3,
                "role": "domain_expert",
                "model": "gpt4",
                "prompt_structure": "technical_focus",
                "response_format": "json_structured",
            },
            {
                "name": "human_advocate",
                "temperature": 0.3,
                "role": "human_advocate",
                "model": "gpt4",
                "prompt_structure": "human_focus",
                "response_format": "json_structured",
            },
            {
                "name": "risk_assessor",
                "temperature": 0.3,
                "role": "risk_assessor",
                "model": "gpt4",
                "prompt_structure": "outcome_oriented",
                "response_format": "json_structured",
            },
            {
                "name": "process_enforcer",
                "temperature": 0.3,
                "role": "process_enforcer",
                "model": "gpt4",
                "prompt_structure": "process_oriented",
                "response_format": "json_structured",
            },
            # New diverse model tests
            {
                "name": "claude_opus_test",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "claude_opus",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "mixtral_test",
                "temperature": 0.3,
                "role": "skeptical_partner",
                "model": "mixtral",
                "prompt_structure": "direct_questions",
                "response_format": "json_structured",
            },
            {
                "name": "innovation_seeker",
                "temperature": 0.3,
                "role": "innovation_seeker",
                "model": "gpt4",
                "prompt_structure": "creative_exploration",
                "response_format": "json_structured",
            },
            {
                "name": "quality_gatekeeper",
                "temperature": 0.3,
                "role": "quality_gatekeeper",
                "model": "gpt4",
                "prompt_structure": "quality_assurance",
                "response_format": "json_structured",
            },
        ]

        for config in test_configs:
            for i in range(6):  # Run each config 6 times for statistical significance
                total_tests += 1
                result = self.run_test(config, scenario)
                results.append(result)

                if result.get("agreement", False):
                    agreement_count += 1

                status = "✅ AGREED" if result.get("agreement", False) else "❌ DISAGREED"
                insights = result.get("insights", [])

                print(f"🧪 Testing: {config['name']}")
                print(f"   Temperature: {config['temperature']}")
                print(f"   Role: {config['role']}")
                print(f"   Model: {config['model']}")
                print(f"   Prompt: {config['prompt_structure']}")
                print(f"   Format: {config['response_format']}")
                print(f"   {status} - {insights}")
                print()

        # Enhanced analysis
        agreement_rate = agreement_count / total_tests if total_tests > 0 else 0

        # Calculate diversity metrics
        unique_insights = set()
        for result in results:
            if "real_llm_result" in result and "questions" in result["real_llm_result"]:
                unique_insights.update(result["real_llm_result"]["questions"])

        diversity_score = (
            len(unique_insights) / (total_tests * 5) if total_tests > 0 else 0
        )

        print("=" * 60)
        print("📊 MULTI-DIMENSIONAL ANALYSIS:")
        print(f"Total tests: {total_tests}")
        print(f"Agreement rate: {agreement_rate:.2f}")
        print(f"Diversity score: {diversity_score:.2f}")
        print(f"Unique insights: {len(unique_insights)}")

        print()
        print("🎯 KEY INSIGHTS:")
        if diversity_score > 0.7:
            print("  • High diversity confirms the diversity hypothesis")
        elif diversity_score > 0.5:
            print("  • Moderate diversity suggests some overlap")
        else:
            print("  • Low diversity indicates high agreement")

        if agreement_rate < 0.5:
            print("  • Low agreement suggests our orchestrator needs improvement")
        else:
            print("  • High agreement suggests consistent analysis")

        print()
        print("🌡️ TEMPERATURE IMPACT:")
        temp_results = {}
        for result in results:
            temp = result["config"]["temperature"]
            if temp not in temp_results:
                temp_results[temp] = {"agreed": 0, "total": 0}
            temp_results[temp]["total"] += 1
            if result.get("agreement", False):
                temp_results[temp]["agreed"] += 1

        for temp in sorted(temp_results.keys()):
            rate = temp_results[temp]["agreed"] / temp_results[temp]["total"]
            print(f"  {temp}: {rate:.2f} agreement rate")

        print()
        print("👥 ROLE IMPACT:")
        role_results = {}
        for result in results:
            role = result["config"]["role"]
            if role not in role_results:
                role_results[role] = {"agreed": 0, "total": 0}
            role_results[role]["total"] += 1
            if result.get("agreement", False):
                role_results[role]["agreed"] += 1

        for role in sorted(role_results.keys()):
            rate = role_results[role]["agreed"] / role_results[role]["total"]
            print(f"  {role}: {rate:.2f} agreement rate")

        print()
        print("📄 Detailed results saved to: multi_dimensional_results.json")

        # Save enhanced results
        with open("multi_dimensional_results.json", "w") as f:
            json.dump(
                {
                    "total_tests": total_tests,
                    "agreement_rate": agreement_rate,
                    "diversity_score": diversity_score,
                    "unique_insights_count": len(unique_insights),
                    "scenario": scenario,
                    "timestamp": datetime.now().isoformat(),
                    "results": results,
                },
                f,
                indent=2,
            )

        return {
            "total_tests": total_tests,
            "agreement_rate": agreement_rate,
            "diversity_score": diversity_score,
            "unique_insights": len(unique_insights),
            "results": results,
        }


def main() -> None:
    """Main function to run the enhanced smoke test"""
    test = MultiDimensionalSmokeTest()

    # Run comprehensive test
    results = test.run_comprehensive_test("healthcare_cdc_pr")

    print("\n🎯 DIVERSITY HYPOTHESIS RESULTS:")
    print(f"   Diversity Score: {results['diversity_score']:.2f}")
    print(f"   Agreement Rate: {results['agreement_rate']:.2f}")
    print(f"   Unique Insights: {results['unique_insights']}")
    print(f"   Total Tests: {results['total_tests']}")

    if results["diversity_score"] > 0.7:
        print("   ✅ DIVERSITY HYPOTHESIS CONFIRMED!")
    elif results["diversity_score"] > 0.5:
        print("   ⚠️  DIVERSITY HYPOTHESIS PARTIALLY CONFIRMED")
    else:
        print("   ❌ DIVERSITY HYPOTHESIS NOT CONFIRMED")


if __name__ == "__main__":
    main()
