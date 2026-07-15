"""
Project Verification Script
Checks all critical components and files
"""
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[MISSING] {description}: {filepath} - MISSING!")
        return False

def verify_project():
    """Verify all project components"""
    print("=" * 60)
    print("PROJECT VERIFICATION")
    print("=" * 60)
    
    issues = []
    
    # Check backend files
    print("\n[Backend Files]")
    backend_files = [
        ("backend/app/main.py", "Main FastAPI app"),
        ("backend/app/database.py", "Database configuration"),
        ("backend/app/models.py", "Database models"),
        ("backend/app/schemas.py", "Pydantic schemas"),
        ("backend/app/auth.py", "Authentication utilities"),
        ("backend/app/routers/auth.py", "Auth router"),
        ("backend/app/routers/data.py", "Data router"),
        ("backend/app/routers/predict.py", "Predict router"),
        ("backend/app/routers/chat.py", "Chat router"),
        ("backend/scripts/migrate_user_table.py", "User table migration"),
        ("backend/scripts/migrate_model_performance.py", "Model performance migration"),
    ]
    
    for filepath, desc in backend_files:
        if not check_file_exists(filepath, desc):
            issues.append(f"Missing: {filepath}")
    
    # Check ML files
    print("\n[ML Files]")
    ml_files = [
        ("ml/train_models.py", "Model training script"),
        ("ml/utils.py", "ML utilities"),
        ("ml/models/.gitkeep", "Models directory"),
    ]
    
    for filepath, desc in ml_files:
        if not check_file_exists(filepath, desc):
            issues.append(f"Missing: {filepath}")
    
    # Check frontend files
    print("\n[Frontend Files]")
    frontend_files = [
        ("frontend/src/App.jsx", "React App component"),
        ("frontend/src/main.jsx", "React entry point"),
        ("frontend/src/pages/Dashboard.jsx", "Dashboard page"),
        ("frontend/src/pages/Login.jsx", "Login page"),
        ("frontend/src/pages/Signup.jsx", "Signup page"),
        ("frontend/src/pages/Predictions.jsx", "Predictions page"),
        ("frontend/src/pages/Chat.jsx", "Chat page"),
        ("frontend/src/components/Layout.jsx", "Layout component"),
        ("frontend/src/components/ModelComparison.jsx", "Model Comparison component"),
        ("frontend/src/contexts/AuthContext.jsx", "Auth context"),
        ("frontend/src/services/api.js", "API service"),
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/vite.config.js", "Vite configuration"),
    ]
    
    for filepath, desc in frontend_files:
        if not check_file_exists(filepath, desc):
            issues.append(f"Missing: {filepath}")
    
    # Check data files
    print("\n[Data Files]")
    data_files = [
        ("data.csv", "Sample data file"),
        ("requirements.txt", "Python dependencies"),
        (".env", "Environment variables (should exist)"),
    ]
    
    for filepath, desc in data_files:
        if not check_file_exists(filepath, desc):
            if filepath != ".env":
                issues.append(f"Missing: {filepath}")
            else:
                print(f"[WARNING] {desc}: {filepath} - Should be created by user")
    
    # Check directories
    print("\n[Required Directories]")
    directories = [
        ("user_uploads", "User uploads directory"),
        ("ml/models", "ML models directory"),
    ]
    
    for dirpath, desc in directories:
        if Path(dirpath).exists():
            print(f"[OK] {desc}: {dirpath}")
        else:
            print(f"[INFO] {desc}: {dirpath} - Will be created automatically")
    
    # Summary
    print("\n" + "=" * 60)
    if issues:
        print(f"[ERROR] Found {len(issues)} issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n[WARNING] Please fix these issues before running the project.")
    else:
        print("[SUCCESS] All critical files are present!")
        print("\n[Next Steps]")
        print("   1. Run database migrations:")
        print("      python backend/scripts/migrate_user_table.py")
        print("      python backend/scripts/migrate_model_performance.py")
        print("   2. Start backend: python run_server.py")
        print("   3. Start frontend: cd frontend && npm run dev")
    print("=" * 60)

if __name__ == "__main__":
    verify_project()

