from discord.ext import commands
from utils.bot_emojis import E

async def setup(bot):
    # Remove existing commands before re-registering (fixes reload)
    bot.remove_command("userid")

    @bot.command(name="userid")
    async def userid(ctx, *, username: str):
        if not ctx.guild:
            return await ctx.reply(f"{E('error')} Server only command.", mention_author=False)
        target = username.lower().strip()
        matches = []
        for m in ctx.guild.members:
            names = {
                (m.name or "").lower(),
                (m.display_name or "").lower(),
                (getattr(m, "global_name", None) or "").lower(),
            }
            if target in names or any(target in n for n in names if n):
                matches.append(m)
        if not matches:
            return await ctx.reply(f"{E('error')} No matching member found.", mention_author=False)
        m = matches[0]
        await ctx.reply(f"{E('info')} **{m.display_name}** → `{m.id}`", mention_author=False)
