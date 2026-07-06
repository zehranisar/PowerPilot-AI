from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import auth, predict, chat, data, password_reset
from backend.app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Electricity Forecasting API",
    description="API for electricity consumption forecasting and analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(predict.router, prefix="/api/v1/predict", tags=["predictions"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(data.router, prefix="/api/v1/data", tags=["data"])
app.include_router(password_reset.router, prefix="/api/v1/auth", tags=["password-reset"])

@app.get("/")
async def root():
    return {"message": "Electricity Forecasting API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

