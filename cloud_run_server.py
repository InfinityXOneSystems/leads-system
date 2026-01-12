#!/usr/bin/env python3
"""
LEAD SNIPER - CLOUD RUN SERVER
==============================
110% Protocol | FAANG Enterprise-Grade | Zero Human Hands

This server provides HTTP endpoints for Cloud Run deployment,
enabling autonomous operation with health checks, pipeline triggers,
and real-time status monitoring.
"""

import os
import sys
import json
import asyncio
import threading
import time
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('LeadSniper.CloudRun')

app = Flask(__name__)

# Global state
pipeline_status = {
    "status": "idle",
    "last_run": None,
    "last_result": None,
    "uptime_seconds": 0,
    "runs_completed": 0,
    "leads_total": 0,
    "errors": []
}
start_time = time.time()
pipeline_lock = threading.Lock()


def run_pipeline_async():
    """Run the pipeline in a background thread"""
    global pipeline_status
    
    try:
        with pipeline_lock:
            if pipeline_status["status"] == "running":
                logger.warning("Pipeline already running, skipping...")
                return
            pipeline_status["status"] = "running"
            pipeline_status["last_run"] = datetime.now().isoformat()
        
        logger.info("🚀 Starting Lead Sniper pipeline...")
        
        # Import here to avoid circular imports
        from pipeline.autonomous_pipeline import AutonomousPipeline, PipelineConfig
        
        config = PipelineConfig(
            max_parallel_scrapers=int(os.environ.get('MAX_SCRAPERS', 50)),
            max_parallel_analysis=int(os.environ.get('MAX_ANALYSIS', 25)),
            triple_check_enabled=True,
            store_to_bigquery=True,
            sync_to_firestore=True,
            save_to_local=True
        )
        
        # Run pipeline
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        pipeline = AutonomousPipeline(config)
        result = loop.run_until_complete(pipeline.run())
        
        loop.close()
        
        with pipeline_lock:
            pipeline_status["status"] = "completed"
            pipeline_status["runs_completed"] += 1
            pipeline_status["leads_total"] += result.leads_stored
            pipeline_status["last_result"] = {
                "run_id": result.run_id,
                "leads_scraped": result.leads_scraped,
                "leads_validated": result.leads_validated,
                "leads_analyzed": result.leads_analyzed,
                "leads_stored": result.leads_stored,
                "errors": len(result.errors),
                "completed_at": datetime.now().isoformat()
            }
        
        logger.info(f"✅ Pipeline completed: {result.leads_stored} leads stored")
        
    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}")
        with pipeline_lock:
            pipeline_status["status"] = "error"
            pipeline_status["errors"].append({
                "time": datetime.now().isoformat(),
                "error": str(e)
            })
            # Keep only last 10 errors
            pipeline_status["errors"] = pipeline_status["errors"][-10:]


@app.route('/')
def index():
    """Root endpoint - service info"""
    return jsonify({
        "service": "Lead Sniper",
        "version": "1.0.0",
        "status": "healthy",
        "protocol": "110%",
        "standard": "FAANG Enterprise-Grade",
        "uptime_seconds": int(time.time() - start_time),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/health')
def health():
    """Health check endpoint for Cloud Run"""
    is_healthy = pipeline_status["status"] not in ["error"]
    
    return jsonify({
        "status": "healthy" if is_healthy else "unhealthy",
        "pipeline_status": pipeline_status["status"],
        "uptime_seconds": int(time.time() - start_time),
        "runs_completed": pipeline_status["runs_completed"],
        "leads_total": pipeline_status["leads_total"]
    }), 200 if is_healthy else 503


@app.route('/status')
def status():
    """Detailed status endpoint"""
    pipeline_status["uptime_seconds"] = int(time.time() - start_time)
    
    # Check for results files
    results_dir = Path("/app/results/leads") if os.path.exists("/app/results") else Path("results/leads")
    lead_files = list(results_dir.glob("*.json")) if results_dir.exists() else []
    
    return jsonify({
        "service": "Lead Sniper",
        "pipeline": pipeline_status,
        "environment": {
            "project_id": os.environ.get("PROJECT_ID", "infinity-x-one-systems"),
            "region": os.environ.get("REGION", "us-central1"),
            "max_scrapers": os.environ.get("MAX_SCRAPERS", "50")
        },
        "results": {
            "files_count": len(lead_files),
            "latest_file": str(lead_files[-1]) if lead_files else None
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/run', methods=['POST'])
def run_pipeline():
    """Trigger pipeline execution"""
    if pipeline_status["status"] == "running":
        return jsonify({
            "status": "already_running",
            "message": "Pipeline is already running",
            "started_at": pipeline_status["last_run"]
        }), 409
    
    # Start pipeline in background thread
    thread = threading.Thread(target=run_pipeline_async, daemon=True)
    thread.start()
    
    return jsonify({
        "status": "started",
        "message": "Pipeline execution started",
        "started_at": datetime.now().isoformat()
    }), 202


@app.route('/results')
def get_results():
    """Get latest pipeline results"""
    results_dir = Path("/app/results/leads") if os.path.exists("/app/results") else Path("results/leads")
    
    if not results_dir.exists():
        return jsonify({"error": "Results directory not found"}), 404
    
    lead_files = sorted(results_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not lead_files:
        return jsonify({"error": "No results found"}), 404
    
    # Get latest file
    latest_file = lead_files[0]
    
    try:
        with open(latest_file) as f:
            data = json.load(f)
        
        return jsonify({
            "file": str(latest_file),
            "leads_count": len(data) if isinstance(data, list) else 1,
            "data": data[:100] if isinstance(data, list) else data,  # Limit to 100 leads
            "timestamp": datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/metrics')
def metrics():
    """Prometheus-compatible metrics endpoint"""
    metrics_text = f"""# HELP lead_sniper_uptime_seconds Time since service started
# TYPE lead_sniper_uptime_seconds gauge
lead_sniper_uptime_seconds {int(time.time() - start_time)}

# HELP lead_sniper_runs_total Total pipeline runs completed
# TYPE lead_sniper_runs_total counter
lead_sniper_runs_total {pipeline_status["runs_completed"]}

# HELP lead_sniper_leads_total Total leads processed
# TYPE lead_sniper_leads_total counter
lead_sniper_leads_total {pipeline_status["leads_total"]}

# HELP lead_sniper_errors_total Total errors encountered
# TYPE lead_sniper_errors_total counter
lead_sniper_errors_total {len(pipeline_status["errors"])}
"""
    return metrics_text, 200, {'Content-Type': 'text/plain'}


@app.route('/api/leads', methods=['GET'])
def api_leads():
    """REST API endpoint for leads"""
    results_dir = Path("/app/results/leads") if os.path.exists("/app/results") else Path("results/leads")
    
    if not results_dir.exists():
        return jsonify({"leads": [], "total": 0})
    
    all_leads = []
    for lead_file in results_dir.glob("*.json"):
        try:
            with open(lead_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_leads.extend(data)
                else:
                    all_leads.append(data)
        except:
            continue
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        "leads": all_leads[start:end],
        "total": len(all_leads),
        "page": page,
        "per_page": per_page,
        "pages": (len(all_leads) + per_page - 1) // per_page
    })


if __name__ == '__main__':
    print("=" * 80)
    print("LEAD SNIPER - CLOUD RUN SERVER")
    print("110% Protocol | FAANG Enterprise-Grade")
    print("=" * 80)
    
    # Create necessary directories
    os.makedirs('/app/results/leads', exist_ok=True)
    os.makedirs('/app/results/raw', exist_ok=True)
    os.makedirs('/app/results/processed', exist_ok=True)
    os.makedirs('/app/logs', exist_ok=True)
    
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}...")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=port, debug=False)
