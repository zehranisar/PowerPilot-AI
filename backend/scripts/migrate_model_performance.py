"""
Migration script to add model_performances table and selected_model column
Run this script once to update the database schema
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.app.database import engine

def migrate_model_performance():
    """Add model_performances table and selected_model column"""
    with engine.begin() as conn:
        try:
            # Add selected_model column to users table
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='users' AND column_name='selected_model'
                    ) THEN
                        ALTER TABLE users ADD COLUMN selected_model VARCHAR;
                    END IF;
                END $$;
            """))
            
            # Create model_performances table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS model_performances (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    model_name VARCHAR NOT NULL,
                    r2_score FLOAT NOT NULL,
                    rmse FLOAT NOT NULL,
                    mae FLOAT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create index on user_id for faster queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_model_performances_user_id 
                ON model_performances(user_id);
            """))
            
            # Verify
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='selected_model'
            """))
            columns = [row[0] for row in result]
            
            table_check = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'model_performances'
                );
            """))
            table_exists = table_check.scalar()
            
            print("[SUCCESS] Migration completed successfully!")
            if columns:
                print("  Added column: selected_model to users table")
            if table_exists:
                print("  Created table: model_performances")
            
        except Exception as e:
            print(f"[ERROR] Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    print("Running database migration for model performance...")
    migrate_model_performance()
    print("Migration script finished.")

