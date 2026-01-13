#!/usr/bin/env python3
"""
LOCAL SCRAPER BOOTSTRAP
=======================
Initializes the local execution environment for Lead Sniper
OMNI-LOCK PROTOCOL | Alpha-Sprint 01
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | LOCAL-NODE | %(levelname)s | %(message)s'
)
logger = logging.getLogger('LocalBootstrap')


async def verify_ollama():
    """Verify Ollama is accessible"""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:11434/api/tags') as resp:
                if resp.status == 200:
                    logger.info("✓ Ollama connection verified")
                    return True
    except Exception as e:
        logger.warning(f"✗ Ollama not accessible: {e}")
        return False


async def pull_ollama_model():
    """Pull llama3 model if not present"""
    import aiohttp
    try:
        logger.info("Pulling llama3 model...")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:11434/api/pull',
                json={'name': 'llama3'}
            ) as resp:
                async for line in resp.content:
                    if line:
                        data = json.loads(line)
                        if 'status' in data:
                            logger.info(f"  {data['status']}")
        logger.info("✓ Model ready")
        return True
    except Exception as e:
        logger.error(f"✗ Model pull failed: {e}")
        return False


async def verify_gcp_credentials():
    """Verify GCP credentials are configured"""
    cred_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if cred_file and Path(cred_file).exists():
        logger.info("✓ GCP credentials found")
        return True
    logger.warning("✗ GCP credentials not configured (cloud sync disabled)")
    return False


async def initialize_directories():
    """Create required directories"""
    dirs = ['results/raw', 'results/processed', 'results/leads', 'results/reports', 'logs', 'data']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    logger.info("✓ Directory structure initialized")


async def main():
    """Bootstrap local execution environment"""
    logger.info("=" * 60)
    logger.info("LEAD SNIPER LOCAL NODE - BOOTSTRAP")
    logger.info("OMNI-LOCK PROTOCOL | Alpha-Sprint 01")
    logger.info("=" * 60)

    # Initialize
    await initialize_directories()

    # Verify Ollama
    ollama_ready = await verify_ollama()
    if not ollama_ready:
        logger.info("Waiting for Ollama to start...")
        await asyncio.sleep(5)
        ollama_ready = await verify_ollama()

    if ollama_ready:
        await pull_ollama_model()

    # Verify GCP
    await verify_gcp_credentials()

    logger.info("=" * 60)
    logger.info("✓ BOOTSTRAP COMPLETE")
    logger.info("  Ready for autonomous execution")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
