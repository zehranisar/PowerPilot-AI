from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import pandas as pd
import os
import shutil
from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.routers.auth import get_current_user

router = APIRouter()

# Directory for user uploaded files
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "user_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/load-sample-data")
async def load_sample_data(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Load sample data from data.csv for the current user"""
    try:
        # Get project root folder
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        data_file = project_root / "data.csv"

        # Check file exist
        if not data_file.exists():
            raise HTTPException(
                status_code=404,
                detail="data.csv file not found in project root folder"
            )

        # Remove existing records for this user
        existing = db.query(models.ConsumptionRecord).filter(
            models.ConsumptionRecord.user_id == current_user.id
        ).count()

        if existing > 0:
            db.query(models.ConsumptionRecord).filter(
                models.ConsumptionRecord.user_id == current_user.id
            ).delete()

        # Load CSV
        df = pd.read_csv(data_file)

        added = 0
        for _, row in df.iterrows():

            # Parse datetime → extract hour
            datetime_str = str(row.get("datetime", ""))

            try:
                dt = pd.to_datetime(datetime_str)
                hour = dt.hour
            except:
                hour = 12  # fallback

            temperature = float(row.get("temperature", 20))
            consumption = float(row.get("consumption", 0))

            # CSV might give True/False OR 0/1
            weekend_value = row.get("is_weekend", 0)

            # Convert to boolean safely
            if str(weekend_value).lower() in ["true", "1", "yes"]:
                is_weekend = True
            else:
                is_weekend = False

            # Create record
            record = models.ConsumptionRecord(
                user_id=current_user.id,
                hour=hour,
                temperature=temperature,
                consumption=consumption,
                is_weekend=is_weekend
            )

            db.add(record)
            added += 1

        db.commit()

        return {
            "message": f"Successfully loaded {added} records from data.csv",
            "records_added": added
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


@router.get("/has-data")
async def check_has_data(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has consumption data"""
    count = db.query(models.ConsumptionRecord).filter(
        models.ConsumptionRecord.user_id == current_user.id
    ).count()

    return {
        "has_data": count > 0,
        "record_count": count
    }

@router.get("/training-status", response_model=schemas.TrainingStatusResponse)
async def get_training_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's training status"""
    return {
        "data_source_chosen": current_user.data_source_chosen,
        "model_trained": current_user.model_trained,
        "uses_own_data": current_user.uses_own_data
    }

@router.post("/choose-data-source")
async def choose_data_source(
    choice: schemas.DataSourceChoice,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User chooses to use existing data or upload own file"""
    if current_user.data_source_chosen:
        raise HTTPException(
            status_code=400,
            detail="Data source has already been chosen"
        )
    
    current_user.data_source_chosen = True
    current_user.uses_own_data = not choice.use_existing
    
    if choice.use_existing:
        # Use existing data.csv
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        data_file = project_root / "data.csv"
        
        if not data_file.exists():
            raise HTTPException(
                status_code=404,
                detail="data.csv file not found in project root folder"
            )
        current_user.uploaded_file_path = str(data_file)
        db.commit()
        
        # Automatically train model if using existing data
        try:
            # Load data from file
            df = pd.read_csv(data_file)
            
            # Validate required columns
            required_columns = ['datetime', 'temperature', 'consumption']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"CSV file is missing required columns: {', '.join(missing_columns)}"
                )
            
            # Clear existing records for this user
            db.query(models.ConsumptionRecord).filter(
                models.ConsumptionRecord.user_id == current_user.id
            ).delete()
            
            # Process and save records (optimized batch insert)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['hour'] = df['datetime'].dt.hour
            df['is_weekend'] = df['datetime'].dt.dayofweek >= 5
            
            # Batch insert for better performance
            records = []
            for _, row in df.iterrows():
                record = models.ConsumptionRecord(
                    user_id=current_user.id,
                    hour=int(row['hour']),
                    temperature=float(row['temperature']),
                    consumption=float(row['consumption']),
                    is_weekend=bool(row['is_weekend'])
                )
                records.append(record)
            
            db.bulk_save_objects(records)
            added = len(records)
            
            # Train models on this user's data
            from ml.train_models import train_user_models
            
            train_user_models(
                user_id=current_user.id,
                data_path=data_file,
                db_session=db
            )
            
            current_user.model_trained = True
            db.commit()
            
            return {
                "message": "Data source chosen and model trained successfully",
                "records_loaded": added,
                "model_trained": True
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error training model: {str(e)}"
            )
    else:
        # If not using existing, user will upload file next
        db.commit()
        return {"message": "Data source choice saved. Please upload your CSV file."}

@router.post("/upload-data-file")
async def upload_data_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user's own CSV data file"""
    if not current_user.data_source_chosen:
        raise HTTPException(
            status_code=400,
            detail="Please choose data source first"
        )
    
    if current_user.uses_own_data == False:
        raise HTTPException(
            status_code=400,
            detail="You chose to use existing data, not upload your own file"
        )
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )
    
    # Save uploaded file
    user_upload_dir = UPLOAD_DIR / str(current_user.id)
    user_upload_dir.mkdir(exist_ok=True)
    
    file_path = user_upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    current_user.uploaded_file_path = str(file_path)
    db.commit()
    
    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }

@router.post("/train-model", response_model=schemas.TrainingResponse)
async def train_model(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train model on user's chosen data source"""
    if not current_user.data_source_chosen:
        raise HTTPException(
            status_code=400,
            detail="Please choose data source first"
        )
    
    if not current_user.uploaded_file_path:
        raise HTTPException(
            status_code=400,
            detail="No data file available. Please upload a file or use existing data."
        )
    
    data_file = Path(current_user.uploaded_file_path)
    if not data_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Data file not found"
        )
    
    try:
        # Load data from file
        df = pd.read_csv(data_file)
        
        # Validate required columns
        required_columns = ['datetime', 'temperature', 'consumption']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"CSV file is missing required columns: {', '.join(missing_columns)}"
            )
        
        # Clear existing records for this user
        db.query(models.ConsumptionRecord).filter(
            models.ConsumptionRecord.user_id == current_user.id
        ).delete()
        
        # Process and save records (optimized batch insert)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['hour'] = df['datetime'].dt.hour
        df['is_weekend'] = df['datetime'].dt.dayofweek >= 5
        
        # Batch insert for better performance
        records = []
        for _, row in df.iterrows():
            record = models.ConsumptionRecord(
                user_id=current_user.id,
                hour=int(row['hour']),
                temperature=float(row['temperature']),
                consumption=float(row['consumption']),
                is_weekend=bool(row['is_weekend'])
            )
            records.append(record)
        
        db.bulk_save_objects(records)
        added = len(records)
        
        # Train models on this user's data
        from ml.train_models import train_user_models
        
        train_user_models(
            user_id=current_user.id,
            data_path=data_file,
            db_session=db
        )
        
        current_user.model_trained = True
        db.commit()
        
        return {
            "message": "Model trained successfully",
            "records_loaded": added
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error training model: {str(e)}"
        )

@router.get("/model-comparison", response_model=schemas.ModelComparisonResponse)
async def get_model_comparison(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comparison of all trained models for the user"""
    if not current_user.model_trained:
        raise HTTPException(
            status_code=400,
            detail="Models not trained yet. Please train models first."
        )
    
    # Get all model performances for this user
    performances = db.query(models.ModelPerformance).filter(
        models.ModelPerformance.user_id == current_user.id
    ).order_by(models.ModelPerformance.r2_score.desc()).all()
    
    if not performances:
        raise HTTPException(
            status_code=404,
            detail="No model performance data found"
        )
    
    # Find best model (highest R²)
    best_model = max(performances, key=lambda p: p.r2_score).model_name
    
    return {
        "models": [
            {
                "model_name": p.model_name,
                "r2_score": p.r2_score,
                "rmse": p.rmse,
                "mae": p.mae,
                "created_at": p.created_at
            }
            for p in performances
        ],
        "best_model": best_model
    }

@router.post("/select-model", response_model=schemas.SelectModelResponse)
async def select_model(
    request: schemas.SelectModelRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Select which model to use for predictions"""
    if not current_user.model_trained:
        raise HTTPException(
            status_code=400,
            detail="Models not trained yet. Please train models first."
        )
    
    # Validate model exists for this user
    model_perf = db.query(models.ModelPerformance).filter(
        models.ModelPerformance.user_id == current_user.id,
        models.ModelPerformance.model_name == request.model_name
    ).first()
    
    if not model_perf:
        available_models = db.query(models.ModelPerformance.model_name).filter(
            models.ModelPerformance.user_id == current_user.id
        ).all()
        available_names = [m[0] for m in available_models]
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model_name}' not found. Available models: {', '.join(available_names)}"
        )
    
    # Update selected model
    current_user.selected_model = request.model_name
    db.commit()
    
    return {
        "message": f"Model '{request.model_name}' selected successfully",
        "selected_model": request.model_name
    }

@router.get("/selected-model")
async def get_selected_model(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get currently selected model"""
    if not current_user.model_trained:
        return {"selected_model": None, "message": "No model trained yet"}
    
    return {
        "selected_model": current_user.selected_model,
        "message": "Model selection retrieved successfully"
    }

@router.get("/model-comparison", response_model=schemas.ModelComparisonResponse)
async def get_model_comparison(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comparison of all trained models for the user"""
    if not current_user.model_trained:
        raise HTTPException(
            status_code=400,
            detail="Models not trained yet. Please train models first."
        )
    
    # Get all model performances for this user
    performances = db.query(models.ModelPerformance).filter(
        models.ModelPerformance.user_id == current_user.id
    ).order_by(models.ModelPerformance.r2_score.desc()).all()
    
    if not performances:
        raise HTTPException(
            status_code=404,
            detail="No model performance data found"
        )
    
    # Find best model (highest R²)
    best_model = max(performances, key=lambda p: p.r2_score).model_name
    
    return {
        "models": [
            {
                "model_name": p.model_name,
                "r2_score": p.r2_score,
                "rmse": p.rmse,
                "mae": p.mae,
                "created_at": p.created_at
            }
            for p in performances
        ],
        "best_model": best_model
    }

@router.post("/select-model", response_model=schemas.SelectModelResponse)
async def select_model(
    request: schemas.SelectModelRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Select which model to use for predictions"""
    if not current_user.model_trained:
        raise HTTPException(
            status_code=400,
            detail="Models not trained yet. Please train models first."
        )
    
    # Validate model exists for this user
    model_perf = db.query(models.ModelPerformance).filter(
        models.ModelPerformance.user_id == current_user.id,
        models.ModelPerformance.model_name == request.model_name
    ).first()
    
    if not model_perf:
        available_models = db.query(models.ModelPerformance.model_name).filter(
            models.ModelPerformance.user_id == current_user.id
        ).all()
        available_names = [m[0] for m in available_models]
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model_name}' not found. Available models: {', '.join(available_names)}"
        )
    
    # Update selected model
    current_user.selected_model = request.model_name
    db.commit()
    
    return {
        "message": f"Model '{request.model_name}' selected successfully",
        "selected_model": request.model_name
    }

@router.get("/selected-model")
async def get_selected_model(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get currently selected model"""
    if not current_user.model_trained:
        return {"selected_model": None, "message": "No model trained yet"}
    
    return {
        "selected_model": current_user.selected_model,
        "message": "Model selection retrieved successfully"
    }
