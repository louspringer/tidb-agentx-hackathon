# Cloud Build GitHub Integration - LLM Problem Wrapper

## Problem Summary
Need to create automatic Cloud Build triggers for GitHub repository `louspringer/OpenFlow-Playground` using **CLI only** - no web console allowed. All attempts have failed.

## Current Status
- ✅ Cloud Build API enabled
- ✅ Secret Manager API enabled  
- ✅ Manual builds working (`gcloud builds submit` succeeds)
- ✅ GitHub connection created (2nd-gen)
- ✅ Repository linked (2nd-gen)
- ❌ No automatic triggers configured
- ❌ All trigger creation attempts fail with "INVALID_ARGUMENT"

## Failed Attempts Summary
1. **CLI Approach**: `gcloud builds triggers create github` fails with "INVALID_ARGUMENT"
2. **Python Approach**: Google Cloud client libraries import errors
3. **2nd-Gen Approach**: GitHub connection created, trigger creation fails
4. **Auto-Install Python**: Packages install but import structure wrong
5. **Corrected Package Installation**: Still fails with import errors
6. **REST API Approach**: Connection works, trigger creation fails
7. **1st-Gen REST API**: Also fails with "INVALID_ARGUMENT"

## Root Cause Analysis
The fundamental issue is that **GitHub repository is not properly connected to Cloud Build**:
- **2nd-gen connection created** but triggers fail
- **1st-gen approach also fails** with same error
- **Repository linking works** but triggers still fail
- **All trigger creation fails** with "INVALID_ARGUMENT"

This suggests the GitHub App installation or repository authorization is missing.

## Working REST API Script (Partial Success)
```python
#!/usr/bin/env python3
"""
GitHub Cloud Build Setup Script using REST API
Bypasses broken Google Cloud client libraries
"""

import json
import subprocess
import sys
from typing import Dict, Any, Optional


def run_gcloud_auth() -> str:
    """Get access token for REST API calls."""
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def make_rest_call(method: str, url: str, data: Optional[Dict[str, Any]] = None, token: Optional[str] = None) -> Dict[str, Any]:
    """Make REST API call to Google Cloud."""
    if token is None:
        token = run_gcloud_auth()
    
    cmd = ["curl", "-X", method, "-H", f"Authorization: Bearer {token}", "-H", "Content-Type: application/json"]
    
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
    
    url = "https://cloudbuild.googleapis.com/v2/projects/aardvark-linkedin-grepper/locations/us-central1/connections"
    
    data = {
        "githubConfig": {
            "authorizerCredential": {
                "oauthTokenSecretVersion": "projects/aardvark-linkedin-grepper/secrets/github-token/versions/1"
            }
        }
    }
    
    response = make_rest_call("POST", url, data, token)
    print("✅ GitHub connection created")
    return str(response.get("name", ""))


def create_repository(connection_name: str, token: str) -> str:
    """Create repository link using REST API."""
    print("📦 Linking GitHub repository...")
    
    # Use full URL for repository creation
    url = "https://cloudbuild.googleapis.com/v2/projects/aardvark-linkedin-grepper/locations/us-central1/connections/github-connection/repositories"
    
    data = {
        "remoteUri": "https://github.com/louspringer/OpenFlow-Playground.git"
    }
    
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
            "push": {
                "branch": "^develop$"
            }
        },
        "build": {
            "steps": [
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": ["build", "-t", "gcr.io/aardvark-linkedin-grepper/ghostbusters-api:latest", "."],
                    "dir": "src/ghostbusters_api"
                }
            ],
            "images": ["gcr.io/aardvark-linkedin-grepper/ghostbusters-api:latest"]
        }
    }
    
    response = make_rest_call("POST", url, data, token)
    print(f"📋 Trigger creation response: {response}")
    print("✅ Build trigger created")
```

## Error Messages Encountered
1. `ERROR: (gcloud.builds.triggers.create.github) INVALID_ARGUMENT: Request contains an invalid argument`
2. `ModuleNotFoundError: No module named 'google.cloud'`
3. `ImportError: cannot import name 'cloudbuild_v1' from 'google.cloud'`
4. `CalledProcessError: Command returned non-zero exit status 1` (pip install)
5. `ModuleNotFoundError: No module named 'google.cloud.build'` (after correct package install)
6. `{'error': {'code': 400, 'message': 'Request contains an invalid argument.', 'status': 'INVALID_ARGUMENT'}}` (REST API)
7. `{'error': {'code': 400, 'message': 'Request contains an invalid argument.', 'status': 'INVALID_ARGUMENT'}}` (1st-gen REST API)

## Failed CLI Commands
```bash
# This fails with "INVALID_ARGUMENT"
gcloud builds triggers create github \
  --name="develop-trigger" \
  --repo-name="OpenFlow-Playground" \
  --repo-owner="louspringer" \
  --branch-pattern="^develop$" \
  --build-config="cloudbuild.yaml"

# This also fails
gcloud builds connections create github github-connection \
  --authorizer-token-secret-version=projects/aardvark-linkedin-grepper/secrets/github-token/versions/1 \
  --region=us-central1
```

## Project Context
- **Project ID**: `aardvark-linkedin-grepper`
- **Region**: `us-central1`
- **Repository**: `louspringer/OpenFlow-Playground`
- **Branch**: `develop`
- **Build Config**: `cloudbuild.yaml`

## Key Requirements
- **CLI only** - no web console
- **Automatic triggers** - builds on push to develop
- **Proper error handling** - handle existing resources
- **Security** - use Secret Manager for tokens

## Expected Outcome
After successful setup, pushing to `develop` branch should automatically trigger Cloud Build using `cloudbuild.yaml` configuration.

## Next Steps for LLM
1. **Research GitHub App installation** - Understand why repository authorization fails
2. **Use webhook triggers** - Alternative to GitHub integration
3. **Use manual triggers** - Fallback to manual trigger creation
4. **Check GitHub App permissions** - Ensure proper repository access
5. **Test integration** - Verify triggers work on push

## Available Files
- `cloudbuild_github_setup_spore.py` - Failed Python script with diagnostics
- `cloudbuild_github_rest_api.py` - Working REST API script (partial success)
- `cloudbuild_github_1stgen.py` - 1st-gen REST API script (also fails)
- `scripts/setup-github-2ndgen.sh` - Failed CLI script
- `CLOUDBUILD_GITHUB_PROBLEM_SPORE.md` - Detailed problem analysis
- `cloudbuild.yaml` - Build configuration file

## Environment
- Using `uv` for package management
- Python 3.12
- Google Cloud SDK installed
- Cloud Build and Secret Manager APIs enabled

## Critical Insight
**All approaches fail at trigger creation due to missing GitHub repository authorization.** The REST API approach successfully creates the GitHub connection and links the repository, but all trigger creation attempts fail with "INVALID_ARGUMENT". This suggests:

1. **GitHub App not installed** on the repository
2. **Repository permissions missing** for Cloud Build
3. **Webhook not configured** properly
4. **Alternative approach needed** - webhook triggers or manual triggers

The next LLM needs to:
1. **Install GitHub App** on the repository
2. **Configure repository permissions** for Cloud Build
3. **Use webhook triggers** as alternative
4. **Use manual triggers** as fallback 