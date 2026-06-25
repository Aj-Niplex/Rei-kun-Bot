"""
Advanced Activity Logger - Tracks all bot interactions
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import discord
from typing import Dict, Any

class ActivityLogger:
    def __init__(self, bot):
        self.bot = bot
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path("activity_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create session log file
        self.log_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self.stats_file = self.log_dir / f"stats_{self.session_id}.json"
        
        # Initialize stats
        self.stats = {
            "session_id": self.session_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "total_commands": 0,
            "total_messages": 0,
            "total_responses": 0,
            "commands_without_response": 0,
            "average_response_time_ms": 0,
            "animations_shown": 0,
            "errors_detected": 0,
            "response_times": []
        }
        
        # Track pending commands (commands waiting for response)
        self.pending_commands = {}
        
        print(f"[ACTIVITY_LOGGER] Session started: {self.session_id}")
        self._write_session_start()
    
    def _write_log(self, event: Dict[str, Any]):
        """Write event to JSONL log file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[ACTIVITY_LOGGER] Error writing log: {e}")
    
    def _update_stats(self):
        """Update stats file"""
        try:
            # Calculate average response time
            if self.stats["response_times"]:
                avg = sum(self.stats["response_times"]) / len(self.stats["response_times"])
                self.stats["average_response_time_ms"] = round(avg, 2)
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ACTIVITY_LOGGER] Error updating stats: {e}")
    
    def _write_session_start(self):
        """Log session start"""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "SESSION_START",
            "session_id": self.session_id,
            "bot_name": str(self.bot.user) if self.bot.user else "Unknown",
            "bot_id": self.bot.user.id if self.bot.user else None
        }
        self._write_log(event)
    
    def log_message(self, message: discord.Message):
        """Log incoming message"""
        if message.author.bot:
            return
        
        self.stats["total_messages"] += 1
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "MESSAGE_RECEIVED",
            "user_id": message.author.id,
            "username": str(message.author),
            "channel_id": message.channel.id,
            "guild_id": message.guild.id if message.guild else None,
            "content": message.content[:500],  # Limit content length
            "has_attachments": len(message.attachments) > 0,
            "message_id": message.id
        }
        self._write_log(event)
        self._update_stats()
    
    def log_command_start(self, interaction: discord.Interaction):
        """Log command invocation"""
        command_name = interaction.command.name if interaction.command else "unknown"
        command_id = f"{interaction.user.id}_{interaction.id}"
        
        self.stats["total_commands"] += 1
        
        # Track pending command
        self.pending_commands[command_id] = {
            "started_at": datetime.now(timezone.utc),
            "command_name": command_name,
            "user_id": interaction.user.id
        }
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "COMMAND_START",
            "command_id": command_id,
            "command_name": command_name,
            "user_id": interaction.user.id,
            "username": str(interaction.user),
            "channel_id": interaction.channel_id,
            "guild_id": interaction.guild_id,
            "options": str(interaction.data) if hasattr(interaction, 'data') else None
        }
        self._write_log(event)
        self._update_stats()
    
    def log_command_response(self, interaction: discord.Interaction, response_content: str, animation_shown: bool = False):
        """Log command response"""
        command_name = interaction.command.name if interaction.command else "unknown"
        command_id = f"{interaction.user.id}_{interaction.id}"
        
        # Calculate response time
        response_time_ms = None
        if command_id in self.pending_commands:
            pending = self.pending_commands[command_id]
            delta = datetime.now(timezone.utc) - pending["started_at"]
            response_time_ms = delta.total_seconds() * 1000
            self.stats["response_times"].append(response_time_ms)
            del self.pending_commands[command_id]
        
        self.stats["total_responses"] += 1
        if animation_shown:
            self.stats["animations_shown"] += 1
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "COMMAND_RESPONSE",
            "command_id": command_id,
            "command_name": command_name,
            "user_id": interaction.user.id,
            "response_time_ms": response_time_ms,
            "animation_shown": animation_shown,
            "response_preview": response_content[:200] if response_content else None
        }
        self._write_log(event)
        self._update_stats()
    
    def log_command_error(self, interaction: discord.Interaction, error: Exception):
        """Log command error"""
        command_name = interaction.command.name if interaction.command else "unknown"
        command_id = f"{interaction.user.id}_{interaction.id}"
        
        self.stats["errors_detected"] += 1
        
        # Remove from pending
        if command_id in self.pending_commands:
            del self.pending_commands[command_id]
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "COMMAND_ERROR",
            "command_id": command_id,
            "command_name": command_name,
            "user_id": interaction.user.id,
            "error_type": type(error).__name__,
            "error_message": str(error)[:500]
        }
        self._write_log(event)
        self._update_stats()
    
    def log_no_response(self, command_id: str, reason: str = "Unknown"):
        """Log command without response"""
        self.stats["commands_without_response"] += 1
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "NO_RESPONSE",
            "command_id": command_id,
            "reason": reason
        }
        self._write_log(event)
        self._update_stats()
    
    def check_pending_commands(self):
        """Check for commands that never received response (>30s)"""
        now = datetime.now(timezone.utc)
        timeout_seconds = 30
        
        for command_id, pending in list(self.pending_commands.items()):
            delta = now - pending["started_at"]
            if delta.total_seconds() > timeout_seconds:
                self.log_no_response(
                    command_id, 
                    f"Command '{pending['command_name']}' timed out after {timeout_seconds}s"
                )
                del self.pending_commands[command_id]
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current session stats"""
        return self.stats.copy()
    
    def get_log_file_path(self) -> str:
        """Get current log file path"""
        return str(self.log_file)
