from fastapi import status,HTTPException,Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models import User,Watchlist,Review,Media
from datetime import datetime,UTC,date
from src.media.service import MediaService
from src.services.tmdb.services import search_movie,search_tv,trending_movies,trending_tv
from .schemas import UpdateReviewRequest
from src.enums import MediaType


class ReviewService:

    def add_review(self,
                  tmdb_id:int,
                  media_type:MediaType,
                  rating:int,
                  content:str,
                  db:Session,
                  current_user:User):
        media_id = MediaService.get_or_create_media(tmdb_id,media_type,db)

        review = Review(
            media_id = media_id,
            user_id = current_user.id,
            rating = rating,
            content = content
        )
        try:
            db.add(review)
            db.commit()
            db.refresh(review)

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="review already exists")
        
        return {
                "id":review.id,
                "rating":review.rating,
                "review":review.content,
                "created_at":review.created_at,
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                }
        }

                


    def get_reviews(self,
                   media_id:int,
                   db:Session):
        media = db.scalar(select(Media).where(Media.id == media_id))
        if not media:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=("Media not found"))
        reviews = []
        for review in media.reviews:
            item ={
                "id":review.id,
                "rating":review.rating,
                "review":review.content,
                "created_at":review.created_at,
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                     }
            }
            reviews.append(item)
        return reviews
    
    def get_my_reviews(self,
                      db:Session,
                      current_user:User):
        reviews = []
        for review in current_user.reviews:
            item ={
                "id":review.id,
                "rating":review.rating,
                "review":review.content,
                "created_at":review.created_at,
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                     }
            }
            reviews.append(item)
        return reviews
    
    def get_review_by_id(self,
                        review_id:int,
                        db:Session,
                        current_user:User):
        review = db.scalar(select(Review).where(Review.id == review_id,Review.user_id == current_user.id))
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Review not found")
        
        return {
                "id":review.id,
                "rating":review.rating,
                "review":review.content,
                "created_at":review.created_at,
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                }
        }
    def edit_review(self,
                    review_id:int,
                    update:UpdateReviewRequest,
                    db:Session,
                    current_user:User):
        review = db.scalar(select(Review).where(Review.id == review_id,Review.user_id == current_user.id))
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Review not found")
        
        update = update.model_dump(exclude_unset=True)
        for field,value in update.items():
            setattr(review,field,value)

        db.commit()
        db.refresh(review)
        return {
                "id":review.id,
                "rating":review.rating,
                "review":review.content,
                "created_at":review.created_at,
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                }
        }
       
    def delete_review(self,
                      review_id:int,
                      db:Session,
                      current_user:User):
        review = db.scalar(select(Review).where(Review.id == review_id,Review.user_id == current_user.id))
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Review not found")
        db.delete(review)
        db.commit()
                




        
