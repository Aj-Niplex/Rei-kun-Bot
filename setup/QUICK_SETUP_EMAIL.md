# ⚡ Quick Email Setup (5 Minutes)

## Step 1: Generate Gmail App Password

1. Go to: **https://myaccount.google.com/apppasswords**
2. Sign in to `mind87353@gmail.com`
3. Click **"Select app"** → Choose **"Mail"**
4. Click **"Select device"** → Choose **"Other"** → Type: **"Rei-kun Bot"**
5. Click **"Generate"**
6. **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)

---

## Step 2: Update .env File

Open `/.env` and update these lines:

```env
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ERROR REPORTING & AI ERROR HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ERROR_HANDLER_ENABLED=true
ERROR_REPORT_EMAIL=mind87353@gmail.com

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=mind87353@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # ← PASTE YOUR APP PASSWORD HERE
```

**Replace `xxxx xxxx xxxx xxxx` with your actual App Password!**

---

## Step 3: Restart Bot

```bash
# The bot restarts automatically on .env changes
# Or manually restart:
!reload all
```

---

## Step 4: Test It

### Option A: Create Test Command
Add this to `/slash_commands.py` temporarily:

```python
@bot.tree.command(name="testerror", description="[OWNER] Test error handler")
async def testerror_slash(interaction: discord.Interaction):
    """Test error reporting."""
    if not _is_admin(interaction.user):
        return await interaction.response.send_message("Admin only", ephemeral=True)
    
    # Force an error
    raise ValueError("This is a test error for email reporting!")
```

Then run: `/testerror`

### Option B: Trigger Natural Error
Just use any broken command or API that's rate-limited.

---

## Step 5: Check Results

### In Discord:
```
⚠️ Something went wrong!

🤖 [AI explains the error]

📧 A detailed error report has been sent to the
owner. Please wait while they investigate and
fix the issue!
```

### In Your Gmail:
You'll receive a professional HTML email with:
- 🚨 Error type & message
- 👤 User who triggered it
- 📁 Source file & line number
- 📝 Full stack trace
- 🤖 AI diagnosis with fix suggestions

### In Console:
```
[ERROR_HANDLER] ✅ Email sent to mind87353@gmail.com
```

---

## ✅ That's It!

Now every command error automatically:
1. ✅ Sends you a detailed email
2. ✅ Includes AI diagnosis
3. ✅ Notifies the user you're aware
4. ✅ Logs to console

**No more users saying "it's broken" without context!**

---

## 🔧 Troubleshooting

### Email not sending?

**Check console output:**
```
[ERROR_HANDLER] ❌ Email failed: SMTP auth error
```

**Common issues:**

1. **Wrong password format:**
   - ❌ Don't use your regular Gmail password
   - ✅ Must use App Password from myaccount.google.com/apppasswords

2. **Spaces in password:**
   - ✅ Keep spaces: `xxxx xxxx xxxx xxxx`
   - ✅ Or remove them: `xxxxxxxxxxxxxxxx`
   - Both work!

3. **Gmail security:**
   - ✅ 2FA must be enabled on your Gmail
   - ✅ App Passwords only work with 2FA

4. **Firewall/Port blocked:**
   - Try port `465` instead of `587` in `.env`:
     ```env
     SMTP_PORT=465
     ```

---

## 📧 Alternative: Use SendGrid (No Gmail needed)

If Gmail isn't working or you want professional email:

1. Sign up: https://app.sendgrid.com/ (Free: 100 emails/day)
2. Generate API key
3. Update `.env`:
```env
ERROR_HANDLER_ENABLED=true
ERROR_REPORT_EMAIL=mind87353@gmail.com

# Instead of SMTP, use SendGrid:
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_EMAIL=noreply@rei-kun.bot  # From address (can be anything)
```

SendGrid bypasses SMTP entirely and is more reliable!

---

## 🎯 Done!

Your bot now has professional error reporting. Every error = instant email notification with AI diagnosis! ✨
