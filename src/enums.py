from enum import Enum

class MediaType(str,Enum):
    tv = 'tv'
    movie = 'movie'


class SearchMediaType(str,Enum):
    movie="movie"
    tv="tv"
    all="all"

class RequestStatus(str,Enum):
    pending="pending"

class Action(str,Enum):
    accept="accept"
    reject="reject"