# GitHub Cloud Build Trigger Setup - CLI Only Solution

## Problem Statement
Need to create automatic Cloud Build triggers for GitHub repository using **CLI only** - no web console allowed. The repository is `louspringer/OpenFlow-Playground` and we need triggers for the `develop` branch.

## Current Status
- ✅ Cloud Build API enabled
- ✅ Secret Manager API enabled  
- ✅ Manual builds working (`gcloud builds submit` succeeds)
- ❌ No automatic triggers configured
- ❌ GitHub connection not established

## Failed Attempts
1. **1st-gen approach**: `gcloud builds triggers create github` fails with "INVALID_ARGUMENT"
2. **2nd-gen approach**: Requires GitHub connection first
3. **Webhook approach**: Requires secret configuration
4. **Manual triggers**: Not automatic

## Required Solution
Use **2nd-gen GitHub connection** approach with proper CLI commands:

### Step 1: Create GitHub Personal Access Token
- Go to: https://github.com/settings/tokens
- Generate new token (classic)
- Permissions: `repo`, `read:user`, `read:org`
- Copy token (starts with `ghp_`)

### Step 2: Store Token in Secret Manager
```bash
echo -n "YOUR_GITHUB_TOKEN" | gcloud secrets create github-token --data-file=- --project=aardvark-linkedin-grepper
```

### Step 3: Grant Cloud Build Access
```bash
PROJECT_NUMBER=$(gcloud projects describe aardvark-linkedin-grepper --format="value(projectNumber)")
CLOUD_BUILD_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
gcloud secrets add-iam-policy-binding github-token \
  --member="serviceAccount:${CLOUD_BUILD_SERVICE_AGENT}" \
  --role="roles/secretmanager.secretAccessor" \
  --project=aardvark-linkedin-grepper
```

### Step 4: Create GitHub Connection
```bash
gcloud builds connections create github github-connection \
  --authorizer-token-secret-version=projects/aardvark-linkedin-grepper/secrets/github-token/versions/1 \
  --region=us-central1 \
  --project=aardvark-linkedin-grepper
```

### Step 5: Create Repository Link
```bash
gcloud builds repositories create OpenFlow-Playground \
  --remote-uri=https://github.com/louspringer/OpenFlow-Playground.git \
  --connection=github-connection \
  --region=us-central1 \
  --project=aardvark-linkedin-grepper
```

### Step 6: Create Trigger
```bash
REPOSITORY_RESOURCE="projects/aardvark-linkedin-grepper/locations/us-central1/connections/github-connection/repositories/OpenFlow-Playground"
gcloud builds triggers create github \
  --name=ghostbusters-api-develop-trigger \
  --repository="$REPOSITORY_RESOURCE" \
  --branch-pattern="^develop$" \
  --build-config=cloudbuild.yaml \
  --region=us-central1 \
  --project=aardvark-linkedin-grepper \
  --description="Automatic build and deploy Ghostbusters API on push to develop branch"
```

## Key Requirements
- **CLI only** - no web console
- **2nd-gen approach** - modern GitHub integration
- **Automatic triggers** - builds on push to develop
- **Proper error handling** - handle existing resources
- **Security** - use Secret Manager for tokens

## Expected Outcome
After setup, pushing to `develop` branch should automatically trigger Cloud Build using `cloudbuild.yaml` configuration.

## Files Created
- `scripts/setup-github-2ndgen.sh` - Complete setup script
- `scripts/setup-github-connection.sh` - Alternative approach
- `develop-trigger.yaml` - Trigger configuration file

## Current Project Context
- Project ID: `aardvark-linkedin-grepper`
- Region: `us-central1`
- Repository: `louspringer/OpenFlow-Playground`
- Branch: `develop`
- Build Config: `cloudbuild.yaml`

## Next Steps for LLM
1. Get GitHub token from user
2. Run the 2nd-gen setup script
3. Verify trigger creation
4. Test with a push to develop branch 