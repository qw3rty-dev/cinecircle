from fastapi import Depends,APIRouter,status,HTTPException
from sqlalchemy.orm import Session
from src.db import get_db
from src.models import User

from .schemas import UserCreate,UserResponse,TokenResponse,ChangePassword,MessageResponse
from .service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
from src.security.jwt_handler import get_current_user
router = APIRouter(prefix="/auth",tags=["authentication"])


auth_service = AuthService()
@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(user:UserCreate,
             db:Session=Depends(get_db)):
    
    new_user = auth_service.register(
        username=user.username,
        email=user.email,
        password=user.password,
        db=db
    )
    return new_user

@router.post("/login",response_model=TokenResponse,status_code=status.HTTP_200_OK)
def login(formdata:OAuth2PasswordRequestForm=Depends(),
          db:Session=Depends(get_db)):
    
    token = auth_service.login(
        email= formdata.username,
        password=formdata.password,
        db=db
    )
    return token

@router.patch("/change_password",response_model=MessageResponse,status_code=status.HTTP_200_OK)
def change_password(password:ChangePassword,
             db:Session=Depends(get_db),
             user:User=Depends(get_current_user)):
    
    return auth_service.change_password(user=user,
                                         current_password=password.current_password,
                                         new_password=password.new_password,
                                         db=db
                                        )
