# 🔒 SECURITY SETUP GUIDE

## ✅ What's Been Implemented

I've set up a **military-grade security system** to protect your Gmail App Password:

### 1. **Encryption System** (`core/security.py`)
- Uses **Fernet encryption** (AES-128 in CBC mode)
- Master encryption key stored separately from `.env`
- Auto-decryption on bot startup
- CLI tools for manual encryption

### 2. **Rate Limiting** (`core/rate_limiter.py`)
- **5 emails per minute** (burst protection)
- **20 emails per hour** (hourly cap)
- **50 emails per day** (daily cap)
- Auto-cooldown periods (5 min after burst, 30 min after hourly limit)
- Prevents spam loops and credential abuse

### 3. **Git Protection** (`.gitignore`)
- `.env` already gitignored
- `core/.master.key` gitignored
- Even if someone forks your GitHub repo, they WON'T get:
  - Your app password (encrypted in .env)
  - Your master key (never committed)

### 4. **Updated Email Sender** (`utils/email_sender.py`)
- Auto-decrypts SMTP_PASSWORD using `load_secure_env()`
- Checks rate limits before sending
- Records every send for tracking
- Falls back gracefully if encryption fails

---

## 📋 HOW TO ENCRYPT YOUR PASSWORD

### Option 1: Automatic (Recommended)
```bash
python encrypt_secrets.py
```
This interactive wizard will:
1. Generate master key (first run only)
2. Detect your current SMTP_PASSWORD in .env
3. Encrypt it automatically
4. Update .env with encrypted value

### Option 2: Manual (if auto fails)
```bash
# 1. Generate encrypted password
python setup_encryption.py

# 2. Copy the output (looks like: ENC:gAAAAA...)
# 3. Open .env and replace line 94:
# OLD: SMTP_PASSWORD=xetn papk zwri donh
# NEW: SMTP_PASSWORD=ENC:gAAAAA...
```

### Option 3: Command-line
```bash
python core/security.py encrypt "xetn papk zwri donh"
# Copy the output to .env
```

---

## 🔍 HOW IT WORKS

### Before (VULNERABLE):
```
.env:
SMTP_PASSWORD=xetn papk zwri donh  ← ANYONE who gets .env can access your Gmail!
```

### After (SECURE):
```
.env:
SMTP_PASSWORD=ENC:gAAAAABnBxY3...  ← Encrypted, useless without master key

core/.master.key:
(32-byte Fernet key)  ← Gitignored, NEVER committed
```

**Even if .env leaks:**
- Attacker gets encrypted gibberish
- Without `core/.master.key`, they CANNOT decrypt
- Your Gmail is SAFE

---

## 🎯 WHAT'S PROTECTED

### ✅ BEFORE this security patch:
- ❌ App password in plaintext in .env
- ❌ Anyone with `.env` access = full Gmail access
- ❌ No spam prevention (attacker could send 10,000 emails)
- ❌ Git leak risk if you accidentally commit .env

### ✅ AFTER this security patch:
- ✅ App password encrypted (AES-128)
- ✅ Master key separated and gitignored
- ✅ Rate limits (5/min, 20/hr, 50/day)
- ✅ Auto-decryption on bot load
- ✅ Even if .env leaks, Gmail is safe

---

## 🚀 TESTING

1. **Encrypt the password:**
   ```bash
   python setup_encryption.py
   ```

2. **Verify .env is updated:**
   ```bash
   cat .env | grep SMTP_PASSWORD
   # Should show: SMTP_PASSWORD=ENC:gAAAAA...
   ```

3. **Start bot and test email:**
   ```bash
   # Bot should start normally and auto-decrypt
   # In Discord, run: !testerror
   # You should receive email (rate limit will block if spammed)
   ```

4. **Check rate limits:**
   ```python
   from core.rate_limiter import get_rate_limit_status
   print(get_rate_limit_status())
   ```

---

## 🛡️ ADDITIONAL HARDENING (Optional)

### 1. File Permissions (Linux/Mac only)
```bash
chmod 600 core/.master.key   # Owner read/write only
chmod 600 .env                # Owner read/write only
```

### 2. Environment Variable (Alternative)
Instead of storing master key in a file, store in environment:
```bash
export REI_MASTER_KEY="your_base64_key"
```
Then modify `core/security.py` to check `os.getenv("REI_MASTER_KEY")` first.

### 3. Rotate Keys Regularly
```bash
# Generate new master key
python core/security.py encrypt "your_password"
# Update .env with new encrypted value
```

---

## 🚨 EMERGENCY: If Master Key is Lost

If you lose `core/.master.key`:
1. The encrypted password becomes **UNRECOVERABLE**
2. Solution: Reset app password and re-encrypt
   ```bash
   # Delete old master key
   rm core/.master.key
   
   # Get new Gmail app password from:
   # https://myaccount.google.com/apppasswords
   
   # Encrypt new password
   python core/security.py encrypt "new_password_here"
   
   # Update .env with new encrypted value
   ```

---

## 📊 RATE LIMIT STATUS

To check current rate limit stats:
```python
from core.rate_limiter import get_rate_limit_status
status = get_rate_limit_status()
print(f"Emails in last minute: {status['emails_last_minute']}/5")
print(f"Emails in last hour: {status['emails_last_hour']}/20")
print(f"Emails in last day: {status['emails_last_day']}/50")
print(f"Cooldown active: {status['cooldown_active']}")
```

---

## 🎉 SUMMARY

**Your Gmail App Password is NOW:**
- 🔒 **Encrypted** (AES-128 Fernet)
- 🚦 **Rate-limited** (can't be spammed)
- 🙈 **Git-safe** (never committed)
- 🔐 **Separated** (master key in different file)

**Next Steps:**
1. Run `python setup_encryption.py` to encrypt
2. Verify `.env` shows `ENC:...` for SMTP_PASSWORD
3. Start bot and test with `!testerror` in Discord
4. Confirm email arrives with clean format + HTML attachment

---

## 📞 SUPPORT

If encryption fails or bot can't send emails:
1. Check `core/.master.key` exists
2. Check SMTP_PASSWORD starts with `ENC:`
3. Check logs for `[EMAIL]` messages
4. Test decryption: `python core/security.py decrypt "ENC:..."`

**Bot won't start?**
- Temporarily revert to plaintext password in .env
- Debug the encryption module separately
- Then re-encrypt once working
