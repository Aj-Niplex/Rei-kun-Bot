# 🎭 Bot Configuration Guide

Welcome! If you've downloaded this bot, here's what you **CAN** and **CANNOT** customize.

---

## ✅ **What You CAN Change**

### 1. **Bot Personality & Name**
Edit: `config/bot_identity.yaml`

You can customize:
- ✅ Bot name
- ✅ Personality traits (tone, humor, formality)
- ✅ Catchphrases
- ✅ Emoji usage preferences
- ✅ Response style

**Example:**
```yaml
bot_name: "YourBot"
personality:
  tone: "playful"
  traits:
    humor: 9
    sass: 8
```

### 2. **Bot Owners & Admins**
Edit: `.env`

You can set your own owners/admins:
```env
BOT_OWNER_USER_IDS=YOUR_DISCORD_ID_HERE
BOT_ADMIN_USER_IDS=YOUR_ADMIN_IDS_HERE
```

**Note:** These will be "Owner" or "Admin" roles, NOT "Founder".

### 3. **Your Discord Token & API Keys**
Edit: `.env`

```env
DISCORD_TOKEN=YOUR_BOT_TOKEN
OPENROUTER_API_KEY=YOUR_API_KEY
SMTP_EMAIL=YOUR_EMAIL@gmail.com
SMTP_PASSWORD=YOUR_APP_PASSWORD
```

---

## ❌ **What You CANNOT Change (Hardcoded)**

### 1. **Founder Rights** 🏛️
**File:** `core/ownership.py`

The **Founder** role is **PERMANENTLY LOCKED** to:
- Discord ID: `1489553674287054848` (@dora_aj)
- Email: `aj.jin.japan.2006@gmail.com`

**Why?**
- Error reports always go to the original creator
- Prevents ownership hijacking
- Ensures accountability

**What this means for you:**
- You can be an **Owner** (full bot control)
- But NOT a **Founder** (original creator rights)
- Error emails will ALWAYS go to the founder's inbox

### 2. **System Prompt Core Logic** 🧠
**File:** `core/system_prompt.py`

The core AI instructions are **LOCKED** and include:
- ✅ Permission system architecture
- ✅ Error handling workflow
- ✅ Safety filters
- ✅ Core capabilities

**You CAN'T edit these to prevent:**
- Breaking core functionality
- Bypassing safety systems
- Stealing error reports

### 3. **Error Reporting Email** 📧
**Hardcoded in:** `utils/email_sender.py`

All error reports go to:
```python
ERROR_REPORT_EMAIL = "aj.jin.japan.2006@gmail.com"  # LOCKED
```

**Even if you change `.env`, the hardcoded email takes priority.**

---

## 🛡️ **Permission Hierarchy**

```
🏛️ Founder (LOCKED)  → Original creator (@dora_aj)
   ↓
👑 Owner             → Can manage bot settings (set by you in .env)
   ↓
🛡️ Admin             → Can use admin commands
   ↓
👤 User              → Regular Discord members
```

---

## 📝 **Quick Setup for New Users**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rei-kun-bot.git
   cd rei-kun-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure YOUR credentials**
   - Copy `.env.example` to `.env`
   - Add YOUR Discord token
   - Add YOUR API keys
   - Set YOUR Discord ID as owner:
     ```env
     BOT_OWNER_USER_IDS=YOUR_DISCORD_ID
     ```

4. **Customize personality** (optional)
   - Edit `config/bot_identity.yaml`
   - Change bot name, tone, catchphrases, etc.

5. **Run the bot**
   ```bash
   python app.py
   ```

---

## ⚠️ **Important Notes**

### ✅ You're FREE to:
- Run this bot on your own servers
- Customize personality & behavior
- Add/remove commands
- Modify features

### ❌ You CANNOT:
- Claim to be the original creator
- Remove founder attribution
- Redirect error emails to yourself
- Bypass the permission system

---

## 🤝 **Credits**

**Original Creator:** @dora_aj (Discord ID: `1489553674287054848`)  
**Contact:** aj.jin.japan.2006@gmail.com

If you modify this bot significantly, please:
1. Keep the founder attribution in `core/ownership.py`
2. Create a fork with your own name
3. Give credit to the original project

---

## 📚 **Support**

- **Original Creator:** aj.jin.japan.2006@gmail.com
- **Issues:** Open a GitHub issue
- **Documentation:** Check `docs/` folder

---

**Enjoy your customized bot! 🎉**

Just remember: the founder's email is hardcoded for a reason—it keeps the ecosystem healthy and accountable.
