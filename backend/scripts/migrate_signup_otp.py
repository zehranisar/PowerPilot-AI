"""
Migration script to add signup_otps table
Run this script once to update the database schema
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.app.database import engine

def migrate_signup_otp():
    """Create signup_otps table"""
    with engine.begin() as conn:
        try:
            # Create signup_otps table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS signup_otps (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR NOT NULL,
                    otp_code VARCHAR NOT NULL,
                    password_hash VARCHAR NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    verified BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create index on email for faster queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_signup_otps_email 
                ON signup_otps(email);
            """))
            
            # Verify
            table_check = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'signup_otps'
                );
            """))
            table_exists = table_check.scalar()
            
            print("[SUCCESS] Migration completed successfully!")
            if table_exists:
                print("  Created table: signup_otps")
            
        except Exception as e:
            print(f"[ERROR] Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    print("Running database migration for signup OTP...")
    migrate_signup_otp()
    print("Migration script finished.")

