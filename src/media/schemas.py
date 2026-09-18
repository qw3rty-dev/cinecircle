from datetime import date
from typing import Literal

from pydantic import BaseModel,ConfigDict


class MovieResult(BaseModel):
    tmdb_id : int
    media_type : Literal["movie"]
    poster_path : str|None
    title : str
    overview : str|None
    release_date : date|None
    model_config= ConfigDict(from_attributes=True)


class TvResult(BaseModel):
    tmdb_id : int
    media_type : Literal["tv"]
    poster_path : str|None
    name : str
    overview : str|None
    first_air_date : date|None
    model_config= ConfigDict(from_attributes=True)


class SearchMovieResponse(BaseModel):
    query : str
    page : int
    total_pages: int
    total_results: int
    results: list[MovieResult]
    model_config= ConfigDict(from_attributes=True)


class SearchTvResponse(BaseModel):
    query : str
    page : int
    total_pages : int
    total_results : int
    results : list[TvResult]
    model_config= ConfigDict(from_attributes=True)


class SearchAllResponse(BaseModel):
    query : str
    page : int
    total_pages : int
    total_results : int
    results : list[MovieResult|TvResult]
    model_config= ConfigDict(from_attributes=True)


class TrendingMovieResponse(BaseModel):
    page : int
    total_pages : int
    total_results : int
    results : list[MovieResult]
    model_config= ConfigDict(from_attributes=True)


class TrendingTvResponse(BaseModel):
    page : int
    total_pages : int
    total_results : int
    results : list[TvResult]
    model_config= ConfigDict(from_attributes=True)



