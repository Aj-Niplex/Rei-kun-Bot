# Discord AI Bot Architecture

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-Enabled-5865F2)](https://discordpy.readthedocs.io/)
[![AI](https://img.shields.io/badge/AI-Claude-orange)](https://www.anthropic.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Modular-brightgreen)](#technical-stack)

> **Bot Name:** Python-based Discord AI Assistant  
> **Framework:** Discord.py + Claude AI Integration  
> **Purpose:** Intelligent Discord bot with AI chat, commands, and resource management

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [/utils/ - Utility Modules](#utils---utility-modules)
- [/commands/ - Bot Commands](#commands---bot-commands)
- [/core/ - Core Bot Logic](#core---core-bot-logic)
- [/config/ - Configuration](#config---configuration)
- [/ai/ - AI Knowledge Base](#ai---ai-knowledge-base)
- [/data/ - Data Storage](#data---data-storage)
- [/logs/ - Log Files](#logs---log-files)
- [/setup/ - Setup Guides](#setup---setup-guides)
- [Key Features Summary](#key-features-summary)
- [Technical Stack](#technical-stack)
- [File Count Summary](#file-count-summary)
- [Critical Files for AI Reference](#critical-files-for-ai-reference)

---

## Overview

This repository is structured as a modular Discord bot with separate layers for:

- **Application startup**
- **Slash command handling**
- **Core security and rate limiting**
- **Reusable utility modules**
- **Persistent JSON-based storage**
- **AI prompt and knowledge management**
- **Documentation and deployment guides**

The result is a clean, maintainable architecture that supports AI chat, resource management, moderation, logging, and administrative workflows.

---

## Project Structure

```text
/
├── app.py
├── slash_commands.py
├── config.py
├── reload.py
├── .env
├── encrypt_secrets.py
├── README.md
├── CHANGELOG.txt
├── SECURITY_FEATURES.md
├── SECURITY_IMPLEMENTATION.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── utils/
├── commands/
├── core/
├── config/
├── ai/
├── data/
├── logs/
└── setup/
```

---

## /utils/ - Utility Modules

**Purpose:** Reusable helper functions and modules used across the bot.  
**Total Files:** 21

### AI & Intelligence
- `ai.py` - Claude AI API integration, chat completion requests, conversation context management, streaming responses.
- `code_doctor.py` - Code analysis and debugging assistant, error detection, fix suggestions, code quality checking.
- `conversation.py` - User conversation history management, context window handling, multi-turn tracking.

### Discord UI & Formatting
- `embeds.py` - Rich embed creation, predefined templates, styling utilities.
- `animations.py` - Loading effects, progress indicators, typing feedback.
- `message_utils.py` - Text truncation, sanitization, message splitting.

### Emoji System
- `bot_emojis.py` - Custom emoji management.
- `emoji_assets.py` - Emoji resources and categories.
- `emoji_parser.py` - Unicode and custom emoji parsing.
- `emoji_seed.py` - Default emoji seeding script.

### Data & Storage
- `storage.py` - JSON read/write persistence.
- `resource_store.py` - Resource storage, indexing, search.
- `config_loader.py` - YAML/JSON config parsing.

### Command & Catalog System
- `command_catalog.py` - Command metadata and descriptions for help systems.

### System & Utilities
- `concurrency.py` - Async task handling, scheduling, parallel utilities.
- `logger.py` - Logging output.
- `vps_logger.py` - VPS-specific logs and monitoring.
- `permissions.py` - Permission checks, role-based access control, admin verification.

### Communication
- `email_sender.py` - SMTP notifications, error alerts, HTML templates, multi-recipient support.

### User Management
- `tos.py` - Terms of Service acceptance tracking, consent management, onboarding.

- `__init__.py` - Package initializer.

---

## /commands/ - Bot Commands

**Purpose:** Discord slash command implementation.  
**Total Commands:** 24

### AI Commands
- `/ai` - AI chat functionality, Claude conversations, context-aware responses.
- `/aihelp` - AI usage help and tips.
- `/doctor` - Code debugging assistant, error analysis, code review.
- `/fix` - Quick fix command for common issues.

### Bot Information
- `/botinfo` - Bot information, version, uptime, stats, system metrics.
- `/help` - Interactive help menu, categories, descriptions.
- `/ping` - Latency check, WebSocket/API ping, performance monitoring.

### Conversation Management
- `/save` - Save conversation history.
- `/topic` - Set or view conversation topics.
- `/remember` - Store important points in memory.

### Resource Hub
- `/resourcehub` - Tutorials, guides, documentation storage, search, categorization, add/edit/delete resources.

### Admin Commands
- `/botblock` - Block users, spam prevention.
- `/botunblock` - Unblock users.
- `/logs` - View bot logs, error tracking, admin monitoring.
- `/tell` - Send direct messages / announcements.
- `/userid` - Fetch user ID.
- `/reload` - Hot reload commands without restarting.

### Emoji Management
- `/emojisync` - Sync server emojis into the catalog.

### AI Configuration
- `/prompt` - View the current AI system prompt.
- `/setprompt` - Customize the AI system prompt and bot behavior.

### Promotional & Misc
- `/admin_promo` - Admin promotional commands.
- `/quote` - Random quote generator.

### Testing & Debug
- `/test_error` - Error handling test command.

- `__init__.py` - Package initializer.

---

## /core/ - Core Bot Logic

**Purpose:** Core functionality and critical systems.  
**Total Files:** 4

### Security & Access Control
- `ownership.py` - Bot ownership verification, admin role checking, permission hierarchy.
- `security.py` - Security checks, input sanitization, injection prevention, malicious content detection.

### Rate Limiting
- `rate_limiter.py` - Command rate limiting, spam prevention, per-user tracking, cooldown management.

### AI System
- `system_prompt.py` - AI system prompt management, loading, caching, dynamic prompt generation, context injection.

---

## /config/ - Configuration

**Purpose:** Bot configuration files.  
**Total Files:** 1

- `bot_identity.yaml` - Bot identity, name, personality, behavior settings, response styles, tone.

---

## /ai/ - AI Knowledge Base

**Purpose:** AI system prompts and knowledge files.  
**Total Files:** 1 root + 5 in `knowledge/`

### Root
- `system_prompt.txt` - Main AI system prompt, bot behavior, personality definition, response guidelines.

### /ai/knowledge/
- `bot_help.txt` - Help information for AI reference.
- `command_catalog.json` - Command metadata.
- `emoji_catalog.json` - Detailed emoji catalog with IDs, names, categories.
- `emoji_catalog.txt` - Human-readable emoji reference.
- `version_log_v1.txt` - Version history and changelog for AI reference.

---

## /data/ - Data Storage

**Purpose:** Persistent JSON data storage.

### Structure
```text
/data/
├── blocked_users.json
├── tos.json
├── resources.json
├── resource_index.json
├── conversations/
└── guilds/
    └── [guild_id]/
        └── dm/
```

- `blocked_users.json` - Blocked users list
- `tos.json` - ToS acceptance records
- `resources.json` - Stored resources and tutorials
- `resource_index.json` - Resource search index
- `conversations/` - Per-user conversation histories
- `guilds/` - Server-specific data folders
- `dm/` - DM conversations per guild

---

## /logs/ - Log Files

**Purpose:** Bot activity and error logs.

### Structure
```text
/logs/
├── bot_logs.txt
├── vps.log
└── .gitkeep
```

- `bot_logs.txt` - Main bot activity logs
- `vps.log` - VPS-specific logs
- `.gitkeep` - Placeholder for git

---

## /setup/ - Setup Guides

**Purpose:** Setup and deployment documentation.  
**Total Files:** 12

### Setup Documentation
- `CONFIGURATION_GUIDE.md` - Complete bot configuration guide
- `QUICK_START_SECURITY.md` - Security quick start
- `SECURITY_SETUP.md` - Detailed security setup
- `GITHUB_READY.md` - GitHub deployment guide
- `MIGRATION_COMPLETE.md` - Migration completion notes

### Email System Setup
- `EMAIL_SYSTEM_UPGRADED.md` - Email system upgrade notes
- `EMAIL_TEST_COMPLETE.md` - Email testing completion guide
- `QUICK_SETUP_EMAIL.md` - Quick email setup guide

### Error Handling
- `ERROR_HANDLER_GUIDE.md` - Comprehensive error handling guide
- `AI_ERROR_HANDLER_SUMMARY.md` - AI-powered error handler summary

### Setup Scripts
- `setup_encryption.py` - Encryption setup script

---

## Key Features Summary

### AI Capabilities
- Claude AI integration
- Context-aware conversations
- Multi-turn chat memory
- Code analysis and debugging
- Custom system prompts
- Streaming responses

### Discord Features
- 24 slash commands
- Rich embeds and animations
- Custom emoji system
- Interactive help menu
- Direct messaging support
- Server-specific data storage

### Resource Management
- Tutorial and guide storage
- Search and categorization
- Add, edit, delete resources
- Knowledge base system

### Security & Moderation
- Rate limiting and anti-spam
- User blocking system
- Permission-based access control
- Input validation and sanitization
- Encryption for secrets
- Terms of Service tracking

### Administration
- Bot logs and monitoring
- Error email alerts via SMTP
- Hot reload without restart
- Admin commands: `/logs`, `/tell`, `/reload`
- User ID lookup
- Test error system

### Development Features
- Comprehensive documentation
- Setup and migration guides
- Version control ready
- Modular architecture
- Async/concurrent support
- Error handling system

---

## Technical Stack

| Component | Stack |
|---|---|
| Language | Python 3.x |
| Discord Library | discord.py |
| AI Provider | Anthropic Claude |
| Data Storage | JSON files |
| Email | SMTP |
| Architecture | Modular, command-based |
| Async Support | Yes (`asyncio`) |
| Hot Reload | Yes |
| Security | Rate limiting, input validation, encryption |

---

## File Count Summary

| Location | Count |
|---|---:|
| Root Level | 15 files |
| `/utils/` | 21 files |
| `/commands/` | 24 files |
| `/core/` | 4 files |
| `/config/` | 1 file |
| `/ai/` | 1 file |
| `/ai/knowledge/` | 5 files |
| `/setup/` | 12 files |
| `/data/` | 4 base files + dynamic user/guild data |
| `/logs/` | 3 files |

**Total:** ~90 files, excluding user-generated data and cache.

---

## Critical Files for AI Reference

1. `app.py` - Bot entry point
2. `slash_commands.py` - Command routing
3. `.env` - Secrets, never share
4. `/utils/ai.py` - AI integration
5. `/core/security.py` - Security layer
6. `/core/rate_limiter.py` - Spam prevention
7. `/ai/system_prompt.txt` - AI behavior
8. `/config/bot_identity.yaml` - Bot configuration
9. `/utils/storage.py` - Data persistence
10. `/commands/` - Command implementations

---

## Original Source Notes

- Generated for: AI Bot Architecture Understanding
- Purpose: Complete folder and file structure documentation
- Excludes: User-specific data, cache files, temporary files
- Date: 11 June 2026

---

## License

This document is formatted from the uploaded architecture file and can be reused alongside the project license.

[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

