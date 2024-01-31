from sqlalchemy import Column, Integer, String, DateTime
import datetime

from .database import Base


class Saved(Base):
    __tablename__ = "saved"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(String, primary_key=True)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)


class Done(Base):
    __tablename__ = "done"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(String, primary_key=True)
    done_at = Column(DateTime, default=datetime.datetime.utcnow)


class Ratings(Base):
    __tablename__ = "ratings"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(String, primary_key=True)
    rating = Column(Integer)
    rated_at = Column(DateTime, default=datetime.datetime.utcnow)


class Comments(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    attraction_id = Column(String)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Likes(Base):
    __tablename__ = "likes"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(String, primary_key=True)
    liked_at = Column(DateTime, default=datetime.datetime.utcnow)


class Attractions(Base):
    __tablename__ = "attractions"

    attraction_id = Column(String, primary_key=True)
    likes_count = Column(Integer, default=0)
    saved_count = Column(Integer, default=0)
    done_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    rating_total = Column(Integer, default=0)