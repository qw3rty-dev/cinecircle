from fastapi import status,HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models import User
from src.security.password import hash_password,verify_password
from src.security.jwt_handler import create_token_access
from datetime import datetime,UTC

class AuthService:

    def register(self,
                username: str,
                email: str,
                password: str,
                db:Session):
        
        existing_username = db.scalar(select(User).where(User.username == username))
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="username already exists")
        
        existing_email = db.scalar(select(User).where(User.email == email))
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="email already exists")
        new_user = User(
            username = username,
            email = email,
            password_hash = hash_password(password)
            )
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="user already exists")
        return new_user


    def login(self,
              email: str,
              password: str,
              db: Session):
        user = db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password,user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid credentials")
        access_token = create_token_access(user.id)
        user.last_login = datetime.now(UTC)
        db.commit()
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        

    def change_password(self,
                        user: str,
                        current_password: str,
                        new_password: str,
                        db: Session):
        if not verify_password(current_password,user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect current password")
        user.password_hash = hash_password(new_password)
        db.commit()
        return {"message": "password changed successfully"}
