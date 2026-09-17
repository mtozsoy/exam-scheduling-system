from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.api.deps import get_current_admin

router = APIRouter(tags=["users"], dependencies=[Depends(get_current_admin)])

@router.get("/users", response_model=List[UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.KullaniciID).offset(skip).limit(limit).all()
    return users

@router.post("/users", response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.KullaniciAdi == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        KullaniciAdi=user_in.username,
        SifreHash=hashed_password,
        Rol=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    db_user = db.query(User).filter(User.KullaniciID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_in.username:
        existing = db.query(User).filter(User.KullaniciAdi == user_in.username, User.KullaniciID != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        db_user.KullaniciAdi = user_in.username
    
    if user_in.role:
        db_user.Rol = user_in.role
        
    if user_in.password:
        db_user.SifreHash = get_password_hash(user_in.password)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    if current_user.KullaniciID == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
    db_user = db.query(User).filter(User.KullaniciID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(db_user)
    db.commit()
    return
