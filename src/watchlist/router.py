from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session
from.service import WatchListService
from src.models import User
from src.security.jwt_handler import get_current_user
from src.db import get_db
from.schemas import WatchlistResponse,AddToWatchlistRequest
router = APIRouter(prefix="/watchlist",tags=["watchlist"])
watchlist_service = WatchListService()

@router.post("/",response_model=WatchlistResponse)
def add_to_watchlist(data:AddToWatchlistRequest,
                     db:Session=Depends(get_db),
                     current_user:User=Depends(get_current_user)):
    return watchlist_service.add_to_watchlist(data.tmdb_id,data.media_type,db,current_user)

@router.get("/",response_model=list[WatchlistResponse])
def fetch_watchlist(db:Session=Depends(get_db),
                     current_user:User=Depends(get_current_user)):
    return watchlist_service.fetch_watchlist(db,current_user)

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(id:int,
                          db:Session=Depends(get_db),
                          current_user:User=Depends(get_current_user)):
    return watchlist_service.remove_from_watchlist(id,db,current_user)