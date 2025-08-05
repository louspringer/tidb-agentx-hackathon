#!/usr/bin/env python3
"""
💰 COST ANALYSIS FOR DIVERSITY HYPOTHESIS TESTING

Calculate total tokens and costs for our multi-agent diversity analysis.
"""

import json
import os


# OpenAI GPT-4o-mini pricing (as of 2024)
# Input: $0.15 per 1M tokens
# Output: $0.60 per 1M tokens


def estimate_tokens(text: str) -> int:
    """Rough estimate of tokens (4 characters per token)"""
    return len(text) // 4


    # Analyze each test
    for result in data["results"]:
        if "real_llm_result" in result and "raw_response" in result["real_llm_result"]:
            successful_calls += 1

You are a skeptical partner analyzing a technical decision.

Context: {result.get('scenario', 'technical_decision')}

Analyze this context and identify potential blind spots. Generate 5 challenging questions that reveal assumptions or gaps.

Return your analysis as a JSON array of questions, each with:
- question: A challenging question about blind spots
- confidence: High, Medium, or Low confidence
- blind_spots: Description of the blind spot identified
- recommendation: Recommendation to address the blind spot

Focus on identifying what might be missing or overlooked.
"""

            # Estimate output tokens (response)
            output_text = result["real_llm_result"]["raw_response"]
            output_tokens = estimate_tokens(output_text)
            total_output_tokens += output_tokens

    # Calculate costs
    input_cost = (total_input_tokens / 1_000_000) * INPUT_COST_PER_1M_TOKENS
    output_cost = (total_output_tokens / 1_000_000) * OUTPUT_COST_PER_1M_TOKENS
    total_cost = input_cost + output_cost

    print(f"   Successful calls: {successful_calls}")
    print(f"   Input tokens: {total_input_tokens:,}")
    print(f"   Output tokens: {total_output_tokens:,}")
    print(f"   Total tokens: {total_input_tokens + total_output_tokens:,}")
    print(f"   Input cost: ${input_cost:.4f}")
    print(f"   Output cost: ${output_cost:.4f}")
    print(f"   Total cost: ${total_cost:.4f}")

    return {
        "calls": successful_calls,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,

    # Load analysis data
    analysis_file = "diversity_analysis_output/analysis_data.json"
    if not os.path.exists(analysis_file):
        print("❌ Analysis file not found")
        return {}

    # Each agent made one call
    for analysis in data["analyses"]:
        if analysis["findings"]:  # Successful call
            successful_calls += 1

            # Estimate input tokens (prompt for each agent)
            agent_name = analysis["agent_name"]
            system_message = "You are an expert analyst focused on identifying blind spots and potential issues."
            user_message = f"""
You are {agent_name}, analyzing a GitHub PR for a Healthcare CDC implementation.

Context: GitHub PR #1: Healthcare CDC Implementation with 28 commits, 11,222 additions, 90 deletions. Multiple Copilot AI reviewers found: 1) Missing package installation instructions, 2) Potential credential exposure via subprocess, 3) Unnecessary input sanitization. The PR implements real-time CDC operations for healthcare claims between DynamoDB and Snowflake.

Analyze this context from your perspective and identify blind spots. Generate 5 challenging questions that reveal potential issues.

Return your analysis as a JSON array of findings, each with:
- question: A challenging question about blind spots
- confidence: High, Medium, or Low confidence

- recommendation: Recommendation to address the blind spot
- category: One of: security, performance, ux, code_quality, devops

Focus on your area of expertise and provide unique insights that other perspectives might miss.
"""

            # Estimate output tokens (response with 5 findings)
            # Each finding has question, confidence, blind_spots, recommendation, category
            output_text = json.dumps(analysis["findings"], indent=2)
            output_tokens = estimate_tokens(output_text)
            total_output_tokens += output_tokens

    # Calculate costs
    input_cost = (total_input_tokens / 1_000_000) * INPUT_COST_PER_1M_TOKENS
    output_cost = (total_output_tokens / 1_000_000) * OUTPUT_COST_PER_1M_TOKENS
    total_cost = input_cost + output_cost

    print(f"   Successful calls: {successful_calls}")
    print(f"   Input tokens: {total_input_tokens:,}")
    print(f"   Output tokens: {total_output_tokens:,}")
    print(f"   Total tokens: {total_input_tokens + total_output_tokens:,}")
    print(f"   Input cost: ${input_cost:.4f}")
    print(f"   Output cost: ${output_cost:.4f}")
    print(f"   Total cost: ${total_cost:.4f}")

    return {
        "calls": successful_calls,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,

    # Load synthesis data
    synthesis_file = "synthesis_output/synthesis_data.json"
    if not os.path.exists(synthesis_file):
        print("❌ Synthesis file not found")
        return {}

    # Estimate the synthesis prompt (includes all findings)
    findings_text = ""
    for analysis in data.get("analyses", []):
        for finding in analysis.get("findings", []):
            findings_text += f"• {finding.get('agent', 'Unknown')} ({finding.get('category', 'unknown')}): {finding.get('question', '')} - {finding.get('recommendation', '')}\n"


STAKEHOLDERS (in priority order):
1. Security Team (Security and compliance) - Priority: 1, Decision Power: High
2. DevOps Team (Infrastructure and deployment) - Priority: 2, Decision Power: High
3. Development Team (Code quality and maintainability) - Priority: 3, Decision Power: Medium
4. Product Team (User experience and business value) - Priority: 4, Decision Power: Medium
5. Business Stakeholders (Cost and timeline management) - Priority: 5, Decision Power: Low

FINDINGS TO SYNTHESIZE:
{findings_text}

TASK:

1. Address multiple stakeholder concerns where possible
2. Prioritize by stakeholder ranking (Security Team = highest priority)
3. Consider implementation effort vs. impact
4. Identify dependencies between fixes
5. Provide clear ROI estimates

For each fix, provide:
- fix_title: Clear, actionable title
- description: Detailed description of the fix
- stakeholder_impacts: How this affects each stakeholder
- implementation_effort: Low/Medium/High
- priority_score: 0-1 score based on stakeholder priority
- categories_addressed: Categories this fix addresses
- estimated_roi: High/Medium/Low ROI
- dependencies: Other fixes this depends on
- timeline: Estimated implementation timeline

Return as a JSON array of fixes, prioritizing fixes that address multiple high-priority stakeholder concerns.
"""

    # Calculate costs
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_1M_TOKENS
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_1M_TOKENS
    total_cost = input_cost + output_cost

    print(f"   Input tokens: {input_tokens:,}")
    print(f"   Output tokens: {output_tokens:,}")
    print(f"   Total tokens: {input_tokens + output_tokens:,}")
    print(f"   Input cost: ${input_cost:.4f}")
    print(f"   Output cost: ${output_cost:.4f}")
    print(f"   Total cost: ${total_cost:.4f}")

    return {
        "calls": 1,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,

    # Analyze each component
    multi_dimensional = analyze_multi_dimensional_costs()
    langgraph = analyze_langgraph_costs()
    synthesis = analyze_synthesis_costs()

    print("\n" + "=" * 50)
    print("💰 TOTAL COST SUMMARY")
    print("=" * 50)
    print(f"📊 Total API Calls: {total_calls}")
    print(f"📊 Total Input Tokens: {total_input_tokens:,}")
    print(f"📊 Total Output Tokens: {total_output_tokens:,}")
    print(f"📊 Total Tokens: {total_input_tokens + total_output_tokens:,}")
    print(f"💰 Total Cost: ${total_cost:.4f}")

