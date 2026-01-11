#!/usr/bin/env python3
"""
SCHEDULED TASK RUNNER
=====================
5 AM Daily Execution | Smart Routing | Auto-Recovery

This script is designed to be run by cron or systemd timer
for scheduled autonomous lead generation.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.autonomous_pipeline import AutonomousPipeline, PipelineConfig
from src.sync.hybrid_sync import HybridSyncManager, SyncConfig

# Configure logging
log_file = f"/home/ubuntu/lead-sniper/logs/scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger('ScheduledRunner')


async def run_scheduled_pipeline():
    """Execute scheduled pipeline run"""
    logger.info("=" * 60)
    logger.info("SCHEDULED LEAD SNIPER EXECUTION")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Load configuration
    config_path = "/home/ubuntu/lead-sniper/config/system_manifest.yaml"
    
    # Create pipeline config
    config = PipelineConfig(
        max_parallel_scrapers=100,
        max_parallel_analysis=50,
        batch_size=100,
        auto_start=True,
        auto_heal=True,
        auto_retry=True,
        max_retries=3,
        local_primary=True,
        cloud_fallback=True,
        smart_routing=True,
        triple_check_enabled=True,
        min_confidence_threshold=0.7,
        store_to_bigquery=True,
        sync_to_firestore=True,
        save_to_local=True,
        results_path="/home/ubuntu/lead-sniper/results"
    )
    
    # Initialize sync manager for hybrid operation
    sync_config = SyncConfig(
        local_primary=True,
        cloud_fallback=True,
        smart_routing=True
    )
    sync_manager = HybridSyncManager(sync_config)
    
    try:
        # Initialize sync
        await sync_manager.initialize()
        await sync_manager.start()
        
        # Run pipeline
        pipeline = AutonomousPipeline(config)
        result = await pipeline.run()
        
        # Log results
        logger.info("=" * 60)
        logger.info("EXECUTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Run ID: {result.run_id}")
        logger.info(f"Leads Scraped: {result.leads_scraped}")
        logger.info(f"Leads Validated: {result.leads_validated}")
        logger.info(f"Leads Analyzed: {result.leads_analyzed}")
        logger.info(f"Leads Stored: {result.leads_stored}")
        logger.info(f"Errors: {len(result.errors)}")
        
        if result.end_time and result.start_time:
            duration = (result.end_time - result.start_time).total_seconds()
            logger.info(f"Duration: {duration:.1f} seconds")
        
        # Save execution summary
        summary = {
            'run_id': result.run_id,
            'timestamp': datetime.now().isoformat(),
            'leads_scraped': result.leads_scraped,
            'leads_validated': result.leads_validated,
            'leads_analyzed': result.leads_analyzed,
            'leads_stored': result.leads_stored,
            'errors': result.errors,
            'status': 'success' if not result.errors else 'completed_with_errors'
        }
        
        summary_path = f"/home/ubuntu/lead-sniper/results/reports/execution_{result.run_id}.json"
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return result
        
    except Exception as e:
        logger.error(f"Scheduled execution failed: {e}")
        raise
    
    finally:
        await sync_manager.stop()


def check_local_availability():
    """Check if local system is available"""
    try:
        # Check disk space
        result = subprocess.run(['df', '-h', '/home/ubuntu'], capture_output=True, text=True)
        logger.info(f"Disk status:\n{result.stdout}")
        
        # Check memory
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        logger.info(f"Memory status:\n{result.stdout}")
        
        return True
    except Exception as e:
        logger.warning(f"Local availability check failed: {e}")
        return False


def main():
    """Main entry point for scheduled execution"""
    logger.info("Starting scheduled runner...")
    
    # Check local availability
    if not check_local_availability():
        logger.warning("Local system may have issues, proceeding with cloud fallback enabled")
    
    # Run pipeline
    try:
        asyncio.run(run_scheduled_pipeline())
        logger.info("Scheduled execution completed successfully")
    except Exception as e:
        logger.error(f"Scheduled execution failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
