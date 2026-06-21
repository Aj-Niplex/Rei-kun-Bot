# Python 3.13 | discord.py 2.6.4
import aiohttp, asyncio, json
from pathlib import Path
from discord.ext import commands
import discord
from utils.config_loader import DISCORD_TOKEN, EMOJI_CATALOG_FILE, BOT_ADMIN_USER_IDS, BOT_ADMIN_USERS
from utils.emoji_seed import SEED_EMOJIS   # original 4 named emojis


def _is_admin(u: discord.abc.User) -> bool:
    return (str(u.id) in BOT_ADMIN_USER_IDS
            or str(getattr(u,"name","")).lower() in {x.lower() for x in BOT_ADMIN_USERS})

def _load() -> list[dict]:
    p = Path(EMOJI_CATALOG_FILE)
    if not p.exists(): return []
    try: return json.loads(p.read_text(encoding="utf-8"))
    except: return []

def _save(data: list[dict]) -> None:
    p = Path(EMOJI_CATALOG_FILE)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def _tag(name: str, eid: str, anim: bool) -> str:
    if not name or not eid: return ""
    return f"<a:{name}:{eid}>" if anim else f"<:{name}:{eid}>"


class EmojiSync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="emojisync", aliases=["syncemoji"])
    async def emojisync(self, ctx: commands.Context) -> None:
        if not _is_admin(ctx.author):
            return await ctx.send("❌ No permission.")

        app_id = self.bot.application_id
        if not app_id:
            return await ctx.send("❌ application_id not available yet. Try again.")

        msg = await ctx.send("🔄 Syncing emojis from Discord API...")
        url = f"https://discord.com/api/v10/applications/{app_id}/emojis"
        headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}

        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers) as r:
                if r.status != 200:
                    body = await r.text()
                    return await msg.edit(content=f"❌ API {r.status}:\n```{body[:400]}```")
                raw = await r.json()

        # Handle {items: [...]} or direct list
        emojis: list = raw.get("items") or raw.get("emojis") or (raw if isinstance(raw, list) else [])

        # Start with seed emojis (the 4 named ones)
        catalog: list[dict] = list(SEED_EMOJIS)
        seed_ids = {e["emoji_id"] for e in SEED_EMOJIS}
        added = 0

        for e in emojis:
            if not isinstance(e, dict): continue
            eid  = str(e.get("id","")).strip()
            name = str(e.get("name","")).strip()
            anim = bool(e.get("animated", False))
            if not eid or not name or eid in seed_ids: continue
            t = _tag(name, eid, anim)
            catalog.append({
                "key": name.lower(), "discord_name": name,
                "emoji_id": eid, "animated": anim,
                "tag": t, "pack": "app",
            })
            added += 1

        _save(catalog)

        preview = " ".join(e["tag"] for e in catalog[:6] if e.get("tag"))
        embed = discord.Embed(title="✅ Emoji Sync Complete", color=0x9b59b6)
        embed.add_field(name="🌱 Seeds (named)",  value=str(len(SEED_EMOJIS)), inline=True)
        embed.add_field(name="📥 From Discord",   value=str(added),             inline=True)
        embed.add_field(name="📦 Total",          value=str(len(catalog)),      inline=True)
        if preview:
            embed.add_field(name="👁 Preview", value=preview, inline=False)
        embed.add_field(
            name="✨ Named emojis available",
            value="`purpleribbon` `purplecrown` `flower` `gojo`\n"
                  "Plus all numbered emojis from your app.",
            inline=False
        )
        embed.set_footer(text=f"App ID: {app_id}")
        await msg.edit(content="", embed=embed)

    @commands.command(name="emojilist", aliases=["emojis"])
    async def emojilist(self, ctx: commands.Context) -> None:
        catalog = _load()
        if not catalog:
            return await ctx.send("❌ Run `?emojisync` first.")

        page_size = 15
        pages = [catalog[i:i+page_size] for i in range(0, len(catalog), page_size)]

        def make_embed(entries: list[dict], pn: int, total: int) -> discord.Embed:
            embed = discord.Embed(
                title=f"🎨 Emoji Catalog — Page {pn}/{total}",
                color=0x9b59b6
            )
            lines = []
            for e in entries:
                t    = e.get("tag") or _tag(e.get("discord_name",""), e.get("emoji_id",""), e.get("animated",False))
                name = e.get("discord_name") or e.get("key","")
                anim = " *(anim)*" if e.get("animated") else ""
                lines.append(f"{t}  `:{name}:{anim}`")
            embed.description = f"**{len(catalog)}** total\n\n" + "\n".join(lines)
            embed.set_footer(text="◀▶ to browse")
            return embed

        if len(pages) == 1:
            return await ctx.send(embed=make_embed(pages[0], 1, 1))

        cur = 0
        msg = await ctx.send(embed=make_embed(pages[0], 1, len(pages)))
        for r in ("◀","▶"): await msg.add_reaction(r)

        def check(r, u):
            return u == ctx.author and r.message.id == msg.id and str(r.emoji) in ("◀","▶")

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reactions(); break
            if str(reaction.emoji) == "▶" and cur < len(pages) - 1:
                cur += 1
            elif str(reaction.emoji) == "◀" and cur > 0:
                cur -= 1
            await msg.edit(embed=make_embed(pages[cur], cur+1, len(pages)))
            try: await reaction.remove(user)
            except: pass

    @commands.command(name="emojidebug", aliases=["edebug"])
    async def emojidebug(self, ctx: commands.Context, *, name: str = "") -> None:
        if not _is_admin(ctx.author):
            return await ctx.send("❌ No permission.")
        catalog = _load()
        if not catalog:
            return await ctx.send("❌ Run `?emojisync` first.")
        if not name:
            anim = sum(1 for e in catalog if e.get("animated"))
            return await ctx.send(
                f"📊 **{len(catalog)}** emojis ({anim} animated, {len(catalog)-anim} static)\n"
                f"Use `?emojidebug <name>` to inspect one."
            )
        key = name.lower().strip()
        match = next(
            (e for e in catalog if e.get("key","").lower()==key or e.get("discord_name","").lower()==key),
            None
        )
        if not match:
            return await ctx.send(f"❌ `{name}` not found. Use `?emojilist` to see all names.")
        t = match.get("tag") or _tag(match.get("discord_name",""), match.get("emoji_id",""), match.get("animated",False))
        await ctx.send(
            f"**Result:** {t}\n"
            f"```Name:     {match.get('discord_name')}\n"
            f"ID:       {match.get('emoji_id')}\n"
            f"Animated: {match.get('animated')}\n"
            f"Tag:      {t}```"
        )

    @commands.command(name="emojiname")
    async def emojiname(self, ctx: commands.Context, number_name: str, new_name: str) -> None:
        """Rename a numbered emoji locally. ?emojiname 1000075060 bat"""
        if not _is_admin(ctx.author):
            return await ctx.send("❌ No permission.")
        catalog = _load()
        for e in catalog:
            if e.get("key","").lower() == number_name.lower() or e.get("discord_name","").lower() == number_name.lower():
                old_tag = e.get("tag","")
                e["key"] = new_name.lower()
                e["discord_name"] = new_name
                e["tag"] = _tag(new_name, e.get("emoji_id",""), e.get("animated",False))
                _save(catalog)
                return await ctx.send(
                    f"✅ Renamed `{number_name}` → `{new_name}`\n"
                    f"New tag: {e['tag']}"
                )
        await ctx.send(f"❌ `{number_name}` not found in catalog.")

    @commands.command(name="emojiadd")
    async def emojiadd(self, ctx: commands.Context, name: str, emoji_id: str, animated: str = "no") -> None:
        if not _is_admin(ctx.author): return await ctx.send("❌ No permission.")
        catalog = _load()
        if any(str(e.get("emoji_id")) == emoji_id for e in catalog):
            return await ctx.send(f"⚠️ ID `{emoji_id}` already in catalog.")
        anim = animated.lower() in ("yes","true","1","anim","animated")
        t = _tag(name, emoji_id, anim)
        catalog.append({"key":name.lower(),"discord_name":name,"emoji_id":emoji_id,"animated":anim,"tag":t,"pack":"manual"})
        _save(catalog)
        await ctx.send(f"✅ Added: {t}  Total: **{len(catalog)}**")


async def setup(bot: commands.Bot) -> None:
    if bot.get_cog("EmojiSync"):
        await bot.remove_cog("EmojiSync")
    await bot.add_cog(EmojiSync(bot))
