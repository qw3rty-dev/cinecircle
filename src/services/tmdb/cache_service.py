import json
from datetime import UTC, datetime, timedelta

from src.enums import MediaType


def load_cache():
    try:
        with open("media.json", "r") as f:
            cache = json.load(f)
            cache = cache_cleanup(cache)
            return cache
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_cache(cache, data, ttl, key):
    now = datetime.now(UTC)
    expires_at = now + timedelta(hours=ttl)
    metadata = {
        "cached_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "data": data,
    }
    cache[key.strip().lower()] = metadata
    with open("media.json", "w") as f:
        json.dump(cache, f, indent=4)


def cache_cleanup(cache):
    for key in list(cache):
        expires_at = datetime.fromisoformat(cache[key]["expires_at"])
        now = datetime.now(UTC)
        if now >= expires_at:
            del cache[key]
    return cache


def search_in_cache(cache, search: str, type: str, page: int | None = None):
    key = f"{search}:{type}"
    if page:
        key = f"{search}:{type}:{page}"
    if key in cache:
        print("Using cached result....\n")
        return cache[key]["data"]
    return None


def search_by_id(cache, tmdb_id: int, media_type: MediaType):

    for cache_key, cache_data in cache.items():
        if cache_key.split(":")[-2] != media_type.value:
            continue
        if cache_data["data"] is None:
            print("Oops", cache_key)
            continue

        for media in cache_data["data"]["results"]:
            if media["id"] != tmdb_id:
                continue
            if media_type == MediaType.movie and "title" in media:
                print("Using cached result....\n")
                return media
            if media_type == MediaType.tv and "name" in media:
                print("Using cached result....\n")
                return media

    return None
