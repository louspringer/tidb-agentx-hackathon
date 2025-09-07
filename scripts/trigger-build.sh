#!/bin/bash

# Manual Cloud Build Trigger Script
# This script triggers the Cloud Build pipeline manually

set -e

PROJECT_ID="aardvark-linkedin-grepper"

echo "🚀 Triggering Cloud Build pipeline manually"
echo "📋 Project: $PROJECT_ID"
echo "🔗 Config: cloudbuild.yaml"

# Trigger the build
echo "🔧 Starting Cloud Build..."
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=$PROJECT_ID \
  .

echo "✅ Build triggered successfully!"
echo ""
echo "🔗 View build: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo "🔗 View logs: gcloud builds log [BUILD_ID] --project=$PROJECT_ID" 