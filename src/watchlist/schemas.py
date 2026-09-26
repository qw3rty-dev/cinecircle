from datetime import date,datetime

from pydantic import BaseModel, ConfigDict

from src.enums import MediaType, WatchlistStatus
from src.pagination.schemas import PaginationMeta


class AddToWatchlistRequest(BaseModel):
    tmdb_id: int
    media_type: MediaType
    model_config = ConfigDict(extra="forbid")


class UpdateWatchlistRequest(BaseModel):
    status: WatchlistStatus 
    model_config = ConfigDict(extra="forbid")


class MediaResponse(BaseModel):
    id: int
    title: str
    media_type: MediaType
    premiere_date: date|None
    model_config = ConfigDict(from_attributes=True)


class WatchlistResponse(BaseModel):
    id: int
    status: WatchlistStatus
    created_at: datetime
    media: MediaResponse
    model_config = ConfigDict(from_attributes=True)


class PaginatedWatchlistResponse(BaseModel):
    meta: PaginationMeta
    watchlist: list[WatchlistResponse]
    model_config = ConfigDict(from_attributes=True)