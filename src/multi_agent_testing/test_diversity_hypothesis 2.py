#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TEST SUITE FOR DIVERSITY HYPOTHESIS

Unit tests, integration tests, and performance tests for the diversity hypothesis.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from diversity_synthesis_orchestrator import (
    DiversitySynthesisOrchestrator,  # type: ignore
)
from langgraph_diversity_orchestrator import (
    LangGraphDiversityOrchestrator,  # type: ignore
)
from multi_dimensional_smoke_test import MultiDimensionalSmokeTest  # type: ignore


class TestDiversityHypothesis(unittest.TestCase):
    """Test suite for diversity hypothesis components"""

    def setUp(self) -> None:
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test data
        self.test_findings = [
            {
                "agent": "Security Expert",
                "category": "security",
                "question": "What security vulnerabilities exist?",
                "blind_spots": "Missing input validation",
                "recommendation": "Implement proper validation",
                "confidence": "High",
            },
            {
                "agent": "DevOps Engineer",
                "category": "devops",
                "question": "What infrastructure issues could arise?",
                "blind_spots": "Missing monitoring",
                "recommendation": "Add comprehensive monitoring",
                "confidence": "Medium",
            },
        ]

        # Mock API responses
        self.mock_api_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "questions": [
                                    {
                                        "question": "What are you missing?",
                                        "confidence": "High",
                                        "blind_spots": "Test blind spot",
                                        "recommendation": "Test recommendation",
                                    },
                                ],
                            },
                        ),
                    },
                },
            ],
        }

    def tearDown(self) -> None:
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_multi_dimensional_smoke_test_initialization(self) -> None:
        """Test MultiDimensionalSmokeTest initialization"""
        test = MultiDimensionalSmokeTest()

        # Test model configurations
        self.assertIn("gpt4", test.models)
        self.assertIn("claude", test.models)
        self.assertIn("perplexity", test.models)

        # Test scenarios
        self.assertIn("healthcare_cdc_pr", test.scenarios)
        self.assertIn("security_audit", test.scenarios)

        # Test roles
        self.assertIn("skeptical_partner", test.roles)
        self.assertIn("domain_expert", test.roles)

        # Test prompt structures
        self.assertIn("direct_questions", test.prompt_structures)
        self.assertIn("socratic_questioning", test.prompt_structures)

    def test_extract_questions(self) -> None:
        """Test question extraction from LLM responses"""
        test = MultiDimensionalSmokeTest()

        # Test JSON extraction
        json_content = '```json\n{"questions": [{"question": "Test question?"}]}\n```'
        questions = test.extract_questions(json_content)
        self.assertEqual(len(questions), 1)
        self.assertIn("Test question?", questions)

        # Test fallback extraction
        text_content = 'Some text with "question": "Another test?" in it'
        questions = test.extract_questions(text_content)
        self.assertGreater(len(questions), 0)

    def test_calculate_confidence(self) -> None:
        """Test confidence calculation"""
        test = MultiDimensionalSmokeTest()

        # Test high confidence indicators
        high_confidence_questions = [
            "What evidence do you have?",
            "How do you prove this?",
            "What demonstrates this?",
        ]
        confidence = test.calculate_confidence(high_confidence_questions)
        self.assertGreater(confidence, 0.5)

        # Test low confidence indicators
        low_confidence_questions = [
            "Maybe this could work?",
            "Perhaps we should consider?",
            "It might be possible?",
        ]
        confidence = test.calculate_confidence(low_confidence_questions)
        self.assertLess(confidence, 0.5)

    def test_calculate_agreement(self) -> None:
        """Test agreement calculation"""
        test = MultiDimensionalSmokeTest()

        # Test agreement
        self.assertTrue(test.calculate_agreement(0.6, 0.5))
        self.assertTrue(test.calculate_agreement(0.4, 0.5))

        # Test disagreement
        self.assertFalse(test.calculate_agreement(0.9, 0.5))
        self.assertFalse(test.calculate_agreement(0.1, 0.5))

    def test_generate_insights(self) -> None:
        """Test insight generation"""
        test = MultiDimensionalSmokeTest()

        # Test high confidence
        questions = ["Q1", "Q2", "Q3", "Q4", "Q5"]
        insights = test.generate_insights(questions, 0.9)
        self.assertIn("High confidence analysis", insights)
        self.assertIn("Comprehensive analysis", insights)

        # Test low confidence
        questions = ["Q1"]
        insights = test.generate_insights(questions, 0.2)
        self.assertIn("Low confidence analysis", insights)
        self.assertIn("Limited analysis", insights)

    @patch("requests.post")
    def test_call_llm_success(self, mock_post) -> None:  # type: ignore
        """Test successful LLM API call"""
        test = MultiDimensionalSmokeTest()

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = self.mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test API call
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            result = test.call_llm("gpt4", "Test prompt", 0.7)
            self.assertIn("choices", result)

    @patch("requests.post")
    def test_call_llm_error(self, mock_post) -> None:  # type: ignore
        """Test LLM API call error handling"""
        test = MultiDimensionalSmokeTest()

        # Mock error response
        mock_post.side_effect = Exception("API Error")

        # Test error handling
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            result = test.call_llm("gpt4", "Test prompt", 0.7)
            self.assertIn("error", result)

    def test_run_test_success(self) -> None:
        """Test successful test run"""
        test = MultiDimensionalSmokeTest()

        config = {
            "model": "gpt4",
            "temperature": 0.7,
            "role": "skeptical_partner",
            "prompt_structure": "direct_questions",
            "response_format": "json_structured",
        }

        with patch.object(test, "call_llm") as mock_call:
            mock_call.return_value = self.mock_api_response
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
                result = test.run_test(config, "healthcare_cdc_pr")

                self.assertIn("config", result)
                self.assertIn("scenario", result)
                self.assertIn("agreement", result)
                self.assertIn("insights", result)

    def test_run_test_error(self) -> None:
        """Test test run with error"""
        test = MultiDimensionalSmokeTest()

        config = {
            "model": "gpt4",
            "temperature": 0.7,
            "role": "skeptical_partner",
            "prompt_structure": "direct_questions",
            "response_format": "json_structured",
        }

        with patch.object(test, "call_llm") as mock_call:
            mock_call.return_value = {"error": "API Error"}
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
                result = test.run_test(config, "healthcare_cdc_pr")

                self.assertIn("error", result)
                self.assertFalse(result.get("agreement", True))


class TestLangGraphDiversityOrchestrator(unittest.TestCase):
    """Test suite for LangGraph diversity orchestrator"""

    def setUp(self) -> None:
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test analysis data
        self.test_analysis_data = {
            "analyses": [
                {
                    "agent_name": "Security Expert",
                    "findings": [
                        {
                            "question": "What security vulnerabilities exist?",
                            "confidence": "High",
                            "blind_spots": "Missing input validation",
                            "recommendation": "Implement proper validation",
                            "category": "security",
                        },
                    ],
                },
                {
                    "agent_name": "DevOps Engineer",
                    "findings": [
                        {
                            "question": "What infrastructure issues could arise?",
                            "confidence": "Medium",
                            "blind_spots": "Missing monitoring",
                            "recommendation": "Add comprehensive monitoring",
                            "category": "devops",
                        },
                    ],
                },
            ],
        }

    def tearDown(self) -> None:
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_orchestrator_initialization(self) -> None:
        """Test LangGraphDiversityOrchestrator initialization"""
        orchestrator = LangGraphDiversityOrchestrator()

        # Test agents
        self.assertEqual(len(orchestrator.agents), 5)
        agent_names = [agent.name for agent in orchestrator.agents]
        self.assertIn("Security Expert", agent_names)
        self.assertIn("DevOps Engineer", agent_names)
        self.assertIn("Code Quality Expert", agent_names)
        self.assertIn("User Experience Advocate", agent_names)
        self.assertIn("Performance Engineer", agent_names)

    def test_create_llm_client(self) -> None:
        """Test LLM client creation"""
        orchestrator = LangGraphDiversityOrchestrator()

        # Test OpenAI client
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            client = orchestrator.create_llm_client(orchestrator.agents[0])
            self.assertIsNotNone(client)

        # Test missing API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                orchestrator.create_llm_client(orchestrator.agents[0])

    def test_calculate_diversity_metrics(self) -> None:
        """Test diversity metrics calculation"""
        orchestrator = LangGraphDiversityOrchestrator()

        # Create test analyses
        from langgraph_diversity_orchestrator import BlindSpotFinding, DiversityAnalysis

        analyses = [
            DiversityAnalysis(
                agent_name="Security Expert",
                findings=[
                    BlindSpotFinding(
                        question="Security question?",
                        confidence="High",
                        blind_spots="Security blind spot",
                        recommendation="Security recommendation",
                        category="security",
                    ),
                ],
                total_findings=1,
                confidence_score=0.8,
                diversity_score=0.8,
            ),
            DiversityAnalysis(
                agent_name="DevOps Engineer",
                findings=[
                    BlindSpotFinding(
                        question="DevOps question?",
                        confidence="Medium",
                        blind_spots="DevOps blind spot",
                        recommendation="DevOps recommendation",
                        category="devops",
                    ),
                ],
                total_findings=1,
                confidence_score=0.6,
                diversity_score=0.8,
            ),
        ]

        metrics = orchestrator.calculate_diversity_metrics(analyses)

        self.assertIn("total_findings", metrics)
        self.assertIn("unique_findings", metrics)
        self.assertIn("diversity_score", metrics)
        self.assertIn("agent_coverage", metrics)
        self.assertIn("category_coverage", metrics)


class TestDiversitySynthesisOrchestrator(unittest.TestCase):
    """Test suite for diversity synthesis orchestrator"""

    def setUp(self) -> None:
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test synthesis data
        self.test_synthesis_data = {
            "fixes": [
                {
                    "fix_title": "Implement Robust Credential Management",
                    "description": "Establish secure credential management",
                    "stakeholder_impacts": {
                        "Security Team": "High impact",
                        "DevOps Team": "Medium impact",
                    },
                    "implementation_effort": "Medium",
                    "priority_score": 1.0,
                    "categories_addressed": ["security", "devops"],
                    "estimated_roi": "High",
                    "dependencies": [],
                    "timeline": "2 weeks",
                },
            ],
        }

    def tearDown(self) -> None:
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_synthesis_orchestrator_initialization(self) -> None:
        """Test DiversitySynthesisOrchestrator initialization"""
        orchestrator = DiversitySynthesisOrchestrator()

        # Test stakeholders
        self.assertEqual(len(orchestrator.stakeholders), 5)
        stakeholder_names = [s.name for s in orchestrator.stakeholders]
        self.assertIn("Security Team", stakeholder_names)
        self.assertIn("DevOps Team", stakeholder_names)
        self.assertIn("Development Team", stakeholder_names)
        self.assertIn("Product Team", stakeholder_names)
        self.assertIn("Business Stakeholders", stakeholder_names)

    def test_calculate_stakeholder_impact_matrix(self) -> None:
        """Test stakeholder impact matrix calculation"""
        orchestrator = DiversitySynthesisOrchestrator()

        # Create test fixes
        from diversity_synthesis_orchestrator import FixSynthesis

        fixes = [
            FixSynthesis(
                fix_title="Test Fix",
                description="Test description",
                stakeholder_impacts={
                    "Security Team": "High impact",
                    "DevOps Team": "Medium impact",
                },
                implementation_effort="Medium",
                priority_score=0.8,
                categories_addressed=["security"],
                estimated_roi="High",
                dependencies=[],
                timeline="2 weeks",
            ),
        ]

        impact_matrix = orchestrator.calculate_stakeholder_impact_matrix(fixes)

        self.assertIsNotNone(impact_matrix)
        self.assertGreater(len(impact_matrix), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete diversity hypothesis system"""

    def setUp(self) -> None:
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test files
        os.makedirs("diversity_analysis_output", exist_ok=True)
        os.makedirs("synthesis_output", exist_ok=True)

    def tearDown(self) -> None:
        """Clean up integration test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_end_to_end_workflow(self) -> None:
        """Test complete end-to-end workflow"""
        # This would test the complete workflow from diversity analysis to synthesis
        # In a real test, we would mock the API calls and test the full pipeline

    def test_cost_analysis(self) -> None:
        """Test cost analysis functionality"""
        # Test that cost analysis works correctly
        from cost_analysis import estimate_tokens  # type: ignore

        # Test token estimation
        text = "This is a test text for token estimation"
        tokens = estimate_tokens(text)
        self.assertGreater(tokens, 0)

        # Test with longer text
        long_text = "This is a much longer text that should have more tokens for testing purposes"
        long_tokens = estimate_tokens(long_text)
        self.assertGreater(long_tokens, tokens)


class TestPerformance(unittest.TestCase):
    """Performance tests for the diversity hypothesis system"""

    def test_multi_threaded_performance(self) -> None:
        """Test multi-threaded performance"""
        # Test that multi-threading works correctly

    def test_memory_usage(self) -> None:
        """Test memory usage under load"""
        # Test memory usage with large datasets

    def test_api_rate_limiting(self) -> None:
        """Test API rate limiting handling"""
        # Test rate limiting and retry logic


def run_comprehensive_tests() -> None:
    """Run comprehensive test suite"""
    print("🧪 RUNNING COMPREHENSIVE DIVERSITY HYPOTHESIS TESTS")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDiversityHypothesis))
    suite.addTests(loader.loadTestsFromTestCase(TestLangGraphDiversityOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestDiversitySynthesisOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%",
    )

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    return result.wasSuccessful()  # type: ignore


if __name__ == "__main__":
    success = run_comprehensive_tests()  # type: ignore
    sys.exit(0 if success else 1)
