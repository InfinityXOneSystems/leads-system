# Lead Sniper - Google Cloud Autonomous Deployment Guide

## 🎯 Overview

This guide will help you deploy Lead Sniper as a fully autonomous system on Google Cloud Platform, eliminating the need for expensive third-party platforms like Manus.

**What You'll Get:**
- ✅ Autonomous lead generation pipeline
- ✅ GitHub Actions integration with Gemini CLI
- ✅ Vertex AI Agent Builder for self-operating agents
- ✅ Cloud Run serverless backend
- ✅ BigQuery data warehouse
- ✅ Firestore real-time database
- ✅ Automated daily execution
- ✅ Zero manual intervention required

**Cost Estimate:**
- Cloud Run: ~$10-30/month (with generous free tier)
- Vertex AI: Pay-per-use (~$0.50-2/day for lead scoring)
- BigQuery: ~$5-15/month (first 1TB queries free)
- Storage: ~$1-5/month
- **Total: $20-50/month** (vs $500+/month for Manus)

---

## 📋 Prerequisites

1. **Google Cloud Account**
   - Create account at: https://console.cloud.google.com
   - Enable billing (free tier available)
   - Note your Project ID

2. **GitHub Repository**
   - Fork or clone: https://github.com/InfinityXOneSystems/lead-sniper
   - Ensure you have admin access

3. **API Keys**
   - Gemini API Key: https://makersuite.google.com/app/apikey
   - (Optional) Other data source APIs

---

## 🚀 Step-by-Step Deployment

### Step 1: Setup Google Cloud Infrastructure

Run the automated setup script:

```bash
cd /home/ubuntu/lead-sniper

# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"

# Run setup script
./scripts/setup_google_cloud.sh
```

**What this does:**
- ✅ Enables all required Google Cloud APIs
- ✅ Creates service account with proper permissions
- ✅ Configures Workload Identity Federation (secure, keyless auth)
- ✅ Creates BigQuery dataset and tables
- ✅ Creates Cloud Storage buckets
- ✅ Stores secrets in Secret Manager
- ✅ Deploys initial Cloud Run service
- ✅ Configures Cloud Scheduler for daily runs

---

### Step 2: Configure GitHub Secrets

After running the setup script, it will output GitHub secrets. Add them to your repository:

1. Go to: `https://github.com/InfinityXOneSystems/lead-sniper/settings/secrets/actions`

2. Click "New repository secret" and add each of these:

```
WIF_PROVIDER=projects/123456789/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider
WIF_SERVICE_ACCOUNT=lead-sniper-sa@your-project-id.iam.gserviceaccount.com
GCP_PROJECT_ID=your-project-id
GEMINI_API_KEY=your-gemini-api-key
```

---

### Step 3: Push Code to Trigger Deployment

```bash
cd /home/ubuntu/lead-sniper

# Add all files
git add .

# Commit changes
git commit -m "🎯 Deploy autonomous Lead Sniper to Google Cloud"

# Push to main branch (triggers GitHub Actions)
git push origin main
```

**What happens next:**
1. GitHub Actions workflow starts automatically
2. Authenticates to Google Cloud (no keys needed!)
3. Deploys backend to Cloud Run
4. Uploads Vertex AI pipeline
5. Executes initial lead generation run
6. Triggers Vertex AI lead scoring
7. Commits results back to repository
8. Deploys frontend dashboard

---

### Step 4: Monitor Deployment

Watch the deployment progress:

1. **GitHub Actions**: https://github.com/InfinityXOneSystems/lead-sniper/actions
2. **Cloud Run Console**: https://console.cloud.google.com/run
3. **Vertex AI Pipelines**: https://console.cloud.google.com/vertex-ai/pipelines

---

### Step 5: Access Your Dashboard

Once deployed, access your Lead Sniper dashboard:

```
https://lead-sniper-dashboard-[YOUR-PROJECT-ID].run.app
```

---

## 🤖 Autonomous Operation

### Daily Execution

Lead Sniper runs automatically every day at 5 AM EST via:
1. **Cloud Scheduler** triggers the backend
2. **Backend** executes the scraping pipeline
3. **Vertex AI** scores and enriches leads
4. **GitHub Actions** commits results
5. **Notifications** sent for high-priority leads

### Manual Trigger

Trigger a run manually:

```bash
# Via GitHub Actions
gh workflow run autonomous-deployment.yml

# Via Cloud Run
curl -X POST https://lead-sniper-backend-[PROJECT-ID].run.app/trigger-pipeline
```

---

## 🧠 Vertex AI Agent Configuration

### Creating Lead Sniper Agents

1. Go to: https://console.cloud.google.com/vertex-ai/agents

2. Click "Create Agent"

3. Configure agent:
   - **Name**: Lead Sniper Scout
   - **Model**: gemini-2.0-flash-exp
   - **Instructions**: 
     ```
     You are a lead discovery agent. Your role is to:
     1. Scan data sources for distressed property signals
     2. Identify early indicators of intent
     3. Score leads by urgency and probability
     4. Recommend actions for sales team
     
     Use the Lead Sniper data store for context.
     ```

4. Connect to BigQuery data store:
   - Dataset: `lead_sniper_data`
   - Table: `processed_leads`

5. Deploy agent

### Agent Roles

Create multiple specialized agents:

1. **Signal Scout Agent** - Discovers new data sources
2. **Intent Detection Agent** - Identifies buying signals
3. **Lead Scoring Agent** - Ranks opportunities
4. **Enrichment Agent** - Adds context and data
5. **Deduplication Agent** - Cleans and validates
6. **Delivery Agent** - Packages final output

---

## 📊 Data Flow

```
┌─────────────────┐
│  Web Sources    │ (County clerks, auctions, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Headless       │ (100+ parallel scrapers)
│  Orchestrator   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Raw Data       │ (Cloud Storage)
│  Storage        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gemini 2.0     │ (AI analysis & scoring)
│  Analysis       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vision Cortex  │ (Multi-perspective scoring)
│  Scoring        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  BigQuery       │ (Data warehouse)
│  Storage        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dashboard      │ (Real-time visualization)
│  Frontend       │
└─────────────────┘
```

---

## 🔧 Configuration

### Customizing Target Region

Edit `config/treasure_coast_config.json`:

```json
{
  "region": "Your Region",
  "state": "FL",
  "counties": [
    {
      "name": "Your County",
      "fips": "12345",
      "data_sources": {
        "clerk": "https://...",
        "property_appraiser": "https://..."
      }
    }
  ]
}
```

### Adjusting Scoring Parameters

Edit `src/vision_cortex/scoring_config.py`:

```python
SCORING_WEIGHTS = {
    "distress_level": 0.30,
    "deal_probability": 0.25,
    "timing_urgency": 0.20,
    "market_opportunity": 0.15,
    "risk_factors": 0.10
}
```

---

## 📈 Monitoring & Optimization

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read lead-sniper-backend --region=us-central1

# Vertex AI pipeline logs
gcloud ai pipelines list --region=us-central1
```

### Cost Monitoring

View costs in real-time:
https://console.cloud.google.com/billing/reports

### Performance Tuning

1. **Increase parallelism**: Edit `src/core/manus_core.py`
   ```python
   max_parallel_instances = 200  # Increase from 100
   ```

2. **Optimize Gemini calls**: Use batch processing
   ```python
   batch_size = 50  # Process 50 leads per API call
   ```

3. **Cache results**: Enable Cloud CDN for frontend

---

## 🆘 Troubleshooting

### Deployment Fails

**Issue**: GitHub Actions workflow fails
**Solution**: Check secrets are correctly configured

```bash
# Verify secrets
gh secret list
```

### No Leads Generated

**Issue**: Pipeline runs but no leads appear
**Solution**: Check data source URLs and selectors

```bash
# Test scraper manually
python src/crawlers/test_scraper.py
```

### High Costs

**Issue**: Unexpected Google Cloud charges
**Solution**: Review and optimize

```bash
# Check BigQuery costs
bq ls --max_results=10 --format=prettyjson

# Reduce Vertex AI calls
# Edit: infrastructure/vertex_ai/lead_scoring_pipeline.yaml
# Set: batch_size: 100
```

---

## 🎓 Advanced Features

### Multi-Region Deployment

Deploy to multiple regions for redundancy:

```bash
# Deploy to us-east1
gcloud run deploy lead-sniper-backend \
  --region=us-east1 \
  --source=.

# Setup Traffic Manager
gcloud run services update-traffic lead-sniper-backend \
  --to-revisions=LATEST=100 \
  --region=us-east1
```

### Custom Vertex AI Models

Train custom AutoML models:

```bash
# Create training dataset
bq extract \
  --destination_format=CSV \
  lead_sniper_data.processed_leads \
  gs://your-bucket/training_data.csv

# Train model via Vertex AI Console
# https://console.cloud.google.com/vertex-ai/training
```

### Webhook Integration

Connect to CRM systems:

```python
# Add to cloud_run_server.py
@app.post("/webhook/new-lead")
async def webhook_handler(lead: dict):
    # Send to your CRM
    await send_to_crm(lead)
```

---

## 📚 Additional Resources

- **Vertex AI Documentation**: https://cloud.google.com/vertex-ai/docs
- **Gemini API Guide**: https://ai.google.dev/docs
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **BigQuery Guide**: https://cloud.google.com/bigquery/docs
- **GitHub Actions**: https://docs.github.com/actions

---

## ✅ Success Checklist

- [ ] Google Cloud project created and billing enabled
- [ ] Setup script executed successfully
- [ ] GitHub secrets configured
- [ ] Code pushed to trigger deployment
- [ ] Backend deployed to Cloud Run
- [ ] Vertex AI pipeline uploaded
- [ ] BigQuery dataset created
- [ ] Cloud Scheduler configured
- [ ] Dashboard accessible
- [ ] First lead generation run completed
- [ ] Leads visible in dashboard

---

## 🎯 You're Now Autonomous!

Your Lead Sniper system is now:
- ✅ Running 24/7 on Google Cloud
- ✅ Generating leads automatically every day
- ✅ Scoring with Gemini 2.0 AI
- ✅ Storing data in BigQuery
- ✅ Committing results to GitHub
- ✅ Costing ~$20-50/month (vs $500+)

**No more Manus. No more manual work. Just autonomous lead generation.**

---

**Questions?** Open an issue: https://github.com/InfinityXOneSystems/lead-sniper/issues
