#!/bin/bash

# Setup GitHub Connection and Cloud Build Trigger using 2nd-gen approach
# Based on: https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github

set -e

PROJECT_ID="aardvark-linkedin-grepper"
REGION="us-central1"
CONNECTION_NAME="github-connection"
REPO_NAME="OpenFlow-Playground"
REPO_OWNER="louspringer"
SECRET_NAME="github-token"
TRIGGER_NAME="ghostbusters-api-develop-trigger"

echo "🚀 Setting up GitHub connection using 2nd-gen approach"
echo "📋 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🔗 Connection: $CONNECTION_NAME"
echo "📦 Repository: $REPO_OWNER/$REPO_NAME"

# Check if token is provided
if [ $# -eq 0 ]; then
    echo ""
    echo "❌ No GitHub token provided!"
    echo "   Create a token at: https://github.com/settings/tokens"
    echo "   Permissions needed: repo, read:user, read:org"
    echo "   Then run: ./scripts/setup-github-2ndgen.sh YOUR_TOKEN"
    exit 1
fi

GITHUB_TOKEN=$1

# Step 1: Store token in Secret Manager
echo ""
echo "🔐 Step 1: Storing GitHub token in Secret Manager..."
echo -n "$GITHUB_TOKEN" | gcloud secrets create "$SECRET_NAME" --data-file=- --project="$PROJECT_ID" || echo "Secret already exists"

# Step 2: Grant access to Cloud Build Service Agent
echo ""
echo "🔓 Step 2: Granting access to Cloud Build Service Agent..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
CLOUD_BUILD_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-cloudbuild.iam.gserviceaccount.com"

gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
  --member="serviceAccount:${CLOUD_BUILD_SERVICE_AGENT}" \
  --role="roles/secretmanager.secretAccessor" \
  --project="$PROJECT_ID"

# Step 3: Create GitHub connection
echo ""
echo "🔗 Step 3: Creating GitHub connection..."
gcloud builds connections create github "$CONNECTION_NAME" \
  --authorizer-token-secret-version="projects/$PROJECT_ID/secrets/$SECRET_NAME/versions/1" \
  --region="$REGION" \
  --project="$PROJECT_ID"

# Step 4: Create repository link
echo ""
echo "📦 Step 4: Creating repository link..."
REPO_URI="https://github.com/$REPO_OWNER/$REPO_NAME.git"

gcloud builds repositories create "$REPO_NAME" \
  --remote-uri="$REPO_URI" \
  --connection="$CONNECTION_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID"

# Step 5: Create trigger using 2nd-gen repository
echo ""
echo "🎯 Step 5: Creating Cloud Build trigger..."
REPOSITORY_RESOURCE="projects/$PROJECT_ID/locations/$REGION/connections/$CONNECTION_NAME/repositories/$REPO_NAME"

gcloud builds triggers create github \
  --name="$TRIGGER_NAME" \
  --repository="$REPOSITORY_RESOURCE" \
  --branch-pattern="^develop$" \
  --build-config="cloudbuild.yaml" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --description="Automatic build and deploy Ghostbusters API on push to develop branch"

echo ""
echo "✅ GitHub connection and trigger setup complete!"
echo ""
echo "📊 Setup Summary:"
echo "   Connection: $CONNECTION_NAME"
echo "   Repository: $REPO_NAME"
echo "   Trigger: $TRIGGER_NAME"
echo "   Branch: develop"
echo "   Region: $REGION"
echo ""
echo "🔗 View triggers: https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
echo "🔗 View builds: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo ""
echo "🧪 Test the trigger:"
echo "   git add . && git commit -m 'test: trigger cloud build' && git push" 