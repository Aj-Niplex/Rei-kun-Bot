# 🔒 QUICK START - SECURE YOUR GMAIL PASSWORD NOW

## ⚡ 3-STEP SETUP (Takes 2 minutes)

### Step 1: Encrypt Password
```bash
python setup_encryption.py
```

**Output:**
```
🔑 Loading master key...
✅ Master key ready

======================================================================
🔒 ENCRYPTED SMTP PASSWORD
======================================================================

Original: xetn papk zwri donh
Encrypted: ENC:gAAAAABnBxY3Q2b5...

📋 Copy this to .env line 94:
SMTP_PASSWORD=ENC:gAAAAABnBxY3Q2b5...
======================================================================
```

### Step 2: Update .env
```bash
nano .env
# Find line 94:
# OLD: SMTP_PASSWORD=xetn papk zwri donh
# NEW: SMTP_PASSWORD=ENC:gAAAAABnBxY3Q2b5...
# Save and exit (Ctrl+X, Y, Enter)
```

### Step 3: Test
```bash
# Bot should already be running
# In Discord, type: !testerror
# Check your Gmail - you should receive the error report
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] `core/.master.key` file exists (created by step 1)
- [ ] `.env` line 94 starts with `SMTP_PASSWORD=ENC:` (not plaintext)
- [ ] Bot starts without errors
- [ ] `!testerror` command sends email to your Gmail
- [ ] Second `!testerror` within 1 minute shows rate limit

---

## 🛡️ WHAT YOU GET

### Before Encryption:
```
.env: SMTP_PASSWORD=xetn papk zwri donh
      ↑ If this leaks → YOUR GMAIL IS COMPROMISED
```

### After Encryption:
```
.env: SMTP_PASSWORD=ENC:gAAAAABnBxY3Q2b5...
core/.master.key: (32-byte encryption key)
      ↑ BOTH files needed to decrypt
      ↑ If .env leaks alone → SAFE (just encrypted gibberish)
      ↑ Rate limits prevent spam (5/min, 20/hr, 50/day)
```

---

## 🚨 TROUBLESHOOTING

### "Bot won't start after encryption"
```bash
# Check if password starts with ENC:
cat .env | grep SMTP_PASSWORD

# If yes but bot still fails:
# Temporarily revert to plaintext to verify bot works
SMTP_PASSWORD=xetn papk zwri donh

# Then debug encryption separately
python setup_encryption.py
```

### "Email not sending"
```bash
# Check rate limits
python -c "from core.rate_limiter import get_rate_limit_status; print(get_rate_limit_status())"

# If cooldown active, wait 5 minutes
```

### "Lost master key"
```bash
# If core/.master.key is deleted, encryption is UNRECOVERABLE
# Solution: Get new Gmail app password and re-encrypt
rm core/.master.key
python setup_encryption.py  # Will generate new master key
# Update .env with NEW encrypted password
```

---

## 📚 FULL DOCUMENTATION

- **SECURITY_FEATURES.md** - Complete breakdown of all features
- **SECURITY_SETUP.md** - Detailed setup guide
- **core/security.py** - Encryption engine source code
- **core/rate_limiter.py** - Rate limiting source code

---

## 🎯 TL;DR

**One command to secure your Gmail:**
```bash
python setup_encryption.py && nano .env
# Copy the ENC:... output to line 94, save
```

**GGs bro! 🔥**
