from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.routers.auth import get_current_user
from ml.utils import predict_consumption
import numpy as np

router = APIRouter()

@router.post("/knn", response_model=schemas.PredictionResponse)
async def predict_consumption_endpoint(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict electricity consumption using selected model"""
    try:
        # Get selected model for user, or use default
        model_name = current_user.selected_model if current_user.selected_model else None
        
        prediction = predict_consumption(
            hour=request.hour,
            temperature=request.temperature,
            is_weekend=request.is_weekend,
            user_id=current_user.id,
            model_name=model_name
        )
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/summary", response_model=schemas.SummaryResponse)
async def get_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary statistics of consumption data"""
    records = db.query(models.ConsumptionRecord).filter(
        models.ConsumptionRecord.user_id == current_user.id
    ).all()
    
    if not records:
        return {
            "total_consumption": 0.0,
            "avg_consumption": 0.0,
            "peak_hour": None,
            "lowest_hour": None
        }
    
    total_consumption = sum(r.consumption for r in records)
    avg_consumption = total_consumption / len(records)
    
    # Group by hour to find peak and lowest
    hour_consumption = {}
    for record in records:
        if record.hour not in hour_consumption:
            hour_consumption[record.hour] = []
        hour_consumption[record.hour].append(record.consumption)
    
    hour_avg = {h: sum(vals) / len(vals) for h, vals in hour_consumption.items()}
    
    peak_hour = max(hour_avg.items(), key=lambda x: x[1])[0] if hour_avg else None
    lowest_hour = min(hour_avg.items(), key=lambda x: x[1])[0] if hour_avg else None
    
    return {
        "total_consumption": total_consumption,
        "avg_consumption": avg_consumption,
        "peak_hour": peak_hour,
        "lowest_hour": lowest_hour
    }

@router.get("/clusters", response_model=schemas.ClusterResponse)
async def get_clusters(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consumption clusters using KMeans"""
    import joblib
    from pathlib import Path
    
    # Load KMeans model (user-specific if available)
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    models_dir = project_root / "ml" / "models"
    user_models_dir = models_dir / f"user_{current_user.id}"
    
    if user_models_dir.exists() and (user_models_dir / "kmeans_model.joblib").exists():
        kmeans_model = joblib.load(user_models_dir / "kmeans_model.joblib")
    else:
        kmeans_model = joblib.load(models_dir / "kmeans_model.joblib")
    
    records = db.query(models.ConsumptionRecord).filter(
        models.ConsumptionRecord.user_id == current_user.id
    ).all()
    
    if not records:
        return {
            "cluster_centers": [],
            "cluster_counts": []
        }
    
    # Get consumption values
    consumptions = np.array([[r.consumption] for r in records])
    
    # Predict clusters
    clusters = kmeans_model.predict(consumptions)
    
    # Get cluster centers and counts
    cluster_centers = kmeans_model.cluster_centers_.flatten().tolist()
    unique, counts = np.unique(clusters, return_counts=True)
    cluster_counts = [0] * len(cluster_centers)
    for idx, count in zip(unique, counts):
        cluster_counts[int(idx)] = int(count)
    
    return {
        "cluster_centers": cluster_centers,
        "cluster_counts": cluster_counts
    }

