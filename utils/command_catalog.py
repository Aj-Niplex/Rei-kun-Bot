# Central command catalog for help menus and slash command registration.
# Keep names and descriptions in one place so prefix/slash help stay in sync.

COMMAND_GROUPS = [
    (
        "AI",
        [
            ("ai", "/ai <text>", "Ask AI to explain, translate, summarize or chat"),
            ("aihelp", "/aihelp", "Show AI usage examples and tips"),
            ("clearhistory", "/clearhistory", "Reset AI conversation memory for this channel"),
        ],
    ),
    (
        "Utility",
        [
            ("help", "/help", "Open the full command menu"),
            ("ping", "/ping", "Show bot latency, CPU & RAM"),
            ("quote", "/quote", "Get a random inspirational quote"),
            ("topic", "/topic", "Get a fun conversation starter"),
        ],
    ),
    (
        "Memory",
        [
            ("save", "/save <message_id>", "Save a message to server memory"),
            ("remember", "/remember", "Show a random saved memory"),
        ],
    ),
    (
        "Text",
        [
            ("tell", "/tell <message_id>", "Explain or translate a message"),
            ("fix", "/fix <message_id>", "Rewrite a message softly and clearly"),
        ],
    ),
    (
        "Info",
        [
            ("botinfo", "/botinfo", "Show bot version, owner & purpose"),
            ("userid", "/userid <name>", "Find a member's user ID"),
            ("logs", "/logs <user_id>", "Search logs by User ID"),
        ],
    ),
    (
        "Admin",
        [
            ("botblock", "/botblock <user>", "Block a user from the bot"),
            ("botunblock", "/botunblock <user>", "Remove a user block"),
            ("promote", "/promote <user>", "Give user the Admin role"),
            ("demote", "/demote <user>", "Remove Admin role from user"),
            ("admins", "/admins", "List users with Admin role"),
        ],
    ),
    (
        "Dev",
        [
            ("reload", "/reload <module>", "Reload a command or utility module"),
            ("emojisync", "/emojisync", "Sync all app emojis from Discord"),
            ("emojilist", "/emojilist", "Browse available custom emojis"),
            ("doctor", "/doctor <file>", "Analyze code and propose fixes"),
            ("setprompt", "/setprompt <text>", "Update AI system prompt"),
            ("prompt", "/prompt", "View current AI system prompt"),
        ],
    ),
    (
        "Resources",
        [
            ("resource", "/resource <code>", "Get a study resource by code"),
            ("resourceadd", "/resourceadd", "Add a new study resource"),
            ("resourceedit", "/resourceedit <code>", "Edit an existing resource"),
            ("resourcelist", "/resourcelist", "List all resource codes"),
        ],
    ),
]
