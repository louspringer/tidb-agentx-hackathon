#!/usr/bin/env python3
"""
🎯 DIVERSITY SYNTHESIS ORCHESTRATOR

A sophisticated system that synthesizes diverse AI findings into prioritized,
multi-stakeholder solutions using advanced prompt engineering.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

@dataclass
class Stakeholder:
    name: str
    role: str
    priority: int  # 1=highest, 5=lowest
    impact_areas: List[str]
    decision_power: str  # "High", "Medium", "Low"

@dataclass
class SynthesizedFix:
    title: str
    description: str
    stakeholder_impact: Dict[str, str]  # stakeholder -> impact description
    implementation_effort: str  # "Low", "Medium", "High"
    priority_score: float
    categories_addressed: List[str]
    estimated_roi: str  # "High", "Medium", "Low"

class FixSynthesis(BaseModel):
    fix_title: str = Field(description="Clear, actionable title for the fix")
    description: str = Field(description="Detailed description of the fix")
    stakeholder_impacts: Dict[str, str] = Field(description="Impact on each stakeholder")
    implementation_effort: str = Field(description="Low, Medium, or High effort")
    priority_score: float = Field(description="Priority score from 0-1")
    categories_addressed: List[str] = Field(description="Categories this fix addresses")
    estimated_roi: str = Field(description="High, Medium, or Low ROI")
    dependencies: List[str] = Field(description="Other fixes this depends on")
    timeline: str = Field(description="Estimated timeline for implementation")

class DiversitySynthesisOrchestrator:
    def __init__(self):
        self.stakeholders = [
            Stakeholder(
                name="Security Team",
                role="Security and compliance",
                priority=1,
                impact_areas=["security", "compliance", "risk"],
                decision_power="High"
            ),
            Stakeholder(
                name="DevOps Team", 
                role="Infrastructure and deployment",
                priority=2,
                impact_areas=["devops", "performance", "scalability"],
                decision_power="High"
            ),
            Stakeholder(
                name="Development Team",
                role="Code quality and maintainability",
                priority=3,
                impact_areas=["code_quality", "maintainability", "testing"],
                decision_power="Medium"
            ),
            Stakeholder(
                name="Product Team",
                role="User experience and business value",
                priority=4,
                impact_areas=["ux", "business_value", "user_adoption"],
                decision_power="Medium"
            ),
            Stakeholder(
                name="Business Stakeholders",
                role="Cost and timeline management",
                priority=5,
                impact_areas=["cost", "timeline", "business_impact"],
                decision_power="Low"
            )
        ]
        
        self.output_dir = Path("synthesis_output")
        self.output_dir.mkdir(exist_ok=True)

    def create_llm_client(self) -> ChatOpenAI:
        """Create LLM client for synthesis"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OPENAI_API_KEY found")
        
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=api_key
        )

    def load_diversity_findings(self, analysis_file: str) -> Dict[str, Any]:
        """Load findings from diversity analysis"""
        with open(analysis_file, 'r') as f:
            data = json.load(f)
        return data

    def synthesize_fixes(self, findings_data: Dict[str, Any]) -> List[FixSynthesis]:
        """Synthesize diverse findings into prioritized fixes"""
        
        llm = self.create_llm_client()
        
        # Prepare findings for synthesis
        all_findings = []
        for analysis in findings_data['analyses']:
            agent_name = analysis['agent_name']
            for finding in analysis['findings']:
                all_findings.append({
                    'agent': agent_name,
                    'category': finding['category'],
                    'question': finding['question'],
                    'blind_spots': finding['blind_spots'],
                    'recommendation': finding['recommendation'],
                    'confidence': finding['confidence']
                })
        
        # Create synthesis prompt
        synthesis_prompt = f"""
You are a senior technical architect tasked with synthesizing diverse findings into prioritized, actionable fixes.

CONTEXT:
We have analyzed a GitHub PR for a Healthcare CDC implementation and found {len(all_findings)} diverse issues from multiple AI perspectives.

STAKEHOLDERS (in priority order):
{chr(10).join([f"{i+1}. {s.name} ({s.role}) - Priority: {s.priority}, Decision Power: {s.decision_power}" for i, s in enumerate(self.stakeholders)])}

FINDINGS TO SYNTHESIZE:
{chr(10).join([f"• {f['agent']} ({f['category']}): {f['question']} - {f['recommendation']}" for f in all_findings])}

TASK:
Synthesize these findings into 5-8 prioritized fixes that:
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

        messages = [
            SystemMessage(content="You are an expert technical architect specializing in synthesizing diverse technical findings into actionable, prioritized solutions."),
            HumanMessage(content=synthesis_prompt)
        ]
        
        response = llm.invoke(messages)
        
        # Parse response
        try:
            content = response.content
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content
            
            fixes_data = json.loads(json_content)
            
            if isinstance(fixes_data, dict) and "fixes" in fixes_data:
                fixes_data = fixes_data["fixes"]
            
            fixes = [FixSynthesis(**fix) for fix in fixes_data]
            return fixes
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing synthesis response: {e}")
            return []

    def calculate_stakeholder_impact_matrix(self, fixes: List[FixSynthesis]) -> pd.DataFrame:
        """Calculate stakeholder impact matrix"""
        
        # Create impact matrix
        stakeholders = [s.name for s in self.stakeholders]
        impact_matrix = []
        
        for fix in fixes:
            row = []
            for stakeholder in stakeholders:
                impact = fix.stakeholder_impacts.get(stakeholder, "No impact")
                # Convert impact to numeric score using mapping
                # If impact string contains a known key, use its score; else default to 0
                score = 0
                for key, val in impact_score_map.items():
                    if key in impact:
                        score = val
                        break
                row.append(score)
            impact_matrix.append(row)
        
        return pd.DataFrame(impact_matrix, index=[fix.fix_title for fix in fixes], columns=stakeholders)

    def create_synthesis_visualizations(self, fixes: List[FixSynthesis], impact_matrix: pd.DataFrame):
        """Create visualizations for synthesis results"""
        
        # 1. Priority vs. ROI Scatter Plot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Priority vs. ROI
        roi_mapping = {"High": 3, "Medium": 2, "Low": 1}
        effort_mapping = {"High": 3, "Medium": 2, "Low": 1}
        
        priorities = [fix.priority_score for fix in fixes]
        rois = [roi_mapping.get(fix.estimated_roi, 1) for fix in fixes]
        efforts = [effort_mapping.get(fix.implementation_effort, 1) for fix in fixes]
        
        scatter = ax1.scatter(priorities, rois, s=[e*50 for e in efforts], 
                             c=efforts, cmap='viridis', alpha=0.7)
        ax1.set_xlabel('Priority Score')
        ax1.set_ylabel('ROI Score')
        ax1.set_title('Fix Priority vs. ROI (Size = Effort)')
        
        # Add fix labels
        for i, fix in enumerate(fixes):
            ax1.annotate(fix.fix_title[:20] + "...", 
                        (priorities[i], rois[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # 2. Stakeholder Impact Heatmap
        sns.heatmap(impact_matrix, annot=True, fmt='d', cmap='YlOrRd', ax=ax2)
        ax2.set_title('Stakeholder Impact Matrix')
        ax2.set_xlabel('Stakeholders')
        ax2.set_ylabel('Fixes')
        
        # 3. Categories Addressed
        all_categories = set()
        for fix in fixes:
            all_categories.update(fix.categories_addressed)
        
        category_counts = {}
        for category in all_categories:
            count = sum(1 for fix in fixes if category in fix.categories_addressed)
            category_counts[category] = count
        
        categories = list(category_counts.keys())
        counts = list(category_counts.values())
        
        bars = ax3.bar(categories, counts, color=plt.cm.Set3(np.linspace(0, 1, len(categories))))
        ax3.set_title('Categories Addressed by Fixes')
        ax3.set_ylabel('Number of Fixes')
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        # 4. Implementation Timeline
        timeline_mapping = {"1-2 weeks": 1, "2-4 weeks": 2, "1-2 months": 3, "2-3 months": 4}
        timelines = [timeline_mapping.get(fix.timeline, 2) for fix in fixes]
        
        timeline_labels = [fix.timeline for fix in fixes]
        bars = ax4.bar(range(len(fixes)), timelines, color=plt.cm.Pastel1(np.linspace(0, 1, len(fixes))))
        ax4.set_title('Implementation Timeline')
        ax4.set_ylabel('Timeline Score')
        ax4.set_xticks(range(len(fixes)))
        ax4.set_xticklabels([fix.fix_title[:15] + "..." for fix in fixes], rotation=45)
        
        # Add timeline labels
        for bar, timeline in zip(bars, timeline_labels):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    timeline, ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'synthesis_analysis.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'synthesis_analysis.svg', format='svg', bbox_inches='tight')
        plt.close()

    def generate_prioritized_report(self, fixes: List[FixSynthesis], impact_matrix: pd.DataFrame):
        """Generate prioritized implementation report"""
        
        # Sort fixes by priority score
        sorted_fixes = sorted(fixes, key=lambda x: x.priority_score, reverse=True)
        
        report = f"""# 🎯 SYNTHESIZED FIXES - PRIORITIZED IMPLEMENTATION PLAN

## Executive Summary

This report synthesizes {len(fixes)} diverse findings into prioritized, actionable fixes that address multiple stakeholder concerns.

### Key Metrics
- **Total Fixes**: {len(fixes)}
- **Average Priority Score**: {sum(f.priority_score for f in fixes)/len(fixes):.2f}
- **High ROI Fixes**: {sum(1 for f in fixes if f.estimated_roi == 'High')}
- **Low Effort Fixes**: {sum(1 for f in fixes if f.implementation_effort == 'Low')}

## Prioritized Implementation Plan

### Phase 1: Critical Fixes (Priority Score > 0.8)

"""
        
        for i, fix in enumerate(sorted_fixes, 1):
            if fix.priority_score > 0.8:
                report += f"""
#### {i}. {fix.fix_title}

**Priority Score**: {fix.priority_score:.2f}
**Implementation Effort**: {fix.implementation_effort}
**Estimated ROI**: {fix.estimated_roi}
**Timeline**: {fix.timeline}

**Description**: {fix.description}

**Stakeholder Impacts**:
"""
                for stakeholder, impact in fix.stakeholder_impacts.items():
                    report += f"- **{stakeholder}**: {impact}\n"
                
                report += f"""
**Categories Addressed**: {', '.join(fix.categories_addressed)}
**Dependencies**: {', '.join(fix.dependencies) if fix.dependencies else 'None'}

---
"""

        report += f"""
### Phase 2: High Priority Fixes (Priority Score 0.6-0.8)

"""
        
        for i, fix in enumerate(sorted_fixes, 1):
            if 0.6 <= fix.priority_score <= 0.8:
                report += f"""
#### {i}. {fix.fix_title}

**Priority Score**: {fix.priority_score:.2f}
**Implementation Effort**: {fix.implementation_effort}
**Estimated ROI**: {fix.estimated_roi}
**Timeline**: {fix.timeline}

**Description**: {fix.description}

**Stakeholder Impacts**:
"""
                for stakeholder, impact in fix.stakeholder_impacts.items():
                    report += f"- **{stakeholder}**: {impact}\n"
                
                report += f"""
**Categories Addressed**: {', '.join(fix.categories_addressed)}
**Dependencies**: {', '.join(fix.dependencies) if fix.dependencies else 'None'}

---
"""

        report += f"""
### Phase 3: Medium Priority Fixes (Priority Score < 0.6)

"""
        
        for i, fix in enumerate(sorted_fixes, 1):
            if fix.priority_score < 0.6:
                report += f"""
#### {i}. {fix.fix_title}

**Priority Score**: {fix.priority_score:.2f}
**Implementation Effort**: {fix.implementation_effort}
**Estimated ROI**: {fix.estimated_roi}
**Timeline**: {fix.timeline}

**Description**: {fix.description}

**Stakeholder Impacts**:
"""
                for stakeholder, impact in fix.stakeholder_impacts.items():
                    report += f"- **{stakeholder}**: {impact}\n"
                
                report += f"""
**Categories Addressed**: {', '.join(fix.categories_addressed)}
**Dependencies**: {', '.join(fix.dependencies) if fix.dependencies else 'None'}

---
"""

        report += f"""
## Stakeholder Impact Analysis

The following matrix shows the impact of each fix on different stakeholders:

```
{impact_matrix.to_string()}
```

## Implementation Recommendations

1. **Start with Phase 1 fixes** - These address the highest priority stakeholder concerns
2. **Consider dependencies** - Some fixes may depend on others being completed first
3. **Balance effort vs. impact** - Focus on high-ROI, low-effort fixes when possible
4. **Stakeholder communication** - Keep all stakeholders informed of progress and impact

## Success Metrics

- **Security Team Satisfaction**: Address all security-related findings
- **DevOps Team Efficiency**: Reduce deployment and infrastructure issues
- **Development Team Productivity**: Improve code quality and maintainability
- **Product Team Success**: Enhance user experience and business value
- **Business Stakeholder ROI**: Demonstrate clear value and cost savings
"""

        # Save report
        with open(self.output_dir / "prioritized_implementation_plan.md", "w") as f:
            f.write(report)
        
        return report

    def run_synthesis(self, analysis_file: str) -> Dict[str, Any]:
        """Run complete synthesis analysis"""
        
        print("🎯 Starting Diversity Synthesis Orchestrator...")
        print(f"📁 Loading analysis from: {analysis_file}")
        
        # Load findings
        findings_data = self.load_diversity_findings(analysis_file)
        
        # Synthesize fixes
        print("🧠 Synthesizing diverse findings into prioritized fixes...")
        fixes = self.synthesize_fixes(findings_data)
        
        if not fixes:
            print("❌ No fixes synthesized")
            return {}
        
        print(f"✅ Synthesized {len(fixes)} prioritized fixes")
        
        # Calculate impact matrix
        impact_matrix = self.calculate_stakeholder_impact_matrix(fixes)
        
        # Create visualizations
        print("📊 Creating synthesis visualizations...")
        self.create_synthesis_visualizations(fixes, impact_matrix)
        
        # Generate report
        print("📄 Generating prioritized implementation plan...")
        report = self.generate_prioritized_report(fixes, impact_matrix)
        
        # Save synthesis data
        with open(self.output_dir / "synthesis_data.json", "w") as f:
            json.dump({
                "fixes": [fix.model_dump() for fix in fixes],
                "impact_matrix": impact_matrix.to_dict(),
                "stakeholders": [asdict(s) for s in self.stakeholders],
                "analysis_file": analysis_file
            }, f, indent=2)
        
        print("✅ Synthesis complete!")
        print(f"📁 Output directory: {self.output_dir}")
        
        return {
            "fixes": fixes,
            "impact_matrix": impact_matrix,
            "report": report,
            "output_dir": str(self.output_dir)
        }

def main():
    """Main function to run synthesis"""
    
    orchestrator = DiversitySynthesisOrchestrator()
    
    # Use the analysis data from our previous run
    analysis_file = "diversity_analysis_output/analysis_data.json"
    
    if not os.path.exists(analysis_file):
        print(f"❌ Analysis file not found: {analysis_file}")
        print("Please run the diversity analysis first")
        return
    
    results = orchestrator.run_synthesis(analysis_file)
    
    if results:
        print("\n🎯 SYNTHESIS RESULTS:")
        print(f"   Total Fixes: {len(results['fixes'])}")
        print(f"   Average Priority: {sum(f.priority_score for f in results['fixes'])/len(results['fixes']):.2f}")
        print(f"   High ROI Fixes: {sum(1 for f in results['fixes'] if f.estimated_roi == 'High')}")
        print(f"   Low Effort Fixes: {sum(1 for f in results['fixes'] if f.implementation_effort == 'Low')}")
        
        print("\n📋 Top 3 Prioritized Fixes:")
        sorted_fixes = sorted(results['fixes'], key=lambda x: x.priority_score, reverse=True)
        for i, fix in enumerate(sorted_fixes[:3], 1):
            print(f"   {i}. {fix.fix_title} (Priority: {fix.priority_score:.2f}, ROI: {fix.estimated_roi})")

if __name__ == "__main__":
    main() 