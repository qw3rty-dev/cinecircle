import os
from datetime import datetime,timedelta,UTC

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.models import User


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
if not ALGORITHM:
    raise ValueError("SECRET_KEY environment variable is not set")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_token_access(user_id:int):
    expire = datetime.now(UTC)+ timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(payload,
                      SECRET_KEY,
                      ALGORITHM)


def verify_token_access(token:str):
    try:
        payload = jwt.decode(token,
                        SECRET_KEY,
                        [ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid access token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized")
    user_id = int(sub)
    return user_id


async def get_current_user(token:str = Depends(oauth2_scheme),
                     db:AsyncSession=Depends(get_db)):
    current_user_id = verify_token_access(token)
    current_user = await db.scalar(select(User).where(User.id == current_user_id))
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid authentication credentials")
    return current_user


