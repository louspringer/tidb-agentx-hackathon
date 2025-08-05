#!/usr/bin/env python3
"""Live smoke test using LangChain"""

import json
import os
from typing import Any, Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate


class LiveLLMOrchestrator:
    """Live LLM orchestrator using LangChain"""

    def __init__(self, api_key: Optional[str] = None, provider: str = "openai") -> None:
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")

        if not self.api_key:
            msg = f"Unsupported provider: {provider}"
            raise ValueError(msg)

        # Initialize LangChain models (only if API key is available)
        self.llm = None
        if self.api_key:
            try:
                # Initialize LLM based on provider
                if provider == "openai":
                    from langchain_openai import ChatOpenAI

                    self.llm = ChatOpenAI(api_key=self.api_key, model="gpt-4-turbo")
                elif provider == "anthropic":
                    from langchain_anthropic import ChatAnthropic

                    self.llm = ChatAnthropic(
                        api_key=self.api_key,
                        model="claude-3-5-sonnet-20241022",
                    )
            except ImportError as e:
                msg = f"Failed to import {provider} dependencies: {str(e)}. Install required packages."
                raise ValueError(msg)
            except ValueError as e:
                msg = (
                    f"Invalid {provider} configuration: {str(e)}. Check API key format."
                )
                raise ValueError(msg)
            except Exception as e:
                msg = f"Failed to initialize {provider} model: {str(e)}. Check API key validity and model availability."
                raise ValueError(msg)

        # Set up JSON output parser
        self.output_parser = JsonOutputParser()

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_template(
            """
You are a partner LLM helping to detect blind spots and unknown unknowns.

Context: {context}
Jeopardy Question: {jeopardy_question}

Generate 5 probing questions that would reveal blind spots, assumptions, or unknown unknowns.
Focus on questions that challenge the approach and reveal what might be missing.

{format_instructions}
""",
        )

        # Create the chain (only if LLM is available)
        self.chain = None
        if self.llm:
            self.chain = self.prompt | self.llm | self.output_parser

    def call_live_llm(self, context: str, jeopardy_question: str) -> dict[str, Any]:
        """Call live LLM API using LangChain"""

        if not self.api_key or not self.chain:
            return {
                "error": f"No {self.provider.upper()}_API_KEY available",
                "questions": [],
            }

        try:
            # Execute the chain
            return self.chain.invoke(
                {
                    "context": context,
                    "jeopardy_question": jeopardy_question,
                    "format_instructions": self.output_parser.get_format_instructions(),
                },
            )

        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "questions": []}


def test_live_scenario_1() -> None:
    """Test with real LLM - Healthcare CDC implementation"""
    print("=== LIVE TEST 1: Healthcare CDC Implementation ===")

    context = """
    I'm implementing a Healthcare CDC pipeline with DynamoDB and Snowflake.
    I think using CloudFormation for infrastructure is the right approach.
    Obviously the data model should match the Snowflake quickstart.
    I assume the CDC events will work the same way as other databases.
    """

    # Test with OpenAI if available
    try:
        openai_llm = LiveLLMOrchestrator(provider="openai")
        live_result = openai_llm.call_live_llm(context, "What assumptions am I making?")
        print("🤖 Live OpenAI Analysis:")
        print(json.dumps(live_result, indent=2))
    except Exception as e:
        print(f"⚠️ Live LLM failed: {e}")


def main() -> None:
    """Main function"""
    test_live_scenario_1()


if __name__ == "__main__":
    main()
