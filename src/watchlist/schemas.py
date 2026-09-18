from datetime import date,datetime

from pydantic import BaseModel

from src.enums import MediaType


class MediaResponse(BaseModel):
    id: int
    title: str
    media_type: MediaType
    premiere_date: date|None


class WatchlistResponse(BaseModel):
    id: int
    created_at: datetime
    media: MediaResponse


class AddToWatchlistRequest(BaseModel):
    tmdb_id: int
    media_type: MediaType