# Python 3.13 | discord.py 2.6.4
import discord
from discord.ext import commands
from utils.ai import ask_ai
from utils.animations import AIAnimation
from utils.bot_emojis import E
from utils.concurrency import check_user_cooldown, get_active_count, get_queue_size
from utils.conversation import clear as clear_history
from utils.config_loader import BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS


def _is_admin(user: discord.abc.User) -> bool:
    return (str(user.id) in BOT_ADMIN_USER_IDS
            or str(getattr(user, "name", "")).lower() in {x.lower() for x in BOT_ADMIN_USERS})


async def setup(bot: commands.Bot) -> None:
    bot.remove_command("ai")
    bot.remove_command("clearhistory")

    @bot.command(name="ai")
    async def ai_cmd(ctx: commands.Context, *, prompt: str = "") -> None:
        uid = str(ctx.author.id)
        is_admin = _is_admin(ctx.author)

        # Rate limit
        wait = None
        if not is_admin:
            wait = check_user_cooldown(uid)

        if wait and wait > 0:
            return await ctx.reply(
              f"{E('warning')} Wait **{wait}**s before using `?ai` again.",
                mention_author=False,
                delete_after=5,
            )

        # Queue info
        active = get_active_count()
        if active >= 10 and not is_admin:
            q = get_queue_size()
            await ctx.reply(
                f"{E('loading')} Server busy ({active} active{f', {q} queued' if q else ''}). Your request is queued...",
                mention_author=False, delete_after=8,
            )

        # Replied message context
        replied_content = ""
        if ctx.message.reference:
            try:
                ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                replied_content = (ref.content or "").strip()
            except Exception:
                pass

        # Build prompt
        if replied_content and not prompt:
            final_prompt = f"Explain this message in simple words:\n\n{replied_content}"
        elif replied_content and prompt:
            final_prompt = f"{prompt}\n\nMessage context:\n{replied_content}"
        elif prompt:
            final_prompt = prompt
        else:
            return await ctx.reply(
                f"{E('info')} **?ai usage:**\n"
                f"• `?ai <question>` — Ask anything\n"
                f"• Reply to a message + `?ai` — Explain it\n"
                f"• Reply + `?ai <text>` — Apply your prompt to it\n"
                f"• `?clearhistory` — Start fresh conversation",
                mention_author=False,
            )

        anim = AIAnimation(bot, ctx)
        await anim.start()
        try:
            result = await ask_ai(
                final_prompt,
                guild_id=(ctx.guild.id if ctx.guild else "dm"),
                channel_id=ctx.channel.id,
                author_name=str(ctx.author.display_name),
            )
            await anim.finish(result)
        except Exception as e:
            await anim.error(f"{E('error')} Something went wrong: `{e}`")

    @bot.command(name="clearhistory", aliases=["clearchat", "resetai"])
    async def clear_history_cmd(ctx: commands.Context) -> None:
        """Clear conversation history for this channel."""
        clear_history(ctx.channel.id)
        await ctx.reply(
            f"{E('success')} Conversation history cleared. Fresh start! {E('sparkle')}",
            mention_author=False,
        )
 
