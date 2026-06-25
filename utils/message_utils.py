


def chunk_text(text: str, limit: int = 1900) -> list[str]:
    """
    Split long text into Discord-safe chunks.
    """
    text = (text or "").strip()
    if not text:
        return [""]

    if limit < 100:
        limit = 100

    parts: list[str] = []
    for start in range(0, len(text), limit):
        parts.append(text[start:start + limit])

    return parts or [""]


async def send_discord_text(
    ctx,
    text: str,
    *,
    reply: bool = False,
    mention_author: bool = False,
    limit: int = 1900,
):
    parts = chunk_text(text, limit=limit)
    sent = None

    for index, part in enumerate(parts):
        if index == 0 and reply:
            try:
                sent = await ctx.reply(
                    part,
                    mention_author=mention_author,
                    fail_if_not_exists=False
                )
            except Exception:
                sent = await ctx.send(part)
        else:
            sent = await ctx.send(part)

    return sent