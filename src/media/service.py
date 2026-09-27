import httpx
from sqlalchemy import select
from fastapi import HTTPException,status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Media
from src.enums import MediaType,SearchMediaType
from src.services.tmdb.service import search_movie,search_tv,trending_movies,trending_tv,get_by_id,get_media_info


async def get_or_fetch(func,
                 media_type:MediaType,
                 client: httpx.AsyncClient,
                 search:str|None=None,
                 page:int=1):
    results=[]
    tmdb_response = await func(client,search,page)       
    
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

    async def search(self,
               search: str,
               media_type:SearchMediaType,
               page:int,
               client:httpx.AsyncClient):

        if media_type == SearchMediaType.movie:
          search_results = await get_or_fetch(search_movie,SearchMediaType.movie,client,search,page)

        if media_type == SearchMediaType.tv:
          search_results = await get_or_fetch(search_tv,SearchMediaType.tv,client,search,page)

        if media_type == SearchMediaType.all:
          movie = await get_or_fetch(search_movie,SearchMediaType.movie,client,search,page)
          tv = await get_or_fetch(search_tv,SearchMediaType.tv,client,search,page)
          search_results = {
              "query":search,
              "page":page,
              "total_pages":max(movie.get("total_pages"),tv.get("total_pages")),
              "total_results":movie.get("total_results") + tv.get("total_results"),
              "results":movie.get("results") + tv.get("results")
          }
         
        return search_results


    async def trending_movies(self,
                        page:int,
                        client:httpx.AsyncClient):
        
        results = await get_or_fetch(trending_movies,MediaType.movie,client,page=page)
        return results

    
    async def trending_tv(self,
                    page:int,
                    client:httpx.AsyncClient):
        
        results = await get_or_fetch(trending_tv,MediaType.tv,client,page=page)   
        return results
    

    async def get_by_id(self,
                  tmdb_id:int,
                  media_type:MediaType,
                  client:httpx.AsyncClient):
       data = await get_by_id(client,tmdb_id,media_type)
       return data


    @staticmethod
    async def get_or_create_media(tmdb_id:int,
                                  media_type:MediaType,
                                  db:AsyncSession):
        existing_media = await db.scalar(select(Media).where(Media.tmdb_id == tmdb_id,Media.media_type == media_type))
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
            await db.commit()
            await db.refresh(new_media)

        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Media already exists")
        
        return new_media.id