from datetime import date,datetime

from pydantic import BaseModel,ConfigDict,Field

from src.enums import MediaType
from src.pagination.schemas import PaginationMeta


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


class UpdateCommentRequest(BaseModel):
    content: str|None= Field(default=None,min_length=1,max_length=1000)
    model_config=ConfigDict(extra="forbid")


class CreateComment(BaseModel):
    content: str = Field(min_length=1,max_length=1000)
    model_config=ConfigDict(extra="forbid")


class AuthorResponse(BaseModel):
    id: int
    username: str
    model_config=ConfigDict(from_attributes=True)


class MediaResponse(BaseModel):
    id: int
    title: str
    media_type: MediaType
    premiere_date: date|None
    model_config=ConfigDict(from_attributes=True)


class ReviewInfo(BaseModel):
    id: int
    user: AuthorResponse
    rating: int
    content: str
    upvotes: int
    downvotes: int
    my_vote: str|None
    created_at: datetime
    model_config=ConfigDict(from_attributes=True)


class ReviewResponse(BaseModel):
    media: MediaResponse
    review: ReviewInfo
    model_config=ConfigDict(from_attributes=True)

    
class PaginatedReviewResponse(BaseModel):
    meta: PaginationMeta
    media: MediaResponse
    reviews: list[ReviewInfo]
    model_config=ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: AuthorResponse
    model_config=ConfigDict(from_attributes=True)


class NewCommentResponse(CommentResponse):
    review_id: int
    model_config=ConfigDict(from_attributes=True)


class PaginatedCommentResponse(BaseModel):
    meta: PaginationMeta
    review: ReviewInfo
    comments: list[CommentResponse]
    model_config=ConfigDict(from_attributes=True)


class MyReviewResponse(BaseModel):
    id: int
    rating: int
    content: str
    upvotes: int
    downvotes: int
    my_vote: str|None
    created_at: datetime
    media:MediaResponse
    model_config=ConfigDict(from_attributes=True)


class PaginatedMyReviewResponse(BaseModel):
   
    meta: PaginationMeta
    reviews: list[MyReviewResponse]
    model_config=ConfigDict(from_attributes=True)


class VoteResponse(BaseModel):
    vote_type: str|None
    model_config=ConfigDict(from_attributes=True)