from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from typing import Optional
import os
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ENV = os.environ.get("ENV", "development").lower()
_SECRET = os.environ.get("JWT_SECRET")

if not _SECRET:
    if ENV == "production":
        raise ValueError("JWT_SECRET is missing! Application cannot start in production without a secure JWT_SECRET.")
    else:
        _SECRET = secrets.token_hex(32)

SECRET_KEY = _SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
