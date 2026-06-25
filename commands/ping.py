import discord
import psutil
import os
import time
from utils.bot_emojis import E

_process = psutil.Process(os.getpid())


async def setup(bot):
    # Remove existing commands before re-registering (fixes reload)
    bot.remove_command("ping")

    @bot.command(name='ping')
    async def ping(ctx):
        start = time.perf_counter()
        msg = await ctx.send(f"{E('loading')} Checking...")
        latency = (time.perf_counter() - start) * 1000

        cpu    = psutil.cpu_percent()
        ram    = _process.memory_info().rss
        ram_mb = ram / (1024 ** 2)
        try:
            total = psutil.virtual_memory().total / (1024 ** 2)
        except Exception:
            total = 0

        embed = discord.Embed(
            title=f"{E('ping')} Rei-kun Status",
            color=0xff4da6
        )
        embed.add_field(name=f"{E('online')} Latency",  value=f"`{latency:.1f}ms`", inline=True)
        embed.add_field(name=f"{E('info')} WS Ping",    value=f"`{bot.latency * 1000:.1f}ms`", inline=True)
        embed.add_field(name=f"{E('loading')} CPU",     value=f"`{cpu}%`", inline=True)
        embed.add_field(name=f"{E('memory')} RAM",      value=f"`{ram_mb:.0f} / {total:.0f} MB`", inline=True)
        embed.set_footer(text=f"Rei-kun {E('ribbon')}")
        await msg.edit(content="", embed=embed)
