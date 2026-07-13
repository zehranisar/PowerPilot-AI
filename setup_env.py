"""
Setup script to create .env file with database configuration
"""
import os
from pathlib import Path

def create_env_file():
    """Create .env file with default configuration"""
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print(".env file already exists. Skipping...")
        return
    
    # Database configuration from user
    db_config = {
        'user': 'postgres',
        'password': '294bibah',
        'host': 'localhost',
        'port': '5432',
        'database': 'Electricity_forcasting'
    }
    
    # Generate secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    env_content = f"""# Database Configuration
DB_USER={db_config['user']}
DB_PASSWORD={db_config['password']}
DB_HOST={db_config['host']}
DB_PORT={db_config['port']}
DB_NAME={db_config['database']}

# JWT Secret Key (generated automatically)
SECRET_KEY={secret_key}

# Google Gemini API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print("\n⚠️  IMPORTANT:")
    print("1. Add your Google Gemini API key to GEMINI_API_KEY in .env")
    print("2. Get your API key from: https://makersuite.google.com/app/apikey")
    print("3. Never commit .env file to version control")

if __name__ == "__main__":
    create_env_file()

