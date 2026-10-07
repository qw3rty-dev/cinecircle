import asyncio
import os

import httpx
from dotenv import load_dotenv

from src.enums import MediaType

from .cache_service import load_cache, save_cache, search_by_id, search_in_cache
from .exceptions import TMDBServiceError

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3


async def request_data(client: httpx.AsyncClient, url, params: dict | None = None):
    headers = {
        "User-Agent": "CineSearch/1.0 (+https://example.com)",
        "accept": "application/json",
        "Authorization": ACCESS_TOKEN,
    }
    print("Calling TMDB....\n")
    for attempt in range(1, MAX_RETRIES + 1):
        print(attempt)
        delay = 2**attempt
        try:
            req = await client.get(url=url, params=params, headers=headers)
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
            print("Could not connect to TMDB.  ")
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


async def get_genres(client: httpx.AsyncClient):
    results = []
    for media_type in ["tv", "movie"]:
        url = f"https://api.themoviedb.org/3/genre/{media_type}/list"
        data = await request_data(client, url)
        for item in data["genres"]:
            if item not in results:
                results.append(item)
    return results


async def get_recommendation(
    media_type: MediaType, tmdb_id: int, client: httpx.AsyncClient
):
    cache = load_cache()
    cached_result = search_in_cache(
        cache, f"recommendation:{tmdb_id}", media_type.value
    )
    if cached_result is not None:
        return cached_result
    url = f"https://api.themoviedb.org/3/{media_type.value}/{tmdb_id}/recommendations?language=en-US&page=1"
    data = await request_data(client, url)
    key = f"recommendation:{tmdb_id}:{media_type.value}"
    save_cache(cache, data, 24, key)
    return data


async def search_tv(client: httpx.AsyncClient, search: str, page: int = 1):
    search = search.lower().strip()
    cache = load_cache()
    cached_result = search_in_cache(cache, f"search:{search}", "tv", page)
    if cached_result is not None:
        return cached_result

    url = "https://api.themoviedb.org/3/search/tv"
    params = {"query": search, "page": page}

    data = await request_data(client, url, params)
    key = f"search:{search}:tv:{page}"
    save_cache(cache, data, 2, key)

    return data


async def search_movie(client: httpx.AsyncClient, search: str, page: int = 1):
    search = search.lower().strip()
    cache = load_cache()
    cached_result = search_in_cache(cache, f"search:{search}", "movie", page)
    if cached_result is not None:
        return cached_result

    url = "https://api.themoviedb.org/3/search/movie"
    params = {"query": search, "page": page}

    data = await request_data(client, url, params)
    key = f"search:{search}:movie:{page}"
    save_cache(cache, data, 2, key)

    return data


async def trending_movies(client: httpx.AsyncClient, page: int = 1):

    cache = load_cache()
    cached_result = search_in_cache(
        cache=cache, search="trending", type="movie", page=page
    )
    if cached_result is not None:
        return cached_result

    url = "https://api.themoviedb.org/3/trending/movie/day"
    params = {"page": page}
    data = await request_data(client, url, params)
    key = f"trending:movie:{page}"
    save_cache(cache, data, 1, key)
    return data


async def trending_tv(client: httpx.AsyncClient, page: int = 1):

    cache = load_cache()
    cached_result = search_in_cache(
        cache=cache, search="trending", type="tv", page=page
    )
    if cached_result is not None:
        return cached_result

    url = "https://api.themoviedb.org/3/trending/tv/day"
    params = {"page": page}
    data = await request_data(client, url, params)
    key = f"trending:tv:{page}"
    save_cache(cache, data, 1, key)
    return data


async def get_by_id(client: httpx.AsyncClient, tmdb_id: int, media_type: MediaType):
    cache = load_cache()
    media = search_by_id(cache=cache, tmdb_id=tmdb_id, media_type=media_type)
    if media is not None:
        return media
    url = f"https://api.themoviedb.org/3/{media_type.value}/{tmdb_id}"
    media = await request_data(client, url)
    return media
