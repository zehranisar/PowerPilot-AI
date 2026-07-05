import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.cluster import KMeans
import joblib
import os
from pathlib import Path
from datetime import datetime

# Get project root directory
project_root = Path(__file__).resolve().parent.parent

def train_user_models(user_id: int, data_path: Path, db_session=None):
    """Train multiple models for a specific user on their data"""
    print(f"Training models for user {user_id} using data from: {data_path}")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found at {data_path}")
    
    # Load data
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records from {data_path}")
    
    # Generate features
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    df['is_weekend'] = df['datetime'].dt.dayofweek >= 5
    
    # Prepare features
    X = df[['hour', 'temperature', 'is_weekend']].values
    y = df['consumption'].values
    
    # Train StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Create user-specific models directory
    user_models_dir = project_root / "ml" / "models" / f"user_{user_id}"
    os.makedirs(user_models_dir, exist_ok=True)
    
    # Save scaler
    joblib.dump(scaler, user_models_dir / "scaler.joblib")
    
    # Train and evaluate multiple models (optimized for speed)
    # Reduced complexity for faster training while maintaining good accuracy
    models_to_train = {
        'linear_regression': LinearRegression(),
        'decision_tree': DecisionTreeRegressor(random_state=42, max_depth=8),
        'random_forest': RandomForestRegressor(n_estimators=30, random_state=42, max_depth=8, n_jobs=-1, max_samples=0.8),
        'knn': KNeighborsRegressor(n_neighbors=5, n_jobs=-1)
    }
    
    model_performances = {}
    total_models = len(models_to_train)
    
    for idx, (model_name, model) in enumerate(models_to_train.items(), 1):
        print(f"\nTraining {model_name} ({idx}/{total_models})...")
        
        # Train model
        if model_name == 'knn':
            model.fit(X_scaled, y)
            X_pred = X_scaled
        else:
            model.fit(X, y)
            X_pred = X
        
        # Make predictions
        y_pred = model.predict(X_pred)
        
        # Calculate metrics
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)
        
        # Save model
        joblib.dump(model, user_models_dir / f"{model_name}_model.joblib")
        
        model_performances[model_name] = {
            'r2_score': r2,
            'rmse': rmse,
            'mae': mae
        }
        
        print(f"  [OK] R² Score: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")
    
    # Train KMeans (for clustering)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(df[['consumption']].values)
    joblib.dump(kmeans, user_models_dir / "kmeans_model.joblib")
    
    print(f"\nAll models trained and saved successfully for user {user_id}!")
    
    # Save performance metrics to database if session provided
    if db_session:
        from backend.app import models
        
        # Delete old performance records for this user
        db_session.query(models.ModelPerformance).filter(
            models.ModelPerformance.user_id == user_id
        ).delete()
        
        # Save new performance records
        for model_name, metrics in model_performances.items():
            perf = models.ModelPerformance(
                user_id=user_id,
                model_name=model_name,
                r2_score=float(metrics['r2_score']),  # Convert numpy types to Python float
                rmse=float(metrics['rmse']),
                mae=float(metrics['mae']) if metrics['mae'] is not None else None
            )
            db_session.add(perf)
        
        # Set best model as selected (highest R²)
        best_model = max(model_performances.items(), key=lambda x: x[1]['r2_score'])[0]
        user = db_session.query(models.User).filter(models.User.id == user_id).first()
        if user:
            user.selected_model = best_model
        
        db_session.commit()
        print(f"Performance metrics saved to database. Best model: {best_model}")
    
    return model_performances

# Legacy function for training on default data.csv (for backward compatibility)
def train_default_models():
    """Train models on default data.csv file"""
    data_path = project_root / "data.csv"
    
    print(f"Loading data from: {data_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"data.csv not found at {data_path}. Please ensure data.csv is in the project root.")
    
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records from data.csv")
    
    # Generate features
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['hour'] = df['datetime'].dt.hour
    df['is_weekend'] = df['datetime'].dt.dayofweek >= 5
    
    # Prepare features
    X = df[['hour', 'temperature', 'is_weekend']].values
    y = df['consumption'].values
    
    # Train StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train multiple models
    models_to_train = {
        'linear_regression': LinearRegression(),
        'decision_tree': DecisionTreeRegressor(random_state=42, max_depth=10),
        'random_forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
        'knn': KNeighborsRegressor(n_neighbors=5)
    }
    
    # Create models directory
    os.makedirs("ml/models", exist_ok=True)
    
    # Save scaler
    joblib.dump(scaler, "ml/models/scaler.joblib")
    
    # Train and save models
    for model_name, model in models_to_train.items():
        if model_name == 'knn':
            model.fit(X_scaled, y)
        else:
            model.fit(X, y)
        joblib.dump(model, f"ml/models/{model_name}_model.joblib")
        print(f"{model_name} trained and saved")
    
    # Train KMeans
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(df[['consumption']].values)
    joblib.dump(kmeans, "ml/models/kmeans_model.joblib")
    
    print("All models trained and saved successfully!")

# If run directly, train default models
if __name__ == "__main__":
    train_default_models()

