from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Auth schemas
class UserSignup(BaseModel):
    email: EmailStr
    password: str

class SignupOTPRequest(BaseModel):
    email: EmailStr
    password: str

class SignupOTPVerify(BaseModel):
    email: EmailStr
    otp_code: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Prediction schemas
class PredictionRequest(BaseModel):
    hour: int
    temperature: float
    is_weekend: bool

class PredictionResponse(BaseModel):
    prediction: float

class SummaryResponse(BaseModel):
    total_consumption: float
    avg_consumption: float
    peak_hour: Optional[int]
    lowest_hour: Optional[int]

class ClusterResponse(BaseModel):
    cluster_centers: list[float]
    cluster_counts: list[int]

# Consumption record schemas
class ConsumptionRecordCreate(BaseModel):
    hour: int
    temperature: float
    is_weekend: bool
    consumption: float

class ConsumptionRecordResponse(BaseModel):
    id: int
    hour: int
    temperature: float
    is_weekend: bool
    consumption: float
    created_at: datetime

    class Config:
        from_attributes = True

# Chat schemas
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    history_id: int

class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True

# Password reset schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyResetCodeRequest(BaseModel):
    email: EmailStr
    reset_code: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str

class ForgotPasswordResponse(BaseModel):
    message: str

class VerifyResetCodeResponse(BaseModel):
    valid: bool
    message: str

class ResetPasswordResponse(BaseModel):
    message: str

# Training schemas
class DataSourceChoice(BaseModel):
    use_existing: bool  # True to use data.csv, False to upload own file

class TrainingStatusResponse(BaseModel):
    data_source_chosen: bool
    model_trained: bool
    uses_own_data: bool

class TrainingResponse(BaseModel):
    message: str
    records_loaded: int

# Model comparison schemas
class ModelPerformanceResponse(BaseModel):
    model_name: str
    r2_score: float
    rmse: float
    mae: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ModelComparisonResponse(BaseModel):
    models: list[ModelPerformanceResponse]
    best_model: Optional[str] = None  # Model name with best R² score

class SelectModelRequest(BaseModel):
    model_name: str  # 'linear_regression', 'decision_tree', 'random_forest'

class SelectModelResponse(BaseModel):
    message: str
    selected_model: str

