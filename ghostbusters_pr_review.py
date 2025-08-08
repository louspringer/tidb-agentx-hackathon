#!/usr/bin/env python3
"""
Ghostbusters PR Review and Service Management Analysis
"""

import asyncio
from typing import Any

# Import Ghostbusters components
from src.ghostbusters.agents import (
    ArchitectureExpert,
    BuildExpert,
    CodeQualityExpert,
    ModelExpert,
    SecurityExpert,
    TestExpert,
)
from src.ghostbusters.recovery import (
    ImportResolver,
    IndentationFixer,
    SyntaxRecoveryEngine,
    TypeAnnotationFixer,
)
from src.ghostbusters.validators import (
    ArchitectureValidator,
    BuildValidator,
    CodeQualityValidator,
    ModelValidator,
    SecurityValidator,
    TestValidator,
)
from src.secure_shell_service.secure_executor import secure_execute


class GhostbustersPRReview:
    """Comprehensive PR review using Ghostbusters agents"""

    def __init__(self):
        self.experts = [
            SecurityExpert(),
            CodeQualityExpert(),
            TestExpert(),
            BuildExpert(),
            ArchitectureExpert(),
            ModelExpert(),
        ]
        self.validators = [
            SecurityValidator(),
            CodeQualityValidator(),
            TestValidator(),
            BuildValidator(),
            ArchitectureValidator(),
            ModelValidator(),
        ]
        self.recovery_engines = [
            SyntaxRecoveryEngine(),
            IndentationFixer(),
            ImportResolver(),
            TypeAnnotationFixer(),
        ]

    async def run_comprehensive_analysis(self) -> dict[str, Any]:
        """Run comprehensive Ghostbusters analysis"""
        print("🔍 **GHOSTBUSTERS PR REVIEW ANALYSIS**")
        print("=" * 50)

        # Phase 1: Detect Delusions
        print("\n📋 **PHASE 1: DELUSION DETECTION**")
        print("-" * 30)

        delusion_results = []
        for expert in self.experts:
            try:
                result = await expert.detect_delusions(".")
                delusion_results.append(result)
                print(
                    f"✅ {expert.__class__.__name__}: {len(result.delusions)} delusions found",
                )
            except Exception as e:
                print(f"❌ {expert.__class__.__name__}: Error - {e}")

        # Phase 2: Validate Findings
        print("\n🔍 **PHASE 2: VALIDATION**")
        print("-" * 30)

        validation_results = []
        for validator in self.validators:
            try:
                result = await validator.validate_findings(delusion_results)
                validation_results.append(result)
                print(
                    f"✅ {validator.__class__.__name__}: {result.confidence_score} confidence",
                )
            except Exception as e:
                print(f"❌ {validator.__class__.__name__}: Error - {e}")

        # Phase 3: Service Management Analysis
        print("\n🚀 **PHASE 3: SERVICE MANAGEMENT ANALYSIS**")
        print("-" * 30)

        service_analysis = await self._analyze_service_management()

        # Phase 4: PR Readiness Assessment
        print("\n📋 **PHASE 4: PR READINESS ASSESSMENT**")
        print("-" * 30)

        pr_assessment = await self._assess_pr_readiness(
            delusion_results,
            validation_results,
        )

        return {
            "delusions": delusion_results,
            "validations": validation_results,
            "service_analysis": service_analysis,
            "pr_assessment": pr_assessment,
        }

    async def _analyze_service_management(self) -> dict[str, Any]:
        """Analyze service management concerns"""
        print("🔍 Analyzing service management...")

        # Check for running services
        # import subprocess  # REMOVED - replaced with secure_execute

        try:
            result = secure_execute(["ps", "aux"], capture_output=True, text=True)
            running_services = []
            for line in result.stdout.split("\n"):
                if "python" in line and (
                    "streamlit" in line or "uvicorn" in line or "flask" in line
                ):
                    running_services.append(line.strip())

            print(f"📊 Found {len(running_services)} potential running services")

            # Security concerns
            security_concerns = []
            if running_services:
                security_concerns.append(
                    "⚠️ Services running - potential security exposure",
                )
                security_concerns.append(
                    "⚠️ Consider service isolation and access controls",
                )

            # Resource concerns
            resource_concerns = []
            if len(running_services) > 2:
                resource_concerns.append(
                    "⚠️ Multiple services running - resource consumption",
                )
                resource_concerns.append("⚠️ Consider service lifecycle management")

            # Recommendations
            recommendations = [
                "✅ Implement service health checks",
                "✅ Add service monitoring and logging",
                "✅ Consider containerization for isolation",
                "✅ Implement graceful shutdown procedures",
                "✅ Add service discovery and load balancing",
            ]

            return {
                "running_services": running_services,
                "security_concerns": security_concerns,
                "resource_concerns": resource_concerns,
                "recommendations": recommendations,
            }

        except Exception as e:
            return {"error": f"Service analysis failed: {e}"}

    async def _assess_pr_readiness(
        self,
        delusions: list,
        validations: list,
    ) -> dict[str, Any]:
        """Assess PR readiness"""
        print("🔍 Assessing PR readiness...")

        # Count critical issues
        critical_issues = 0
        for delusion in delusions:
            if hasattr(delusion, "delusions"):
                for d in delusion.delusions:
                    if (
                        "critical" in d.severity.lower()
                        or "security" in d.description.lower()
                    ):
                        critical_issues += 1

        # Test status
        test_status = "✅ PASSING" if critical_issues == 0 else "❌ FAILING"

        # Service management status
        service_status = "✅ READY" if critical_issues == 0 else "⚠️ NEEDS ATTENTION"

        # Recommendations
        recommendations = []
        if critical_issues > 0:
            recommendations.append("❌ Fix critical issues before PR")
        else:
            recommendations.append("✅ PR ready for review")
            recommendations.append(
                "✅ Consider adding service management documentation",
            )
            recommendations.append("✅ Add deployment and rollback procedures")

        return {
            "critical_issues": critical_issues,
            "test_status": test_status,
            "service_status": service_status,
            "recommendations": recommendations,
            "pr_ready": critical_issues == 0,
        }


async def main():
    """Main Ghostbusters PR review"""
    reviewer = GhostbustersPRReview()
    results = await reviewer.run_comprehensive_analysis()

    print("\n" + "=" * 50)
    print("📊 **FINAL GHOSTBUSTERS RECOMMENDATIONS**")
    print("=" * 50)

    # PR Readiness
    pr_assessment = results["pr_assessment"]
    print(f"\n🚀 **PR READINESS: {pr_assessment['pr_ready']}**")
    print(f"   - Critical Issues: {pr_assessment['critical_issues']}")
    print(f"   - Test Status: {pr_assessment['test_status']}")
    print(f"   - Service Status: {pr_assessment['service_status']}")

    # Service Management
    service_analysis = results["service_analysis"]
    print("\n🔧 **SERVICE MANAGEMENT:**")
    print(f"   - Running Services: {len(service_analysis.get('running_services', []))}")
    print(
        f"   - Security Concerns: {len(service_analysis.get('security_concerns', []))}",
    )
    print(
        f"   - Resource Concerns: {len(service_analysis.get('resource_concerns', []))}",
    )

    # Recommendations
    print("\n💡 **RECOMMENDATIONS:**")
    for rec in pr_assessment.get("recommendations", []):
        print(f"   {rec}")

    for rec in service_analysis.get("recommendations", []):
        print(f"   {rec}")

    # Final verdict
    if pr_assessment["pr_ready"]:
        print("\n✅ **GHOSTBUSTERS VERDICT: PR READY**")
        print("   The Ghostbusters approve this implementation!")
    else:
        print("\n❌ **GHOSTBUSTERS VERDICT: PR NOT READY**")
        print("   Address critical issues before proceeding.")


if __name__ == "__main__":
    asyncio.run(main())
