from fastapi import APIRouter,Depends,status
from .service import UserService
from src.db import get_db
from src.security.jwt_handler import get_current_user
from sqlalchemy.orm import Session
from src.models import User
from .schemas import UserPrivateProfile,UserPublicProfile,UserTitleCardResponse,FollowRequestResponse,MessageResponse,FollowListResponse,PrivacyPreference
from src.enums import Action
router = APIRouter(prefix="/users",tags=["users"])

user_service = UserService()



@router.post("/{user_id}/follow",response_model=MessageResponse)
def follow_user(user_id:int,
                db:Session=Depends(get_db),
                current_user:User=Depends(get_current_user)):
    return user_service.follow_user(user_id,db,current_user)

@router.get("/search",response_model=list[UserTitleCardResponse])
def search_users(query:str,
                 db:Session= Depends(get_db)):
    return user_service.search_user(query,db)


@router.get("/follow-requests",response_model=list[FollowRequestResponse])
def get_follow_requests(current_user:User=Depends(get_current_user)):
    return user_service.get_follow_request(current_user)

@router.get("/{user_id}/followers",response_model=list[FollowListResponse])
def show_follower_list(user_id:int,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
    return user_service.show_followers(user_id,db,current_user)

@router.get("/{user_id}/following",response_model=list[FollowListResponse])
def show_following_list(user_id:int,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
    return user_service.show_following(user_id,db,current_user)


@router.get("/{username}",response_model=UserPublicProfile|UserPrivateProfile)
def show_user_profile(username:str,
                      current_user:User=Depends(get_current_user),
                      db:Session= Depends(get_db)):
    return user_service.show_user_profile(username,current_user.username,db)

@router.patch("/follow-requests/{request_id}/{action}",response_model=MessageResponse)
def request_action(request_id:int,
                   action:Action,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
    return user_service.request_action(request_id,action,db,current_user)

@router.patch("/me/privacy")
def privacy_preferences(preference:PrivacyPreference,
                        db:Session=Depends(get_db),
                        current_user:User=Depends(get_current_user)):
    return user_service.privacy_preferences(preference.is_private,db,current_user)


@router.delete("/{user_id}/follow",status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user_or_unsend_request(user_id:int,
                db:Session=Depends(get_db),
                current_user:User=Depends(get_current_user)):
    return user_service.unfollow_user_or_unsend_request(user_id,db,current_user)