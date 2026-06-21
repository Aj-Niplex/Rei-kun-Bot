"""
Seed emojis — only keep ones with VERIFIED working IDs.
purpleribbon and gojo seeds removed (wrong IDs).
Use ?emojiname 1000075079 gojo  to rename your actual gojo emoji.
Use ?emojiname 1000075050 purpleribbon  (or whichever number is the ribbon)
"""
SEED_EMOJIS: list[dict] = [
    {
        "key": "purplecrown",
        "discord_name": "purplecrown",
        "emoji_id": "1509805047247147008",
        "animated": False,
        "tag": "<:purplecrown:1509805047247147008>",
        "pack": "seed",
    },
    {
        "key": "flower",
        "discord_name": "flower",
        "emoji_id": "1509805044701073478",
        "animated": False,
        "tag": "<:flower:1509805044701073478>",
        "pack": "seed",
    },
]
