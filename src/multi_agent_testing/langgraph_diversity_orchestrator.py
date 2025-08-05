
#!/usr/bin/env python3
"""
🎯 LANGGRAPH DIVERSITY ORCHESTRATOR

A sophisticated multi-agent system for testing the diversity hypothesis using LangGraph,
multi-threading, and comprehensive visualizations.
"""


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import networkx as nx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import markdown
from jinja2 import Template


@dataclass
class DiversityAgent:
    name: str
    role: str
    focus: str
    perspective: str
    model: str
    temperature: float
    api_key_env: str


class BlindSpotFinding(BaseModel):
    question: str = Field(description="The challenging question about blind spots")
    confidence: str = Field(description="High, Medium, or Low confidence")
    blind_spots: str = Field(description="Description of the blind spot identified")
    recommendation: str = Field(description="Recommendation to address the blind spot")


class DiversityAnalysis(BaseModel):
    agent_name: str
    findings: List[BlindSpotFinding]
    total_findings: int
    confidence_score: float
    diversity_score: float


        self.agents = [
            DiversityAgent(
                name="Security Expert",
                role="Security-focused reviewer",
                focus="Credential exposure, authentication, authorization",
                perspective="What security vulnerabilities exist?",
                model="gpt-4o-mini",
                temperature=0.7,

                focus="CI/CD, deployment, monitoring, scalability",
                perspective="What infrastructure issues could arise?",
                model="gpt-4o-mini",
                temperature=0.7,

            ),
            DiversityAgent(
                name="Code Quality Expert",
                role="Code quality and maintainability specialist",

            ),
            DiversityAgent(
                name="User Experience Advocate",
                role="Human-centered design expert",
                focus="User experience, accessibility, usability",
                perspective="What UX issues could impact users?",

            ),
            DiversityAgent(
                name="Performance Engineer",
                role="Performance and scalability expert",
                focus="Performance, efficiency, resource usage",
                perspective="What performance issues could occur?",
                model="gpt-4o-mini",
                temperature=0.7,

        sns.set_palette("husl")

    def create_llm_client(self, agent: DiversityAgent) -> Any:
        """Create LLM client based on agent configuration"""
        api_key = os.getenv(agent.api_key_env)
        if not api_key:
            raise ValueError(f"No API key for {agent.api_key_env}")

            )
        else:
            raise ValueError(f"Unsupported API key environment: {agent.api_key_env}")


        """Analyze context with a specific agent"""
        try:
            llm = self.create_llm_client(agent)
            parser = JsonOutputParser(pydantic_object=BlindSpotFinding)

            prompt = f"""
You are {agent.name}, a {agent.role}.

Your focus: {agent.focus}
Your perspective: {agent.perspective}

Context: {context}

Analyze this context from your perspective and identify blind spots. Generate 5 challenging questions that reveal potential issues.

Return your analysis as a JSON array of findings, each with:
- question: A challenging question about blind spots
- confidence: High, Medium, or Low confidence

- recommendation: Recommendation to address the blind spot
- category: One of: security, performance, ux, code_quality, devops

Focus on your area of expertise and provide unique insights that other perspectives might miss.
"""

            messages = [

            # Parse the response
            try:
                # Extract JSON from markdown code blocks if present
                content = response.content
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_content = content[json_start:json_end].strip()
                else:
                    json_content = content

                return DiversityAnalysis(
                    agent_name=agent.name,
                    findings=findings,
                    total_findings=total_findings,
                    confidence_score=avg_confidence,

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing response from {agent.name}: {e}")
                return DiversityAnalysis(
                    agent_name=agent.name,
                    findings=[],
                    total_findings=0,
                    confidence_score=0.0,

        except Exception as e:
            print(f"Error with agent {agent.name}: {e}")
            return DiversityAnalysis(
                agent_name=agent.name,
                findings=[],
                total_findings=0,
                confidence_score=0.0,

            )

    def run_multi_threaded_analysis(self, context: str) -> List[DiversityAnalysis]:
        """Run analysis with all agents in parallel"""
        print("🚀 Starting multi-threaded diversity analysis...")

                        agent_name=agent.name,
                        findings=[],
                        total_findings=0,
                        confidence_score=0.0,

        # Agent Performance
        agent_names = [a.agent_name for a in analyses]
        findings_counts = [a.total_findings for a in analyses]
        confidence_scores = [a.confidence_score for a in analyses]

        # Add edges based on category overlap
        for i, analysis1 in enumerate(analyses):
            for j, analysis2 in enumerate(analyses):
                if i < j:
                    categories1 = set(f.category for f in analysis1.findings)
                    categories2 = set(f.category for f in analysis2.findings)
                    overlap = len(categories1.intersection(categories2))

        # Create colorbar properly
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca())

        <b>Key Metrics:</b>
        • Total Findings: {metrics['total_findings']}
        • Unique Findings: {metrics['unique_findings']}
        • Diversity Score: {metrics['diversity_score']:.2f}
        • Agent Coverage: {metrics['agent_coverage']}/{len(self.agents)}
        • Category Coverage: {metrics['category_coverage']} categories

                    finding_text = f"""
                    <b>Finding {i}:</b> {finding.question}
                    <b>Category:</b> {finding.category}
                    <b>Confidence:</b> {finding.confidence}
                    <b>Blind Spot:</b> {finding.blind_spots}
                    <b>Recommendation:</b> {finding.recommendation}
                    """

        template = """
# 🎯 Diversity Hypothesis Analysis Report

## Executive Summary

This report presents the results of a multi-agent diversity analysis using LangGraph orchestration.

### Key Metrics
- **Total Findings**: {{ metrics.total_findings }}
- **Unique Findings**: {{ metrics.unique_findings }}
- **Diversity Score**: {{ "%.2f"|format(metrics.diversity_score) }}
- **Agent Coverage**: {{ metrics.agent_coverage }}/{{ agents|length }}
- **Category Coverage**: {{ metrics.category_coverage }} categories

### Analysis Context
{{ context }}

## Agent Analysis Results

| Agent | Findings | Confidence | Diversity Score |
|-------|----------|------------|-----------------|
{% for analysis in analyses %}
| {{ analysis.agent_name }} | {{ analysis.total_findings }} | {{ "%.2f"|format(analysis.confidence_score) }} | {{ "%.2f"|format(analysis.diversity_score) }} |
{% endfor %}

## Detailed Findings by Agent

{% for analysis in analyses %}
{% if analysis.findings %}
### {{ analysis.agent_name }}

{% for finding in analysis.findings %}
**Finding {{ loop.index }}:** {{ finding.question }}

- **Category:** {{ finding.category }}
- **Confidence:** {{ finding.confidence }}
- **Blind Spot:** {{ finding.blind_spots }}
- **Recommendation:** {{ finding.recommendation }}

{% endfor %}
{% endif %}
{% endfor %}

## Diversity Metrics

### Category Distribution
{% for category, count in metrics.findings_by_category.items() %}
- **{{ category }}**: {{ count }} findings
{% endfor %}

### Confidence Distribution
{% for confidence, count in metrics.confidence_distribution.items() %}
- **{{ confidence }}**: {{ count }} findings
{% endfor %}

## Visualizations

The following visualizations are available:
- `diversity_overview.png` - Overview of agent performance and findings
- `agent_network.svg` - Network graph showing agent interactions
- `findings_analysis.png` - Detailed analysis of findings distribution

## Conclusion

The diversity hypothesis is {{ "CONFIRMED" if metrics.diversity_score > 0.5 else "PARTIALLY CONFIRMED" if metrics.diversity_score > 0.3 else "NOT CONFIRMED" }} with a diversity score of {{ "%.2f"|format(metrics.diversity_score) }}.

Multiple AI perspectives provide {{ "excellent" if metrics.diversity_score > 0.7 else "good" if metrics.diversity_score > 0.5 else "moderate" }} blind spot detection coverage.
"""

            <!DOCTYPE html>
            <html>
            <head>
                <title>Diversity Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    h1, h2, h3 {{ color: #333; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>

        # Generate reports
        print("📄 Generating reports...")
        self.generate_pdf_report(analyses, metrics, context)
        self.generate_markdown_report(analyses, metrics, context)

    print("\n🎯 DIVERSITY HYPOTHESIS RESULTS:")
    print(f"   Diversity Score: {results['metrics']['diversity_score']:.2f}")
    print(f"   Total Findings: {results['metrics']['total_findings']}")
    print(f"   Unique Findings: {results['metrics']['unique_findings']}")

        print("   ⚠️  DIVERSITY HYPOTHESIS PARTIALLY CONFIRMED")
    else:
        print("   ❌ DIVERSITY HYPOTHESIS NOT CONFIRMED")


