from fastapi import APIRouter,HTTPException,status

from .service import MediaService
from src.enums import SearchMediaType,MediaType
from src.services.tmdb.exceptions import TMDBServiceError
from .schemas import SearchAllResponse,SearchMovieResponse,SearchTvResponse,TrendingMovieResponse,TrendingTvResponse,MovieResult,TvResult

router = APIRouter(prefix="/media",tags=["media"])

media_service = MediaService()

@router.get("/search/{search}",response_model=SearchMovieResponse|SearchTvResponse|SearchAllResponse)
def search_media(search: str,
                media_type:SearchMediaType=SearchMediaType.all,
                page:int=1 ):
    try:
        results = media_service.search(search,
                                    media_type=media_type,
                                    page=page)
        return results
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail= "TMDB service didn't respond")


@router.get("/trending/movie",response_model=TrendingMovieResponse)
def trending_movies(page:int=1):
    try:
        results = media_service.trending_movies(page=page)
        return results
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail= "TMDB service didn't respond")


@router.get("/trending/tv",response_model=TrendingTvResponse)
def trending_tv(page:int=1):
    try:
        results = media_service.trending_tv(page=page)
        return results
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="TMDB service didn't respond")


@router.get("/{id}",response_model=MovieResult|TvResult)
def get_by_id(id:int,
              media_type:MediaType):
    try:
        results = media_service.get_by_id(id,media_type)
        return results
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="TMDB service didn't respond")

