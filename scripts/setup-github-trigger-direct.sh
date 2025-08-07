#!/bin/bash

# Direct CLI Setup for GitHub Cloud Build Trigger
# Using 1st-gen repository approach - no GitHub App required

set -e

PROJECT_ID="aardvark-linkedin-grepper"
TRIGGER_NAME="ghostbusters-api-develop-trigger"
REPO_NAME="OpenFlow-Playground"
REPO_OWNER="louspringer"

echo "🚀 Setting up GitHub Cloud Build trigger (1st-gen approach)"
echo "📋 Project: $PROJECT_ID"
echo "🔗 Trigger: $TRIGGER_NAME"
echo "📦 Repository: $REPO_OWNER/$REPO_NAME"

# Create the trigger directly using 1st-gen repository
echo "🔧 Creating Cloud Build trigger..."

gcloud builds triggers create github \
  --name="$TRIGGER_NAME" \
  --repo-name="$REPO_NAME" \
  --repo-owner="$REPO_OWNER" \
  --branch-pattern="^develop$" \
  --build-config="cloudbuild.yaml" \
  --project="$PROJECT_ID" \
  --description="Automatic build and deploy Ghostbusters API on push to develop branch"

echo ""
echo "✅ Cloud Build trigger created successfully!"
echo ""
echo "📊 Trigger Details:"
echo "   Name: $TRIGGER_NAME"
echo "   Repository: $REPO_NAME"
echo "   Owner: $REPO_OWNER"
echo "   Branch: develop"
echo "   Config: cloudbuild.yaml"
echo ""
echo "🔗 View triggers: https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
echo "🔗 View builds: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"

# Test the trigger
echo ""
echo "🧪 Test the trigger:"
echo "   git add . && git commit -m 'test: trigger cloud build' && git push" 