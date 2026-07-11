"""
Migration script to add new columns to users table
Run this script once to update the database schema
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.app.database import engine

def migrate_user_table():
    """Add new columns to users table if they don't exist"""
    with engine.begin() as conn:  # Use begin() for automatic transaction management
        # Check if columns exist and add them if they don't
        try:
            # Add data_source_chosen column
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='users' AND column_name='data_source_chosen'
                    ) THEN
                        ALTER TABLE users ADD COLUMN data_source_chosen BOOLEAN NOT NULL DEFAULT FALSE;
                    END IF;
                END $$;
            """))
            
            # Add uses_own_data column
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='users' AND column_name='uses_own_data'
                    ) THEN
                        ALTER TABLE users ADD COLUMN uses_own_data BOOLEAN NOT NULL DEFAULT FALSE;
                    END IF;
                END $$;
            """))
            
            # Add model_trained column
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='users' AND column_name='model_trained'
                    ) THEN
                        ALTER TABLE users ADD COLUMN model_trained BOOLEAN NOT NULL DEFAULT FALSE;
                    END IF;
                END $$;
            """))
            
            # Add uploaded_file_path column
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='users' AND column_name='uploaded_file_path'
                    ) THEN
                        ALTER TABLE users ADD COLUMN uploaded_file_path VARCHAR;
                    END IF;
                END $$;
            """))
            
            # Verify columns were added
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' 
                AND column_name IN ('data_source_chosen', 'uses_own_data', 'model_trained', 'uploaded_file_path')
            """))
            columns = [row[0] for row in result]
            
            print("[SUCCESS] Migration completed successfully!")
            print(f"  Verified columns exist: {', '.join(columns)}")
            
        except Exception as e:
            print(f"[ERROR] Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    print("Running database migration...")
    migrate_user_table()
    print("Migration script finished.")

