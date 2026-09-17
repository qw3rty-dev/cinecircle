from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from src.db import Base
from datetime import datetime, UTC, date
from src.enums import RequestStatus,MediaType


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True) 
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(UTC))
    is_private: Mapped[bool] = mapped_column(default=False,nullable=False)
    last_login: Mapped[datetime|None] = mapped_column(nullable=True)
    watchlist: Mapped[list["Watchlist"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    follower_links: Mapped[list["Follow"]] = relationship("Follow",foreign_keys="Follow.follower_id",back_populates="follower")
    following_links: Mapped[list["Follow"]] = relationship("Follow",foreign_keys="Follow.following_id",back_populates="following")
    sent_follow_requests: Mapped[list["Follow"]] = relationship("FollowRequest",foreign_keys="FollowRequest.follower_id",back_populates="follower")
    recieved_follow_requests: Mapped[list["Follow"]] = relationship("FollowRequest",foreign_keys="FollowRequest.following_id",back_populates="following")


class Media(Base):
    __tablename__ = "media"
    __table_args__= (UniqueConstraint("tmdb_id","media_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int|None] = mapped_column(nullable=True)
    media_type:Mapped[MediaType] = mapped_column(nullable=False)
    title: Mapped[str]= mapped_column(nullable=False)
    premiere_date: Mapped[date|None]= mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(UTC))
    last_synced: Mapped[datetime]= mapped_column(default=lambda:datetime.now(UTC),nullable=False)
    saved_by: Mapped[list["Watchlist"]] = relationship(back_populates="media")
    reviews: Mapped[list["Review"]] = relationship(back_populates="media")

class Watchlist(Base):
    __tablename__ = "watchlist"
    __table_args__= (UniqueConstraint("media_id","user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    media_id: Mapped[int] = mapped_column(ForeignKey("media.id"),nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(UTC))
    user: Mapped["User"] = relationship(back_populates="watchlist")
    media: Mapped["Media"] = relationship(back_populates="saved_by")
    
class Review(Base):
    __tablename__ = "reviews"
    __table_args__= (UniqueConstraint("media_id","user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    media_id: Mapped[int] = mapped_column(ForeignKey("media.id"),nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    content:Mapped[str] = mapped_column(nullable=False)
    rating:Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(UTC))
    media: Mapped["Media"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")
    

class Follow(Base):
    __tablename__ ='follows'
    __table_args__ = (UniqueConstraint("follower_id","following_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False) 
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(UTC))
    follower: Mapped["User"] = relationship("User",foreign_keys=[follower_id],back_populates="following_links")
    following: Mapped["User"] = relationship("User",foreign_keys=[following_id],back_populates="follower_links")
    
class FollowRequest(Base):
    __tablename__ ='follow_requests'
    __table_args__ = (UniqueConstraint("follower_id","following_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False) 
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    status:Mapped[RequestStatus] = mapped_column(default=RequestStatus.pending,nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(UTC))
    follower: Mapped["User"] = relationship("User",foreign_keys=[follower_id],back_populates="sent_follow_requests")
    following: Mapped["User"] = relationship("User",foreign_keys=[following_id],back_populates="recieved_follow_requests")
    
