from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from src.models import Media
from fastapi import HTTPException,status
from src.enums import MediaType,SearchMediaType

from src.services.tmdb.services import search_movie,search_tv,trending_movies,trending_tv,get_by_id,get_media_info


def get_or_fetch(func,
                 media_type:MediaType,
                 search:str|None=None,
                 page:int=1):
    results=[]
    tmdb_response = func(search,page)       
    
    search_results = {
              "query":search,
              "page":page,
              "total_pages":tmdb_response.get("total_pages") or 0,
              "total_results":tmdb_response.get("total_results") or 0

               }
    
    movies= tmdb_response.get("results")
    for item in movies:
        movie_info = get_media_info(item,media_type)
        results.append(movie_info)
    search_results["results"] = results

    return search_results

class MediaService:

        
    def search(self,
               search: str,
               media_type:SearchMediaType,
               page:int):

        if media_type == SearchMediaType.movie:
          search_results = get_or_fetch(search_movie,SearchMediaType.movie,search,page)

        if media_type == SearchMediaType.tv:
          search_results = get_or_fetch(search_tv,SearchMediaType.tv,search,page)

        if media_type == SearchMediaType.all:
          movie = get_or_fetch(search_movie,SearchMediaType.movie,search,page)
          tv = get_or_fetch(search_tv,SearchMediaType.tv,search,page)
          search_results = {
              "query":search,
              "page":page,
              "total_pages":max(movie.get("total_pages"),tv.get("total_pages")),
              "total_results":movie.get("total_results") + tv.get("total_results"),
              "results":movie.get("results") + tv.get("results")
          }
         
        return search_results

    def trending_movies(self,
                        page:int):
        
        results=get_or_fetch(trending_movies,MediaType.movie,page=page)
        return results
    
    def trending_tv(self,
                    page:int):
        
        results=get_or_fetch(trending_tv,MediaType.tv,page=page)   
        return results

    def get_by_id(self,tmdb_id:int,
                  media_type:MediaType):
       data = get_by_id(tmdb_id,media_type)
       return data

    @staticmethod
    def get_or_create_media(tmdb_id,media_type,db):
        existing_media = db.scalar(select(Media).where(Media.tmdb_id == tmdb_id,Media.media_type == media_type))
        if existing_media:
          return existing_media.id
        
        data = get_by_id(tmdb_id,media_type)
        new_media = Media(
            tmdb_id = tmdb_id,
            media_type = media_type,
            title=data.get('title') or data.get('name'),
            premiere_date =data.get('release_date') or data.get('first_air_date'),
        )
        try:
            db.add(new_media)
            db.commit()
            db.refresh(new_media)

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Media already exists")
        
        return new_media.id