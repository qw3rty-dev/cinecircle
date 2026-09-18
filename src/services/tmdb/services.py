import os 
import time

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter

from src.enums import MediaType
from urllib3.util.retry import Retry
from .exceptions import TMDBServiceError
from .utils import save_cache,load_cache,search_in_cache,search_by_id,str_to_date


load_dotenv()
ACCESS_TOKEN= os.getenv("ACCESS_TOKEN")


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

def request_data(url,params:dict|None=None):
    SESSION = make_session()
    print("Calling TMDB....\n")
    try:
        req= SESSION.get(url=url,params=params,timeout=20)
        req.raise_for_status()
        data= req.json()
        return data
    except requests.exceptions.ConnectionError as e:
        print(f"Could not connect to TMDB.  ")
        raise TMDBServiceError("Could not connect to TMDB.") from e

    except requests.exceptions.Timeout:
        print("TMDB took too long to respond.")
        raise TMDBServiceError("TMDB took too long to respond.") from e

    except requests.exceptions.HTTPError as e:
        print(f"TMDB returned an HTTP error: {e}")
        print(req.text)
        raise TMDBServiceError(f"TMDB returned an HTTP error:{e}") from e

def search_tv(search:str,
              page:int=1):
    search = search.lower().strip()    
    cache=load_cache()
    cached_result= search_in_cache(cache,search,"tv",page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/search/tv"
    params = {"query":search,
              "page":page}
    
    data = request_data(url,params)
    key = f"search:{search}:tv:{page}"
    save_cache(cache,data,2,key)

    return data

def search_movie(search:str,
                 page:int=1):
    search = search.lower().strip()    
    cache=load_cache()
    cached_result= search_in_cache(cache,search,"movie",page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/search/movie"
    params = {"query":search,
              "page":page}
    
    data = request_data(url,params)
    key = f"search:{search}:movie:{page}"
    save_cache(cache,data,2,key)

    return data


def trending_movies(search=None,
                    page:int=1):

    cache=load_cache()
    cached_result= search_in_cache(cache=cache,search="trending:movie",page=page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/trending/movie/day"
    data = request_data(url,params={"page":page})
    key = f"trending:movie:{page}"
    save_cache(cache,data,1,key)
    return data

def trending_tv(search=None,
                page:int=1):

    cache=load_cache()
    cached_result= search_in_cache(cache=cache,search="trending:tv",page=page)
    if cached_result is not None:
        return cached_result
    
    url= "https://api.themoviedb.org/3/trending/tv/day"
    data = request_data(url,params={"page":page})
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


def get_by_id(tmdb_id:int,
              media_type:MediaType):
    cache=load_cache()
    media = search_by_id(cache=cache,tmdb_id=tmdb_id,media_type=media_type)
    if media is not None:
        return get_media_info(media,media_type)
    url = f"https://api.themoviedb.org/3/{media_type.value}/{tmdb_id}"
    media = request_data(url)
    return get_media_info(media,media_type)


