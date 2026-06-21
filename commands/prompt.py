from discord.ext import commands
from pathlib import Path
from utils.config_loader import BOT_ADMIN_USERS
from utils.bot_emojis import E

PROMPT_FILE = Path("ai/system prompt.txt")

def is_admin(user):
    return str(user.name).lower() in {x.lower() for x in BOT_ADMIN_USERS}

async def setup(bot):
    # Remove existing commands before re-registering (fixes reload)
    bot.remove_command("prompt")

    @bot.command()
    async def prompt(ctx):
        if not is_admin(ctx.author): return
        if ctx.guild is not None:
            return await ctx.reply(f"{E('error')} DM only.", mention_author=False)
        if not PROMPT_FILE.exists():
            return await ctx.reply(f"{E('error')} Prompt file not found.", mention_author=False)
        content = PROMPT_FILE.read_text(encoding="utf-8")
        if len(content) > 1900: content = content[:1900]
        await ctx.reply(f"{E('dev')} ```txt\n{content}\n```", mention_author=False)
