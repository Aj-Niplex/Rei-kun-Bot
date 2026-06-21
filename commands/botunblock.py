import discord
from discord.ext import commands
from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS
from utils.storage import unblock_user
from utils.vps_logger import log_action, log_error, log_success
from utils import embeds as emb

def _is_admin(ctx: commands.Context) -> bool:
    return (str(ctx.author.id) in BOT_ADMIN_USER_IDS
            or str(getattr(ctx.author,"name","")).lower() in {x.lower() for x in BOT_ADMIN_USERS})

async def setup(bot: commands.Bot) -> None:
    bot.remove_command("botunblock")

    @bot.command(name="botunblock")
    async def botunblock(ctx: commands.Context, member: discord.Member) -> None:
        if not _is_admin(ctx):
            log_error("BOTUNBLOCK_DENIED", f"actor={ctx.author}")
            return await ctx.reply(embed=emb.error("No Permission"), mention_author=False)
        unblock_user(member.id)
        log_action("BOTUNBLOCK", ctx.author, f"target={member.id}")
        log_success("BOTUNBLOCK_DONE", f"target={member.id}")
        await ctx.send(embed=emb.admin_action_embed("User Unblocked", ctx.author, member, emb.COLOR_SUCCESS))
