"""
Script to add sample consumption data to the database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app import models
import pandas as pd
import random

def add_sample_data(user_email: str = None):
    """Add sample consumption data from data.csv to a user's account"""
    db: Session = SessionLocal()
    
    try:
        # Get or create a user
        if user_email:
            user = db.query(models.User).filter(models.User.email == user_email).first()
            if not user:
                print(f"User with email {user_email} not found. Please create an account first.")
                return
        else:
            # Get first user or create a test user
            user = db.query(models.User).first()
            if not user:
                print("No users found. Please create an account first through the signup page.")
                return
        
        print(f"Adding sample data for user: {user.email}")
        
        # Load data.csv
        data_file = project_root / "data.csv"
        if not data_file.exists():
            print(f"Error: {data_file} not found")
            return
        
        df = pd.read_csv(data_file)
        print(f"Loaded {len(df)} records from data.csv")
        
        # Check if user already has records
        existing_count = db.query(models.ConsumptionRecord).filter(
            models.ConsumptionRecord.user_id == user.id
        ).count()
        
        if existing_count > 0:
            print(f"User already has {existing_count} records. Skipping...")
            response = input("Do you want to add more records? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Add records
        added = 0
        for _, row in df.iterrows():
            # Extract hour from datetime
            datetime_str = str(row.get('datetime', ''))
            try:
                from datetime import datetime
                dt = pd.to_datetime(datetime_str)
                hour = dt.hour
            except:
                hour = 12  # Default hour if parsing fails
            
            temperature = float(row.get('temperature', 20))
            is_weekend = bool(int(row.get('is_weekend', 0)))
            consumption = float(row.get('consumption', 0))
            
            # Check if record already exists
            existing = db.query(models.ConsumptionRecord).filter(
                models.ConsumptionRecord.user_id == user.id,
                models.ConsumptionRecord.hour == hour,
                models.ConsumptionRecord.temperature == temperature,
                models.ConsumptionRecord.is_weekend == is_weekend,
                models.ConsumptionRecord.consumption == consumption
            ).first()
            
            if not existing:
                record = models.ConsumptionRecord(
                    user_id=user.id,
                    hour=hour,
                    temperature=temperature,
                    is_weekend=is_weekend,
                    consumption=consumption
                )
                db.add(record)
                added += 1
        
        db.commit()
        print(f"Successfully added {added} new consumption records!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Add sample consumption data to database")
    parser.add_argument("--email", type=str, help="User email to add data for")
    args = parser.parse_args()
    
    add_sample_data(args.email)

