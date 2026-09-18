from datetime import date,datetime

from pydantic import BaseModel,ConfigDict,Field

from src.enums import MediaType


class MediaResponse(BaseModel):
    id : int
    title: str
    media_type: MediaType
    premiere_date: date|None
    model_config=ConfigDict(from_attributes=True)


class ReviewResponse(BaseModel):
    id: int
    rating: int
    content: str
    created_at: datetime
    media: MediaResponse
    model_config=ConfigDict(from_attributes=True)


class CreateReviewRequest(BaseModel):
    
    tmdb_id: int
    media_type: MediaType
    rating: int= Field(ge=1, le=5)
    content: str= Field(min_length=1,max_length=1000)
    model_config=ConfigDict(extra="forbid")


class UpdateReviewRequest(BaseModel):

    rating: int|None= Field(default=None,ge=1,le=5)
    content: str|None= Field(default=None,min_length=1,max_length=1000)
    model_config=ConfigDict(extra="forbid")