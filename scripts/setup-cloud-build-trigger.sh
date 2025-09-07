#!/bin/bash

# Setup Cloud Build Trigger for Automatic CI/CD
# This creates a trigger that automatically builds and deploys on git pushes

set -e

PROJECT_ID="aardvark-linkedin-grepper"
TRIGGER_NAME="ghostbusters-api-trigger"
REPO_NAME="OpenFlow-Playground"
BRANCH_PATTERN="^ghostbusters-gcp-implementation$"

echo "🚀 Setting up Cloud Build Trigger for automatic CI/CD"
echo "📋 Project: $PROJECT_ID"
echo "🔗 Trigger: $TRIGGER_NAME"
echo "🌿 Branch: $BRANCH_PATTERN"

# Create Cloud Build trigger
echo "🔧 Creating Cloud Build trigger..."

gcloud builds triggers create github \
  --name="$TRIGGER_NAME" \
  --repo-name="$REPO_NAME" \
  --repo-owner="lou" \
  --branch-pattern="$BRANCH_PATTERN" \
  --build-config="cloudbuild.yaml" \
  --project="$PROJECT_ID" \
  --description="Automatic build and deploy Ghostbusters API on push to ghostbusters-gcp-implementation branch"

echo "✅ Cloud Build trigger created successfully!"
echo ""
echo "📊 Trigger Details:"
echo "   Name: $TRIGGER_NAME"
echo "   Repository: $REPO_NAME"
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