from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from src.db import Base
from datetime import datetime, UTC, timedelta, date

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True) 
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(UTC))
    last_login: Mapped[datetime|None] = mapped_column(nullable=True)
    watchlist: Mapped[list["Watchlist"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")

class Media(Base):
    __tablename__ = "media"
    __table_args__= (UniqueConstraint("tmdb_id","media_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int|None] = mapped_column(nullable=True)
    media_type:Mapped[str] = mapped_column(nullable=False)
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
    