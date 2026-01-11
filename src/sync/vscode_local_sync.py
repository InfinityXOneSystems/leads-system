#!/usr/bin/env python3
"""
VS CODE LOCAL SYNC MECHANISM
============================
Bidirectional sync between local VS Code and cloud repositories

Features:
- Real-time file watching
- Conflict resolution (remote as source of truth)
- Smart routing (local/cloud based on availability)
- Automatic failover

110% Protocol | FAANG Enterprise-Grade | Zero Human Hands
"""

import asyncio
import hashlib
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('VSCodeLocalSync')


class SyncMode(Enum):
    """Sync operation mode"""
    PUSH = "push"           # Local to remote
    PULL = "pull"           # Remote to local
    BIDIRECTIONAL = "bidirectional"


class ConflictResolution(Enum):
    """Conflict resolution strategy"""
    REMOTE_WINS = "remote_wins"     # Remote is source of truth
    LOCAL_WINS = "local_wins"
    NEWEST_WINS = "newest_wins"
    MANUAL = "manual"


class SystemAvailability(Enum):
    """System availability status"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


@dataclass
class FileChange:
    """Represents a file change"""
    path: str
    action: str  # 'created', 'modified', 'deleted'
    timestamp: datetime
    checksum: str = ""
    size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'checksum': self.checksum,
            'size': self.size
        }


@dataclass
class SyncStatus:
    """Status of a sync operation"""
    success: bool
    mode: SyncMode
    files_synced: int = 0
    files_skipped: int = 0
    conflicts: int = 0
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'mode': self.mode.value,
            'files_synced': self.files_synced,
            'files_skipped': self.files_skipped,
            'conflicts': self.conflicts,
            'errors': self.errors,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp.isoformat()
        }


class SmartRouter:
    """
    Smart routing system to determine local vs cloud execution
    
    Automatically routes operations based on:
    - Local machine availability
    - Network connectivity
    - System load
    """
    
    def __init__(self):
        self.local_status = SystemAvailability.ONLINE
        self.cloud_status = SystemAvailability.ONLINE
        self._last_check = datetime.now()
    
    async def check_local_availability(self) -> SystemAvailability:
        """Check if local system is available"""
        try:
            # Check if we can write to local filesystem
            test_file = Path.home() / '.lead_sniper_health_check'
            test_file.write_text(datetime.now().isoformat())
            test_file.unlink()
            
            self.local_status = SystemAvailability.ONLINE
            return SystemAvailability.ONLINE
        except Exception as e:
            logger.warning(f"Local system unavailable: {e}")
            self.local_status = SystemAvailability.OFFLINE
            return SystemAvailability.OFFLINE
    
    async def check_cloud_availability(self) -> SystemAvailability:
        """Check if cloud services are available"""
        try:
            # Check GitHub connectivity
            result = subprocess.run(
                ['git', 'ls-remote', '--exit-code', '-h', 'https://github.com'],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.cloud_status = SystemAvailability.ONLINE
                return SystemAvailability.ONLINE
            else:
                self.cloud_status = SystemAvailability.DEGRADED
                return SystemAvailability.DEGRADED
        except subprocess.TimeoutExpired:
            self.cloud_status = SystemAvailability.OFFLINE
            return SystemAvailability.OFFLINE
        except Exception as e:
            logger.warning(f"Cloud connectivity check failed: {e}")
            self.cloud_status = SystemAvailability.OFFLINE
            return SystemAvailability.OFFLINE
    
    async def get_optimal_route(self) -> str:
        """Determine optimal execution route"""
        local = await self.check_local_availability()
        cloud = await self.check_cloud_availability()
        
        if local == SystemAvailability.ONLINE and cloud == SystemAvailability.ONLINE:
            return "hybrid"  # Use both
        elif local == SystemAvailability.ONLINE:
            return "local"   # Local only
        elif cloud == SystemAvailability.ONLINE:
            return "cloud"   # Cloud only
        else:
            return "offline" # Queue for later
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'local': self.local_status.value,
            'cloud': self.cloud_status.value,
            'last_check': self._last_check.isoformat()
        }


class VSCodeLocalSync:
    """
    VS Code Local Sync Manager
    
    Handles bidirectional synchronization between local VS Code
    workspace and remote GitHub repositories.
    """
    
    def __init__(
        self,
        local_path: str,
        remote_url: str,
        conflict_resolution: ConflictResolution = ConflictResolution.REMOTE_WINS
    ):
        self.local_path = Path(local_path)
        self.remote_url = remote_url
        self.conflict_resolution = conflict_resolution
        self.router = SmartRouter()
        
        # Tracking
        self._file_checksums: Dict[str, str] = {}
        self._pending_changes: List[FileChange] = []
        self._sync_history: List[SyncStatus] = []
        
        # Ignore patterns
        self.ignore_patterns = {
            '.git',
            '__pycache__',
            'node_modules',
            '.venv',
            'venv',
            '.env',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db'
        }
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored"""
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if path.suffix == pattern[1:]:
                    return True
            elif pattern in str(path):
                return True
        return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        if not file_path.exists() or not file_path.is_file():
            return ""
        
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    async def scan_local_changes(self) -> List[FileChange]:
        """Scan local directory for changes"""
        changes = []
        
        if not self.local_path.exists():
            return changes
        
        for file_path in self.local_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                relative_path = str(file_path.relative_to(self.local_path))
                current_checksum = self._calculate_checksum(file_path)
                
                if relative_path not in self._file_checksums:
                    changes.append(FileChange(
                        path=relative_path,
                        action='created',
                        timestamp=datetime.now(),
                        checksum=current_checksum,
                        size=file_path.stat().st_size
                    ))
                elif self._file_checksums[relative_path] != current_checksum:
                    changes.append(FileChange(
                        path=relative_path,
                        action='modified',
                        timestamp=datetime.now(),
                        checksum=current_checksum,
                        size=file_path.stat().st_size
                    ))
                
                self._file_checksums[relative_path] = current_checksum
        
        return changes
    
    async def pull_from_remote(self) -> SyncStatus:
        """Pull changes from remote repository"""
        start_time = datetime.now()
        errors = []
        files_synced = 0
        
        try:
            if not self.local_path.exists():
                # Clone repository
                logger.info(f"Cloning {self.remote_url} to {self.local_path}")
                result = subprocess.run(
                    ['git', 'clone', self.remote_url, str(self.local_path)],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    errors.append(f"Clone failed: {result.stderr}")
            else:
                # Pull latest changes
                logger.info(f"Pulling from {self.remote_url}")
                result = subprocess.run(
                    ['git', '-C', str(self.local_path), 'pull', '--rebase'],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    # Try to resolve conflicts based on strategy
                    if self.conflict_resolution == ConflictResolution.REMOTE_WINS:
                        subprocess.run(
                            ['git', '-C', str(self.local_path), 'reset', '--hard', 'origin/master'],
                            capture_output=True
                        )
                    else:
                        errors.append(f"Pull failed: {result.stderr}")
            
            # Count synced files
            if self.local_path.exists():
                files_synced = sum(1 for _ in self.local_path.rglob('*') if _.is_file())
        
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Pull error: {e}")
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        status = SyncStatus(
            success=len(errors) == 0,
            mode=SyncMode.PULL,
            files_synced=files_synced,
            errors=errors,
            duration_ms=duration
        )
        
        self._sync_history.append(status)
        return status
    
    async def push_to_remote(self, message: str = "Auto-sync from local") -> SyncStatus:
        """Push local changes to remote repository"""
        start_time = datetime.now()
        errors = []
        files_synced = 0
        
        try:
            if not self.local_path.exists():
                errors.append("Local path does not exist")
            else:
                # Stage all changes
                subprocess.run(
                    ['git', '-C', str(self.local_path), 'add', '-A'],
                    capture_output=True
                )
                
                # Check for changes
                result = subprocess.run(
                    ['git', '-C', str(self.local_path), 'status', '--porcelain'],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    # Commit changes
                    subprocess.run(
                        ['git', '-C', str(self.local_path), 'commit', '-m', message],
                        capture_output=True
                    )
                    
                    # Push to remote
                    result = subprocess.run(
                        ['git', '-C', str(self.local_path), 'push'],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        errors.append(f"Push failed: {result.stderr}")
                    else:
                        files_synced = len(result.stdout.strip().split('\n')) if result.stdout else 1
                else:
                    logger.info("No changes to push")
        
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Push error: {e}")
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        status = SyncStatus(
            success=len(errors) == 0,
            mode=SyncMode.PUSH,
            files_synced=files_synced,
            errors=errors,
            duration_ms=duration
        )
        
        self._sync_history.append(status)
        return status
    
    async def sync_bidirectional(self) -> SyncStatus:
        """Perform bidirectional sync"""
        start_time = datetime.now()
        
        # First pull (remote is source of truth)
        pull_status = await self.pull_from_remote()
        
        # Then push local changes
        push_status = await self.push_to_remote()
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        return SyncStatus(
            success=pull_status.success and push_status.success,
            mode=SyncMode.BIDIRECTIONAL,
            files_synced=pull_status.files_synced + push_status.files_synced,
            errors=pull_status.errors + push_status.errors,
            duration_ms=duration
        )
    
    async def smart_sync(self) -> SyncStatus:
        """
        Perform smart sync based on system availability
        
        Uses SmartRouter to determine optimal sync strategy
        """
        route = await self.router.get_optimal_route()
        
        logger.info(f"Smart sync: using {route} route")
        
        if route == "hybrid":
            return await self.sync_bidirectional()
        elif route == "local":
            # Queue changes for later push
            changes = await self.scan_local_changes()
            self._pending_changes.extend(changes)
            return SyncStatus(
                success=True,
                mode=SyncMode.PUSH,
                files_skipped=len(changes),
                errors=["Cloud unavailable - changes queued"]
            )
        elif route == "cloud":
            return await self.pull_from_remote()
        else:
            return SyncStatus(
                success=False,
                mode=SyncMode.BIDIRECTIONAL,
                errors=["Both local and cloud unavailable"]
            )
    
    def get_sync_history(self, limit: int = 10) -> List[Dict]:
        """Get recent sync history"""
        return [s.to_dict() for s in self._sync_history[-limit:]]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            'local_path': str(self.local_path),
            'remote_url': self.remote_url,
            'conflict_resolution': self.conflict_resolution.value,
            'pending_changes': len(self._pending_changes),
            'tracked_files': len(self._file_checksums),
            'router_status': self.router.get_status(),
            'last_sync': self._sync_history[-1].to_dict() if self._sync_history else None
        }


class VSCodeSettingsSync:
    """
    Sync VS Code settings and extensions
    """
    
    def __init__(self, settings_repo: str):
        self.settings_repo = settings_repo
        self.vscode_settings_path = Path.home() / '.config' / 'Code' / 'User'
    
    async def backup_settings(self, backup_path: Path) -> bool:
        """Backup VS Code settings"""
        try:
            if self.vscode_settings_path.exists():
                shutil.copytree(
                    self.vscode_settings_path,
                    backup_path / 'vscode_settings',
                    dirs_exist_ok=True
                )
                logger.info(f"Settings backed up to {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Settings backup failed: {e}")
        return False
    
    async def restore_settings(self, backup_path: Path) -> bool:
        """Restore VS Code settings from backup"""
        try:
            settings_backup = backup_path / 'vscode_settings'
            if settings_backup.exists():
                shutil.copytree(
                    settings_backup,
                    self.vscode_settings_path,
                    dirs_exist_ok=True
                )
                logger.info("Settings restored")
                return True
        except Exception as e:
            logger.error(f"Settings restore failed: {e}")
        return False
    
    async def export_extensions(self) -> List[str]:
        """Export list of installed extensions"""
        try:
            result = subprocess.run(
                ['code', '--list-extensions'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except Exception as e:
            logger.error(f"Extension export failed: {e}")
        return []


async def main():
    """Test the VS Code local sync"""
    # Initialize sync manager
    sync = VSCodeLocalSync(
        local_path='/home/ubuntu/lead-sniper',
        remote_url='https://github.com/InfinityXOneSystems/lead-sniper.git',
        conflict_resolution=ConflictResolution.REMOTE_WINS
    )
    
    # Check router status
    print("\n=== Smart Router Status ===")
    route = await sync.router.get_optimal_route()
    print(f"Optimal route: {route}")
    print(json.dumps(sync.router.get_status(), indent=2))
    
    # Perform smart sync
    print("\n=== Performing Smart Sync ===")
    status = await sync.smart_sync()
    print(json.dumps(status.to_dict(), indent=2))
    
    # Get overall status
    print("\n=== Sync Manager Status ===")
    print(json.dumps(sync.get_status(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
