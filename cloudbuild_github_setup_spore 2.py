#!/usr/bin/env python3
"""
GitHub Cloud Build Setup Script
Sets up automatic triggers for GitHub repository using Google Cloud APIs
"""

import importlib
import subprocess
import sys
from typing import Optional


def ensure_package(pkg_name: str, import_name: Optional[str] = None) -> None:
    """Ensure a package is installed, install if missing."""
    try:
        importlib.import_module(import_name or pkg_name)
    except ImportError:
        try:
            subprocess.check_call(["uv", "add", pkg_name])
        except Exception:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])


# Diagnostic: Check installed packages
print("📦 Checking installed packages...")
subprocess.call([sys.executable, "-m", "pip", "freeze"])

# Ensure correct Google packages are installed
ensure_package("google-cloud-secret-manager", "google.cloud.secretmanager")
ensure_package("google-cloud-build", "google.cloud.devtools")

# Diagnostic: Check google.cloud structure
try:
    import google.cloud

    print("🔍 Scanning google.cloud modules:")
    import pkgutil

    for importer, modname, ispkg in pkgutil.walk_packages(
        path=google.cloud.__path__,
        prefix="google.cloud.",
    ):
        print(f"  - {modname}")
except Exception as e:
    print(f"❌ Failed to scan google.cloud: {e}")

# Try imports
try:
    from google.cloud import cloudbuild_v1, secretmanager_v1
    from google.cloud.devtools import cloudbuild_v2

    print("✅ Google Cloud imports successful")
except ImportError as e:
    print(f"❌ Google Cloud imports failed: {e}")
    print("🔄 Switching to REST API approach...")
    sys.exit(1)

PROJECT_ID = "aardvark-linkedin-grepper"
REGION = "us-central1"
REPO_NAME = "OpenFlow-Playground"
REPO_URI = f"https://github.com/louspringer/{REPO_NAME}.git"
CONNECTION_ID = "github-connection"
SECRET_ID = "github-token"
SECRET_VERSION = "1"
TRIGGER_NAME = "ghostbusters-api-develop-trigger"
BRANCH_PATTERN = "^develop$"
BUILD_CONFIG_FILE = "cloudbuild.yaml"

PARENT = f"projects/{PROJECT_ID}/locations/{REGION}"
SECRET_VERSION_PATH = (
    f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/{SECRET_VERSION}"
)
CONNECTION_RESOURCE = f"{PARENT}/connections/{CONNECTION_ID}"
REPO_RESOURCE = f"{CONNECTION_RESOURCE}/repositories/{REPO_NAME}"

# Init clients
sm_client = secretmanager_v1.SecretManagerServiceClient()
cb2_client = cloudbuild_v2.RepositoryManagerClient()
cb1_client = cloudbuild_v1.CloudBuildClient()

# Step 1: Create GitHub connection
conn = cloudbuild_v2.Connection(
    github_config=cloudbuild_v2.GitHubConfig(
        authorizer_credential=cloudbuild_v2.OAuthCredential(
            oauth_token_secret_version=SECRET_VERSION_PATH,
        ),
    ),
)
conn_op = cb2_client.create_connection(
    parent=PARENT,
    connection_id=CONNECTION_ID,
    connection=conn,
)
print("⏳ Creating GitHub connection...")
conn_op.result()

# Step 2: Link repository
repo = cloudbuild_v2.Repository(remote_uri=REPO_URI)
repo_op = cb2_client.create_repository(
    parent=CONNECTION_RESOURCE,
    repository_id=REPO_NAME,
    repository=repo,
)
print("🔗 Linking GitHub repository...")
repo_op.result()

# Step 3: Create build trigger
trigger = cloudbuild_v1.BuildTrigger(
    name=TRIGGER_NAME,
    description="Automatic build and deploy Ghostbusters API on push to develop branch",
    github={
        "name": REPO_NAME,
        "owner": "louspringer",
        "push": {"branch": BRANCH_PATTERN},
    },
    build=cloudbuild_v1.Build(filename=BUILD_CONFIG_FILE),
)
cb1_client.create_build_trigger(project_id=PROJECT_ID, trigger=trigger)
print("🚀 Trigger created.")
