import joblib
import numpy as np
import os
from pathlib import Path

# Get project root and models directory
project_root = Path(__file__).resolve().parent.parent
models_dir = project_root / "ml" / "models"

# Cache for loaded models per user
_model_cache = {}

def _load_user_models(user_id: int):
    """Load models for a specific user"""
    if user_id in _model_cache:
        return _model_cache[user_id]
    
    user_models_dir = models_dir / f"user_{user_id}"
    
    # Check if user-specific models exist
    if user_models_dir.exists() and (user_models_dir / "knn_model.joblib").exists():
        try:
            scaler = joblib.load(user_models_dir / "scaler.joblib")
            knn_model = joblib.load(user_models_dir / "knn_model.joblib")
            kmeans_model = joblib.load(user_models_dir / "kmeans_model.joblib")
        except FileNotFoundError:
            # Fallback to default models if user models incomplete
            scaler = joblib.load(models_dir / "scaler.joblib")
            knn_model = joblib.load(models_dir / "knn_model.joblib")
            kmeans_model = joblib.load(models_dir / "kmeans_model.joblib")
    else:
        # Fallback to default models
        scaler = joblib.load(models_dir / "scaler.joblib")
        knn_model = joblib.load(models_dir / "knn_model.joblib")
        kmeans_model = joblib.load(models_dir / "kmeans_model.joblib")
    
    _model_cache[user_id] = {
        'scaler': scaler,
        'knn_model': knn_model,
        'kmeans_model': kmeans_model
    }
    
    return _model_cache[user_id]

def predict_consumption(hour: int, temperature: float, is_weekend: bool, user_id: int = None, model_name: str = None) -> float:
    """Predict consumption using selected model"""
    if user_id is None:
        # Legacy: use default models
        scaler = joblib.load(models_dir / "scaler.joblib")
        if model_name is None:
            model_name = 'knn'  # Default fallback
        model = joblib.load(models_dir / f"{model_name}_model.joblib")
    else:
        user_models_dir = models_dir / f"user_{user_id}"
        
        if not user_models_dir.exists():
            # Fallback to default models
            scaler = joblib.load(models_dir / "scaler.joblib")
            if model_name is None:
                model_name = 'knn'
            model = joblib.load(models_dir / f"{model_name}_model.joblib")
        else:
            try:
                scaler = joblib.load(user_models_dir / "scaler.joblib")
                if model_name is None:
                    # Try to load selected model, fallback to best available
                    model_name = 'random_forest'  # Default to best performing
                model = joblib.load(user_models_dir / f"{model_name}_model.joblib")
            except FileNotFoundError:
                # Fallback to default models if user model not found
                scaler = joblib.load(models_dir / "scaler.joblib")
                if model_name is None:
                    model_name = 'knn'
                model = joblib.load(models_dir / f"{model_name}_model.joblib")
    
    features = np.array([[hour, temperature, 1 if is_weekend else 0]])
    
    # Use scaled features for KNN, raw features for others
    if model_name == 'knn' or (user_id is None and model_name is None):
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)
    else:
        prediction = model.predict(features)
    
    return float(prediction[0])

# Keep backward compatibility
def predict_knn(hour: int, temperature: float, is_weekend: bool, user_id: int = None) -> float:
    """Predict consumption using KNN model (backward compatibility)"""
    return predict_consumption(hour, temperature, is_weekend, user_id, 'knn')


def predict_cluster(consumption: float, user_id: int = None) -> int:
    """Predict cluster for given consumption value"""
    if user_id is None:
        # Legacy: use default models
        kmeans_model = joblib.load(models_dir / "kmeans_model.joblib")
    else:
        models = _load_user_models(user_id)
        kmeans_model = models['kmeans_model']
    
    consumption_array = np.array([[consumption]])
    cluster = kmeans_model.predict(consumption_array)
    return int(cluster[0])

