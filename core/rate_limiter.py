"""
🚦 RATE LIMITER - Prevent email spam abuse
Tracks email sends and enforces cooldowns to prevent:
- Spam loops (bot sending 1000s of error emails)
- Credential abuse (if .env leaks, attacker can't spam your Gmail)
"""

import time
from collections import deque
from datetime import datetime, timedelta

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RATE LIMIT CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Max emails per time window
MAX_EMAILS_PER_MINUTE = 5
MAX_EMAILS_PER_HOUR = 20
MAX_EMAILS_PER_DAY = 50

# Cooldown after hitting limits (seconds)
COOLDOWN_AFTER_BURST = 300  # 5 minutes after hitting per-minute limit
COOLDOWN_AFTER_HOURLY = 1800  # 30 minutes after hitting per-hour limit

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RATE LIMITER STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Track timestamps of recent email sends
email_history = deque(maxlen=MAX_EMAILS_PER_DAY)  # Circular buffer
last_cooldown_start = None

def record_email_send():
    """Record that an email was just sent."""
    email_history.append(time.time())

def get_email_count(window_seconds: int) -> int:
    """Count emails sent in the last N seconds."""
    now = time.time()
    cutoff = now - window_seconds
    return sum(1 for ts in email_history if ts >= cutoff)

def is_rate_limited() -> tuple[bool, str]:
    """
    Check if email sending should be blocked.
    
    Returns:
        (is_blocked: bool, reason: str)
    """
    global last_cooldown_start
    
    # Check cooldown period
    if last_cooldown_start:
        cooldown_elapsed = time.time() - last_cooldown_start
        if cooldown_elapsed < COOLDOWN_AFTER_BURST:
            remaining = int(COOLDOWN_AFTER_BURST - cooldown_elapsed)
            return True, f"🚦 Email cooldown active. {remaining}s remaining."
    
    # Check per-minute limit
    count_1min = get_email_count(60)
    if count_1min >= MAX_EMAILS_PER_MINUTE:
        last_cooldown_start = time.time()
        return True, f"🚦 Rate limit: {count_1min} emails in last minute (max {MAX_EMAILS_PER_MINUTE}). Cooling down for {COOLDOWN_AFTER_BURST}s."
    
    # Check per-hour limit
    count_1hour = get_email_count(3600)
    if count_1hour >= MAX_EMAILS_PER_HOUR:
        last_cooldown_start = time.time()
        return True, f"🚦 Rate limit: {count_1hour} emails in last hour (max {MAX_EMAILS_PER_HOUR}). Cooling down for {COOLDOWN_AFTER_HOURLY}s."
    
    # Check per-day limit
    count_1day = get_email_count(86400)
    if count_1day >= MAX_EMAILS_PER_DAY:
        return True, f"🚦 Rate limit: {count_1day} emails in last 24h (max {MAX_EMAILS_PER_DAY}). Try again tomorrow."
    
    return False, ""

def get_rate_limit_status() -> dict:
    """Get current rate limit stats (for debugging/monitoring)."""
    return {
        "emails_last_minute": get_email_count(60),
        "emails_last_hour": get_email_count(3600),
        "emails_last_day": get_email_count(86400),
        "limits": {
            "per_minute": MAX_EMAILS_PER_MINUTE,
            "per_hour": MAX_EMAILS_PER_HOUR,
            "per_day": MAX_EMAILS_PER_DAY
        },
        "cooldown_active": last_cooldown_start is not None and (time.time() - last_cooldown_start) < COOLDOWN_AFTER_BURST
    }
