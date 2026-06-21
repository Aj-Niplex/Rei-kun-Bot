
import asyncio
import random
import string
from typing import Dict, Any, List, Optional

import discord
from discord.ext import commands

from utils.bot_emojis import E

from utils.config_loader import (
    BOT_ADMIN_USERS,
    BOT_ADMIN_USER_IDS,
    BOT_OWNER_USER_IDS,
    BOT_DEV,
    RESOURCE_ALLOWED_USER_IDS,
    RESOURCE_ALLOWED_ROLE_IDS,
    RESOURCE_ALLOW_ADMINISTRATOR,
    RESOURCE_TRIGGER_CHANNEL_ID,
    RESOURCE_NOTIFY_USER_ID,
)
from utils.resource_store import (
    load_resources,
    save_resources,
    load_index,
    save_index,
    parse_code,
    build_code,
    normalize_text,
    extract_number,
    make_index_entry,
    is_code_message,
)

TEMPLATE_TEXT = """Paste this template and fill it.

Subject:
Chapter:
Video Title:
YouTube:
Topics:

Notes:
MindMap:
Audio:
Quiz:
Revision:
"""

DM_TEMPLATE = f"""╔══════════════════════════════════════╗
║          {E('flower')} Rei-Kun Assistant {E('flower')}          ║
╚══════════════════════════════════════╝

«👋 Kon'nichiwa {{user_name}}!
Your BoardReady study resources are ready. ✨»

━━━━━━━━━━━━━━━━━━━━━━

📚 CHAPTER RESOURCE HUB

━━━━━━━━━━━━━━━━━━━━━━

🎯 Chapter: "[Chapter Name]"

🎬 Video Lesson

«[Video Title]
🔗 [YouTube Link]»

📖 Topics Covered

«[Topics]»

━━━━━━━━━━━━━━━━━━━━━━

🎁 FREE STUDY RESOURCES

━━━━━━━━━━━━━━━━━━━━━━

📄 Notes
└ 🔗 [Google Drive Link]

🧠 Mind Map
└ 🔗 [Gamma/Drive Link]

🎧 Audio Summary
└ 🔗 [Audio Link]

📝 Quiz
└ 🔗 [Quiz Link]

🔁 Revision Sheet
└ 🔗 [Revision Link]

━━━━━━━━━━━━━━━━━━━━━━

{E('star')} SUPPORTER BENEFITS

━━━━━━━━━━━━━━━━━━━━━━

Unlock exclusive study tools and early-access resources.

📌 Eligibility

🔹 Support @boards-ready for at least 1 week

🔹 Stay active through:

«{E('heart')} Likes
💬 Comments
🔔 Community Engagement»

🔹 Follow server rules and maintain a positive presence

━━━━━━━━━━━━━━━━━━━━━━

🎓 REI-KUN CAN HELP WITH

━━━━━━━━━━━━━━━━━━━━━━

✅ Study Guidance
✅ Chapter Explanations
✅ Doubt Solving
✅ Exam Preparation
✅ Learning Resources
✅ Productivity Tips
✅ General Questions

━━━━━━━━━━━━━━━━━━━━━━
{E('flower')} Keep learning. Keep improving.
📚 BoardReady × Rei-Kun Assistant
━━━━━━━━━━━━━━━━━━━━━━
"""

FIELD_ORDER = [
    "subject",
    "chapter",
    "video_title",
    "youtube",
    "topics",
    "notes",
    "mindmap",
    "audio",
    "quiz",
    "revision",
]

FIELD_LABELS = {
    "subject": "Subject",
    "chapter": "Chapter",
    "video_title": "Video Title",
    "youtube": "YouTube",
    "topics": "Topics",
    "notes": "Notes",
    "mindmap": "MindMap",
    "audio": "Audio",
    "quiz": "Quiz",
    "revision": "Revision",
}

EDITABLE_FIELDS = FIELD_ORDER


def _rand_hash(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits + "#$=@"
    return "".join(random.choice(chars) for _ in range(length))


def _norm(v: str) -> str:
    return normalize_text(v)


def _is_allowed_member(member: discord.Member) -> bool:
    if not isinstance(member, discord.Member):
        return False

    resource_allowed_ids = {int(x) for x in RESOURCE_ALLOWED_USER_IDS if str(x).isdigit()}
    if member.id in resource_allowed_ids:
        return True

    if RESOURCE_ALLOW_ADMINISTRATOR and member.guild_permissions.administrator:
        return True

    role_ids = {r.id for r in getattr(member, "roles", [])}
    if role_ids.intersection({int(x) for x in RESOURCE_ALLOWED_ROLE_IDS if str(x).isdigit()}):
        return True

    if member.id in {int(x) for x in BOT_OWNER_USER_IDS if str(x).isdigit()}:
        return True

    if str(member.name).lower() in {x.lower() for x in BOT_ADMIN_USERS}:
        return True

    if str(member.id) in {str(x).strip() for x in BOT_ADMIN_USER_IDS}:
        return True

    return False


def _find_owner_candidate(bot: commands.Bot):
    if str(RESOURCE_NOTIFY_USER_ID).isdigit() and int(RESOURCE_NOTIFY_USER_ID) > 0:
        u = bot.get_user(int(RESOURCE_NOTIFY_USER_ID))
        if u:
            return u
    target = str(BOT_DEV or "").strip().lstrip("@").lower()
    if target:
        for user in bot.users:
            if str(user.name).lower() == target:
                return user
    return None


async def _notify_owner(bot: commands.Bot, text: str):
    user = _find_owner_candidate(bot)
    if user is None:
        return
    try:
        await user.send(text)
    except Exception:
        pass


async def _safe_delete(message: discord.Message):
    try:
        await message.delete()
    except Exception:
        pass


def _field_label_to_key(label: str) -> str | None:
    cleaned = _norm(label).replace(" ", "")
    mapping = {
        "subject": "subject",
        "chapter": "chapter",
        "videotitle": "video_title",
        "youtube": "youtube",
        "topics": "topics",
        "notes": "notes",
        "mindmap": "mindmap",
        "audio": "audio",
        "quiz": "quiz",
        "revision": "revision",
    }
    return mapping.get(cleaned)


def _parse_template(text: str) -> dict[str, Any | None]:
    lines = [line.rstrip() for line in text.splitlines()]
    data: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    def flush():
        nonlocal current_key, current_lines
        if current_key:
            data[current_key] = "\n".join(current_lines).strip()
        current_key = None
        current_lines = []

    for raw in lines:
        line = raw.strip()
        if not line:
            if current_key:
                current_lines.append("")
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            mapped = _field_label_to_key(key)
            if mapped:
                flush()
                current_key = mapped
                current_lines = [value.strip()] if value.strip() else []
                continue

        if current_key:
            current_lines.append(raw)

    flush()

    subject = data.get("subject", "").strip()
    chapter = data.get("chapter", "").strip()
    video_title = data.get("video_title", "").strip()
    if not subject or not chapter or not video_title:
        return None

    chapter_num = extract_number(chapter) or 1
    video_num = extract_number(video_title) or 1

    return {
        "subject": subject,
        "chapter": chapter,
        "chapter_num": chapter_num,
        "video_num": video_num,
        "video_title": video_title,
        "youtube": data.get("youtube", "").strip(),
        "topics": data.get("topics", "").strip(),
        "notes": data.get("notes", "").strip(),
        "mindmap": data.get("mindmap", "").strip(),
        "audio": data.get("audio", "").strip(),
        "quiz": data.get("quiz", "").strip(),
        "revision": data.get("revision", "").strip(),
    }


def _build_dm(record: dict[str, Any], user_name: str) -> str:
    return DM_TEMPLATE.format(
        user_name=user_name,
        chapter=record.get("chapter", "Unknown"),
        video_title=record.get("video_title", "Unknown"),
        youtube=record.get("youtube", "N/A"),
        topics=record.get("topics", "N/A"),
        notes=record.get("notes", "N/A"),
        mindmap=record.get("mindmap", "N/A"),
        audio=record.get("audio", "N/A"),
        quiz=record.get("quiz", "N/A"),
        revision=record.get("revision", "N/A"),
    )


def _chapter_search(subject: str | None, chapter: str | None) -> list[tuple[str, dict[str, Any]]]:
    resources = load_resources()
    out: list[tuple[str, dict[str, Any]]] = []
    subj = _norm(subject) if subject else None
    chap_num = extract_number(chapter) if chapter else None
    chap_text = _norm(chapter) if chapter else None

    for code, record in resources.items():
        if subj and _norm(record.get("subject", "")) != subj:
            continue
        rec_chapter = record.get("chapter", "")
        rec_chap_num = extract_number(rec_chapter)
        rec_chap_text = _norm(rec_chapter)
        if chapter:
            if chap_num is not None and rec_chap_num != chap_num:
                continue
            if chap_num is None and chap_text and chap_text not in rec_chap_text:
                continue
        out.append((code, record))
    return out


def _topic_search(query: str) -> list[tuple[str, dict[str, Any]]]:
    resources = load_resources()
    q = _norm(query)
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for code, record in resources.items():
        blob = " ".join(str(record.get(k, "")) for k in ["subject", "chapter", "video_title", "topics"]).lower()
        score = 0
        if q and q in blob:
            score += 3
        for token in q.split():
            if token and token in blob:
                score += 1
        if score:
            scored.append((score, code, record))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [(code, record) for _, code, record in scored]


def _format_matches(results: list[tuple[str, dict[str, Any]]]) -> str:
    if not results:
        return "No matching resources found."
    lines = [
        "Matched resources:",
        "",
    ]
    for code, record in results[:10]:
        lines.append(
            f"- {code} | {record.get('subject','')} | {record.get('chapter','')} | {record.get('video_title','')}"
        )
    lines.append("")
    lines.append("Watch the video first, then use the matching code to fetch the files.")
    return "\n".join(lines)


def _resource_summary(record: dict[str, Any]) -> str:
    return (
        f"Subject={record.get('subject','')} | "
        f"Chapter={record.get('chapter','')} | "
        f"Video={record.get('video_title','')}"
    )


def _create_code(record: dict[str, Any]) -> str:
    subject = "".join(ch for ch in str(record.get("subject", "XX")).upper() if ch.isalnum())[:12] or "XX"
    chapter_num = extract_number(record.get("chapter", 1)) or 1
    video_num = extract_number(record.get("video_title", 1)) or 1
    return build_code(subject, chapter_num, video_num, _rand_hash())


class ResourceHub(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if RESOURCE_TRIGGER_CHANNEL_ID and message.channel.id == int(RESOURCE_TRIGGER_CHANNEL_ID):
            raw = message.content.strip()
            if is_code_message(raw):
                parsed = parse_code(raw)
                if parsed:
                    resources = load_resources()
                    record = resources.get(parsed["code"])
                    if record:
                        try:
                            await message.author.send(_build_dm(record, message.author.name))
                        except discord.Forbidden:
                            await message.reply("I could not DM you. Please enable DMs from server members.")
                    else:
                        await _notify_owner(
                            self.bot,
                            f"⚠ Missing resource code\nUser: {message.author} ({message.author.id})\nCode: {parsed['code']}\nSummary: no stored record",
                        )
                        try:
                            await message.reply("No stored resource exists for that code.")
                        except Exception:
                            pass


    @commands.command(name="resource")
    async def resource(self, ctx: commands.Context, *, code: str):
        parsed = parse_code(code)
        if not parsed:
            return await ctx.reply("Invalid code format.", mention_author=False)

        resources = load_resources()
        record = resources.get(parsed["code"])
        if not record:
            await _notify_owner(
                self.bot,
                f"⚠ Missing resource lookup\nUser: {ctx.author} ({ctx.author.id})\nCode: {parsed['code']}\nSummary: user asked for a missing resource",
            )
            return await ctx.reply("No resource found for that code.", mention_author=False)

        try:
            await ctx.author.send(_build_dm(record, ctx.author.name))
            await ctx.reply("I sent the resource to your DMs.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("I could not DM you. Please enable DMs.", mention_author=False)

    @commands.command(name="resourceadd")
    async def resource_add(self, ctx: commands.Context):
        if not isinstance(ctx.author, discord.Member) or not _is_allowed_member(ctx.author):
            return await ctx.reply("You do not have permission to use this command.", mention_author=False)

        prompt = await ctx.reply(TEMPLATE_TEXT, mention_author=False)
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=300,
                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
            )
        except asyncio.TimeoutError:
            return await prompt.edit(content="Timed out waiting for the template.")

        await _safe_delete(msg)

        record = _parse_template(msg.content)
        if record is None:
            return await prompt.edit(content="Invalid template format.")

        code = _create_code(record)
        record["code"] = code

        resources = load_resources()
        resources[code] = record
        save_resources(resources)

        index = load_index()
        index[make_index_entry(record)] = code
        save_index(index)

        await prompt.edit(content=f"✅ Resource saved.\nCode: {code}")
        await _notify_owner(
            self.bot,
            f"✅ Resource added\nUser: {ctx.author} ({ctx.author.id})\nCode: {code}\nSummary: {_resource_summary(record)}",
        )

    @commands.command(name="resourceedit")
    async def resource_edit(self, ctx: commands.Context):
        if not isinstance(ctx.author, discord.Member) or not _is_allowed_member(ctx.author):
            return await ctx.reply("You do not have permission to edit resources.", mention_author=False)

        prompt = await ctx.reply("Which Subject and Chapter do you want to edit? Send it like: `PE 1`", mention_author=False)

        try:
            first = await self.bot.wait_for(
                "message",
                timeout=300,
                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
            )
        except asyncio.TimeoutError:
            return await prompt.edit(content="Timed out.")

        await _safe_delete(first)

        parts = first.content.strip().replace(",", " ").split()
        if len(parts) < 2:
            return await prompt.edit(content="Invalid format. Use: `SUBJECT CHAPTER`")

        subject = parts[0]
        chapter = " ".join(parts[1:])
        matches = _chapter_search(subject, chapter)

        if not matches:
            await prompt.edit(content="No stored data found for that subject/chapter.")
            await _notify_owner(
                self.bot,
                f"⚠ Missing resource during edit\nUser: {ctx.author} ({ctx.author.id})\nSummary: {subject} {chapter}",
            )
            return

        lines = ["Available parts:", ""]
        for i, (code, record) in enumerate(matches, start=1):
            lines.append(f"{i}. {code} | {record.get('video_title','')}")
        await prompt.edit(content="\n".join(lines))
        try:
            choose = await self.bot.wait_for(
                "message",
                timeout=300,
                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
            )
        except asyncio.TimeoutError:
            return await prompt.edit(content="Timed out.")

        await _safe_delete(choose)
        if not choose.content.isdigit():
            return await prompt.edit(content="Invalid part number.")

        idx = int(choose.content)
        if idx < 1 or idx > len(matches):
            return await prompt.edit(content="Invalid part number.")

        code, record = matches[idx - 1]
        current_text = [f"Editing `{code}`", "", "Current values:", ""]
        for key in EDITABLE_FIELDS:
            current_text.append(f"{FIELD_LABELS[key]}: {record.get(key, '')}")
        current_text += ["", "Send the updated template now."]

        await prompt.edit(content="\n".join(current_text))

        try:
            update_msg = await self.bot.wait_for(
                "message",
                timeout=300,
                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id,
            )
        except asyncio.TimeoutError:
            return await prompt.edit(content="Timed out.")

        await _safe_delete(update_msg)

        new_record = _parse_template(update_msg.content)
        if new_record is None:
            return await prompt.edit(content="Invalid updated template format.")

        new_record["code"] = code

        resources = load_resources()
        resources[code] = new_record
        save_resources(resources)

        index = load_index()
        index[make_index_entry(new_record)] = code
        save_index(index)

        await prompt.edit(content=f"✅ Resource updated.\nCode: {code}")
        await _notify_owner(
            self.bot,
            f"✅ Resource edited\nUser: {ctx.author} ({ctx.author.id})\nCode: {code}\nSummary: {_resource_summary(new_record)}",
        )

    @commands.command(name="ai-code-detection")
    async def ai_code_detection(self, ctx: commands.Context, *, query: str = ""):
        q = query.strip()
        if not q:
            return await ctx.reply("Send a subject, chapter, or topic to search.", mention_author=False)

        results = _topic_search(q)
        await ctx.reply(_format_matches(results), mention_author=False)


async def setup(bot):
    if bot.get_cog("ResourceHub"):
        await bot.remove_cog("ResourceHub")
    await bot.add_cog(ResourceHub(bot))
