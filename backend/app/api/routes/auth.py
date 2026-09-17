from datetime import timedelta
import time
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.user import Token

router = APIRouter(tags=["auth"])

# Simple in-memory rate limiting dictionary for login brute-force protection
# Maps IP address -> list of failure timestamps
failed_login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME_SECONDS = 300  # 5 minutes

@router.post("/auth/login", response_model=Token)
def login(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Rate limiting check
    if client_ip in failed_login_attempts:
        # Filter attempts within the lockout window
        failed_login_attempts[client_ip] = [ts for ts in failed_login_attempts[client_ip] if now - ts < LOCKOUT_TIME_SECONDS]
        if len(failed_login_attempts[client_ip]) >= MAX_ATTEMPTS:
            raise HTTPException(
                status_code=429,
                detail="Too many failed login attempts. Please try again later."
            )
            
    user = db.query(User).filter(User.KullaniciAdi == form_data.username).first()
    if not user or not verify_password(form_data.password, user.SifreHash):
        # Record failed attempt
        if client_ip not in failed_login_attempts:
            failed_login_attempts[client_ip] = []
        failed_login_attempts[client_ip].append(now)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # On successful login, clear failed attempts for this IP
    if client_ip in failed_login_attempts:
        del failed_login_attempts[client_ip]
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.KullaniciID), "role": user.Rol}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.Rol,
        "username": user.KullaniciAdi
    }
