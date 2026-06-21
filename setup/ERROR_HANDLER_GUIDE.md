# 🚨 AI-Powered Error Handler + Email Reporting

## Overview

Rei-kun now features a comprehensive AI-powered error handling system that:
1. **Catches ALL command errors** (both prefix `!command` and slash `/command`)
2. **Uses AI to diagnose** the issue with full context
3. **Formats an email report** with HTML styling
4. **Sends to your Gmail** automatically (`mind87353@gmail.com`)
5. **Notifies the user** that the issue has been reported to you

---

## 🔧 How It Works

### When ANY Command Breaks:

```
User runs: /ai test
↓
Error occurs: OpenRouterAPIError
↓
System captures:
  ✓ Error type & message
  ✓ Full stack trace
  ✓ User info (name, ID)
  ✓ Server & channel info
  ✓ Command used
  ✓ Source file that failed
↓
AI analyzes error:
  ✓ Root cause
  ✓ Why it happened
  ✓ How to fix it
  ✓ Code suggestion
↓
Email formatted as HTML:
  ✓ Professional layout
  ✓ Color-coded sections
  ✓ Full diagnosis
↓
Email sent to: mind87353@gmail.com
↓
User sees:
  "⚠️ Something went wrong!
   🤖 [AI Explanation]
   📧 A detailed error report has been sent
       to the owner. Please wait while they
       investigate and fix the issue!"
```

---

## 📧 Email Setup

### Option 1: Gmail (Recommended)

1. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in to your Google account
   - Select "Mail" and "Other" device
   - Generate password
   - Copy the 16-character password

2. **Update `.env`:**
```env
ERROR_HANDLER_ENABLED=true
ERROR_REPORT_EMAIL=mind87353@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Your App Password
```

### Option 2: Other SMTP (Outlook, Yahoo, etc.)

**Outlook:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_EMAIL=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**Yahoo:**
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_EMAIL=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

### Option 3: SendGrid API (Professional)

1. Get API key from: https://app.sendgrid.com/settings/api_keys
2. Update `.env`:
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_EMAIL=noreply@your-domain.com  # From address
```

---

## 📬 Email Report Format

You'll receive beautifully formatted HTML emails like:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 Rei-kun Error Report
An error occurred while processing a command
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Error Details
Type: OpenRouterAPIError
Message: HTTP 429: Rate limit exceeded

👤 User Information
User: username#1234 (ID: 1234567890)
Server: My Discord Server (ID: 9876543210)
Channel: #general
Command: /ai explain quantum physics

📁 Source Location
File: /home/container/commands/ai.py

📝 Stack Trace
Traceback (most recent call last):
  File "/commands/ai.py", line 45, in ai_command
    result = await ask_ai(prompt)
  ...
OpenRouterAPIError: HTTP 429: Rate limit exceeded

🤖 AI Diagnosis
The error occurred because the OpenRouter API
returned a 429 rate limit error. This means:

1. Too many requests in a short time
2. The free tier has daily limits
3. Multiple users hitting AI at once

FIX:
- Implement request queueing
- Add user cooldowns
- Consider upgrading OpenRouter plan

CODE SUGGESTION:
# Add to utils/concurrency.py
MAX_CONCURRENT = 5
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

async def ask_ai(...):
    async with semaphore:
        # API call here
        ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated error report from Rei-kun Bot
To disable error emails, set ERROR_HANDLER_ENABLED=false
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ⚙️ Configuration

### Enable/Disable Error Handler

```env
# Disable all error emails (errors still logged to console)
ERROR_HANDLER_ENABLED=false

# Enable error emails
ERROR_HANDLER_ENABLED=true
```

### Change Recipient Email

```env
# Send to different email
ERROR_REPORT_EMAIL=admin@example.com

# Send to multiple (NOT SUPPORTED YET - future feature)
# ERROR_REPORT_EMAIL=admin1@example.com,admin2@example.com
```

---

## 🧪 Testing

### Test the error handler:

1. **Create a test error:**
```python
# Add to any command file temporarily
@bot.command()
async def testerror(ctx):
    raise ValueError("This is a test error!")
```

2. **Run the command:**
```
!testerror
```

3. **Expected result:**
   - ✅ User sees AI explanation + "Report sent to owner"
   - ✅ Console shows: `[ERROR_HANDLER] ✅ Email sent to mind87353@gmail.com`
   - ✅ You receive HTML email with full details

4. **If email fails:**
   - Check console: `[ERROR_HANDLER] ❌ Email failed: [reason]`
   - Verify SMTP credentials in `.env`
   - Check Gmail "Less secure app access" if using Gmail
   - Ensure you're using App Password, not regular password

---

## 🔍 What Gets Captured

### Error Information:
- ✅ Error type (ValueError, KeyError, APIError, etc.)
- ✅ Error message
- ✅ Full stack trace with line numbers
- ✅ Source file path

### Context Information:
- ✅ User (username, ID, mention)
- ✅ Server (name, ID)
- ✅ Channel (name)
- ✅ Command used (exact text)
- ✅ Timestamp (IST timezone)

### AI Diagnosis:
- ✅ Root cause explanation
- ✅ Why it happened
- ✅ How to fix it
- ✅ Code suggestions (when applicable)

---

## 📊 Error Categories

### Errors that SKIP email reporting:
- `CommandNotFound` (user typos)
- `MissingRequiredArgument` (expected user errors)
- `BadArgument` (expected user errors)
- `MissingPermissions` (expected permission errors)

### Errors that TRIGGER email reporting:
- API errors (OpenRouter, Discord API)
- Database errors
- File I/O errors
- Logic errors (ValueError, KeyError, etc.)
- Unexpected exceptions
- Rate limits (429 errors)
- Auth failures (401, 403)

---

## 🛠️ Troubleshooting

### Email Not Sending?

**Check 1: SMTP credentials**
```bash
# Verify .env has correct values
grep SMTP .env
grep ERROR_REPORT .env
```

**Check 2: Gmail App Password**
- Must be 16 characters (with spaces: `xxxx xxxx xxxx xxxx`)
- NOT your regular Gmail password
- Generated from: https://myaccount.google.com/apppasswords

**Check 3: Console logs**
```bash
# Look for error handler messages
!logs
# Or check console output
```

**Check 4: Test email manually**
```python
# Add to slash_commands.py (owner command)
@bot.tree.command(name="testemail")
async def testemail(interaction):
    from utils.email_sender import send_error_email
    success, msg = await send_error_email(
        subject="Test Email from Rei-kun",
        body_html="<h1>Test</h1><p>If you see this, email works!</p>"
    )
    await interaction.response.send_message(f"Result: {msg}")
```

### AI Diagnosis Failing?

If AI fails, the email still sends but without AI diagnosis:
```
🤖 AI Diagnosis
All AI models failed.
Last error: [OpenRouter error]
```

**Fix:**
- Check `OPENROUTER_API_KEY` in `.env`
- Verify OpenRouter account has credits
- Check console for AI errors: `[AI] ❌ model_name | error`

---

## 🎯 Benefits

### For You (Owner):
1. ✅ **Get instant alerts** when users hit errors
2. ✅ **Full context** - no need to ask "what did you do?"
3. ✅ **AI explains** the error before you even read the code
4. ✅ **Fix suggestions** included in every report
5. ✅ **Professional format** - easy to scan and prioritize

### For Users:
1. ✅ **Immediate feedback** - they know you're aware
2. ✅ **AI explanation** - they understand what went wrong
3. ✅ **No need to screenshot/explain** - system captures everything
4. ✅ **Confidence** - "owner will fix this soon"

---

## 📝 Example User Experience

### Before (Without Error Handler):
```
User: /ai test
Bot: ❌ Error: HTTP 429: Rate limit exceeded

User: (confused, takes screenshot)
User: @owner why is it broken?
Owner: (hours later) What command did you use?
User: I forgot... something with AI
Owner: (frustrated) Can you try again?
User: (gives up, leaves server)
```

### After (With Error Handler):
```
User: /ai test
Bot: ⚠️ Something went wrong!

     🤖 The API is currently rate-limited due
     to high usage. This happens when many
     people use AI commands at once.

     📧 A detailed error report has been sent
     to the owner. Please wait while they
     investigate and fix the issue!

Owner: (instant email notification)
Owner: (reads AI diagnosis)
Owner: (fixes queue system)
Owner: (replies in 5 minutes)
User: (happy, stays)
```

---

## 🔐 Security

### Credentials Safety:
- ✅ SMTP password stored in `.env` (git-ignored)
- ✅ Never logged to console
- ✅ Never sent to users
- ✅ Only used for email sending

### Email Content:
- ✅ Only sent to `ERROR_REPORT_EMAIL` (you)
- ✅ Never includes user's personal data beyond Discord ID
- ✅ Never includes API keys or tokens
- ✅ Stack traces safe to share with you

---

## 🚀 Next Steps

1. **Set up Gmail App Password** (5 minutes)
2. **Update `.env` with SMTP credentials**
3. **Test with `!testerror` command**
4. **Verify email arrives**
5. **Remove test error command**
6. **Done!** ✨

Now every time a user hits an error, you'll get:
- 📧 Instant email notification
- 🤖 AI diagnosis
- 🔧 Fix suggestions
- 📊 Full context

**No more "it's broken" messages without context!**

---

## 📚 Files Modified

- `/app.py` - Added global error handlers (prefix + slash)
- `/utils/email_sender.py` - NEW: Email sending + HTML formatting
- `/utils/config_loader.py` - Added ERROR_HANDLER_ENABLED config
- `/.env` - Added SMTP + error handler settings

---

## ❓ Questions?

Check console output for detailed logs:
```
[ERROR_HANDLER] ✅ Email sent to mind87353@gmail.com
[ERROR_HANDLER] ❌ Email failed: SMTP auth error
[AI] ❌ deepseek/deepseek-r1:free | HTTP 429
```

Every error is logged with full context!
