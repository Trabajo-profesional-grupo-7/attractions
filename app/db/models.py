from sqlalchemy import Column, Integer, String, DateTime
import datetime

from .database import Base


class SavedAttractions(Base):
    __tablename__ = "saved_attractions"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)


class DoneAttractions(Base):
    __tablename__ = "done_attractions"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    done_at = Column(DateTime, default=datetime.datetime.utcnow)


class AttractionRatings(Base):
    __tablename__ = "attraction_ratings"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    rated_at = Column(DateTime, default=datetime.datetime.utcnow)


class CommentAttraction(Base):
    __tablename__ = "attraction_comments"

    comment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    attraction_id = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AttractionLikes(Base):
    __tablename__ = "attraction_likes"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    liked_at = Column(DateTime, default=datetime.datetime.utcnow)
