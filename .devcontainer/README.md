# SHADOW-BOX README
# Container-Based Execution Environment

## Overview
Shadow-Box is a privileged Docker container that bypasses OS-level restrictions (DLL blocks, Application Control policies) by virtualizing the entire execution environment.

## Architecture
```
Host OS (Windows)
  └── Docker Engine
      └── Infinity Dev Container (Privileged)
          ├── Python 3.11 + Dependencies
          ├── Playwright + Chromium
          ├── Google Cloud SDK
          ├── Direct access to host network
          └── Connection to Ollama (host.docker.internal:11434)
```

## Quick Start

### Initialize Container
```powershell
.\init-shadowbox.ps1
```

### Run Pipeline
```powershell
.\run-in-container.ps1
```

### Interactive Shell
```powershell
.\run-in-container.ps1 -Interactive
```

### Execute Custom Command
```powershell
.\run-in-container.ps1 -Command "python main.py --test"
```

## VS Code Integration
When you open this folder in VS Code, it will automatically detect `.devcontainer/devcontainer.json` and prompt:

> "Reopen in Container"

Click **Reopen in Container** to work directly inside the Shadow-Box. All terminal commands will execute inside the container with full privileges.

## Container Features
- **Privileged Mode**: Full system access within container
- **Network Host**: Direct host network access
- **Docker-in-Docker**: Can run Docker commands
- **Volume Mounts**: Workspace synced in real-time
- **Ollama Bridge**: AI model access via host.docker.internal
- **Persistent Caches**: Python and Playwright caches preserved

## Autonomous Operation
Once initialized, the container runs continuously in the background. Commands are routed through `run-in-container.ps1` wrapper script.

## Troubleshooting

### Container Not Starting
```powershell
docker-compose down
docker-compose build --no-cache
.\init-shadowbox.ps1
```

### Dependencies Missing
```powershell
docker exec infinity-dev-container pip install -r requirements.txt
```

### Validate Environment
```powershell
docker exec infinity-dev-container bash /workspace/validate-container.sh
```

## Silent Autonomous Execution
No user prompts. No permission requests. All operations self-contained within privileged container.

**OMNI-LOCK PROTOCOL ENGAGED**
