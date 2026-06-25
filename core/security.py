"""
🔒 SECURITY MODULE - ENCRYPTION & KEY MANAGEMENT
Protects sensitive credentials (SMTP passwords, API keys) using Fernet encryption.

ARCHITECTURE:
- Master encryption key stored separately from .env
- Sensitive values encrypted in .env (format: ENC:base64cipher)
- Auto-decryption on load
- CLI tools for encrypting new secrets
"""

import os
import base64
from cryptography.fernet import Fernet
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MASTER KEY MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY_FILE = Path(__file__).parent / ".master.key"

def generate_master_key() -> bytes:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key()

def save_master_key(key: bytes):
    """Save master key to secure file (chmod 600)."""
    KEY_FILE.write_bytes(key)
    os.chmod(KEY_FILE, 0o600)  # Owner read/write only
    print(f"🔑 Master key saved to: {KEY_FILE}")

def load_master_key() -> bytes:
    """Load master key from file, or generate if missing."""
    if not KEY_FILE.exists():
        print("⚠️  Master key not found. Generating new one...")
        key = generate_master_key()
        save_master_key(key)
        return key
    
    key = KEY_FILE.read_bytes()
    return key

def get_cipher() -> Fernet:
    """Get Fernet cipher using master key."""
    key = load_master_key()
    return Fernet(key)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENCRYPTION / DECRYPTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext value using Fernet.
    Returns: ENC:base64cipher (prefix marks it as encrypted)
    """
    cipher = get_cipher()
    encrypted_bytes = cipher.encrypt(plaintext.encode())
    encrypted_b64 = base64.urlsafe_b64encode(encrypted_bytes).decode()
    return f"ENC:{encrypted_b64}"

def decrypt_value(encrypted: str) -> str:
    """
    Decrypt a Fernet-encrypted value.
    Input format: ENC:base64cipher
    Returns: plaintext
    """
    if not encrypted.startswith("ENC:"):
        # Not encrypted, return as-is (backward compatibility)
        return encrypted
    
    cipher = get_cipher()
    encrypted_b64 = encrypted[4:]  # Remove "ENC:" prefix
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_b64)
    plaintext_bytes = cipher.decrypt(encrypted_bytes)
    return plaintext_bytes.decode()

def is_encrypted(value: str) -> bool:
    """Check if a value is encrypted (starts with ENC:)."""
    return value.startswith("ENC:")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECURE ENV LOADER (AUTO-DECRYPT)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def load_secure_env(key: str, default: str = "") -> str:
    """
    Load environment variable and auto-decrypt if encrypted.
    
    Args:
        key: Environment variable name (e.g., "SMTP_PASSWORD")
        default: Default value if not found
    
    Returns:
        Decrypted plaintext value
    """
    value = os.getenv(key, default)
    if not value:
        return default
    
    if is_encrypted(value):
        try:
            return decrypt_value(value)
        except Exception as e:
            print(f"⚠️  Failed to decrypt {key}: {e}")
            print("   If you rotated the master key, re-encrypt all secrets!")
            return default
    
    # Not encrypted (backward compat or non-sensitive value)
    return value

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI TOOLS (for manual secret encryption)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("🔒 REI-KUN SECURITY - SECRET ENCRYPTOR")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("\n📖 Usage:")
        print("  python core/security.py encrypt <plaintext>")
        print("  python core/security.py decrypt <encrypted>")
        print("\n📝 Example:")
        print('  python core/security.py encrypt "xetn papk zwri donh"')
        print('  python core/security.py decrypt "ENC:gAAAAA..."')
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "encrypt":
        if len(sys.argv) < 3:
            print("❌ Error: Provide plaintext to encrypt")
            sys.exit(1)
        
        plaintext = sys.argv[2]
        encrypted = encrypt_value(plaintext)
        print("\n✅ Encrypted value (copy to .env):")
        print(f"   {encrypted}")
        print("\n📋 Full .env line example:")
        print(f"   SMTP_PASSWORD={encrypted}")
    
    elif command == "decrypt":
        if len(sys.argv) < 3:
            print("❌ Error: Provide encrypted value to decrypt")
            sys.exit(1)
        
        encrypted = sys.argv[2]
        try:
            plaintext = decrypt_value(encrypted)
            print("\n✅ Decrypted plaintext:")
            print(f"   {plaintext}")
        except Exception as e:
            print(f"\n❌ Decryption failed: {e}")
            sys.exit(1)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use: encrypt or decrypt")
        sys.exit(1)
