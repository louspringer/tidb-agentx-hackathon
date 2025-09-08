#!/bin/bash

# Setup Cloud Build Trigger for Develop Branch
# This creates a trigger that automatically builds and deploys on pushes to develop

set -e

PROJECT_ID="aardvark-linkedin-grepper"
TRIGGER_NAME="ghostbusters-api-develop-trigger"
REPO_NAME="OpenFlow-Playground"
REPO_OWNER="louspringer"
BRANCH_PATTERN="^develop$"

echo "🚀 Setting up Cloud Build Trigger for develop branch"
echo "📋 Project: $PROJECT_ID"
echo "🔗 Trigger: $TRIGGER_NAME"
echo "🌿 Branch: $BRANCH_PATTERN"
echo "👤 Owner: $REPO_OWNER"

# Create Cloud Build trigger
echo "🔧 Creating Cloud Build trigger..."

gcloud builds triggers create github \
  --name="$TRIGGER_NAME" \
  --repo-name="$REPO_NAME" \
  --repo-owner="$REPO_OWNER" \
  --branch-pattern="$BRANCH_PATTERN" \
  --build-config="cloudbuild.yaml" \
  --project="$PROJECT_ID" \
  --description="Automatic build and deploy Ghostbusters API on push to develop branch"

echo "✅ Cloud Build trigger created successfully!"
echo ""
echo "📊 Trigger Details:"
echo "   Name: $TRIGGER_NAME"
echo "   Repository: $REPO_NAME"
echo "   Owner: $REPO_OWNER"
echo "   Branch: $BRANCH_PATTERN"
echo "   Config: cloudbuild.yaml"
echo ""
echo "🔗 View triggers: https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
echo "🔗 View builds: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"

# Test the trigger
echo ""
echo "🧪 Testing the trigger..."
echo "   Push a commit to trigger the build:"
echo "   git add . && git commit -m 'test: trigger cloud build' && git push" 