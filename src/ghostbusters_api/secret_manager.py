#!/usr/bin/env python3
"""
Google Cloud Secret Manager Integration
Access API keys securely from GCP Secret Manager
"""

import logging
from typing import Optional

from google.cloud import secretmanager

logger = logging.getLogger(__name__)

PROJECT_ID = "aardvark-linkedin-grepper"


def get_secret(secret_name: str) -> Optional[str]:
    """Get a secret from Google Cloud Secret Manager"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"

        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")

        logger.info(f"Successfully retrieved secret: {secret_name}")
        return secret_value

    except Exception as e:
        logger.warning(f"Failed to retrieve secret {secret_name}: {e}")
        return None


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from GCP Secret Manager"""
    return get_secret("openai-api-key")


def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from GCP Secret Manager"""
    return get_secret("anthropic-api-key")


def get_perplexity_api_key() -> Optional[str]:
    """Get Perplexity API key from GCP Secret Manager"""
    return get_secret("perplexity-api-key")


def get_mistral_api_key() -> Optional[str]:
    """Get Mistral API key from GCP Secret Manager"""
    return get_secret("mistral-api-key")


def get_all_api_keys() -> dict[str, Optional[str]]:
    """Get all available API keys from GCP Secret Manager"""
    return {
        "openai": get_openai_api_key(),
        "anthropic": get_anthropic_api_key(),
        "perplexity": get_perplexity_api_key(),
        "mistral": get_mistral_api_key(),
    }


def check_api_keys_availability() -> dict[str, bool]:
    """Check which API keys are available"""
    keys = get_all_api_keys()
    return {provider: key is not None for provider, key in keys.items()}


if __name__ == "__main__":
    # Test the secret manager
    print("🔐 Testing Google Cloud Secret Manager")
    print("=" * 40)

    availability = check_api_keys_availability()

    print("\n📋 API Key Availability:")
    for provider, available in availability.items():
        status = "✅ AVAILABLE" if available else "❌ NOT AVAILABLE"
        print(f"  {provider}: {status}")

    print("\n💡 To add API keys:")
    print(
        "  echo -n 'your-openai-key' | gcloud secrets versions add openai-api-key --data-file=-",
    )
    print(
        "  echo -n 'your-anthropic-key' | gcloud secrets versions add anthropic-api-key --data-file=-",
    )
    print(
        "  echo -n 'your-perplexity-key' | gcloud secrets versions add perplexity-api-key --data-file=-",
    )
    print(
        "  echo -n 'your-mistral-key' | gcloud secrets versions add mistral-api-key --data-file=-",
    )
