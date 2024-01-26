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


class AttractionComments(Base):
    __tablename__ = "attraction_comments"

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    attraction_id = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AttractionLikes(Base):
    __tablename__ = "attraction_likes"

    user_id = Column(Integer, primary_key=True)
    attraction_id = Column(Integer, primary_key=True)
    liked_at = Column(DateTime, default=datetime.datetime.utcnow)


class Attractions(Base):
    __tablename__ = "attractions"

    attraction_id = Column(Integer, primary_key=True)
    likes_count = Column(Integer, default=0)
    saved_count = Column(Integer, default=0)
    done_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    rating_total = Column(Integer, default=0)