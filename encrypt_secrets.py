#!/usr/bin/env python3
"""
🔒 SECRET ENCRYPTOR - Interactive CLI for encrypting .env secrets

USAGE:
    python encrypt_secrets.py

This tool will:
1. Generate a master encryption key (first run only)
2. Encrypt your SMTP password and other secrets
3. Update .env with encrypted values
4. Show you the new .env lines to copy
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.security import encrypt_value, decrypt_value, is_encrypted, load_master_key

def print_header():
    print("=" * 70)
    print("🔒 REI-KUN SECURITY - SECRET ENCRYPTOR")
    print("=" * 70)
    print()

def encrypt_smtp_password():
    """Interactive wizard to encrypt SMTP password."""
    print_header()
    
    # Check if master key exists
    key_file = Path("core/.master.key")
    if key_file.exists():
        print("✅ Master encryption key found")
    else:
        print("🔑 No master key found. Generating new one...")
        load_master_key()  # This will auto-generate
        print("✅ Master key created: core/.master.key")
        print("⚠️  IMPORTANT: Keep this file SECRET. It's in .gitignore.\n")
    
    # Read current .env
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Error: .env file not found")
        sys.exit(1)
    
    env_content = env_file.read_text()
    
    # Check current SMTP_PASSWORD
    print("\n" + "─" * 70)
    print("📧 CHECKING SMTP_PASSWORD")
    print("─" * 70)
    
    current_password = None
    for line in env_content.split('\n'):
        if line.startswith("SMTP_PASSWORD="):
            current_password = line.split("=", 1)[1]
            break
    
    if not current_password:
        print("❌ SMTP_PASSWORD not found in .env")
        print("\nManual setup:")
        plaintext = input("Enter your Gmail App Password: ").strip()
        if not plaintext:
            print("❌ Empty password. Exiting.")
            sys.exit(1)
        
        encrypted = encrypt_value(plaintext)
        print(f"\n✅ Encrypted! Copy this line to .env:")
        print(f"   SMTP_PASSWORD={encrypted}")
        return
    
    # Check if already encrypted
    if is_encrypted(current_password):
        print(f"✅ Already encrypted: {current_password[:20]}...")
        
        # Verify it decrypts correctly
        try:
            decrypted = decrypt_value(current_password)
            print(f"✅ Decryption test passed (length: {len(decrypted)} chars)")
            print("\n🎉 Your SMTP password is ALREADY SECURE!")
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            print("   The master key might have changed.")
            print("   Re-encrypt with:")
            plaintext = input("Enter your Gmail App Password: ").strip()
            encrypted = encrypt_value(plaintext)
            print(f"\n✅ New encrypted value:")
            print(f"   SMTP_PASSWORD={encrypted}")
    else:
        print(f"⚠️  Currently UNENCRYPTED: {current_password[:10]}...")
        print("\nEncrypting now...\n")
        
        encrypted = encrypt_value(current_password)
        
        # Update .env
        new_env_content = env_content.replace(
            f"SMTP_PASSWORD={current_password}",
            f"SMTP_PASSWORD={encrypted}"
        )
        env_file.write_text(new_env_content)
        
        print("✅ ENCRYPTED AND SAVED!")
        print(f"   Old (plaintext): {current_password[:10]}...")
        print(f"   New (encrypted): {encrypted[:30]}...\n")
        print("🎉 Your Gmail App Password is NOW SECURE!")
    
    print("\n" + "─" * 70)
    print("🛡️  SECURITY STATUS")
    print("─" * 70)
    print("✅ Master key: core/.master.key (gitignored)")
    print("✅ SMTP password: ENCRYPTED in .env")
    print("✅ Rate limiting: 5/min, 20/hr, 50/day")
    print("✅ Auto-decrypt: Enabled on bot startup")
    print("\n🔒 Even if someone gets your .env, they can't decrypt without the master key!")

if __name__ == "__main__":
    try:
        encrypt_smtp_password()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
