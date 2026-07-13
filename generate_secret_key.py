"""
Generate a secure SECRET_KEY for JWT token signing
"""
import secrets

# Generate a secure random key
secret_key = secrets.token_urlsafe(32)

print("=" * 60)
print("SECRET_KEY Generator")
print("=" * 60)
print()
print("Generated SECRET_KEY:")
print(secret_key)
print()
print("Copy this to your .env file:")
print(f"SECRET_KEY={secret_key}")
print()
print("=" * 60)
print("IMPORTANT:")
print("- Keep this key secret!")
print("- Never commit it to version control")
print("- Use different keys for development and production")
print("=" * 60)

