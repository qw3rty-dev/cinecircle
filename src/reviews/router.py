from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.orm import Session
from.service import ReviewService
from src.models import User
from src.security.jwt_handler import get_current_user
from src.db import get_db
from src.services.tmdb.exceptions import TMDBServiceError
from.schemas import ReviewResponse,CreateReviewRequest,UpdateReviewRequest

router = APIRouter(prefix="/reviews",tags=["reviews"])
review_service = ReviewService()

@router.post("/",response_model=ReviewResponse)
def add_review( data:CreateReviewRequest,
                db:Session=Depends(get_db),
                current_user:User=Depends(get_current_user)):
    try:
         return review_service.add_review(data.tmdb_id,data.media_type,data.rating,data.content,db,current_user)
    except TMDBServiceError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail= "Movie service is temporarily unavailable")

@router.get("/media/{media_id}",response_model=list[ReviewResponse])
def get_media_reviews(media_id:int,
                      db:Session=Depends(get_db)):
    return review_service.get_reviews(media_id,db)

@router.get("/me",response_model=list[ReviewResponse])
def get_my_reviews(db:Session=Depends(get_db),
                   current_user:User=Depends(get_current_user)):
    return review_service.get_my_reviews(db,current_user)

@router.get("/{review_id}",response_model=ReviewResponse)
def get_review(review_id:int,
               db:Session=Depends(get_db),
               current_user:User=Depends(get_current_user)):
    return review_service.get_review_by_id(review_id,db,current_user)

@router.patch("/{review_id}",response_model=ReviewResponse)
def edit_review(review_id:int,
               update:UpdateReviewRequest,
               db:Session=Depends(get_db),
               current_user:User=Depends(get_current_user)):
    return review_service.edit_review(review_id,update,db,current_user)

@router.delete("/{review_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id:int,
               db:Session=Depends(get_db),
               current_user:User=Depends(get_current_user)):
    return review_service.delete_review(review_id,db,current_user)


