from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,status,HTTPException,Query

from src.db import get_db
from src.models import User
from src.enums import WatchlistStatus, SortWatchlist, SortOrder
from .service import WatchListService
from src.security.jwt_handler import get_current_user
from src.services.tmdb.exceptions import TMDBServiceError
from .schemas import WatchlistResponse,AddToWatchlistRequest,PaginatedWatchlistResponse, UpdateWatchlistRequest


router = APIRouter(prefix="/watchlist",tags=["watchlist"])
watchlist_service = WatchListService()

@router.post("/",response_model=WatchlistResponse)
async def add_to_watchlist(data:AddToWatchlistRequest,
                     db:AsyncSession=Depends(get_db),
                     current_user:User=Depends(get_current_user)):
        try:
          return await watchlist_service.add_to_watchlist(data.tmdb_id,data.media_type,db,current_user)
        
        except TMDBServiceError:
             raise HTTPException(status_code=503,detail= "TMDB service didn't respond")

        
@router.get("/",response_model=PaginatedWatchlistResponse)
async def fetch_watchlist(search:str|None = Query(default=None),
                    status:WatchlistStatus|None = Query(default=None),
                    sort_by:SortWatchlist = Query(default=SortWatchlist.created_at),
                    sort_order:SortOrder = Query(default=SortOrder.desc),
                    limit:int = Query(default=20,ge=1,le=100),
                    page:int = Query(default=1,ge=1),
                    db:AsyncSession = Depends(get_db),
                    current_user:User = Depends(get_current_user)):
    
    return await watchlist_service.fetch_watchlist(search,status,sort_by,sort_order,limit,page,db,current_user)

@router.patch("/{id}/status",response_model=WatchlistResponse)
async def change_watching_status(id:int,
               update:UpdateWatchlistRequest,
               db:AsyncSession=Depends(get_db),
               current_user:User=Depends(get_current_user)):
    
    return await watchlist_service.change_status(id,update.status,db,current_user)


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(id:int,
                          db:AsyncSession=Depends(get_db),
                          current_user:User=Depends(get_current_user)):
    
    return await watchlist_service.remove_from_watchlist(id,db,current_user)