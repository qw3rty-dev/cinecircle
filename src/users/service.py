from fastapi import HTTPException,status

from sqlalchemy import select,exists,func
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from src.enums import Action,SortUsers, SortOrder, BulkAction
from src.pagination.utils import generate_meta
from src.models import User,Follow,FollowRequest



def get_follow_requests(user:User,
                        search:str,
                        limit:int,
                        page:int,
                        sort_by:SortUsers,
                        sort_order:SortOrder,
                        db:Session):
    
    query = select(FollowRequest).where(FollowRequest.following_id==user.id)
    query = query.join(FollowRequest.follower).options(selectinload(FollowRequest.follower))
    if search:
        search = search.strip().lower()
        query = query.where(User.username.ilike(f"{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    sort_fields= {
            SortUsers.created_at:FollowRequest.created_at,
            SortUsers.username:func.lower(User.username)
        }
    sort_expression = sort_fields[sort_by]
    order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
    query = query.order_by(order,FollowRequest.id.desc())
    offset = (page-1)*limit
    query = query.limit(limit).offset(offset)
    request_list = db.scalars(query).all()
    results = []
    for request in request_list:
        account = {
                    "request_id":request.id,
                    "username":request.follower.username,
                    "user_id":request.follower_id,
                    "created_at":request.created_at
        }
        results.append(account)
    return results, total


def check_profile_access(user_id:int,
                            current_user:User,
                            db:Session):
    
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    if not user.is_private or user.id == current_user.id:
        return user
    
    is_following = db.scalar(select(exists().where(Follow.follower_id == current_user.id,Follow.following_id == user_id)))

    if not is_following:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User profile is private")
    return user

         
def get_followers(user:User,
                  search:str,
                  limit:int,
                  page:int,
                  sort_by:SortUsers,
                  sort_order:SortOrder,
                  db:Session):
    
    query = select(Follow).where(Follow.following_id==user.id)
    query = query.join(Follow.follower).options(selectinload(Follow.follower))
    if search:
        search = search.strip().lower()
        query = query.where(User.username.ilike(f"{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    sort_fields= {
            SortUsers.created_at:Follow.created_at,
            SortUsers.username:func.lower(User.username)
        }
    sort_expression = sort_fields[sort_by]
    order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
    query = query.order_by(order,Follow.id.desc())
    offset = (page-1)*limit
    query = query.limit(limit).offset(offset)
    follower_list = db.scalars(query).all()
    results = []
    for follower in follower_list:
        account = {
                    "username":follower.follower.username,
                    "user_id":follower.follower_id,
                    "created_at":follower.created_at
        }
        results.append(account)
    return results, total

def get_following(user:User,
                  search:str,
                  limit:int,
                  page:int,
                  sort_by:SortUsers,
                  sort_order:SortOrder,
                  db:Session):
    query = select(Follow).where(Follow.follower_id==user.id)
    query = query.join(Follow.following).options(selectinload(Follow.following))

    if search:
        search = search.strip().lower()
        query = query.where(User.username.ilike(f"{search}%"))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    sort_fields= {
            SortUsers.created_at:Follow.created_at,
            SortUsers.username:func.lower(User.username)
        }
    
    sort_expression = sort_fields[sort_by]
    order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
    query = query.order_by(order,Follow.id.desc())
    offset = (page-1)*limit
    query = query.limit(limit).offset(offset)
    following_list = db.scalars(query).all()
    results = []
    for following in following_list:
        account = {
                    "username":following.following.username,
                    "user_id":following.following_id,
                    "created_at":following.created_at
        }
        results.append(account)
    return results, total

def search_user_results(
                  search:str,
                  limit:int,
                  page:int,
                  sort_by:SortUsers,
                  sort_order:SortOrder,
                  db:Session):
    
    search = search.strip().lower()
    query = select(User).where(User.username.ilike(f"{search}%"))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    sort_fields= {
            SortUsers.created_at:User.created_at,
            SortUsers.username:func.lower(User.username)
        }
    
    sort_expression = sort_fields[sort_by]
    order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
    query = query.order_by(order,User.id.desc())
    offset = (page-1)*limit
    query = query.limit(limit).offset(offset)
    users = db.scalars(query).all()
    results = []
    for user in users:
        account = {
                    "username":user.username,
                    "user_id":user.id,
                    "created_at":user.created_at
        }
        results.append(account)
    return results, total


class UserService():

    def show_user_profile(self,
                          id:int,
                          current_user:User,
                          db:Session):
 
        user = db.scalar(select(User).where(User.id == id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

        my_profile = current_user.id == id
        is_following = False

        if not my_profile and user.is_private:
            is_following = db.scalar(select(exists().where(Follow.follower_id==current_user.id,Follow.following_id==user.id)))

        can_view_content = (my_profile or not user.is_private or is_following)
        followers_len = db.scalar(select(func.count()).where(Follow.following_id == user.id))
        following_len = db.scalar(select(func.count()).where(Follow.follower_id == user.id))

        return {
            "username": user.username,
            "is_private":user.is_private,
            "followers": followers_len,
            "following": following_len,
            "my_profile": my_profile,
            "can_view_content": can_view_content
            }


    def search_user(self,
                    search:str,
                    limit:int,
                    page:int,
                    sort_by:SortUsers,
                    sort_order:SortOrder,
                    db:Session):
        
        users, total = search_user_results(search,limit,page,sort_by,sort_order,db)
        meta = generate_meta(page,limit,total)

        return {"meta":meta,
                "results":users}


    def follow_user(self,
                    user_id: int,
                    db:Session,
                    current_user:User):
        
        user = db.scalar(select(User).where(User.id==user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        
        if user_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You cannot follow yourself")
        
        existing_follow = db.scalar(select(exists().where(Follow.follower_id==current_user.id,Follow.following_id==user_id)))
        if existing_follow:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Already following")
        
        if user.is_private:
            new_follow_request = FollowRequest(
                follower_id = current_user.id,
                following_id = user_id
            )
            try:
                db.add(new_follow_request)
                db.commit()
                db.refresh(new_follow_request)
                return {"message": "follow request sent"}
            except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Request already sent")

        new_following = Follow(
            follower_id = current_user.id,
            following_id = user_id
        )
        try:
            db.add(new_following)
            db.commit()
            db.refresh(new_following)
            return {"message": "Following"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Already following")


    def unfollow_user_or_unsend_request(self,
                                        user_id:int,
                                        db:Session,
                                        current_user:User):
                            
        existing_follow = db.scalar(select(Follow).where(Follow.follower_id==current_user.id,Follow.following_id==user_id))

        if not existing_follow:
            existing_follow_request =db.scalar(select(FollowRequest).where(FollowRequest.follower_id == current_user.id,FollowRequest.following_id == user_id))

            if not existing_follow_request:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No follow or follow request exists")
            db.delete(existing_follow_request)
            db.commit()
            return
        
        db.delete(existing_follow)
        db.commit()
        return


    def request_action(self,
                    request_id:int,
                    action:Action,
                    db:Session,
                    current_user:User):
        request = db.scalar(select(FollowRequest).where(FollowRequest.id == request_id,FollowRequest.following_id == current_user.id))
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Request not found")
        
        if action == Action.accept:
            new_follow = Follow(
                follower_id=request.follower_id,
                following_id=request.following_id
            )
            try:
                db.add(new_follow)
                db.delete(request)
                db.commit()
                db.refresh(new_follow)
            except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Already accepted")
            return {"message": "Request accepted"}
        if action == Action.reject:
            db.delete(request)
            db.commit()
            return {"message":"Request rejected"}

    def request_action_bulk(self,
                            action:BulkAction,
                            db:Session,
                            current_user:User):
        requests = db.scalars(select(FollowRequest).where(FollowRequest.following_id == current_user.id)).all()
        if not requests:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No pending request")
        
        if action == BulkAction.accept_all:
            for request in requests:
                new_follow = Follow(
                    follower_id=request.follower_id,
                    following_id=request.following_id
                )
                db.add(new_follow)
                db.delete(request)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Could not accept requests")
            return {"message": "Requests accepted"}
    
        if action == BulkAction.reject_all:
            for request in requests:
                db.delete(request)
            db.commit()
            return {"message":"Requests rejected"}

        
    def show_follow_requests(self,
                           search:str,
                           limit:int,
                           page:int,
                           sort_by:SortUsers,
                           sort_order:SortOrder,
                           db:Session,
                           current_user:User):
                
        follow_requests, total = get_follow_requests(current_user,search,limit,page,sort_by,sort_order,db)
        meta = generate_meta(page,limit,total)

        return {"meta":meta,
                "results":follow_requests}
        
    def show_followers(self,
                       user_id:int,
                       search:str,
                       limit:int,
                       page:int,
                       sort_by:SortUsers,
                       sort_order:SortOrder,
                       db:Session,
                       current_user:User):
        
        user = check_profile_access(user_id,current_user,db)
        
        followers, total = get_followers(user,search,limit,page,sort_by,sort_order,db)
        meta = generate_meta(page,limit,total)

        return {"meta":meta,
                "results":followers}
        
    def show_following(self,
                       user_id:int,
                       search:str,
                       limit:int,
                       page:int,
                       sort_by:SortUsers,
                       sort_order:SortOrder,
                       db:Session,
                       current_user:User):
        
        user = check_profile_access(user_id,current_user,db)

        following, total = get_following(user,search,limit,page,sort_by,sort_order,db)
        meta = generate_meta(page,limit,total)

        return {"meta":meta,
                "results":following}
    


    def privacy_preferences(self,
                            is_private:bool,
                            db:Session,
                            current_user:User):
        if current_user.is_private != is_private:
            current_user.is_private = is_private
            db.commit()
        return {"is_private":current_user.is_private}
