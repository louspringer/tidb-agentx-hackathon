#!/usr/bin/env python3
"""
Multi-Dimensional Smoke Test for Meta-Cognitive Orchestrator
Tests all dimensions: temperature, roles, models, prompts, formats
"""

import json
import requests
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from meta_cognitive_orchestrator import MetaCognitiveOrchestrator

@dataclass
class TestConfiguration:
    """Configuration for a single test run"""
    name: str
    temperature: float
    role: str
    model: str
    prompt_structure: str
    response_format: str
    api_key_env: str

class MultiDimensionalSmokeTest:
    """Comprehensive smoke test across all dimensions"""
    
    def __init__(self):
        self.orchestrator = MetaCognitiveOrchestrator()
        
        # Test scenarios
        self.scenarios = {
            "llm_tiebreaker": """
                You are a tie-breaker for a meta-cognitive orchestrator test.
                
                Scenario: We have two test approaches for our meta-cognitive orchestrator:
                
                Option A: Recursive Test
                - Test the orchestrator on itself
                - Meta-cognitive validation
                - Higher risk, higher reward
                - 30 seconds to know
                
                Option B: Simple Test  
                - Test on database migration scenario
                - Clear success/failure criteria
                - Lower risk, predictable outcome
                - 30 seconds to know
                
                Question: Which test will give us the most interesting failure or success?
                
                Consider:
                - Which failure would be more revealing?
                - Which success would be more validating?
                - Which approach tests the meta-cognitive capability better?
                - Which is more likely to reveal unknown unknowns?
                
                Make a decision and explain your reasoning.
            """,
            "web_search_test": """
                You are testing a meta-cognitive orchestrator that claims to detect blind spots.
                
                Context: The orchestrator uses pattern matching to detect hardcoded credentials,
                but it might miss context-dependent patterns like UUIDs in legitimate contexts.
                
                Research Question: What are the latest best practices for detecting hardcoded
                secrets in code? Are there any new techniques that might outperform
                simple pattern matching?
                
                Use web search to find current information about:
                - Secret detection tools and their limitations
                - Context-aware scanning techniques
                - False positive reduction strategies
                - Industry standards for credential management
                
                Then evaluate: Is our pattern-matching approach sufficient, or are we missing
                something important?
            """,
            "recursive_test": """
                I created a meta-cognitive orchestrator that detects blind spots.
                I think it will work well for all scenarios.
                Obviously this approach will solve the "not knowing what you don't know" problem.
                I assume the hardcoded patterns are sufficient.
            """,
            "database_migration": """
                I'm planning to migrate our production database from MySQL to PostgreSQL.
                I think I can just use pg_dump and restore it directly.
                Obviously this will work fine since both are SQL databases.
            """,
            "security_implementation": """
                I'm implementing OAuth2 for our application.
                I assume using the standard library will be secure enough.
                Probably I don't need to worry about token refresh.
            """,
            "pr_workflow": """
                I created beautiful PR markdown files but never actual GitHub PRs.
                I did git merges directly instead of creating proper GitHub Pull Requests.
                I thought git merge was the proper PR workflow.
            """,
            "edge_case_legitimate": """
                I think the user is right about the PR workflow.
                Obviously we should use GitHub PRs instead of direct merges.
                I assume this is the standard approach.
            """
        }
        
        # Role definitions
        self.roles = {
            "skeptical_partner": {
                "description": "Always questions assumptions and finds blind spots",
                "prompt": "You are a skeptical partner LLM. Your job is to question assumptions and find blind spots. Always ask 'What are you missing?' and 'How do you know that?'"
            },
            "supportive_partner": {
                "description": "Supportive but still identifies potential issues",
                "prompt": "You are a supportive partner LLM. Help identify potential issues while being encouraging. Ask 'What could be improved?' and 'Have you considered...?'"
            },
            "domain_expert": {
                "description": "Technical domain expert who challenges from expertise",
                "prompt": "You are a domain expert. Challenge the approach from a technical perspective. Ask 'What's the standard process?' and 'What are the technical risks?'"
            },
            "human_advocate": {
                "description": "Represents human expectations and common sense",
                "prompt": "You represent human expectations and common sense. Ask 'What would a human expect?' and 'Is this user-friendly?'"
            },
            "risk_assessor": {
                "description": "Assesses risks and potential failure modes",
                "prompt": "You assess risks and potential failure modes. Ask 'What could go wrong?' and 'What are the consequences?'"
            },
            "process_enforcer": {
                "description": "Enforces standard processes and best practices",
                "prompt": "You enforce standard processes and best practices. Ask 'What's the proper workflow?' and 'Are you following standards?'"
            }
        }
        
        # Model configurations
        self.models = {
            "gpt4": {
                "api_key_env": "OPENAI_API_KEY",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "model_name": "gpt-4-turbo"
            },
            "gpt4o": {
                "api_key_env": "OPENAI_API_KEY",
                "endpoint": "https://api.openai.com/v1/chat/completions", 
                "model_name": "gpt-4-turbo"
            },
            "gpt4_turbo": {
                "api_key_env": "OPENAI_API_KEY",
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "model_name": "gpt-4-turbo"
            },
            "claude": {
                "api_key_env": "ANTHROPIC_API_KEY", 
                "endpoint": "https://api.anthropic.com/v1/messages",
                "model_name": "claude-3-sonnet-20240229"
            },
            "claude_web": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "model_name": "claude-3-sonnet-20240229"
            },
            "claude_haiku": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "endpoint": "https://api.anthropic.com/v1/messages", 
                "model_name": "claude-3-haiku-20240307"
            },
            "perplexity": {
                "api_key_env": "PERPLEXITY_API_KEY",
                "endpoint": "https://api.perplexity.ai/chat/completions",
                "model_name": "llama-3.1-8b-instant"
            }
        }
        
        # Prompt structures
        self.prompt_structures = {
            "direct_questions": "Generate 5 direct questions that challenge the approach.",
            "socratic_questioning": "Use Socratic questioning to guide discovery of blind spots.",
            "technical_focus": "Focus on technical implementation details and risks.",
            "human_focus": "Focus on human expectations and user experience.",
            "process_oriented": "Focus on proper processes and workflows.",
            "outcome_oriented": "Focus on desired outcomes and success criteria."
        }
        
        # Response formats
        self.response_formats = {
            "json_structured": "Return JSON with questions, confidence, blind_spots, recommendation.",
            "free_text": "Return free-form text with questions and analysis.",
            "bullet_points": "Return bullet points of questions and issues.",
            "narrative": "Return narrative analysis with embedded questions."
        }
        
        # Temperature settings
        self.temperatures = [0.0, 0.3, 0.7, 1.0]

    def call_llm_api(self, config: TestConfiguration, context: str, jeopardy_question: str) -> Dict[str, Any]:
        """Call LLM API with specific configuration"""
        
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            return {"error": f"No API key for {config.api_key_env}", "questions": []}
        
        model_config = self.models[config.model]
        role_config = self.roles[config.role]
        
        # Build prompt based on configuration
        prompt = f"""
{role_config['prompt']}

Context: {context}

Jeopardy Question: {jeopardy_question}

{self.prompt_structures[config.prompt_structure]}

{self.response_formats[config.response_format]}

Focus on: {role_config['description']}
"""
        
        try:
            if config.model == "gpt4":
                response = requests.post(
                    model_config["endpoint"],
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_config["model_name"],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": config.temperature,
                        "max_tokens": 500
                    },
                    timeout=30
                )
            elif config.model == "claude":
                response = requests.post(
                    model_config["endpoint"],
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_config["model_name"],
                        "max_tokens": 500,
                        "temperature": config.temperature,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                if config.model == "gpt4":
                    content = result["choices"][0]["message"]["content"]
                else:  # claude
                    content = result["content"][0]["text"]
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"raw_response": content, "questions": [content]}
            else:
                return {"error": f"API error: {response.status_code}", "questions": []}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "questions": []}

    def create_test_configurations(self) -> List[TestConfiguration]:
        """Create comprehensive test configurations"""
        
        configs = []
        
        # Test key combinations
        key_combinations = [
            # Temperature variations
            ("temp_0.0", 0.0, "skeptical_partner", "gpt4", "direct_questions", "json_structured"),
            ("temp_0.7", 0.7, "skeptical_partner", "gpt4", "direct_questions", "json_structured"),
            
            # Role variations
            ("skeptical_vs_supportive", 0.3, "skeptical_partner", "gpt4", "direct_questions", "json_structured"),
            ("supportive_role", 0.3, "supportive_partner", "gpt4", "direct_questions", "json_structured"),
            
            # Model variations
            ("gpt4_vs_claude", 0.3, "skeptical_partner", "gpt4", "direct_questions", "json_structured"),
            ("claude_model", 0.3, "skeptical_partner", "claude", "direct_questions", "json_structured"),
            
            # Prompt structure variations
            ("direct_vs_socratic", 0.3, "skeptical_partner", "gpt4", "direct_questions", "json_structured"),
            ("socratic_questioning", 0.3, "skeptical_partner", "gpt4", "socratic_questioning", "json_structured"),
            
            # Response format variations
            ("json_vs_narrative", 0.3, "skeptical_partner", "gpt4", "direct_questions", "json_structured"),
            ("narrative_format", 0.3, "skeptical_partner", "gpt4", "direct_questions", "narrative"),
            
            # Domain expert variations
            ("domain_expert", 0.3, "domain_expert", "gpt4", "technical_focus", "json_structured"),
            ("human_advocate", 0.3, "human_advocate", "gpt4", "human_focus", "json_structured"),
            ("risk_assessor", 0.3, "risk_assessor", "gpt4", "outcome_oriented", "json_structured"),
            ("process_enforcer", 0.3, "process_enforcer", "gpt4", "process_oriented", "json_structured")
        ]
        
        for name, temp, role, model, prompt, response_format in key_combinations:
            model_config = self.models[model]
            configs.append(TestConfiguration(
                name=name,
                temperature=temp,
                role=role,
                model=model,
                prompt_structure=prompt,
                response_format=response_format,
                api_key_env=model_config["api_key_env"]
            ))
        
        return configs

    def run_single_test(self, config: TestConfiguration, scenario_name: str, context: str) -> Dict[str, Any]:
        """Run a single test configuration"""
        
        print(f"\n🧪 Testing: {config.name}")
        print(f"   Temperature: {config.temperature}")
        print(f"   Role: {config.role}")
        print(f"   Model: {config.model}")
        print(f"   Prompt: {config.prompt_structure}")
        print(f"   Format: {config.response_format}")
        
        # Get our orchestrator's analysis
        our_result = self.orchestrator.orchestrate(context)
        
        # Get real LLM analysis
        real_result = self.call_llm_api(config, context, our_result["jeopardy_question"])
        
        # Compare results
        comparison = {
            "config": {
                "name": config.name,
                "temperature": config.temperature,
                "role": config.role,
                "model": config.model,
                "prompt_structure": config.prompt_structure,
                "response_format": config.response_format
            },
            "scenario": scenario_name,
            "our_result": {
                "assumptions": len(our_result["assumptions_detected"]),
                "blind_spots": len(our_result["blind_spots_identified"]),
                "confidence": our_result["confidence"],
                "decision": our_result["final_decision"]
            },
            "real_llm_result": real_result,
            "agreement": False,
            "insights": []
        }
        
        # Analyze agreement
        if "error" not in real_result:
            our_confidence = our_result["confidence"]
            real_confidence = real_result.get("confidence", 0.5)
            confidence_diff = abs(our_confidence - real_confidence)
            
            if confidence_diff < 0.3:
                comparison["agreement"] = True
                comparison["insights"].append("Confidence agreement")
            else:
                comparison["insights"].append(f"Confidence disagreement: {our_confidence:.2f} vs {real_confidence:.2f}")
        
        return comparison

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive multi-dimensional test"""
        
        print("🔥 MULTI-DIMENSIONAL SMOKE TEST")
        print("=" * 60)
        
        configs = self.create_test_configurations()
        all_results = []
        
        for config in configs:
            for scenario_name, context in self.scenarios.items():
                try:
                    result = self.run_single_test(config, scenario_name, context)
                    all_results.append(result)
                    
                    # Print summary
                    agreement = "✅ AGREED" if result["agreement"] else "❌ DISAGREED"
                    print(f"   {agreement} - {result['insights']}")
                    
                except Exception as e:
                    print(f"❌ {config.name} failed: {e}")
        
        # Analyze patterns
        analysis = self.analyze_results(all_results)
        
        return {
            "total_tests": len(all_results),
            "results": all_results,
            "analysis": analysis
        }

    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in results"""
        
        analysis = {
            "temperature_impact": {},
            "role_impact": {},
            "model_impact": {},
            "prompt_impact": {},
            "format_impact": {},
            "agreement_rate": 0,
            "key_insights": []
        }
        
        # Calculate agreement rate
        agreements = sum(1 for r in results if r["agreement"])
        analysis["agreement_rate"] = agreements / len(results) if results else 0
        
        # Analyze by dimension
        for result in results:
            config = result["config"]
            
            # Temperature impact
            temp = config["temperature"]
            if temp not in analysis["temperature_impact"]:
                analysis["temperature_impact"][temp] = {"agreements": 0, "total": 0}
            analysis["temperature_impact"][temp]["total"] += 1
            if result["agreement"]:
                analysis["temperature_impact"][temp]["agreements"] += 1
            
            # Role impact
            role = config["role"]
            if role not in analysis["role_impact"]:
                analysis["role_impact"][role] = {"agreements": 0, "total": 0}
            analysis["role_impact"][role]["total"] += 1
            if result["agreement"]:
                analysis["role_impact"][role]["agreements"] += 1
        
        # Key insights
        if analysis["agreement_rate"] < 0.5:
            analysis["key_insights"].append("Low agreement suggests our orchestrator needs improvement")
        else:
            analysis["key_insights"].append("Good agreement suggests our orchestrator works well")
        
        return analysis

def main():
    """Run the comprehensive multi-dimensional smoke test"""
    
    test = MultiDimensionalSmokeTest()
    results = test.run_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("📊 MULTI-DIMENSIONAL ANALYSIS:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Agreement rate: {results['analysis']['agreement_rate']:.2f}")
    
    print("\n🎯 KEY INSIGHTS:")
    for insight in results['analysis']['key_insights']:
        print(f"  • {insight}")
    
    print("\n🌡️ TEMPERATURE IMPACT:")
    for temp, data in results['analysis']['temperature_impact'].items():
        rate = data['agreements'] / data['total'] if data['total'] > 0 else 0
        print(f"  {temp}: {rate:.2f} agreement rate")
    
    print("\n👥 ROLE IMPACT:")
    for role, data in results['analysis']['role_impact'].items():
        rate = data['agreements'] / data['total'] if data['total'] > 0 else 0
        print(f"  {role}: {rate:.2f} agreement rate")
    
    # Save detailed results
    with open("multi_dimensional_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: multi_dimensional_results.json")

if __name__ == "__main__":
    main() 