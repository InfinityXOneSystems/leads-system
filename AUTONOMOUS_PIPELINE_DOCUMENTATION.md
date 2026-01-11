# Lead Sniper - Autonomous Pipeline Documentation

## 🎯 System Overview

**Lead Sniper** is a fully autonomous, zero-human-hands lead generation system designed for real estate intelligence. The system operates 24/7 with hybrid local/cloud architecture, integrating Manus Core, Vision Cortex, Google Vertex AI, and a fleet of headless scrapers.

---

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Triple Validation System](#triple-validation-system)
3. [GitHub Actions Workflows](#github-actions-workflows)
4. [GCP & Workspace Integration](#gcp--workspace-integration)
5. [VS Code Local Sync](#vs-code-local-sync)
6. [Smart Routing](#smart-routing)
7. [Scheduled Tasks](#scheduled-tasks)
8. [Configuration](#configuration)

---

## 🏗️ Architecture

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Manus Core** | Central orchestration engine | `src/core/manus_core.py` |
| **Vision Cortex** | AI-powered analysis | `src/vision_cortex/vision_cortex_agent.py` |
| **Vertex AI Integration** | ML predictions & AutoML | `src/vertex_ai/vertex_integration.py` |
| **Headless Orchestrator** | Scraper fleet management | `src/scrapers/headless_orchestrator.py` |
| **Autonomous Pipeline** | E2E pipeline execution | `src/pipeline/autonomous_pipeline.py` |
| **Hybrid Sync** | Local/Cloud synchronization | `src/sync/hybrid_sync.py` |

### Data Flow

```
[Data Sources] → [Headless Scrapers] → [Vision Cortex] → [Triple Validation]
                                                                ↓
[GitHub] ← [Cloud Sync] ← [Vertex AI] ← [Validated Leads]
```

---

## ✅ Triple Validation System

The system implements a rigorous 3-step validation process ensuring 100% data accuracy.

### Step 1: Schema Validation (40% weight)
- Validates data structure and completeness
- Checks required fields presence
- Verifies data types
- **Location:** `src/validation/comprehensive_validator.py`

### Step 2: Cross-Reference Validation (35% weight)
- Verifies against internal sources
- Checks ID format consistency
- Validates internal data consistency
- **Location:** `src/validation/comprehensive_validator.py`

### Step 3: External Verification (25% weight)
- Confirms with outside sources
- Validates API connectivity
- Checks data patterns against known good data
- **Location:** `src/validation/comprehensive_validator.py`

### Validation Levels

| Level | Threshold | Use Case |
|-------|-----------|----------|
| **STRICT** | 100% | Production data |
| **STANDARD** | 90% | Testing |
| **RELAXED** | 75% | Development |

---

## 🔄 GitHub Actions Workflows

> **Note:** Workflow files are located in `/home/ubuntu/github-workflows-to-upload/` and require manual upload due to GitHub App permissions.

### Available Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `autonomous-pipeline.yml` | Daily 5 AM + Push | Main pipeline execution |
| `triple-validation.yml` | Push to results/** | Data validation |
| `gcp-integration.yml` | Push + Manual | GCP service sync |
| `workspace-sync.yml` | Daily + Manual | Google Workspace sync |
| `vscode-sync.yml` | Push + Manual | VS Code settings sync |
| `auto-heal.yml` | On failure | Self-healing |
| `auto-optimize.yml` | Weekly | Performance optimization |
| `repo-backup.yml` | Daily | Repository backup |

### Manual Upload Instructions

1. Navigate to repository Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"
3. Go to Actions tab → New workflow → "set up a workflow yourself"
4. Copy content from each `.yml` file in `/home/ubuntu/github-workflows-to-upload/`
5. Commit directly to master branch

---

## ☁️ GCP & Workspace Integration

### Google Cloud Platform

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Vertex AI** | ML predictions, Gemini | Project: infinity-x-one-systems |
| **BigQuery** | Data warehouse | Dataset: lead_sniper |
| **Firestore** | Real-time database | Collection: leads |
| **Cloud Storage** | File storage | Bucket: ix1-lead-sniper |

### Google Workspace

| Service | Purpose |
|---------|---------|
| **Google Drive** | Document storage |
| **Google Sheets** | Lead export |
| **Google Calendar** | Task scheduling |
| **Gmail** | Notifications |

### Authentication

```python
# GCP Service Account
GCP_SA_KEY = os.environ.get('GCP_SA_KEY')

# Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
```

---

## 💻 VS Code Local Sync

### Features

- **Bidirectional sync** with remote repositories
- **Smart routing** based on system availability
- **Conflict resolution** (remote as source of truth)
- **Automatic failover** when local is offline
- **Pending changes queue** for offline mode

### Sync Modes

| Mode | Direction | Use Case |
|------|-----------|----------|
| **PUSH** | Local → Remote | Upload changes |
| **PULL** | Remote → Local | Download changes |
| **BIDIRECTIONAL** | Both | Full sync |

### Configuration

```python
sync = VSCodeLocalSync(
    local_path='/path/to/local/repo',
    remote_url='https://github.com/InfinityXOneSystems/lead-sniper.git',
    conflict_resolution=ConflictResolution.REMOTE_WINS
)
```

---

## 🛣️ Smart Routing

The smart routing system automatically determines optimal execution path.

### Routes

| Route | Condition | Behavior |
|-------|-----------|----------|
| **hybrid** | Both available | Use local + cloud |
| **local** | Cloud unavailable | Local only, queue cloud ops |
| **cloud** | Local unavailable | Cloud only |
| **offline** | Both unavailable | Queue all operations |

### Implementation

```python
router = SmartRouter()
route = await router.get_optimal_route()
# Returns: 'hybrid', 'local', 'cloud', or 'offline'
```

---

## ⏰ Scheduled Tasks

### Daily Pipeline (5 AM EST)

```
Cron: 0 0 5 * * *
Task: Lead Sniper Daily Pipeline
```

**Execution Steps:**
1. Clone/update repository
2. Run autonomous pipeline
3. Execute headless scrapers
4. Run triple validation
5. Sync to Google Cloud
6. Export to Google Sheets
7. Push results to GitHub
8. Generate daily report

---

## ⚙️ Configuration

### System Manifest

**Location:** `config/system_manifest.yaml`

```yaml
system:
  name: lead-sniper
  version: 1.0.0
  protocol: "110%"
  standard: FAANG_ENTERPRISE_GRADE

scrapers:
  parallel_instances: 3
  headless: true
  
validation:
  level: STRICT
  min_confidence: 0.85
```

### Treasure Coast Config

**Location:** `config/treasure_coast_config.json`

```json
{
  "target_counties": ["St. Lucie", "Martin", "Indian River", "Okeechobee"],
  "zip_codes": ["34945", "34946", "34947", "34948", "34949", "34950"],
  "property_types": ["Single Family", "Multi-Family", "Condo", "Land"]
}
```

---

## 📊 Results

### Data Location

| Type | Path |
|------|------|
| Raw Data | `results/raw/` |
| Processed | `results/processed/` |
| Validated | `results/validated/` |
| Logs | `results/logs/` |

### Treasure Coast 100 Verified Properties

**Location:** `results/raw/treasure_coast_100_verified_properties.csv`

Contains 100 verified distressed property leads from the Treasure Coast region.

---

## 🔐 Security

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `GCP_SA_KEY` | GCP Service Account JSON |
| `GEMINI_API_KEY` | Google Gemini API |
| `GITHUB_TOKEN` | GitHub Actions |

### Best Practices

- All secrets stored in GitHub Secrets
- Service account with minimal required permissions
- API keys rotated quarterly
- Audit logs enabled

---

## 📈 Monitoring

### Health Checks

- Service connectivity validation
- API key verification
- Data pattern analysis
- Sync status monitoring

### Alerts

- Pipeline failure notifications
- Validation threshold breaches
- Service disconnection alerts
- Quota warnings

---

## 🚀 Quick Start

```bash
# Clone repository
gh repo clone InfinityXOneSystems/lead-sniper
cd lead-sniper

# Install dependencies
pip3 install -r requirements.txt

# Run pipeline
python3 main.py
```

---

## 📞 Support

- **Repository:** https://github.com/InfinityXOneSystems/lead-sniper
- **Protocol:** 110% | FAANG Enterprise-Grade | Zero Human Hands

---

*Built with ❤️ by InfinityXOneSystems*
*Powered by Manus Core | Vision Cortex | Vertex AI*
