from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import verify_password, get_password_hash, create_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    from backend.app.auth import decode_access_token
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/signup/request-otp")
async def request_signup_otp(request: schemas.SignupOTPRequest, db: Session = Depends(get_db)):
    """Request OTP for signup - Step 1"""
    from datetime import datetime, timedelta
    from backend.app.email_service import generate_otp, send_signup_otp_email
    
    # Normalize email (lowercase and strip)
    normalized_email = request.email.strip().lower()
    
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Delete any existing OTP for this email
    db.query(models.SignupOTP).filter(
        models.SignupOTP.email == normalized_email
    ).delete()
    
    # Generate OTP (ensure it's a clean string)
    otp_code = str(generate_otp()).strip()
    hashed_password = get_password_hash(request.password)
    
    # Debug: Log what we're storing
    print(f"[OTP Request] Storing OTP for email: '{normalized_email}', OTP: '{otp_code}' (len: {len(otp_code)})")
    
    # Create OTP record (expires in 10 minutes) - use timezone-aware datetime
    from datetime import timezone
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    otp_record = models.SignupOTP(
        email=normalized_email,
        otp_code=otp_code,
        password_hash=hashed_password,
        expires_at=expires_at,
        verified=False
    )
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)
    
    # Verify what was actually stored
    stored = db.query(models.SignupOTP).filter(models.SignupOTP.id == otp_record.id).first()
    print(f"[OTP Request] Stored in DB - Email: '{stored.email}', OTP: '{stored.otp_code}' (type: {type(stored.otp_code)}, len: {len(str(stored.otp_code))})")
    
    # Send OTP email
    email_sent = send_signup_otp_email(request.email, otp_code)
    
    if not email_sent:
        db.delete(otp_record)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again."
        )
    
    return {
        "message": "Verification code sent to your email. Please check your inbox.",
        "email": normalized_email
    }

@router.post("/signup/verify-otp", response_model=schemas.Token)
async def verify_signup_otp(request: schemas.SignupOTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and complete signup - Step 2"""
    from datetime import datetime
    
    # Normalize email for lookup
    normalized_email = request.email.strip().lower()
    provided_otp = str(request.otp_code).strip()
    
    # Debug: Log what we're looking for
    print(f"[OTP Verification] Looking for email: '{normalized_email}', OTP: '{provided_otp}'")
    
    # Find OTP record - try both normalized and original email
    otp_record = db.query(models.SignupOTP).filter(
        models.SignupOTP.email == normalized_email,
        models.SignupOTP.verified == False
    ).order_by(models.SignupOTP.created_at.desc()).first()
    
    # If not found with normalized, try original email
    if not otp_record:
        otp_record = db.query(models.SignupOTP).filter(
            models.SignupOTP.email == request.email.strip(),
            models.SignupOTP.verified == False
        ).order_by(models.SignupOTP.created_at.desc()).first()
    
    if not otp_record:
        # Check if there are any OTPs for this email at all
        all_otps = db.query(models.SignupOTP).filter(
            models.SignupOTP.email.ilike(f"%{normalized_email}%")
        ).all()
        print(f"[OTP Verification] No unverified OTP found. Found {len(all_otps)} total OTP records for similar emails")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new code."
        )
    
    # Check if OTP expired
    from datetime import timezone
    now_utc = datetime.now(timezone.utc)
    expires_at = otp_record.expires_at
    
    # Handle timezone-aware comparison
    if expires_at.tzinfo is None:
        # If expires_at is naive, assume it's UTC
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    print(f"[OTP Verification] Current time: {now_utc}, Expires at: {expires_at}")
    
    if now_utc > expires_at:
        db.delete(otp_record)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )
    
    # Verify OTP - normalize both values
    # Remove all whitespace and convert to string
    stored_otp = ''.join(str(otp_record.otp_code).strip().split())
    provided_otp_normalized = ''.join(str(request.otp_code).strip().split())
    
    # Debug logging
    print(f"[OTP Verification] Email: '{normalized_email}'")
    print(f"[OTP Verification] Stored OTP: '{stored_otp}' (type: {type(otp_record.otp_code)}, len: {len(stored_otp)})")
    print(f"[OTP Verification] Provided OTP: '{provided_otp_normalized}' (type: {type(request.otp_code)}, len: {len(provided_otp_normalized)})")
    print(f"[OTP Verification] Raw stored (repr): {repr(otp_record.otp_code)}")
    print(f"[OTP Verification] Raw provided (repr): {repr(request.otp_code)}")
    print(f"[OTP Verification] Bytes stored: {bytes(str(otp_record.otp_code), 'utf-8')}")
    print(f"[OTP Verification] Bytes provided: {bytes(str(request.otp_code), 'utf-8')}")
    print(f"[OTP Verification] Match: {stored_otp == provided_otp_normalized}")
    
    # Compare normalized OTPs
    if stored_otp != provided_otp_normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please try again."
        )
    
    # Check if user already exists (double check)
    existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
    if existing_user:
        db.delete(otp_record)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = models.User(
        email=normalized_email,
        hashed_password=otp_record.password_hash
    )
    db.add(new_user)
    
    # Mark OTP as verified
    otp_record.verified = True
    
    db.commit()
    db.refresh(new_user)
    
    # Automatically load sample data from data.csv
    try:
        from pathlib import Path
        import pandas as pd
        
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        data_file = project_root / "data.csv"
        
        if data_file.exists():
            df = pd.read_csv(data_file)
            for _, row in df.iterrows():
                datetime_str = str(row.get('datetime', ''))
                try:
                    dt = pd.to_datetime(datetime_str)
                    hour = dt.hour
                except:
                    hour = 12
                
                temperature = float(row.get('temperature', 20))
                is_weekend = bool(int(row.get('is_weekend', 0)))
                consumption = float(row.get('consumption', 0))
                
                record = models.ConsumptionRecord(
                    user_id=new_user.id,
                    hour=hour,
                    temperature=temperature,
                    is_weekend=is_weekend,
                    consumption=consumption
                )
                db.add(record)
            db.commit()
    except Exception as e:
        # If data loading fails, continue anyway (user can load manually)
        db.rollback()
        print(f"Warning: Could not auto-load sample data: {str(e)}")
        db.commit()  # Commit the user creation even if data loading fails
    
    # Create access token
    access_token = create_access_token(data={"sub": normalized_email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password (OAuth2 form)"""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-json", response_model=schemas.Token)
async def login_json(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login with email and password (JSON)"""
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

