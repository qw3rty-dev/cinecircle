from datetime import date
from math import ceil


def str_to_date(date_str):
    if date_str is None or date_str == "":
        return None
    date_obj = date.fromisoformat(date_str)
    return date_obj


def get_genres_name_by_id(genre_info, genre_ids):
    if genre_ids is None:
        return []
    results = []
    for id in genre_ids:
        results.append({"id": id, "name": genre_info[id]})
    return results


def get_media_info(item, media_type: str, genres_info: list):

    genres = item.get("genres") or get_genres_name_by_id(
        genres_info, item.get("genre_ids")
    )
    movie_info = {
        "tmdb_id": item["id"],
        "media_type": media_type,
        "poster_path": item.get("poster_path"),
        "title": item.get("title"),
        "name": item.get("name"),
        "overview": item.get("overview"),
        "genres": genres,
        "release_date": str_to_date(item.get("release_date")),
        "first_air_date": str_to_date(item.get("first_air_date")),
    }
    return movie_info


def generate_meta(page, limit, total):

    total_pages = ceil(total / limit)
    meta = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }

    return meta
