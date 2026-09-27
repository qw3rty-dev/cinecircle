from datetime import datetime,UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status,HTTPException
from sqlalchemy.exc import IntegrityError

from src.models import User
from src.security.password import hash_password,verify_password
from src.security.jwt_handler import create_token_access


class AuthService:

    async def register(self,
                username: str,
                email: str,
                password: str,
                is_private: bool,
                db: AsyncSession):

        username = username.strip().lower()
        email = email.strip().lower()

        existing_username = await db.scalar(select(User).where(User.username == username))
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="username already exists")
        
        existing_email = await db.scalar(select(User).where(User.email == email))
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="email already exists")
        
        new_user = User(
            username = username,
            email = email,
            password_hash = hash_password(password),
            is_private= is_private
            )
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="user already exists")
        return new_user


    async def login(self,
              email: str,
              password: str,
              db: AsyncSession):
        
        user = await db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password,user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid credentials")
       
        access_token = create_token_access(user.id)
        user.last_login = datetime.now(UTC)
        await db.commit()
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        

    async def change_password(self,
                        user: User,
                        current_password: str,
                        new_password: str,
                        db: AsyncSession):
        if not verify_password(current_password,user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect current password")
        user.password_hash = hash_password(new_password)
        await db.commit()
        return {"message": "Password changed successfully"}

    async def delete_account(self,
                       password: str,
                       db: AsyncSession,
                       current_user: User):
        
        if not verify_password(password,current_user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect password")
        await db.delete(current_user)
        await db.commit()
        return {"message":"Account_deleted"}