from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import status,HTTPException
from sqlalchemy.exc import IntegrityError

from src.models import User,Watchlist
from src.media.service import MediaService
from src.enums import MediaType


class WatchListService:

    def add_to_watchlist(self,
                         tmdb_id:int,
                         media_type:MediaType,
                         db:Session,
                         current_user:User):
        media_id = MediaService.get_or_create_media(tmdb_id,media_type,db)

        watchlist_obj = Watchlist(
            media_id = media_id,
            user_id = current_user.id
        )
        try:
            db.add(watchlist_obj)
            db.commit()
            db.refresh(watchlist_obj)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Media already exists in watchlist")
        return {"id":watchlist_obj.id,
                "media_id":watchlist_obj.media_id,
                "user_id":watchlist_obj.user_id,
                "created_at":watchlist_obj.created_at,
                "media":watchlist_obj.media}


    def fetch_watchlist(self,
                        db:Session,
                        current_user:User):
        watchlist = db.scalars(select(Watchlist).where(Watchlist.user_id == current_user.id)).all()
        return watchlist


    def remove_from_watchlist(self,
                              id:int,
                              db:Session,
                              current_user:User):
        media = db.scalar(select(Watchlist).where(Watchlist.id == id,Watchlist.user_id == current_user.id))
        if not media:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Media not found")
        
        db.delete(media)
        db.commit()

        




        
