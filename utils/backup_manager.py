"""
Backup Manager - Creates zip backups with unique codes
"""
import zipfile
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

class BackupManager:
    def __init__(self, bot):
        self.bot = bot
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Files/folders to exclude from backup
        self.exclude_patterns = [
            '__pycache__',
            '*.pyc',
            '.git',
            'backups',  # Don't backup backups
            'activity_logs',  # Don't backup logs (can be huge)
            'venv',
            'node_modules'
        ]
    
    def _generate_backup_code(self) -> str:
        """Generate unique 8-character backup code"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(8))
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from backup"""
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                # Extension pattern
                if file_path.name.endswith(pattern[1:]):
                    return True
            elif pattern in str(file_path):
                return True
        return False
    
    async def create_backup(self, reason: str = "Manual backup", session_id: str = None) -> Dict[str, Any]:
        """Create a backup of all bot files"""
        try:
            # Generate backup code and filename
            backup_code = self._generate_backup_code()
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}_{backup_code}.zip"
            backup_path = self.backup_dir / backup_filename
            
            # Create backup metadata
            metadata = {
                "backup_code": backup_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
                "session_id": session_id,
                "bot_name": str(self.bot.user) if self.bot.user else "Unknown"
            }
            
            # Create zip file
            root_dir = Path.cwd()
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add metadata
                zipf.writestr('backup_metadata.json', __import__('json').dumps(metadata, indent=2))
                
                # Add all files
                file_count = 0
                for file_path in root_dir.rglob('*'):
                    if file_path.is_file() and not self._should_exclude(file_path):
                        arcname = file_path.relative_to(root_dir)
                        try:
                            zipf.write(file_path, arcname)
                            file_count += 1
                        except Exception as e:
                            print(f"[BACKUP] Error adding {file_path}: {e}")
            
            # Get file size
            backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            print(f"[BACKUP] Created: {backup_filename} ({file_count} files, {backup_size_mb:.2f} MB)")
            
            return {
                "success": True,
                "backup_code": backup_code,
                "backup_path": str(backup_path),
                "backup_filename": backup_filename,
                "file_count": file_count,
                "size_mb": round(backup_size_mb, 2),
                "metadata": metadata
            }
        
        except Exception as e:
            print(f"[BACKUP] Error creating backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = []
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            })
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
