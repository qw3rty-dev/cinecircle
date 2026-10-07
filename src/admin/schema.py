from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from src.common.schemas import PaginationMeta


class UserDetail(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool
    is_private: bool
    is_deleted: bool
    is_admin: bool
    created_at: datetime
    last_login: datetime | None
    model_config = ConfigDict(from_attributes=True)


class PaginatedUserResponse(BaseModel):
    meta: PaginationMeta
    results: list[UserDetail]
    model_config = ConfigDict(from_attributes=True)


class StatsResponse(BaseModel):
    total_users: int
    active_users: int
    deleted_users: int
    total_reviews: int
    total_comments: int
    total_media: int
    movies: int
    tv_shows: int
    total_follows: int
    total_watchlist_entries: int
    model_config = ConfigDict(from_attributes=True)


class SyncGenreResponse(BaseModel):
    added: int
    model_config = ConfigDict(from_attributes=True)


class CleanResponse(BaseModel):
    deactivated_accounts_deleted: int
    unverified_accounts_deleted: int
    model_config = ConfigDict(from_attributes=True)
