"""
AI Error Monitor - Monitors logs and detects issues in real-time
"""
import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import discord
from utils.email_sender import send_error_email

class AIMonitor:
    def __init__(self, bot, activity_logger, owner_id: int):
        self.bot = bot
        self.logger = activity_logger
        self.owner_id = owner_id
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_task = None
        
        # Error patterns to detect
        self.error_patterns = {
            "timeout": {
                "keywords": ["timed out", "timeout", "no response"],
                "severity": "medium",
                "fix": "Check if the service is responding. Increase timeout limits or verify API connectivity."
            },
            "rate_limit": {
                "keywords": ["rate limit", "429", "too many requests"],
                "severity": "high",
                "fix": "Implement exponential backoff. Add rate limit handling with delays between requests."
            },
            "permission": {
                "keywords": ["permission", "forbidden", "403", "unauthorized", "401"],
                "severity": "high",
                "fix": "Verify bot permissions in server settings. Check if required intents are enabled."
            },
            "connection": {
                "keywords": ["connection", "network", "unreachable", "ECONNREFUSED"],
                "severity": "critical",
                "fix": "Check internet connectivity. Verify service endpoints are accessible."
            },
            "missing_module": {
                "keywords": ["ModuleNotFoundError", "ImportError", "no module named"],
                "severity": "critical",
                "fix": "Install missing dependencies via requirements.txt. Run: pip install <module_name>"
            },
            "database": {
                "keywords": ["database", "sqlite", "query failed", "transaction"],
                "severity": "high",
                "fix": "Check database file integrity. Verify database schema matches code expectations."
            },
            "api_key": {
                "keywords": ["api key", "invalid token", "authentication failed"],
                "severity": "critical",
                "fix": "Verify API keys in .env file. Check if keys are valid and not expired."
            }
        }
        
        # Track reported issues to avoid spam
        self.reported_issues = set()
        
        print(f"[AI_MONITOR] Initialized for owner: {owner_id}")
    
    async def start_monitoring(self):
        """Start background monitoring task"""
        if self.is_monitoring:
            print("[AI_MONITOR] Already monitoring")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        print("[AI_MONITOR] Started monitoring")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        print("[AI_MONITOR] Stopped monitoring")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        try:
            while self.is_monitoring:
                # Check for pending commands (no response)
                self.logger.check_pending_commands()
                
                # Analyze recent logs
                await self._analyze_recent_logs()
                
                # Wait 15 seconds before next check
                await asyncio.sleep(15)
        except asyncio.CancelledError:
            print("[AI_MONITOR] Monitoring cancelled")
        except Exception as e:
            print(f"[AI_MONITOR] Error in monitor loop: {e}")
    
    async def _analyze_recent_logs(self):
        """Analyze recent log entries for errors"""
        try:
            log_file = self.logger.log_file
            if not log_file.exists():
                return
            
            # Read last 50 lines
            recent_events = []
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    try:
                        event = json.loads(line.strip())
                        recent_events.append(event)
                    except:
                        continue
            
            # Look for errors
            for event in recent_events:
                if event.get("event_type") in ["COMMAND_ERROR", "NO_RESPONSE"]:
                    await self._handle_error_event(event)
        
        except Exception as e:
            print(f"[AI_MONITOR] Error analyzing logs: {e}")
    
    async def _handle_error_event(self, event: Dict[str, Any]):
        """Handle detected error event"""
        event_id = event.get("command_id", event.get("timestamp"))
        
        # Avoid duplicate reports
        if event_id in self.reported_issues:
            return
        
        self.reported_issues.add(event_id)
        
        # Detect error pattern
        error_type = event.get("event_type")
        error_msg = event.get("error_message", event.get("reason", ""))
        
        detected_pattern = None
        for pattern_name, pattern_info in self.error_patterns.items():
            if any(keyword in error_msg.lower() for keyword in pattern_info["keywords"]):
                detected_pattern = pattern_name
                break
        
        # Prepare error report
        report = {
            "timestamp": event.get("timestamp"),
            "error_type": error_type,
            "command": event.get("command_name", "Unknown"),
            "user_id": event.get("user_id"),
            "error_message": error_msg,
            "detected_pattern": detected_pattern,
            "severity": self.error_patterns[detected_pattern]["severity"] if detected_pattern else "unknown",
            "suggested_fix": self.error_patterns[detected_pattern]["fix"] if detected_pattern else "No automatic fix available"
        }
        
        # Send email notification
        await self._send_error_email(report)
        
        # Send DM to owner
        await self._send_owner_dm(report)
    
    async def _send_error_email(self, report: Dict[str, Any]):
        """Send error report via email"""
        try:
            subject = f"🚨 Bot Error Detected: {report['detected_pattern'] or 'Unknown'}"
            
            body = f"""
<h2>Error Detection Report</h2>
<p><strong>Timestamp:</strong> {report['timestamp']}</p>
<p><strong>Severity:</strong> {report['severity'].upper()}</p>
<p><strong>Command:</strong> {report['command']}</p>
<p><strong>Error Type:</strong> {report['error_type']}</p>
<p><strong>Error Message:</strong></p>
<pre>{report['error_message']}</pre>

<h3>💡 Suggested Fix:</h3>
<p>{report['suggested_fix']}</p>

<hr>
<p><em>This is an automated report from AI Monitor. Check your Discord DM for approval to apply fixes.</em></p>
"""
            
            success, message = await send_error_email(
                subject=subject,
                simple_body=f"Error: {report['error_type']} - {report['error_message']}",
                detailed_html=body
            )
            
            if success:
                print(f"[AI_MONITOR] ✅ Email sent for error: {report['detected_pattern']}")
            else:
                print(f"[AI_MONITOR] ❌ Email failed: {message}")
        
        except Exception as e:
            print(f"[AI_MONITOR] Error sending email: {e}")
    
    async def _send_owner_dm(self, report: Dict[str, Any]):
        """Send DM to owner asking for fix approval"""
        try:
            owner = await self.bot.fetch_user(self.owner_id)
            if not owner:
                print("[AI_MONITOR] Could not fetch owner user")
                return
            
            # Create embed
            embed = discord.Embed(
                title="🚨 Error Detected",
                description=f"**Pattern:** {report['detected_pattern'] or 'Unknown'}",
                color=discord.Color.red() if report['severity'] == 'critical' else discord.Color.orange(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="Command",
                value=f"`{report['command']}`",
                inline=True
            )
            
            embed.add_field(
                name="Severity",
                value=report['severity'].upper(),
                inline=True
            )
            
            embed.add_field(
                name="Error Message",
                value=f"```{report['error_message'][:200]}```",
                inline=False
            )
            
            embed.add_field(
                name="💡 Suggested Fix",
                value=report['suggested_fix'],
                inline=False
            )
            
            embed.set_footer(text="Do you want me to create a backup and attempt to fix this?")
            
            # Create view with approval buttons
            view = ErrorApprovalView(self.bot, report, self.logger.session_id)
            
            await owner.send(embed=embed, view=view)
            print(f"[AI_MONITOR] DM sent to owner for error: {report['detected_pattern']}")
        
        except discord.Forbidden:
            print("[AI_MONITOR] Cannot DM owner (DMs closed)")
        except Exception as e:
            print(f"[AI_MONITOR] Error sending DM: {e}")


class ErrorApprovalView(discord.ui.View):
    """View for error fix approval"""
    
    def __init__(self, bot, report: Dict[str, Any], session_id: str):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.bot = bot
        self.report = report
        self.session_id = session_id
    
    @discord.ui.button(label="✅ Backup & Fix", style=discord.ButtonStyle.success)
    async def approve_fix(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Trigger backup
        from utils.backup_manager import BackupManager
        backup_mgr = BackupManager(self.bot)
        
        backup_result = await backup_mgr.create_backup(
            reason=f"Pre-fix backup for {self.report['detected_pattern']}",
            session_id=self.session_id
        )
        
        if backup_result["success"]:
            embed = discord.Embed(
                title="✅ Backup Created",
                description=f"**Code:** `{backup_result['backup_code']}`",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Backup File",
                value=backup_result['backup_path'],
                inline=False
            )
            embed.add_field(
                name="Next Steps",
                value="Manual fix required. Apply the suggested fix and test.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(
                f"❌ Backup failed: {backup_result.get('error')}",
                ephemeral=True
            )
        
        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="❌ Ignore", style=discord.ButtonStyle.danger)
    async def decline_fix(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fix ignored.", ephemeral=True)
        
        # Disable buttons
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
