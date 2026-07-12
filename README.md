# Rei-kun Discord Bot
[![Logo](https://raw.githubusercontent.com/Aj-Niplex/Rei-kun-Bot/main/Rei-kun-Logo.png)](https://github.com/Aj-Niplex/Rei-kun-Bot)

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.6.4+-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI%20Models-FF6B6B)](https://openrouter.ai/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> A powerful, AI-powered Discord bot with personality! Built by [@Aj-Niplex](https://github.com/Aj-Niplex) and trained on Rei-kun's persona.

> ⚠️ **Note**: Rei-kun is an imaginary personality and not real. This is a fictional character used as the bot's persona.

---

## ✨ Features

### 🧠 **Advanced AI System**
- **Multi-model support** with automatic fallback (DeepSeek, LLaMA 4, GPT, Gemini)
- **Identity preservation** system ensures Rei-kun personality across all models
- **Conversation memory** tracks last 10 messages per channel
- **Context-aware responses** with server memory integration
- **Smart intent detection** (version info, help, memory, general chat)

### 🎨 **Custom Emoji Management**
- Sync application emojis from Discord API
- Named emoji support (`[[purpleribbon]]`, `[[flower]]`, `[[gojo]]`)
- Emoji renaming and manual addition
- Paginated emoji browser with reaction navigation
- Debug tools for admins

### 📚 **Resource Hub (Study Platform)**
- Auto-DM study resources via code detection
- Interactive resource creation wizard
- Smart search by subject/chapter/topic
- Supports: Notes, Mind Maps, Audio, Quiz, Revision links
- Role-based permission system

### 🔧 **Developer Tools**
- **Code Doctor**: Auto-diagnose and patch Python files with interactive buttons
- **Hot-reload**: Reload commands without restarting the bot
- **Backup system**: Automatic timestamped backups before edits
- **Smoke testing**: Verify code changes work before committing

### 🛡️ **Security & Access Control**
- Terms of Service agreement system (👍/👎 reactions)
- Admin/Owner role system
- User blocking/unblocking
- DM permission gating
- Environment-based secrets (Git-safe)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+**
- **Discord Bot Token** ([Get one here](https://discord.com/developers/applications))
- **OpenRouter API Key** ([Get one here](https://openrouter.ai/keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aj-Niplex/Rei-kun-Bot.git
   cd Rei-kun-Bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN and OPENROUTER_API_KEY
   ```

4. **Run the bot**
   ```bash
   python app.py
   ```

5. **Initial setup in Discord**
   ```
   ?emojisync      # Sync custom emojis (admin only)
   ?help           # View all commands
   ```

---

## 📖 Commands

### 🤖 AI Commands
| Command | Description |
|---------|-------------|
| `?ai <prompt>` | Chat with Rei-kun AI |
| `?aihelp` | View AI system help and model list |

### 🎨 Emoji Commands
| Command | Description |
|---------|-------------|
| `?emojisync` | Sync emojis from Discord API (admin) |
| `?emojilist` | Browse all available emojis |
| `?emojidebug [name]` | Debug emoji details (admin) |
| `?emojiname <old> <new>` | Rename an emoji (admin) |
| `?emojiadd <name> <id> [anim]` | Manually add emoji (admin) |

### 📚 Resource Hub Commands
| Command | Description |
|---------|-------------|
| `?resource <code>` | Fetch study resource by code |
| `?resourceadd` | Add new resource (interactive wizard) |
| `?resourceedit` | Edit existing resource |
| `?ai-code-detection <query>` | Search resources by topic/subject |

### 🔧 Admin & Utility
| Command | Description |
|---------|-------------|
| `?doctor [target] [--flags]` | Code analysis & auto-patching |
| `?reload <module>` | Hot-reload commands |
| `?logs [lines]` | View bot event logs |
| `?botinfo` | Full bot status & stats |
| `?ping` | Check bot latency |
| `?botblock <user_id>` | Block a user |
| `?botunblock <user_id>` | Unblock a user |
| `?promote <@user>` | Grant admin permissions (owner) |
| `?demote <@user>` | Revoke admin permissions (owner) |
| `?admins` | List all bot admins |
| `?help` | Interactive help system |
| `?userid [@user]` | Get user ID |

---

## ⚙️ Configuration

All configuration is done via the `.env` file. **Never commit `.env` to Git!**

### Required Variables
```env
DISCORD_TOKEN=your_discord_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Optional Variables (with defaults)
```env
# Bot Identity
BOT_PREFIX=?
BOT_VERSION=v1.0.0
BOT_DEV=@your_username

# AI Models (comma-separated)
OPENROUTER_MODELS=openai/gpt-oss-20b:free,deepseek/deepseek-r1:free,openrouter/auto

# Access Control
BOT_ADMIN_USERS=username1,username2
BOT_ADMIN_USER_IDS=123456789,987654321
BOT_OWNER_USER_IDS=123456789

# Resource Hub
RESOURCE_TRIGGER_CHANNEL_ID=0  # Channel ID for auto-trigger
RESOURCE_NOTIFY_USER_ID=0      # User to notify on events
RESOURCE_ALLOWED_USER_IDS=     # Comma-separated user IDs
RESOURCE_ALLOWED_ROLE_IDS=     # Comma-separated role IDs
RESOURCE_ALLOW_ADMINISTRATOR=true
```

See [`.env.example`](.env.example) for full documentation.

---

## 📁 Project Structure

```
rei-kun-bot/
├── .env.example            # Template for .env
├── app.py                  # Main bot entry point
├── config.py               # Environment loader
├── requirements.txt        # Python dependencies
├── CHANGELOG.txt           # Full version history
├── README.md               # This file
│
├── commands/               # All bot commands (auto-loaded)
│   ├── ai.py               # AI chat
│   ├── emojisync.py        # Emoji system
│   ├── doctor.py           # Code doctor
│   ├── resourcehub.py      # Study resources
│   ├── reload.py           # Hot-reload
│   └── ...                 # 24 commands total
│
├── utils/                  # Helper modules
│   ├── ai.py               # AI call logic
│   ├── bot_emojis.py       # Emoji retrieval
│   ├── storage.py          # JSON storage
│   ├── tos.py              # ToS system
│   ├── conversation.py     # Chat history
│   └── ...                 # 19 utility modules
│
├── ai/                     # AI knowledge base
│   ├── system prompt.txt   # Bot personality
│   └── knowledge/
│       ├── emoji_catalog.json
│       ├── bot_help.txt
│       └── version_log_v1.txt
│
├── data/                   # Persistent storage (Git-ignored)
│   ├── server_memories.json
│   ├── blocked_users.json
│   ├── tos_agreements.json
│   ├── resources.json
│   └── resource_index.json
│
└── logs/                   # Event logs (Git-ignored)
    └── bot_events.log
```

---

## 🎭 Bot Personality

Rei-kun is **not** a generic chatbot! The bot:
- Is trained on **Rei-kun's persona** 
- Has a **friendly, helpful, slightly playful** tone
- Uses **custom emojis** in responses (🌸, 👑, ⚔️)
- Maintains **identity across all AI models** via identity seed system
- **Remembers context** from previous messages in the channel

The identity is preserved even when using models that typically override system prompts, thanks to our **identity seed** mechanism.

---

## 🔒 Security Best Practices

✅ **Always use `.env` for secrets** (never hardcode tokens)  
✅ **Set `.env` permissions**: `chmod 600 .env`  
✅ **Never commit `.env` to Git** (it's in `.gitignore`)  
✅ **Use `.env.example` as a template** for collaborators  
✅ **Regenerate tokens if exposed** immediately  
✅ **Review `.gitignore`** before pushing to GitHub  

---

## 📊 Stats

- **24** commands
- **19** utility modules
- **5** AI model fallback chain
- **4+** custom named emojis
- **5** JSON storage databases
- **Max 5 concurrent AI requests** (semaphore-limited)

---

## 🛠️ Development

### Adding a New Command

1. Create `commands/your_command.py`:
   ```python
   from discord.ext import commands

   async def setup(bot: commands.Bot):
       @bot.command(name="yourcommand")
       async def your_command(ctx: commands.Context):
           await ctx.send("Hello from your command!")
   ```

2. Reload without restarting:
   ```
   ?reload your_command
   ```

### Hot-Reload Everything
```
?reload *
```

### Debugging Tips
- Use `?logs 50` to view recent events
- Use `?doctor <file>` to diagnose code issues
- Check `logs/bot_events.log` for detailed logging
- Use `?emojidebug <name>` to debug emoji rendering

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---


---

## 🌸 Emoji Installation Guide

The bot uses a set of custom emojis to maintain Rei-kun's personality. To set them up:

1. **Download the Emoji Packs**: Get the `store-emojigg-pack.zip` and `purple-emojigg-pack.zip` from the project assets.
2. **Unzip the Files**: Extract all images to a local folder.
3. **Upload to Discord**: Upload these images to your Discord server as custom emojis.
4. **Match Names**: Ensure the emoji names in Discord match the `key` values in `knowledge/emoji_catalog.json` (e.g., upload `purpleribbon.gif` as "purpleribbon").

Once uploaded, the bot will automatically use these emojis in its responses! 👑

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Developer**: [@Aj-Niplex](https://github.com/Aj-Niplex)
- **Persona**: Rei-kun (Imaginary Personality)
- **Issues**: [GitHub Issues](https://github.com/Aj-Niplex/Rei-kun-Bot/issues)
- **Discord Server**: [Join here](#) _(add your server invite)_

---

## 🙏 Acknowledgments

- **Discord.py** - Amazing Discord API wrapper
- **OpenRouter** - Multi-model AI API
- **Rei-kun** - Fictional personality inspiration
- **Community** - For bug reports and feature requests

---

## 📝 Changelog

See [CHANGELOG.txt](CHANGELOG.txt) for full version history.

**Current Version**: v1.0.0  
**Release Date**: 2026-06-04

---

<div align="center">

Made with ❤️ by [@Aj-Niplex](https://github.com/Aj-Niplex)

**[⬆ Back to Top](#-rei-kun-discord-bot)**

</div>
