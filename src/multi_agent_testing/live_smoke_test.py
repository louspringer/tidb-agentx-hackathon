#!/usr/bin/env python3


import os
import json
import requests

        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.base_url = self._get_base_url()
        self.model = self._get_model()

    def _get_base_url(self) -> str:
        if self.provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        elif self.provider == "anthropic":
            return "https://api.anthropic.com/v1/messages"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _get_model(self) -> str:
        if self.provider == "openai":
            return "gpt-4-turbo"
        elif self.provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        else:
            return "gpt-4-turbo"

        prompt = f"""
You are a partner LLM helping to detect blind spots and unknown unknowns.

Context: {context}

Jeopardy Question: {jeopardy_question}


        try:
            if self.provider == "openai":
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",

                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,

                )
            elif self.provider == "anthropic":
                response = requests.post(
                    self.base_url,
                    headers={
                        "x-api-key": self.api_key,
                        "Content-Type": "application/json",

                    },
                    json={
                        "model": self.model,
                        "max_tokens": 500,

            if response.status_code == 200:
                result = response.json()
                if self.provider == "openai":
                    content = result["choices"][0]["message"]["content"]
                elif self.provider == "anthropic":
                    content = result["content"][0]["text"]

                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response", "raw": content}
            else:
                return {"error": f"API error: {response.status_code}", "questions": []}

