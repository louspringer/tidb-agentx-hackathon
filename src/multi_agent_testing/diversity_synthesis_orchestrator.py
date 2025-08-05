
#!/usr/bin/env python3
"""
🎯 DIVERSITY SYNTHESIS ORCHESTRATOR

A sophisticated system that synthesizes diverse AI findings into prioritized,
multi-stakeholder solutions using advanced prompt engineering.
"""

import json
import os
from dataclasses import dataclass, asdict

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


    implementation_effort: str = Field(description="Low, Medium, or High effort")
    priority_score: float = Field(description="Priority score from 0-1")
    categories_addressed: List[str] = Field(description="Categories this fix addresses")
    estimated_roi: str = Field(description="High, Medium, or Low ROI")
    dependencies: List[str] = Field(description="Other fixes this depends on")
    timeline: str = Field(description="Estimated timeline for implementation")


        self.stakeholders = [
            Stakeholder(
                name="Security Team",
                role="Security and compliance",
                priority=1,
                impact_areas=["security", "compliance", "risk"],

            ),
            Stakeholder(
                name="Development Team",
                role="Code quality and maintainability",
                priority=3,
                impact_areas=["code_quality", "maintainability", "testing"],

            ),
            Stakeholder(
                name="Product Team",
                role="User experience and business value",
                priority=4,
                impact_areas=["ux", "business_value", "user_adoption"],

            ),
            Stakeholder(
                name="Business Stakeholders",
                role="Cost and timeline management",
                priority=5,
                impact_areas=["cost", "timeline", "business_impact"],

        self.output_dir = Path("synthesis_output")
        self.output_dir.mkdir(exist_ok=True)

    def create_llm_client(self) -> ChatOpenAI:
        """Create LLM client for synthesis"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("No OPENAI_API_KEY found")

            data = json.load(f)
        return data

    def synthesize_fixes(self, findings_data: Dict[str, Any]) -> List[FixSynthesis]:
        """Synthesize diverse findings into prioritized fixes"""

        # Create synthesis prompt
        synthesis_prompt = f"""
You are a senior technical architect tasked with synthesizing diverse findings into prioritized, actionable fixes.

CONTEXT:

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

        # Parse response
        try:
            content = response.content
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing synthesis response: {e}")
            return []


        for fix in fixes:
            row = []
            for stakeholder in stakeholders:
                impact = fix.stakeholder_impacts.get(stakeholder, "No impact")

        # 3. Categories Addressed
        all_categories = set()
        for fix in fixes:
            all_categories.update(fix.categories_addressed)

        category_counts = {}
        for category in all_categories:
            count = sum(1 for fix in fixes if category in fix.categories_addressed)
            category_counts[category] = count

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

**Categories Addressed**: {', '.join(fix.categories_addressed)}
**Dependencies**: {', '.join(fix.dependencies) if fix.dependencies else 'None'}

---
"""


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

**Categories Addressed**: {', '.join(fix.categories_addressed)}
**Dependencies**: {', '.join(fix.dependencies) if fix.dependencies else 'None'}

---
"""


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

**Categories Addressed**: {', '.join(fix.categories_addressed)}
**Dependencies**: {', '.join(fix.dependencies) if fix.dependencies else 'None'}

---
"""


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

        return {
            "fixes": fixes,
            "impact_matrix": impact_matrix,
            "report": report,

    if not os.path.exists(analysis_file):
        print(f"❌ Analysis file not found: {analysis_file}")
        print("Please run the diversity analysis first")
        return

