import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Float, Index, Integer, String

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
    rating = Column(
        Integer, CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating")
    )
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
    attraction_name = Column(String)
    country = Column(String)
    city = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    photo = Column(String)
    likes_count = Column(Integer, default=0)
    saved_count = Column(Integer, default=0)
    done_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    rating_total = Column(Integer, default=0)
    scheduled_count = Column(Integer, default=0)
    types = Column(String, default=[])
    external_rating = Column(Float, default=None)
    formattedAddress = Column(String, default=None)
    googleMapsUri = Column(String, default=None)
    editorialSummary = Column(String, default=None)


class Scheduled(Base):
    __tablename__ = "scheduled"
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    attraction_id = Column(String)
    day = Column(DateTime)
    scheduled_at = Column(DateTime, default=datetime.datetime.utcnow)
