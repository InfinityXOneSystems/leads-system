#!/bin/bash
# Lead Sniper - Google Cloud Setup Script
# Autonomous Infrastructure Deployment

set -e

echo "🎯 Lead Sniper - Google Cloud Setup"
echo "===================================="

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-infinity-x-one-systems}"
REGION="us-central1"
GITHUB_REPO="InfinityXOneSystems/lead-sniper"
SERVICE_ACCOUNT_NAME="lead-sniper-sa"
WIF_POOL_NAME="github-actions-pool"
WIF_PROVIDER_NAME="github-actions-provider"

echo "📋 Project ID: $PROJECT_ID"
echo "📍 Region: $REGION"
echo "🔗 GitHub Repo: $GITHUB_REPO"
echo ""

# Step 1: Enable Required APIs
echo "1️⃣  Enabling Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  --project=$PROJECT_ID

echo "✅ APIs enabled"
echo ""

# Step 2: Create Service Account
echo "2️⃣  Creating Service Account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name="Lead Sniper Autonomous Service Account" \
  --project=$PROJECT_ID || echo "Service account already exists"

SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "✅ Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Step 3: Grant IAM Roles
echo "3️⃣  Granting IAM Roles..."
ROLES=(
  "roles/run.admin"
  "roles/aiplatform.user"
  "roles/bigquery.admin"
  "roles/datastore.user"
  "roles/storage.admin"
  "roles/cloudbuild.builds.editor"
  "roles/cloudscheduler.admin"
  "roles/secretmanager.secretAccessor"
  "roles/iam.serviceAccountUser"
)

for ROLE in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="$ROLE" \
    --condition=None
done

echo "✅ IAM roles granted"
echo ""

# Step 4: Setup Workload Identity Federation
echo "4️⃣  Setting up Workload Identity Federation..."

# Create Workload Identity Pool
gcloud iam workload-identity-pools create $WIF_POOL_NAME \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --project=$PROJECT_ID || echo "Pool already exists"

# Create Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc $WIF_PROVIDER_NAME \
  --location="global" \
  --workload-identity-pool=$WIF_POOL_NAME \
  --display-name="GitHub Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project=$PROJECT_ID || echo "Provider already exists"

# Allow GitHub Actions to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/$WIF_POOL_NAME/attribute.repository/$GITHUB_REPO" \
  --project=$PROJECT_ID

WIF_PROVIDER_FULL="projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/$WIF_POOL_NAME/providers/$WIF_PROVIDER_NAME"

echo "✅ Workload Identity Federation configured"
echo "📋 WIF Provider: $WIF_PROVIDER_FULL"
echo ""

# Step 5: Create BigQuery Dataset
echo "5️⃣  Creating BigQuery Dataset..."
bq mk --dataset \
  --location=$REGION \
  --description="Lead Sniper autonomous data warehouse" \
  ${PROJECT_ID}:lead_sniper_data || echo "Dataset already exists"

# Create tables
bq mk --table \
  ${PROJECT_ID}:lead_sniper_data.raw_leads \
  address:STRING,property_type:STRING,owner_name:STRING,distress_indicators:STRING,tax_status:STRING,created_at:TIMESTAMP,processed:BOOLEAN || echo "Table exists"

bq mk --table \
  ${PROJECT_ID}:lead_sniper_data.processed_leads \
  address:STRING,property_type:STRING,owner_name:STRING,distress_score:INTEGER,deal_probability:INTEGER,urgency:STRING,ai_analysis:JSON,created_at:TIMESTAMP || echo "Table exists"

echo "✅ BigQuery dataset and tables created"
echo ""

# Step 6: Create Cloud Storage Buckets
echo "6️⃣  Creating Cloud Storage Buckets..."
gsutil mb -l $REGION gs://${PROJECT_ID}-lead-sniper-raw || echo "Bucket exists"
gsutil mb -l $REGION gs://${PROJECT_ID}-lead-sniper-processed || echo "Bucket exists"
gsutil mb -l $REGION gs://${PROJECT_ID}-lead-sniper-pipelines || echo "Bucket exists"

echo "✅ Storage buckets created"
echo ""

# Step 7: Create Secrets in Secret Manager
echo "7️⃣  Creating Secrets..."
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic" \
  --project=$PROJECT_ID || echo "Secret already exists"

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID

echo "✅ Secrets created and configured"
echo ""

# Step 8: Deploy Initial Cloud Run Service
echo "8️⃣  Deploying Cloud Run Service..."
gcloud run deploy lead-sniper-backend \
  --source=. \
  --region=$REGION \
  --allow-unauthenticated \
  --service-account=$SERVICE_ACCOUNT_EMAIL \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,GEMINI_MODEL=gemini-2.0-flash-exp" \
  --project=$PROJECT_ID || echo "Deployment will happen via GitHub Actions"

echo "✅ Cloud Run service configured"
echo ""

# Step 9: Setup Cloud Scheduler
echo "9️⃣  Setting up Cloud Scheduler..."
BACKEND_URL=$(gcloud run services describe lead-sniper-backend --region=$REGION --format='value(status.url)' --project=$PROJECT_ID 2>/dev/null || echo "")

if [ -n "$BACKEND_URL" ]; then
  gcloud scheduler jobs create http lead-sniper-daily \
    --location=$REGION \
    --schedule="0 5 * * *" \
    --uri="${BACKEND_URL}/trigger-pipeline" \
    --http-method=POST \
    --oidc-service-account-email=$SERVICE_ACCOUNT_EMAIL \
    --time-zone="America/New_York" \
    --project=$PROJECT_ID || echo "Scheduler job already exists"
  
  echo "✅ Cloud Scheduler configured"
else
  echo "⚠️  Cloud Run service not yet deployed. Scheduler will be configured after first deployment."
fi
echo ""

# Step 10: Output GitHub Secrets
echo "🔐 GitHub Secrets Configuration"
echo "================================"
echo ""
echo "Add these secrets to your GitHub repository:"
echo "Repository: https://github.com/$GITHUB_REPO/settings/secrets/actions"
echo ""
echo "WIF_PROVIDER=$WIF_PROVIDER_FULL"
echo "WIF_SERVICE_ACCOUNT=$SERVICE_ACCOUNT_EMAIL"
echo "GCP_PROJECT_ID=$PROJECT_ID"
echo "GEMINI_API_KEY=<your-gemini-api-key>"
echo ""

echo "✅ Google Cloud Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Add the secrets above to your GitHub repository"
echo "2. Push code to trigger the GitHub Actions workflow"
echo "3. Monitor deployment at: https://github.com/$GITHUB_REPO/actions"
echo "4. Access dashboard at: https://lead-sniper-dashboard-${PROJECT_ID}.run.app"
echo ""
echo "🎯 Lead Sniper is now autonomous!"
