from datetime import datetime

from pydantic import BaseModel,ConfigDict

from src.reviews.schemas import ReviewResponse
from src.watchlist.schemas import WatchlistResponse

class UserPrivateProfile(BaseModel):
    username: str
    is_private: bool = True
    followers: int
    following: int
    my_profile: bool
    model_config = ConfigDict(from_attributes=True)


class UserPublicProfile(BaseModel):
    username: str
    is_private: bool = True
    followers: int
    following: int
    my_profile: bool
    watchlist: list[WatchlistResponse]
    reviews: list[ReviewResponse]
    model_config = ConfigDict(from_attributes=True)


class UserTitleCardResponse(BaseModel):
    id: int
    username: str
    is_private: bool
    model_config = ConfigDict(from_attributes=True)


class FollowRequestResponse(BaseModel):
    request_id: int
    username: str
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class FollowListResponse(BaseModel):
    username: str
    user_id: int
    created_at: datetime


class PrivacyPreference(BaseModel):
    is_private: bool