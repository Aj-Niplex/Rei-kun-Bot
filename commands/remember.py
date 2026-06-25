import random
from utils.storage import get_memories
from utils.bot_emojis import E

async def setup(bot):
    # Remove existing commands before re-registering (fixes reload)
    bot.remove_command("remember")

    @bot.command()
    async def remember(ctx):
        guild_id = ctx.guild.id if ctx.guild else "dm"
        data = get_memories(guild_id, "memories")
        if not data:
            return await ctx.send(f"{E('info')} No memories saved yet. Use `?save` by replying to a message.")
        await ctx.send(f"{E('memory')} {random.choice(data)}")
