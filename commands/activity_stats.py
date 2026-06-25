"""
Activity Stats Command - View session activity statistics
"""
import discord
import psutil
import time
from discord.ext import commands
from utils.bot_emojis import E


async def setup(bot: commands.Bot):
    """Setup activity stats command."""
    
    @bot.command(name="activity")
    async def activity_stats(ctx):
        """Show bot activity and performance stats with loading animation."""
        
        # Show loading animation
        loading_msg = await ctx.send(f"{E('loading')} Gathering activity statistics...")
        
        # Simulate gathering stats (add small delay for realism)
        await ctx.trigger_typing()
        
        # Get process stats
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=0.5)
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 ** 2)
        
        # Calculate uptime
        uptime_seconds = int(time.time() - process.create_time())
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        # Count command handlers
        command_count = len([c for c in bot.commands])
        
        # Create embed
        embed = discord.Embed(
            title=f"{E('info')} Rei-kun Activity Statistics",
            description=f"**Bot:** {bot.user.name}#{bot.user.discriminator}",
            color=0x5865f2,
            timestamp=discord.utils.utcnow()
        )
        
        # Bot stats
        embed.add_field(
            name=f"{E('sparkle')} Bot Status",
            value=(
                f"**Servers:** `{len(bot.guilds)}`\n"
                f"**Commands:** `{command_count}`\n"
                f"**Latency:** `{bot.latency * 1000:.1f}ms`"
            ),
            inline=True
        )
        
        # Performance stats
        embed.add_field(
            name=f"{E('loading')} Performance",
            value=(
                f"**CPU:** `{cpu_percent:.1f}%`\n"
                f"**RAM:** `{memory_mb:.1f} MB`\n"
                f"**Uptime:** `{uptime_str}`"
            ),
            inline=True
        )
        
        # Connection stats
        total_members = sum(g.member_count or 0 for g in bot.guilds)
        embed.add_field(
            name=f"{E('crown')} Reach",
            value=(
                f"**Total Users:** `{total_members}`\n"
                f"**Guilds:** `{len(bot.guilds)}`\n"
                f"**Status:** `Online`"
            ),
            inline=True
        )
        
        embed.set_footer(text="Rei-kun Activity Tracker v7.0")
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        
        await loading_msg.edit(content="", embed=embed)
