"""
Backup Command - Create manual backups with unique code
"""
import discord
from discord.ext import commands
from utils.bot_emojis import E
from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS


def _is_admin(user: discord.abc.User) -> bool:
    """Check if user is bot admin."""
    return (
        str(user.id) in BOT_ADMIN_USER_IDS
        or str(getattr(user, "name", "")).lower() in {x.lower() for x in BOT_ADMIN_USERS}
    )


async def setup(bot: commands.Bot):
    """Setup backup commands."""
    
    
    @bot.command(name="backup")
    async def backup_prefix(ctx, *, reason: str = "Manual backup"):
        """Prefix version of backup command."""
        if not _is_admin(ctx.author):
            return await ctx.send(f"{E('error')} Admin only.")
        
        try:
            from utils.backup_manager import BackupManager
            from app import activity_logger
            
            backup_mgr = BackupManager(bot)
            session_id = None
            if activity_logger:
                session_id = activity_logger.session_id
            
            result = await backup_mgr.create_backup(reason=reason, session_id=session_id)
            
            if result["success"]:
                embed = discord.Embed(
                    title=f"{E('success')} Backup Created",
                    description=f"**Code:** `{result['backup_code']}`",
                    color=0x57f287
                )
                embed.add_field(
                    name="Details",
                    value=f"{result['file_count']} files, {result['size_mb']} MB"
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{E('error')} Backup failed: {result.get('error')}")
        
        except Exception as e:
            await ctx.send(f"{E('error')} Error: `{str(e)[:100]}`")
