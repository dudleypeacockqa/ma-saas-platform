#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for production use
Run this script to generate a cryptographically secure random key
"""

import secrets
import string

def generate_secret_key(length=64):
    """Generate a cryptographically secure random secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Use secrets module for cryptographically strong random generation
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

if __name__ == "__main__":
    print("=" * 70)
    print("SECRET KEY GENERATOR FOR PRODUCTION")
    print("=" * 70)
    print()

    # Generate 32-char key for JWT
    jwt_key = generate_secret_key(32)
    print("JWT SECRET_KEY (32 chars):")
    print(jwt_key)
    print()

    # Generate 64-char key for general encryption
    encryption_key = generate_secret_key(64)
    print("ENCRYPTION KEY (64 chars):")
    print(encryption_key)
    print()

    print("=" * 70)
    print("Add to your Render environment variables:")
    print("=" * 70)
    print(f"SECRET_KEY={jwt_key}")
    print()
    print("⚠️  IMPORTANT: Keep these keys secure!")
    print("- Never commit to git")
    print("- Only set via Render dashboard environment variables")
    print("- Rotate periodically for enhanced security")
    print()
