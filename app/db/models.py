from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class SavedAttractions(Base):
    __tablename__ = "saved_attractions"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    saved_at = Column(DateTime)


class DoneAttractions(Base):
    __tablename__ = "done_attractions"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    done_at = Column(DateTime)


class RateAttraction(Base):
    __tablename__ = "attraction_ratings"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    rated_at = Column(DateTime)


class CommentAttraction(Base):
    __tablename__ = "attraction_comments"

    comment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    attraction_id = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime)


class LikedAttractions(Base):
    __tablename__ = "attraction_likes"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    liked_at = Column(DateTime)
