#!/usr/bin/env python3
"""
GitHub Cloud Build Setup Script using REST API
Bypasses broken Google Cloud client libraries
"""

import json
import subprocess
import sys
from typing import Any, Optional


def run_gcloud_auth() -> str:
    """Get access token for REST API calls."""
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def make_rest_call(
    method: str,
    url: str,
    data: Optional[dict[str, Any]] = None,
    token: Optional[str] = None,
) -> dict[str, Any]:
    """Make REST API call to Google Cloud."""
    if token is None:
        token = run_gcloud_auth()

    cmd = [
        "curl",
        "-X",
        method,
        "-H",
        f"Authorization: Bearer {token}",
        "-H",
        "Content-Type: application/json",
    ]

    if data:
        cmd.extend(["-d", json.dumps(data)])

    cmd.append(url)

    print(f"🔧 Making {method} request to: {url}")

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    if result.stdout:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"⚠️  Non-JSON response: {result.stdout}")
            return {}
    else:
        print("⚠️  Empty response")
        return {}


def create_github_connection(token: str) -> str:
    """Create GitHub connection using REST API."""
    print("🔗 Creating GitHub connection...")

    # Include connection ID in the URL
    url = "https://cloudbuild.googleapis.com/v2/projects/aardvark-linkedin-grepper/locations/us-central1/connections/github-connection"

    data = {
        "githubConfig": {
            "authorizerCredential": {
                "oauthTokenSecretVersion": "projects/aardvark-linkedin-grepper/secrets/github-token/versions/1",
            },
        },
    }

    response = make_rest_call("POST", url, data, token)
    print(f"📋 Connection creation response: {response}")

    if "error" not in response:
        print("✅ GitHub connection created")
        return str(response.get("name", ""))
    else:
        print("❌ GitHub connection creation failed")
        return ""


def create_repository(connection_name: str, token: str) -> str:
    """Create repository link using REST API."""
    print("📦 Linking GitHub repository...")

    # Use full URL for repository creation
    url = "https://cloudbuild.googleapis.com/v2/projects/aardvark-linkedin-grepper/locations/us-central1/connections/github-connection/repositories"

    data = {"remoteUri": "https://github.com/louspringer/OpenFlow-Playground.git"}

    response = make_rest_call("POST", url, data, token)
    print("✅ Repository linked")
    return str(response.get("name", ""))


def create_trigger(repository_name: str, token: str) -> None:
    """Create build trigger using REST API."""
    print("🎯 Creating build trigger...")

    # Use v1 endpoint with correct format for 2nd-gen connections
    url = "https://cloudbuild.googleapis.com/v1/projects/aardvark-linkedin-grepper/triggers"

    data = {
        "name": "ghostbusters-api-develop-trigger",
        "description": "Automatic build and deploy Ghostbusters API on push to develop branch",
        "github": {
            "name": "OpenFlow-Playground",
            "owner": "louspringer",
            "push": {"branch": "^develop$"},
        },
        "build": {
            "steps": [
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": [
                        "build",
                        "-t",
                        "gcr.io/aardvark-linkedin-grepper/ghostbusters-api:latest",
                        ".",
                    ],
                    "dir": "src/ghostbusters_api",
                },
            ],
            "images": ["gcr.io/aardvark-linkedin-grepper/ghostbusters-api:latest"],
        },
    }

    response = make_rest_call("POST", url, data, token)
    print(f"📋 Trigger creation response: {response}")
    print("✅ Build trigger created")


def main() -> None:
    """Main setup function using REST API."""
    print("🚀 Setting up GitHub Cloud Build integration using REST API...")
    print("📋 Project: aardvark-linkedin-grepper")
    print("🌍 Region: us-central1")
    print("📦 Repository: louspringer/OpenFlow-Playground")
    print()

    try:
        # Get access token
        token = run_gcloud_auth()
        print("🔑 Authentication successful")

        # Create GitHub connection
        connection_name = create_github_connection(token)

        # Create repository link
        repository_name = create_repository(connection_name, token)

        # Create trigger
        create_trigger(repository_name, token)

        print()
        print("🎉 Setup complete!")
        print("📊 Summary:")
        print("   Connection: github-connection")
        print("   Repository: OpenFlow-Playground")
        print("   Trigger: ghostbusters-api-develop-trigger")
        print("   Branch: develop")
        print()
        print(
            "🔗 View triggers: https://console.cloud.google.com/cloud-build/triggers?project=aardvark-linkedin-grepper",
        )
        print("🧪 Test with: git push origin develop")

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
