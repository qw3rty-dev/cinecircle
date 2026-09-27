import os 
import time
import asyncio
import httpx
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter

from src.enums import MediaType
from urllib3.util.retry import Retry
from .exceptions import TMDBServiceError
from .utils import save_cache,load_cache,search_in_cache,search_by_id,str_to_date


load_dotenv()
ACCESS_TOKEN= os.getenv("ACCESS_TOKEN")

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3


def make_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "CineSearch/1.0 (+https://example.com)",
        "accept": "application/json",
        "Authorization": ACCESS_TOKEN
    })
    return session

async def request_data(client: httpx.AsyncClient,
                       url,
                       params:dict|None=None
                       ):
    # SESSION = make_session()
    headers = {
        "User-Agent": "CineSearch/1.0 (+https://example.com)",
        "accept": "application/json",
        "Authorization": ACCESS_TOKEN
    }
    print("Calling TMDB....\n")
    for attempt in range(1,MAX_RETRIES+1):
        print(attempt)
        delay = 2**attempt
        try:
            req= await client.get(url=url,params=params,headers=headers)
            if req.status_code in RETRY_STATUS_CODES:
                if req.status_code == 429:
                    retry_after = req.headers.get("Retry-After")
                    if retry_after is not None:
                        try:
                            delay = int(retry_after)
                        except ValueError:
                            pass
                if attempt == MAX_RETRIES:
                    req.raise_for_status()
                await asyncio.sleep(delay)
                continue
            req.raise_for_status()
            return req.json()
        except httpx.ConnectError as e:
            print(f"Could not connect to TMDB.  ")
            if attempt == MAX_RETRIES:
               raise TMDBServiceError("Could not connect to TMDB.") from e
            await asyncio.sleep(2**attempt)

        except httpx.TimeoutException as e:
            print("TMDB took too long to respond.")
            if attempt == MAX_RETRIES:
               raise TMDBServiceError("TMDB took too long to respond.") from e
            await asyncio.sleep(2**attempt)

        except httpx.HTTPStatusError as e:
            print(f"TMDB returned an HTTP error: {e}")
            print(req.text)
            raise TMDBServiceError(f"TMDB returned an HTTP error:{e}") from e

async def search_tv(client: httpx.AsyncClient,
              search:str,
              page:int=1):
    search = search.lower().strip()    
    cache=load_cache()
    cached_result= search_in_cache(cache,search,"tv",page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/search/tv"
    params = {"query":search,
              "page":page}
    
    data = await request_data(client,url,params)
    key = f"search:{search}:tv:{page}"
    save_cache(cache,data,2,key)

    return data

async def search_movie(client: httpx.AsyncClient,
                       search:str,
                       page:int=1):
    search = search.lower().strip()    
    cache=load_cache()
    cached_result= search_in_cache(cache,search,"movie",page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/search/movie"
    params = {"query":search,
              "page":page}
    
    data = await request_data(client,url,params)
    key = f"search:{search}:movie:{page}"
    save_cache(cache,data,2,key)

    return data


async def trending_movies(client: httpx.AsyncClient,
                          search=None,
                          page:int=1):

    cache=load_cache()
    cached_result= search_in_cache(cache=cache,search="trending:movie",page=page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/trending/movie/day"
    params={"page":page}
    data = await request_data(client,url,params)
    key = f"trending:movie:{page}"
    save_cache(cache,data,1,key)
    return data

async def trending_tv(client: httpx.AsyncClient,
                      search=None,
                      page:int=1):

    cache=load_cache()
    cached_result= search_in_cache(cache=cache,search="trending:tv",page=page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/trending/tv/day"
    params={"page":page}
    data = await request_data(client,url,params)
    key = f"trending:tv:{page}"
    save_cache(cache,data,1,key)
    return data

def get_media_info(item,
                   media_type:MediaType):
        movie_info = {
                     "tmdb_id":item['id'],
                     "media_type":media_type.value,
                     "poster_path":item.get("poster_path"),
                     "title": item.get('title'), 
                     "name": item.get('name'),
                     "overview": item.get('overview'),
                     "release_date": str_to_date(item.get("release_date")),
                     "first_air_date": str_to_date(item.get('first_air_date'))
        }
        return movie_info


async def get_by_id(client: httpx.AsyncClient,
                    tmdb_id:int,
                    media_type:MediaType):
    cache=load_cache()
    media = search_by_id(cache=cache,tmdb_id=tmdb_id,media_type=media_type)
    if media is not None:
        return get_media_info(media,media_type)
    url = f"https://api.themoviedb.org/3/{media_type.value}/{tmdb_id}"
    media = await request_data(client,url)
    return get_media_info(media,media_type)


