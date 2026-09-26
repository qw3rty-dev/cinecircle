from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,status,Query

from src.db import get_db
from src.models import User
from src.enums import Action, SortUsers, SortOrder,BulkAction
from .service import UserService
from src.security.jwt_handler import get_current_user
from .schemas import UserProfile,MessageResponse,PaginatedUserResponse,PrivacyPreference,PaginatedFollowRequestResponse


router = APIRouter(prefix="/users",tags=["users"])

user_service = UserService()

@router.post("/{user_id}/follow",response_model=MessageResponse)
def follow_user(user_id:int,
                db:Session=Depends(get_db),
                current_user:User=Depends(get_current_user)):
    return user_service.follow_user(user_id,db,current_user)


@router.get("/search",response_model=PaginatedUserResponse)
def search_users(
                search:str,
                limit:int = Query(default=20,ge=1,le=100),
                page:int = Query(default=1,ge=1),
                sort_by:SortUsers = Query(default=SortUsers.created_at),
                sort_order:SortOrder = Query(default=SortOrder.desc),
                db:Session= Depends(get_db)):
    return user_service.search_user(search,limit,page,sort_by,sort_order,db)


@router.get("/follow-requests",response_model=PaginatedFollowRequestResponse)
def show_follow_requests(
                       search:str|None=None,
                       limit:int = Query(default=20,ge=1,le=100),
                       page:int = Query(default=1,ge=1),
                       sort_by:SortUsers = Query(default=SortUsers.created_at),
                       sort_order:SortOrder = Query(default=SortOrder.desc),
                       db:Session=Depends(get_db),
                       current_user:User=Depends(get_current_user)):
    return user_service.show_follow_requests(search,limit,page,sort_by,sort_order,db,current_user)


@router.get("/{user_id}/followers",response_model=PaginatedUserResponse)
def show_follower_list(user_id:int,
                       search:str|None=None,
                       limit:int = Query(default=20,ge=1,le=100),
                       page:int = Query(default=1,ge=1),
                       sort_by:SortUsers = Query(default=SortUsers.created_at),
                       sort_order:SortOrder = Query(default=SortOrder.desc),
                       db:Session=Depends(get_db),
                       current_user:User=Depends(get_current_user)):
    return user_service.show_followers(user_id,search,limit,page,sort_by,sort_order,db,current_user)


@router.get("/{user_id}/following",response_model=PaginatedUserResponse)
def show_following_list(user_id:int,
                        search:str|None=None,
                        limit:int = Query(default=20,ge=1,le=100),
                        page:int = Query(default=1,ge=1),
                        sort_by:SortUsers = Query(default=SortUsers.created_at),
                        sort_order:SortOrder = Query(default=SortOrder.desc),
                        db:Session=Depends(get_db),
                        current_user:User=Depends(get_current_user)):
    return user_service.show_following(user_id,search,limit,page,sort_by,sort_order,db,current_user)


@router.get("/{user_id}",response_model=UserProfile)
def show_user_profile(user_id:int,
                      current_user:User=Depends(get_current_user),
                      db:Session= Depends(get_db)):
    
    return user_service.show_user_profile(user_id,current_user,db)


@router.patch("/follow-requests/bulk/{action}",response_model=MessageResponse)
def request_action_bulk(action:BulkAction,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
    return user_service.request_action_bulk(action,db,current_user)


@router.patch("/follow-requests/{request_id}/{action}",response_model=MessageResponse)
def request_action(request_id:int,
                   action:Action,
                   db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
    return user_service.request_action(request_id,action,db,current_user)


@router.patch("/me/privacy",response_model=PrivacyPreference)
def privacy_preferences(preference:PrivacyPreference,
                        db:Session=Depends(get_db),
                        current_user:User=Depends(get_current_user)):
    return user_service.privacy_preferences(preference.is_private,db,current_user)


@router.delete("/{user_id}/follow",status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user_or_unsend_request(user_id:int,
                db:Session=Depends(get_db),
                current_user:User=Depends(get_current_user)):
    return user_service.unfollow_user_or_unsend_request(user_id,db,current_user)