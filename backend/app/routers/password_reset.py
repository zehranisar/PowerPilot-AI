from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta, timezone
from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.email_service import send_reset_email, generate_reset_code
from backend.app.auth import get_password_hash

router = APIRouter()

@router.post("/forgot-password", response_model=schemas.ForgotPasswordResponse)
async def forgot_password(
    request: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Send password reset code to user's email"""
    # Normalize email (lowercase and trim)
    email_normalized = request.email.lower().strip()
    
    # Find user by email
    user = db.query(models.User).filter(models.User.email == email_normalized).first()
    
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return {"message": "If the email exists, a reset code has been sent."}
    
    # Generate reset code
    reset_code = generate_reset_code()
    
    # Delete any existing unused reset codes for this user
    db.query(models.PasswordReset).filter(
        and_(
            models.PasswordReset.user_id == user.id,
            models.PasswordReset.used.is_(False)
        )
    ).delete()
    db.commit()
    
    # Create password reset record
    password_reset = models.PasswordReset(
        user_id=user.id,
        reset_code=reset_code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        used=False
    )
    
    db.add(password_reset)
    db.commit()
    db.refresh(password_reset)
    
    # Send email
    email_sent = send_reset_email(user.email, reset_code)
    
    if not email_sent:
        db.delete(password_reset)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email. Please try again later."
        )
    
    return {"message": "If the email exists, a reset code has been sent."}

@router.post("/verify-reset-code", response_model=schemas.VerifyResetCodeResponse)
async def verify_reset_code(
    request: schemas.VerifyResetCodeRequest,
    db: Session = Depends(get_db)
):
    """Verify the reset code"""
    try:
        # Normalize email
        email_normalized = request.email.lower().strip() if request.email else ""
        
        if not email_normalized:
            return {"valid": False, "message": "Email is required."}
        
        # Find user by email
        user = db.query(models.User).filter(models.User.email == email_normalized).first()
        
        if not user:
            return {"valid": False, "message": "Invalid email or reset code."}
        
        # Clean and normalize the reset code (remove spaces, ensure it's 6 digits)
        reset_code_clean = str(request.reset_code).strip().replace(" ", "").replace("-", "") if request.reset_code else ""
        
        if not reset_code_clean or len(reset_code_clean) != 6 or not reset_code_clean.isdigit():
            return {"valid": False, "message": "Invalid reset code format. Please enter a 6-digit code."}
        
        # Find reset code
        password_reset = db.query(models.PasswordReset).filter(
            and_(
                models.PasswordReset.user_id == user.id,
                models.PasswordReset.reset_code == reset_code_clean,
                models.PasswordReset.used.is_(False)
            )
        ).first()
        
        if not password_reset:
            # Check if there are any reset codes for this user
            all_codes = db.query(models.PasswordReset).filter(
                and_(
                    models.PasswordReset.user_id == user.id,
                    models.PasswordReset.used.is_(False)
                )
            ).all()
            
            if not all_codes:
                return {"valid": False, "message": "No reset code found. Please request a new code."}
            
            # Check if expired
            now = datetime.now(timezone.utc)
            for code in all_codes:
                if code.expires_at < now:
                    return {"valid": False, "message": "Reset code has expired. Please request a new one."}
            
            return {"valid": False, "message": "Invalid reset code. Please check and try again."}
        
        # Check if expired
        now = datetime.now(timezone.utc)
        if password_reset.expires_at < now:
            return {"valid": False, "message": "Reset code has expired. Please request a new one."}
        
        return {"valid": True, "message": "Reset code is valid."}
    except Exception as e:
        import traceback
        print(f"Error in verify_reset_code: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while verifying the reset code: {str(e)}"
        )

@router.post("/reset-password", response_model=schemas.ResetPasswordResponse)
async def reset_password(
    request: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using reset code"""
    # Normalize email
    email_normalized = request.email.lower().strip()
    
    # Find user by email
    user = db.query(models.User).filter(models.User.email == email_normalized).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid email or reset code."
        )
    
    # Clean and normalize the reset code
    reset_code_clean = request.reset_code.strip().replace(" ", "").replace("-", "")
    
    if len(reset_code_clean) != 6 or not reset_code_clean.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code format. Please enter a 6-digit code."
        )
    
    # Find reset code
    password_reset = db.query(models.PasswordReset).filter(
        and_(
            models.PasswordReset.user_id == user.id,
            models.PasswordReset.reset_code == reset_code_clean,
            models.PasswordReset.used.is_(False)
        )
    ).first()
    
    if not password_reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or reset code."
        )
    
    # Check if expired
    now = datetime.now(timezone.utc)
    if password_reset.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset code has expired. Please request a new one."
        )
    
    # Validate password
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    
    # Mark reset code as used
    password_reset.used = True
    
    db.commit()
    
    return {"message": "Password has been reset successfully."}

