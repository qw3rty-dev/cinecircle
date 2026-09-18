from fastapi import HTTPException,status

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.enums import Action
from src.models import User,Follow,FollowRequest


def get_followers(user:User):
    followers = user.following_links
    results = []
    for follower in followers:
        account = {
                    "username":follower.follower.username,
                    "user_id":follower.follower_id,
                    "created_at":follower.created_at}
        results.append(account)
    return results


def get_following(user:User):
    following_list = user.follower_links
    results = []
    for following in following_list:
        account = {
                    "username":following.following.username,
                    "user_id":following.following_id,
                    "created_at":following.created_at
        }
        results.append(account)
    return results


class UserService():

    def show_user_profile(self,
                          username:str,
                          current_user:User,
                          db:Session):
 
        user = db.scalar(select(User).where(User.username == username.strip().lower()))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        existing_follow = db.scalar(select(Follow).where(Follow.follower_id==current_user.id,Follow.following_id==user.id))
        if user.username==current_user.username or user.is_private == False or existing_follow:
            
            return {
                "username":user.username,
                "is_private":user.is_private,
                "followers": len(user.following_links),
                "following": len(user.follower_links),
                "my_profile": user.username==current_user.username,
                "watchlist": user.watchlist,
                "reviews": user.reviews


            }
        return {
            "username":user.username,
            "is_private":user.is_private,
            "followers": len(user.follower_links),
            "following": len(user.following_links),
            "my_profile": user.username==current_user.username
        }


    def search_user(self,
                    q:str,
                    db:Session):
        q = q.strip().lower()
        users = db.scalars(select(User).where(User.username.like(f"%{q}%"))).all()
        results =[]
        for user in users:
            data= {
                   "id":user.id,
                   "username":user.username,
                   "is_private":user.is_private
                   }
            results.append(data)
        return results


    def follow_user(self,
                    user_id: int,
                    db:Session,
                    current_user:User):
        
        if user_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You cannot follow yourself")
        
        existing_follow = db.scalar(select(Follow).where(Follow.follower_id==current_user.id,Follow.following_id==user_id))
        if existing_follow:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Already following")
        
        user = db.scalar(select(User).where(User.id==user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
            
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


    def get_follow_request(self,
                           current_user:User):
        requests = current_user.recieved_follow_requests
        results = []
        for request in requests:
            metadata = {"request_id":request.id,
                        "username":request.follower.username,
                        "user_id":request.follower.id,
                        "created_at":request.created_at}
            results.append(metadata)

        return results

        
    def show_followers(self,
                       user_id:int,
                       db:Session,
                       current_user:User):
        user = db.scalar(select(User).where(User.id == user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        
        if not user.is_private or user.id==current_user.id:
            return get_followers(user)

        existing_follow = db.scalar(select(Follow).where(Follow.follower_id == current_user.id,Follow.following_id == user_id))
        if not existing_follow and user.is_private:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User profile is private")
        return get_followers(user)

    
    def show_following(self,
                       user_id:int,
                       db:Session,
                       current_user:User):
        user = db.scalar(select(User).where(User.id == user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        if not user.is_private or user.id == current_user.id:
            return get_following(user)
    
        existing_follow = db.scalar(select(Follow).where(Follow.follower_id == current_user.id,Follow.following_id == user_id))
        if not existing_follow and user.is_private:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User profile is private")
        return get_following(user)


    def privacy_preferences(self,
                            is_private:bool,
                            db:Session,
                            current_user:User):
        if current_user.is_private != is_private:
            current_user.is_private = is_private
            db.commit()
        return {"is_private":current_user.is_private}
