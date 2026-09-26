from math import ceil
from sqlalchemy import select,or_, func
from sqlalchemy.orm import Session, selectinload
from fastapi import status,HTTPException
from sqlalchemy.exc import IntegrityError

from src.media.service import MediaService
from src.pagination.utils import generate_meta
from src.models import User,Review,Media,ReviewVote,Comment
from .schemas import UpdateReviewRequest,UpdateCommentRequest
from src.enums import MediaType, VoteType, SortComments,SortReviews,SortMyReviews, SortOrder, Rating


def extract_votes_of_reviews(review_ids:list,
                             db:Session,
                             current_user:User):
        
        vote_count = db.execute(select(ReviewVote.review_id,func.count().filter(ReviewVote.vote_type==VoteType.upvote).label("upvote"),func.count().filter(ReviewVote.vote_type==VoteType.downvote).label("downvote")).where(ReviewVote.review_id.in_(review_ids)).group_by(ReviewVote.review_id)).all()
        my_votes = db.execute(select(ReviewVote.review_id,ReviewVote.vote_type).where(ReviewVote.user_id==current_user.id,ReviewVote.review_id.in_(review_ids))).all()

        vote_counts = {review_id:{"upvotes":upvotes,"downvotes":downvotes} for review_id, upvotes, downvotes in vote_count }
        my_vote_types = {review_id:vote_type for review_id,vote_type in my_votes}

        return vote_counts,my_vote_types  

def extract_comments_from_review(review_id:int,
                                search:str,
                                sort_by:SortComments,
                                sort_order:SortOrder,
                                limit:int,
                                page:int,
                                db:Session): 

        review = db.scalar(select(Review).where(Review.id == review_id))
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found")
        
        query= select(Comment).where(Comment.review_id==review_id)
        query= query.join(Comment.user).options(selectinload(Comment.user))
        if search:
            query= query.where(Comment.content.ilike(f"%{search}%"))
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        sort_fields= {
            SortComments.created_at:Comment.created_at,
            SortComments.username: func.lower(User.username)
        }
        sort_expression = sort_fields[sort_by]
        order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
        query = query.order_by(order,Comment.id.desc())
        offset = (page-1)*limit
        query = query.limit(limit).offset(offset)
        comments = db.scalars(query).all()
        return comments,review,total

def extract_reviews(media_id:int,
                    search:str,
                    author:str,
                    rating:Rating,
                    sort_by:SortReviews,
                    sort_order:SortOrder,
                    limit:int,
                    page:int,
                    db:Session): 
        
        media = db.scalar(select(Media).where(Media.id == media_id))
        if not media:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Media not found")
        query= select(Review).where(Review.media_id==media_id)
        query = query.join(Review.user).options(selectinload(Review.user))
        if search:
            query= query.where(Review.content.ilike(f"%{search}%"))
        if author:
            query= query.where(User.username.ilike(f"%{author.strip()}%"))
        if rating:
            query= query.where(Review.rating == rating.value)

        total = db.scalar(select(func.count()).select_from(query.subquery()))
        sort_fields= {
            SortReviews.created_at:Review.created_at,
            SortReviews.username: func.lower(User.username),
            SortReviews.rating: Review.rating
        }
        sort_expression = sort_fields[sort_by]
        order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
        query = query.order_by(order,Review.id.desc())

        offset = (page-1)*limit
        query = query.limit(limit).offset(offset)
        reviews = db.scalars(query).all()
        return reviews,media,total

def extract_my_reviews(user_id:int,
                    search:str,
                    rating:Rating,
                    sort_by:SortMyReviews,
                    sort_order:SortOrder,
                    limit:int,
                    page:int,
                    db:Session): 
        query= select(Review).where(Review.user_id == user_id)
        query = query.join(Review.media).options(selectinload(Review.media))
        
        if search:
            query= query.where(or_(Review.content.ilike(f"%{search}%"),Media.title.ilike(f"%{search.strip()}%")))
        if rating:
            query= query.where(Review.rating == rating.value)
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        sort_fields= {
            SortMyReviews.created_at:Review.created_at,
            SortMyReviews.rating:Review.rating,
            SortMyReviews.title: func.lower(Media.title)
        }
        sort_expression = sort_fields[sort_by]
        order = sort_expression.asc() if sort_order == SortOrder.asc else sort_expression.desc()
        query = query.order_by(order,Review.id.desc())

        offset = (page-1)*limit
        query = query.limit(limit).offset(offset)
        reviews = db.scalars(query).all()
        return reviews,total

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
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                },
                "review":{
                    "id":review.id,
                    "user":{
                        "id":review.user.id,
                        "username":review.user.username
                    },
                    "rating":review.rating,
                    "content":review.content,
                    "upvotes":0,
                    "downvotes":0,
                    "my_vote":None,
                    "created_at":review.created_at}
        }

    def vote(self,
             review_id:int,
             vote_type:VoteType,
             db:Session,
             current_user:User):
        
        review = db.scalar(select(Review).where(Review.id == review_id))
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found")
        existing_vote = db.scalar(select(ReviewVote).where(ReviewVote.review_id == review_id,ReviewVote.user_id == current_user.id))
        if not existing_vote:
            vote = ReviewVote(
                review_id=review_id,
                user_id=current_user.id,
                vote_type=vote_type
            )

            db.add(vote)
            db.commit()
            return {"vote_type": vote.vote_type}
        if existing_vote.vote_type == vote_type:
            db.delete(existing_vote)
            db.commit()
            return {"vote_type": None}
        existing_vote.vote_type = vote_type
        db.commit()
        return {"vote_type": existing_vote.vote_type}

    def comment(self,
                review_id:int,
                content:str,
                db:Session,
                current_user:User):
        
        review = db.scalar(select(Review).where(Review.id == review_id))
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Review not found")
        comment = Comment(
            review_id = review_id,
            user_id = current_user.id,
            content = content
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "id":current_user.id,
                "username":current_user.username
            },
            "review_id": review_id
        }

    def edit_comment(self,
                     comment_id:int,
                     update:UpdateCommentRequest,
                     db:Session,
                     current_user:User):

        comment = db.scalar(select(Comment).where(Comment.id == comment_id,Comment.user_id == current_user.id))
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Comment not found")
        
        update = update.model_dump(exclude_unset=True)
        for field,value in update.items():
            setattr(comment,field,value)

        db.commit()
        db.refresh(comment)
        return {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "id":current_user.id,
                "username":current_user.username
            },
            "review_id": comment.review_id
        }      
    def get_comments(self,
                     review_id:int,
                     search:str,
                     sort_by:SortComments,
                     order:SortOrder,
                     limit:int,
                     page:int,
                     db:Session,
                     current_user:User):
        
        comments,review,total = extract_comments_from_review(review_id,search,sort_by,order,limit,page,db)
        results= []
        for comment in comments:
            item = {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user": {
                "id":comment.user_id,
                "username":comment.user.username
            }
        }
            
            results.append(item)

        meta = generate_meta(page,limit,total)

        vote_counts,my_vote_types = extract_votes_of_reviews([review_id],db,current_user)
        votes = vote_counts.get(review.id,{"upvotes": 0 ,"downvotes": 0})
        upvotes = votes["upvotes"]
        downvotes = votes["downvotes"]
        my_vote = my_vote_types.get(review_id)

        review = {
                "id":review.id,
                "rating":review.rating,
                "content":review.content,
                "upvotes":upvotes,
                "downvotes":downvotes,
                "my_vote":my_vote,
                "created_at":review.created_at,
                "user":{"id":review.user_id,
                        "username":review.user.username}
                }

        return {"meta":meta,
                "review":review,
                "comments":results}
        
    def get_reviews(self,
                    media_id:int,
                    search:str,
                    author:str,
                    rating:str,
                    sort_by:SortReviews,
                    sort_order:SortOrder,
                    limit:int,
                    page:int,
                    db:Session,
                    current_user:User):
        
        reviews,media,total = extract_reviews(media_id,search,author,rating,sort_by,sort_order,limit,page,db)
        review_ids = [review.id for review in reviews]
        vote_counts,my_vote_types = extract_votes_of_reviews(review_ids,db,current_user)
        results = []
        for review in reviews:
            votes = vote_counts.get(review.id,{"upvotes": 0 ,"downvotes": 0})
            item = {
                    "id":review.id,
                    "user":{
                        "id":review.user.id,
                        "username":review.user.username
                    },
                    "rating":review.rating,
                    "content":review.content,
                    "upvotes":votes["upvotes"],
                    "downvotes":votes["downvotes"],
                    "my_vote":my_vote_types.get(review.id),
                    "created_at":review.created_at}
                   
            results.append(item)

        meta = generate_meta(page,limit,total)
        media = {
                "id":media.id,
                "title":media.title,
                "media_type":media.media_type,
                "premiere_date":media.premiere_date
            }
        return {"meta":meta,
                "media":media,
                "reviews":results}


    def delete_comment(self,
                       comment_id:int,
                       db:Session,
                       current_user:User):
        
        comment = db.scalar(select(Comment).where(Comment.id == comment_id,Comment.user_id == current_user.id))
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found")
        db.delete(comment)
        db.commit()

    def get_my_reviews(self,
                      search:str,
                      rating:Rating,
                      sort_by:SortMyReviews,
                      sort_order:SortOrder,
                      limit:int,
                      page:int,
                      db:Session,
                      current_user:User):
        
        reviews,total = extract_my_reviews(current_user.id,search,rating,sort_by,sort_order,limit,page,db)
        review_ids = [review.id for review in reviews]
        vote_counts,my_vote_types = extract_votes_of_reviews(review_ids,db,current_user)
        results =[]
        for review in reviews:
            votes = vote_counts.get(review.id,{"upvotes": 0 ,"downvotes": 0})
            item ={
                "id":review.id,
                "rating":review.rating,
                "content":review.content,
                "upvotes":votes["upvotes"],
                "downvotes":votes["downvotes"],
                "my_vote":my_vote_types.get(review.id),
                "created_at":review.created_at,
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                     }
            }
            results.append(item)

        meta = generate_meta(page,limit,total)

        return {"meta":meta,
                "reviews":results}

    
    def get_review_by_id(self,
                        review_id:int,
                        db:Session,
                        current_user:User):
        
        review = db.scalar(select(Review).where(Review.id == review_id))
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= "Review not found")
        
        vote_counts,my_vote_types = extract_votes_of_reviews([review_id],db,current_user)
        votes = vote_counts.get(review.id,{"upvotes": 0 ,"downvotes": 0})
        upvotes = votes["upvotes"]
        downvotes = votes["downvotes"]
        my_vote = my_vote_types.get(review_id)

        return {
                "media":{
                    "id":review.media.id,
                    "title":review.media.title,
                    "media_type":review.media.media_type,
                    "premiere_date":review.media.premiere_date
                },
                "review":{
                    "id":review.id,
                    "user":{
                        "id":review.user.id,
                        "username":review.user.username
                    },
                    "rating":review.rating,
                    "content":review.content,
                    "upvotes":upvotes,
                    "downvotes":downvotes,
                    "my_vote":my_vote,
                    "created_at":review.created_at}
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
        vote_counts,my_vote_types = extract_votes_of_reviews([review_id],db,current_user)
        votes = vote_counts.get(review.id,{"upvotes": 0 ,"downvotes": 0})
        upvotes = votes["upvotes"]
        downvotes = votes["downvotes"]
        my_vote = my_vote_types.get(review_id)
        return {
                "id":review.id,
                "rating":review.rating,
                "content":review.content,
                "upvotes":upvotes,
                "downvotes":downvotes,
                "my_vote":my_vote,
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
                




        
