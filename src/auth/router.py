from fastapi import Depends,APIRouter,status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.db import get_db
from src.models import User
from .service import AuthService
from src.security.jwt_handler import get_current_user
from .schemas import UserCreate,UserResponse,TokenResponse,ChangePassword,MessageResponse,DeleteAccountRequest


router = APIRouter(prefix="/auth",tags=["authentication"])

auth_service = AuthService()

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register(user:UserCreate,
                   db:AsyncSession=Depends(get_db)):
    
    new_user = await auth_service.register(
        username=user.username,
        email=user.email,
        password=user.password,
        is_private=user.is_private,
        db=db
    )
    return new_user


@router.post("/login",response_model=TokenResponse,status_code=status.HTTP_200_OK)
async def login(formdata:OAuth2PasswordRequestForm=Depends(),
                db:AsyncSession=Depends(get_db)):
    
    token = await auth_service.login(
        email= formdata.username,
        password=formdata.password,
        db=db
    )
    return token


@router.patch("/change_password",response_model=MessageResponse,status_code=status.HTTP_200_OK)
async def change_password(password:ChangePassword,
                          db:AsyncSession=Depends(get_db),
                          current_user:User=Depends(get_current_user)):
    
    return await auth_service.change_password(user=current_user,
                                         current_password=password.current_password,
                                         new_password=password.new_password,
                                         db=db
                                        )

@router.delete("/delete-account",status_code=status.HTTP_200_OK,response_model=MessageResponse)
async def delete_account(data:DeleteAccountRequest,
                   db:AsyncSession=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
    return await auth_service.delete_account(data.password,db,current_user)