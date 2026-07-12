# 🌸 Rei-kun Discord Bot
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Platform-Discord-7289DA.svg)](https://discord.com)

> **A powerful, AI-driven Discord orchestrator designed for seamless human-AI interaction. Built by [@Aj-Niplex](https://github.com/Aj-Niplex) and trained on the distinct persona of Rei-kun.**

---

## 🌟 Core Capabilities

### 🧠 Advanced AI Intelligence
- **Multi-Model Orchestration:** Automatic fallback system between **DeepSeek, LLAMA 4, GPT, and Gemini**.
- **Persistent Persona:** Integrated identity system ensuring Rei-kun's unique personality remains consistent across all models.
- **Contextual Memory:** Advanced conversation tracking (last 10 messages) per channel.
- **Context-Aware Responses:** Server-integrated memory for smarter, environment-specific answers.

### 🛠️ Developer & Resource Hub
- **Auto-DM Study Resources:** Intelligent resource discovery via code detection.
- **Interactive Resource Creation:** Dynamic wizard for creating and sharing study materials.
- **Smart Search:** Topic-based resource retrieval using `/search/chapter/topic`.
- **Multi-Format Support:** Integrated handling of Notes, Mind Maps, Audio, Quiz, and Revision links.

### 🔐 Security & Administration
- **Role-Based Access Control (RBAC):** Tiered permission system for users and admins.
- **Admin Command Suite:** Full control over user blocking, unblocking, and role management.
- **Secure Secret Management:** Environment-based configuration using `.env` for maximum security.
- **Automated Backups:** Automatic time-stamped backups before edits.

---

## 🚀 Quick Start

### 📦 Prerequisites
- **Python 3.11+**
- **Discord Bot Token** ([Get one here](https://discord.com/developers/applications))
- **OpenRouter API Key** ([Get one here](https://openrouter.ai/keys))

### 🛠️ Installation
```bash
# 1. Clone the repository
git clone https://github.com/Aj-Niplex/Rei-kun-Bot.git
cd Rei-kun-Bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Environment
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN and OPENROUTER_API_KEY
```

### 🏃 Run the Bot
```bash
python app.py
```

---

## ⌨️ Command Palette

### 🤖 AI Commands
| Command | Description |
| :--- | :--- |
| `?ai <prompt>` | Chat with the Rei-kun AI |
| `?aihelp` | View AI system help and available models |

### 🎮 Emoji & Social
| Command | Description |
| :--- | :--- |
| `?emojisync` | Sync emojis from Discord API (Admin) |
| `?emojilist` | Browse all available emojis |
| `?emojidebug <name>` | Debug emoji details (Admin) |
| `?emojiname <old> <new>` | Rename an emoji (Admin) |
| `?emojiadd <name> <id> [anim]` | Manually add emoji (Admin) |

### 📚 Resource Hub
| Command | Description |
| :--- | :--- |
| `?resource <code>` | Fetch study resource by code |
| `?resourceadd` | Add new resource (Interactive Wizard) |
| `?resourceedit` | Edit existing resource |
| `?ai-code-detection <query>` | Search resources by topic/subject |

### 🛡️ Administration
| Command | Description |
| :--- | :--- |
| `?doctor [target] [--flags]` | Code analysis & auto-patching |
| `?reload <module>` | Hot-reload commands without restart |
| `?logs [lines]` | View recent bot event logs |
| `?botinfo` | View full bot status & stats |
| `?ping` | Check bot latency |
| `?botblock <user_id>` | Block a user |
| `?botunblock <user_id>` | Unblock a user |
| `?promote <user>` | Grant admin permissions (Owner) |
| `?demote <user>` | Revoke admin permissions (Owner) |
| `?admins` | List all bot admins |
| `?userid [@user]` | Get user ID |

---

## 📂 Project Architecture

```text
rei-kun-bot/
├── app.py                # Main entry point
├── config.py             # Environment loader
├── requirements.txt      # Dependencies
├── README.md             # Documentation
├── commands/             # All bot commands (auto-loaded)
├── ai.py                 # AI call logic
├── emojisync.py          # Emoji system
├── doctor.py             # Code doctor
├── resourcehub.py        # Study resources
├── reload.py             # Hot-reload logic
├── utils/                # Helper modules
└── ai/                   # AI knowledge base
```

---

## ⚖️ License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<div align="center">
  Made with ❤️ by [@Aj-Niplex](https://github.com/Aj-Niplex)
</div>
