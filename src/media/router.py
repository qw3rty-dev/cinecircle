from fastapi import APIRouter,HTTPException,status,Query,Request

from .service import MediaService
from src.enums import SearchMediaType,MediaType
from src.services.tmdb.exceptions import TMDBServiceError
from .schemas import SearchAllResponse,SearchMovieResponse,SearchTvResponse,TrendingMovieResponse,TrendingTvResponse,MovieResult,TvResult

router = APIRouter(prefix="/media",tags=["media"])

media_service = MediaService()

@router.get("/search/{search}",response_model=SearchMovieResponse|SearchTvResponse|SearchAllResponse)
async def search_media(request:Request,
                       search: str,
                       media_type:SearchMediaType = Query(default=SearchMediaType.all),
                       page:int = Query(default=1) ):
    try:
        client = request.app.state.http_client
        results = await media_service.search(search,media_type,page,client)
        return results
    
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail= "TMDB service didn't respond")


@router.get("/trending/movie",response_model=TrendingMovieResponse)
async def trending_movies(request: Request,
                          page:int = Query(default=1)):
    try:
        client = request.app.state.http_client
        results = await media_service.trending_movies(page,client)
        return results
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail= "TMDB service didn't respond")


@router.get("/trending/tv",response_model=TrendingTvResponse)
async def trending_tv(request: Request,
                      page:int = Query(default=1)):
    try:
        client = request.app.state.http_client
        results = await media_service.trending_tv(page,client)
        return results
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="TMDB service didn't respond")


@router.get("/{id}",response_model=MovieResult|TvResult)
async def get_by_id(request: Request,
                    id:int,
                    media_type:MediaType):
    try:
        client = request.app.state.http_client
        results = await media_service.get_by_id(id,media_type,client)
        return results
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="TMDB service didn't respond")

