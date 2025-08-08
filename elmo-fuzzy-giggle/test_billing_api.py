"""Test suite for billing_api"""

import asyncio

from src.gemini_billing_analyzer import GeminiBillingAnalyzer


@asyncio.coroutine
def test_billing_data_collection(analyzer) -> bool:
    """Test billing data collection"""
    billing_data = analyzer.get_billing_data()
    return billing_data is not None and "project_id" in billing_data


@asyncio.coroutine
def test_gemini_analysis(analyzer) -> bool:
    """Test Gemini analysis"""
    billing_data = analyzer.get_billing_data()
    if not billing_data:
        return False
    analysis = analyzer.analyze_billing_with_gemini(billing_data)
    return "error" not in analysis


@asyncio.coroutine
def test_ghostbusters_integration(analyzer) -> bool:
    """Test Ghostbusters integration"""
    result = await analyzer.run_ghostbusters_analysis(".")
    return "error" not in result


def main() -> None:
    """Main test runner"""
    print("🧪 Running Gemini Billing Analyzer Tests...")
    analyzer = GeminiBillingAnalyzer()
    print(f'🤖 Gemini LLM: {"✅ Available" if analyzer.llm else "❌ Not available"}')

    # Run tests
    for test_func in [
        test_billing_data_collection,
        test_gemini_analysis,
        test_ghostbusters_integration,
    ]:
        try:
            result = await test_func(analyzer)
            print(f'✅ {test_func.__name__}: {"PASS" if result else "FAIL"}')
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")

    print("🎯 Test suite completed!")
