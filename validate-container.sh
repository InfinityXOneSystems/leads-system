#!/bin/bash
# CONTAINER ENVIRONMENT VALIDATOR
# Verifies all systems operational within Shadow-Box
# OMNI-LOCK Protocol

echo "============================================================"
echo "SHADOW-BOX ENVIRONMENT VALIDATION"
echo "Privileged Container | System Status Check"
echo "============================================================"
echo ""

# Python
echo "[1/8] Python Environment..."
python --version && echo "  ✓ Python operational" || echo "  ✗ Python missing"

# Pip packages
echo ""
echo "[2/8] Core Dependencies..."
python -c "import aiohttp, playwright, google.cloud.aiplatform" 2>/dev/null && echo "  ✓ Core packages installed" || echo "  ✗ Dependencies missing"

# Playwright
echo ""
echo "[3/8] Playwright Browsers..."
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.launch(); p.stop()" 2>/dev/null && echo "  ✓ Chromium ready" || echo "  ⚠ Chromium installation incomplete"

# Network
echo ""
echo "[4/8] Network Connectivity..."
curl -s -m 3 https://www.google.com > /dev/null && echo "  ✓ Internet accessible" || echo "  ✗ No internet"

# Ollama
echo ""
echo "[5/8] Ollama API (Local AI)..."
curl -s -m 3 http://host.docker.internal:11434/api/tags > /dev/null && echo "  ✓ Ollama connected" || echo "  ⚠ Ollama unavailable"

# Docker socket
echo ""
echo "[6/8] Docker-in-Docker..."
docker ps > /dev/null 2>&1 && echo "  ✓ Docker socket accessible" || echo "  ⚠ Docker unavailable"

# Workspace
echo ""
echo "[7/8] Workspace Mount..."
[ -f "/workspace/main.py" ] && echo "  ✓ Workspace mounted correctly" || echo "  ✗ Workspace not mounted"

# Permissions
echo ""
echo "[8/8] Write Permissions..."
touch /workspace/logs/.test 2>/dev/null && rm /workspace/logs/.test && echo "  ✓ Write access granted" || echo "  ✗ Permission denied"

echo ""
echo "============================================================"
echo "✓ VALIDATION COMPLETE"
echo "Container ready for autonomous execution"
echo "============================================================"
