from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Track data source choice and training status
    data_source_chosen = Column(Boolean, default=False, nullable=False)
    uses_own_data = Column(Boolean, default=False, nullable=False)  # True if user uploaded own file, False if using existing data.csv
    model_trained = Column(Boolean, default=False, nullable=False)
    uploaded_file_path = Column(String, nullable=True)  # Path to user's uploaded CSV file
    selected_model = Column(String, nullable=True)  # Selected model name (e.g., 'linear_regression', 'decision_tree', 'random_forest')
    
    # Relationship to consumption records
    consumption_records = relationship("ConsumptionRecord", back_populates="user", cascade="all, delete-orphan")
    # Relationship to chat history
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan", order_by="ChatHistory.created_at")
    # Relationship to password resets
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    # Relationship to model performances
    model_performances = relationship("ModelPerformance", back_populates="user", cascade="all, delete-orphan")

class ConsumptionRecord(Base):
    __tablename__ = "consumption_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hour = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    is_weekend = Column(Boolean, nullable=False)
    consumption = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="consumption_records")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="chat_history")

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reset_code = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="password_resets")

class ModelPerformance(Base):
    __tablename__ = "model_performances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_name = Column(String, nullable=False)  # e.g., 'linear_regression', 'decision_tree', 'random_forest'
    r2_score = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="model_performances")

class SignupOTP(Base):
    __tablename__ = "signup_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    otp_code = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)  # Store password hash temporarily
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

