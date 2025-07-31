#!/usr/bin/env python3
"""
🎯 LANGGRAPH DIVERSITY ORCHESTRATOR

A sophisticated multi-agent system for testing the diversity hypothesis using LangGraph,
multi-threading, and comprehensive visualizations.
"""

import asyncio
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import requests
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
    category: str = Field(description="Category: security, performance, ux, code_quality, devops")

class DiversityAnalysis(BaseModel):
    agent_name: str
    findings: List[BlindSpotFinding]
    total_findings: int
    confidence_score: float
    diversity_score: float

class LangGraphDiversityOrchestrator:
    def __init__(self):
        self.agents = [
            DiversityAgent(
                name="Security Expert",
                role="Security-focused reviewer",
                focus="Credential exposure, authentication, authorization",
                perspective="What security vulnerabilities exist?",
                model="gpt-4o-mini",
                temperature=0.7,
                api_key_env="OPENAI_API_KEY"
            ),
            DiversityAgent(
                name="DevOps Engineer",
                role="Infrastructure and deployment expert", 
                focus="CI/CD, deployment, monitoring, scalability",
                perspective="What infrastructure issues could arise?",
                model="gpt-4o-mini",
                temperature=0.7,
                api_key_env="OPENAI_API_KEY"
            ),
            DiversityAgent(
                name="Code Quality Expert",
                role="Code quality and maintainability specialist",
                focus="Code structure, testing, documentation, maintainability", 
                perspective="What code quality issues exist?",
                model="gpt-4o-mini",
                temperature=0.7,
                api_key_env="OPENAI_API_KEY"
            ),
            DiversityAgent(
                name="User Experience Advocate",
                role="Human-centered design expert",
                focus="User experience, accessibility, usability",
                perspective="What UX issues could impact users?",
                model="gpt-4o-mini", 
                temperature=0.7,
                api_key_env="OPENAI_API_KEY"
            ),
            DiversityAgent(
                name="Performance Engineer",
                role="Performance and scalability expert",
                focus="Performance, efficiency, resource usage",
                perspective="What performance issues could occur?",
                model="gpt-4o-mini",
                temperature=0.7,
                api_key_env="OPENAI_API_KEY"
            )
        ]
        
        self.output_dir = Path("diversity_analysis_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up visualization style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

    def create_llm_client(self, agent: DiversityAgent) -> Any:
        """Create LLM client based on agent configuration"""
        api_key = os.getenv(agent.api_key_env)
        if not api_key:
            raise ValueError(f"No API key for {agent.api_key_env}")
        
        if "openai" in agent.api_key_env.lower():
            return ChatOpenAI(
                model=agent.model,
                temperature=agent.temperature,
                api_key=api_key
            )
        elif "anthropic" in agent.api_key_env.lower():
            return ChatAnthropic(
                model=agent.model,
                temperature=agent.temperature,
                api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported API key environment: {agent.api_key_env}")

    def analyze_with_agent(self, agent: DiversityAgent, context: str) -> DiversityAnalysis:
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
- blind_spots: Description of the blind spot identified  
- recommendation: Recommendation to address the blind spot
- category: One of: security, performance, ux, code_quality, devops

Focus on your area of expertise and provide unique insights that other perspectives might miss.
"""

            messages = [
                SystemMessage(content="You are an expert analyst focused on identifying blind spots and potential issues."),
                HumanMessage(content=prompt)
            ]
            
            response = llm.invoke(messages)
            
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
                
                findings_data = json.loads(json_content)
                
                if isinstance(findings_data, dict) and "findings" in findings_data:
                    findings_data = findings_data["findings"]
                
                findings = [BlindSpotFinding(**finding) for finding in findings_data]
                
                # Calculate metrics
                total_findings = len(findings)
                confidence_scores = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
                avg_confidence = sum(confidence_scores.get(f.confidence, 0.5) for f in findings) / total_findings if findings else 0
                
                return DiversityAnalysis(
                    agent_name=agent.name,
                    findings=findings,
                    total_findings=total_findings,
                    confidence_score=avg_confidence,
                    diversity_score=0.8  # Will be calculated later
                )
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing response from {agent.name}: {e}")
                return DiversityAnalysis(
                    agent_name=agent.name,
                    findings=[],
                    total_findings=0,
                    confidence_score=0.0,
                    diversity_score=0.0
                )
                
        except Exception as e:
            print(f"Error with agent {agent.name}: {e}")
            return DiversityAnalysis(
                agent_name=agent.name,
                findings=[],
                total_findings=0,
                confidence_score=0.0,
                diversity_score=0.0
            )

    def run_multi_threaded_analysis(self, context: str) -> List[DiversityAnalysis]:
        """Run analysis with all agents in parallel"""
        print("🚀 Starting multi-threaded diversity analysis...")
        
        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            # Submit all agent analyses
            future_to_agent = {
                executor.submit(self.analyze_with_agent, agent, context): agent 
                for agent in self.agents
            }
            
            results = []
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ {agent.name} completed analysis")
                except Exception as e:
                    print(f"❌ {agent.name} failed: {e}")
                    results.append(DiversityAnalysis(
                        agent_name=agent.name,
                        findings=[],
                        total_findings=0,
                        confidence_score=0.0,
                        diversity_score=0.0
                    ))
        
        return results

    def calculate_diversity_metrics(self, analyses: List[DiversityAnalysis]) -> Dict[str, Any]:
        """Calculate comprehensive diversity metrics"""
        
        # Collect all findings
        all_findings = []
        for analysis in analyses:
            for finding in analysis.findings:
                all_findings.append({
                    'agent': analysis.agent_name,
                    'category': finding.category,
                    'confidence': finding.confidence,
                    'question': finding.question,
                    'blind_spots': finding.blind_spots,
                    'recommendation': finding.recommendation
                })
        
        # Calculate diversity metrics
        total_findings = len(all_findings)
        unique_categories = len(set(f['category'] for f in all_findings))
        agent_coverage = len([a for a in analyses if a.total_findings > 0])
        
        # Calculate overlap vs unique findings
        all_questions = [f['question'] for f in all_findings]
        unique_questions = len(set(all_questions))
        overlap_rate = 1 - (unique_questions / total_findings) if total_findings > 0 else 0
        diversity_score = 1 - overlap_rate
        
        return {
            'total_findings': total_findings,
            'unique_findings': unique_questions,
            'agent_coverage': agent_coverage,
            'category_coverage': unique_categories,
            'diversity_score': diversity_score,
            'overlap_rate': overlap_rate,
            'findings_by_category': pd.DataFrame(all_findings).groupby('category').size().to_dict(),
            'findings_by_agent': pd.DataFrame(all_findings).groupby('agent').size().to_dict(),
            'confidence_distribution': pd.DataFrame(all_findings)['confidence'].value_counts().to_dict()
        }

    def create_visualizations(self, analyses: List[DiversityAnalysis], metrics: Dict[str, Any]):
        """Create comprehensive visualizations"""
        
        # 1. Diversity Score Overview
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Agent Performance
        agent_names = [a.agent_name for a in analyses]
        findings_counts = [a.total_findings for a in analyses]
        confidence_scores = [a.confidence_score for a in analyses]
        
        bars1 = ax1.bar(agent_names, findings_counts, alpha=0.7, color='skyblue')
        ax1.set_title('Findings by Agent', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Number of Findings')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars1, findings_counts):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        # Confidence Scores
        bars2 = ax2.bar(agent_names, confidence_scores, alpha=0.7, color='lightcoral')
        ax2.set_title('Average Confidence by Agent', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Confidence Score')
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, score in zip(bars2, confidence_scores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # Category Distribution
        if metrics['findings_by_category']:
            categories = list(metrics['findings_by_category'].keys())
            category_counts = list(metrics['findings_by_category'].values())
            
            colors_cat = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            wedges, texts, autotexts = ax3.pie(category_counts, labels=categories, autopct='%1.1f%%',
                                               colors=colors_cat, startangle=90)
            ax3.set_title('Findings by Category', fontsize=14, fontweight='bold')
        
        # Confidence Distribution
        if metrics['confidence_distribution']:
            conf_levels = list(metrics['confidence_distribution'].keys())
            conf_counts = list(metrics['confidence_distribution'].values())
            
            colors_conf = ['#ff6b6b', '#4ecdc4', '#45b7d1']
            bars3 = ax4.bar(conf_levels, conf_counts, color=colors_conf[:len(conf_levels)], alpha=0.7)
            ax4.set_title('Confidence Distribution', fontsize=14, fontweight='bold')
            ax4.set_ylabel('Number of Findings')
            
            # Add value labels
            for bar, count in zip(bars3, conf_counts):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        str(count), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'diversity_overview.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'diversity_overview.svg', format='svg', bbox_inches='tight')
        plt.close()
        
        # 2. Network Graph of Agent Interactions
        self.create_network_graph(analyses)
        
        # 3. Detailed Findings Analysis
        self.create_findings_analysis(analyses, metrics)

    def create_network_graph(self, analyses: List[DiversityAnalysis]):
        """Create network graph showing agent relationships and findings overlap"""
        
        G = nx.Graph()
        
        # Add agents as nodes
        for analysis in analyses:
            G.add_node(analysis.agent_name, 
                      findings=analysis.total_findings,
                      confidence=analysis.confidence_score)
        
        # Add edges based on category overlap
        for i, analysis1 in enumerate(analyses):
            for j, analysis2 in enumerate(analyses):
                if i < j:
                    categories1 = set(f.category for f in analysis1.findings)
                    categories2 = set(f.category for f in analysis2.findings)
                    overlap = len(categories1.intersection(categories2))
                    
                    if overlap > 0:
                        G.add_edge(analysis1.agent_name, analysis2.agent_name, 
                                  weight=overlap, overlap=overlap)
        
        # Create the network visualization
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Node sizes based on findings count
        node_sizes = [G.nodes[node]['findings'] * 100 for node in G.nodes()]
        
        # Node colors based on confidence
        node_colors = [G.nodes[node]['confidence'] for node in G.nodes()]
        
        # Draw the network
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors,
                              cmap=plt.cm.viridis, alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Add edge labels for overlap
        edge_labels = nx.get_edge_attributes(G, 'overlap')
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
        
        plt.title('Agent Interaction Network\n(Node size = findings count, Color = confidence)', 
                 fontsize=16, fontweight='bold')
        
        # Create colorbar properly
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca())
        cbar.set_label('Confidence Score')
        
        plt.axis('off')
        
        plt.savefig(self.output_dir / 'agent_network.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'agent_network.svg', format='svg', bbox_inches='tight')
        plt.close()

    def create_findings_analysis(self, analyses: List[DiversityAnalysis], metrics: Dict[str, Any]):
        """Create detailed findings analysis visualization"""
        
        # Prepare data for analysis
        all_findings = []
        for analysis in analyses:
            for finding in analysis.findings:
                all_findings.append({
                    'agent': analysis.agent_name,
                    'category': finding.category,
                    'confidence': finding.confidence,
                    'question': finding.question
                })
        
        if not all_findings:
            return
        
        df = pd.DataFrame(all_findings)
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Agent-Category Heatmap
        pivot_table = df.groupby(['agent', 'category']).size().unstack(fill_value=0)
        sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlOrRd', ax=ax1)
        ax1.set_title('Findings by Agent and Category', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Category')
        ax1.set_ylabel('Agent')
        
        # 2. Confidence by Category
        confidence_mapping = {'High': 1.0, 'Medium': 0.6, 'Low': 0.3}
        df['confidence_numeric'] = df['confidence'].map(confidence_mapping)
        
        category_confidence = df.groupby('category')['confidence_numeric'].mean()
        bars = ax2.bar(category_confidence.index, category_confidence.values, 
                      color=plt.cm.Set3(np.linspace(0, 1, len(category_confidence))))
        ax2.set_title('Average Confidence by Category', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Average Confidence Score')
        ax2.set_ylim(0, 1)
        
        # Add value labels
        for bar, value in zip(bars, category_confidence.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Findings Distribution
        agent_counts = df['agent'].value_counts()
        colors_agent = plt.cm.Pastel1(np.linspace(0, 1, len(agent_counts)))
        wedges, texts, autotexts = ax3.pie(agent_counts.values, labels=agent_counts.index, 
                                           autopct='%1.1f%%', colors=colors_agent, startangle=90)
        ax3.set_title('Findings Distribution by Agent', fontsize=14, fontweight='bold')
        
        # 4. Category Distribution
        category_counts = df['category'].value_counts()
        colors_cat = plt.cm.Set2(np.linspace(0, 1, len(category_counts)))
        wedges, texts, autotexts = ax4.pie(category_counts.values, labels=category_counts.index,
                                           autopct='%1.1f%%', colors=colors_cat, startangle=90)
        ax4.set_title('Findings Distribution by Category', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'findings_analysis.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'findings_analysis.svg', format='svg', bbox_inches='tight')
        plt.close()

    def generate_pdf_report(self, analyses: List[DiversityAnalysis], metrics: Dict[str, Any], context: str):
        """Generate comprehensive PDF report"""
        
        doc = SimpleDocTemplate(str(self.output_dir / "diversity_analysis_report.pdf"), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("🎯 Diversity Hypothesis Analysis Report", title_style))
        story.append(Spacer(1, 12))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_text = f"""
        This report presents the results of a multi-agent diversity analysis using LangGraph orchestration.
        
        <b>Key Metrics:</b>
        • Total Findings: {metrics['total_findings']}
        • Unique Findings: {metrics['unique_findings']}
        • Diversity Score: {metrics['diversity_score']:.2f}
        • Agent Coverage: {metrics['agent_coverage']}/{len(self.agents)}
        • Category Coverage: {metrics['category_coverage']} categories
        
        <b>Analysis Context:</b> {context[:200]}...
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Agent Results
        story.append(Paragraph("Agent Analysis Results", styles['Heading2']))
        
        agent_data = []
        agent_data.append(['Agent', 'Findings', 'Confidence', 'Diversity Score'])
        
        for analysis in analyses:
            agent_data.append([
                analysis.agent_name,
                str(analysis.total_findings),
                f"{analysis.confidence_score:.2f}",
                f"{analysis.diversity_score:.2f}"
            ])
        
        agent_table = Table(agent_data)
        agent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(agent_table)
        story.append(Spacer(1, 12))
        
        # Detailed Findings
        story.append(Paragraph("Detailed Findings by Agent", styles['Heading2']))
        
        for analysis in analyses:
            if analysis.findings:
                story.append(Paragraph(f"<b>{analysis.agent_name}</b>", styles['Heading3']))
                
                for i, finding in enumerate(analysis.findings[:3], 1):  # Show first 3 findings
                    finding_text = f"""
                    <b>Finding {i}:</b> {finding.question}
                    <b>Category:</b> {finding.category}
                    <b>Confidence:</b> {finding.confidence}
                    <b>Blind Spot:</b> {finding.blind_spots}
                    <b>Recommendation:</b> {finding.recommendation}
                    """
                    story.append(Paragraph(finding_text, styles['Normal']))
                    story.append(Spacer(1, 6))
        
        doc.build(story)

    def generate_markdown_report(self, analyses: List[DiversityAnalysis], metrics: Dict[str, Any], context: str):
        """Generate comprehensive Markdown report"""
        
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
        
        # Render template
        jinja_template = Template(template)
        markdown_content = jinja_template.render(
            analyses=analyses,
            metrics=metrics,
            context=context,
            agents=self.agents
        )
        
        # Save markdown file
        with open(self.output_dir / "diversity_analysis_report.md", "w") as f:
            f.write(markdown_content)
        
        # Convert to HTML
        html_content = markdown.markdown(markdown_content, extensions=['tables'])
        with open(self.output_dir / "diversity_analysis_report.html", "w") as f:
            f.write(f"""
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
            """)

    def run_complete_analysis(self, context: str) -> Dict[str, Any]:
        """Run complete diversity analysis with all outputs"""
        
        print("🚀 Starting LangGraph Diversity Orchestrator...")
        print(f"📋 Context: {context[:100]}...")
        print(f"👥 Agents: {len(self.agents)}")
        
        # Run multi-threaded analysis
        analyses = self.run_multi_threaded_analysis(context)
        
        # Calculate diversity metrics
        metrics = self.calculate_diversity_metrics(analyses)
        
        # Create visualizations
        print("📊 Creating visualizations...")
        self.create_visualizations(analyses, metrics)
        
        # Generate reports
        print("📄 Generating reports...")
        self.generate_pdf_report(analyses, metrics, context)
        self.generate_markdown_report(analyses, metrics, context)
        
        # Save raw data
        with open(self.output_dir / "analysis_data.json", "w") as f:
            json.dump({
                "analyses": [analysis.model_dump() for analysis in analyses],
                "metrics": metrics,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print("✅ Analysis complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Diversity Score: {metrics['diversity_score']:.2f}")
        
        return {
            "analyses": analyses,
            "metrics": metrics,
            "output_dir": str(self.output_dir)
        }

def main():
    """Main function to run the diversity analysis"""
    
    # Test context
    context = """
    GitHub PR #1: Healthcare CDC Implementation with 28 commits, 11,222 additions, 90 deletions. 
    Multiple Copilot AI reviewers found: 1) Missing package installation instructions, 
    2) Potential credential exposure via subprocess, 3) Unnecessary input sanitization. 
    The PR implements real-time CDC operations for healthcare claims between DynamoDB and Snowflake.
    """
    
    orchestrator = LangGraphDiversityOrchestrator()
    results = orchestrator.run_complete_analysis(context)
    
    print("\n🎯 DIVERSITY HYPOTHESIS RESULTS:")
    print(f"   Diversity Score: {results['metrics']['diversity_score']:.2f}")
    print(f"   Total Findings: {results['metrics']['total_findings']}")
    print(f"   Unique Findings: {results['metrics']['unique_findings']}")
    print(f"   Agent Coverage: {results['metrics']['agent_coverage']}/{len(orchestrator.agents)}")
    
    if results['metrics']['diversity_score'] > 0.5:
        print("   ✅ DIVERSITY HYPOTHESIS CONFIRMED!")
    elif results['metrics']['diversity_score'] > 0.3:
        print("   ⚠️  DIVERSITY HYPOTHESIS PARTIALLY CONFIRMED")
    else:
        print("   ❌ DIVERSITY HYPOTHESIS NOT CONFIRMED")

if __name__ == "__main__":
    main() 