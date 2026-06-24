#!/usr/bin/env python3
"""Quick setup to encrypt SMTP password"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.security import encrypt_value, load_master_key

# Generate/load master key
print("🔑 Loading master key...")
load_master_key()
print("✅ Master key ready\n")

# Encrypt the current password
plaintext = "GOOGLE_APP_KEY"
encrypted = encrypt_value(plaintext)

print("=" * 70)
print("🔒 ENCRYPTED SMTP PASSWORD")
print("=" * 70)
print(f"\nOriginal: {plaintext}")
print(f"Encrypted: {encrypted}")
print(f"\n📋 Copy this to .env line 94:")
print(f"SMTP_PASSWORD={encrypted}")
print("=" * 70)
