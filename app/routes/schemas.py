from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SaveAttraction(BaseModel):
    user_id: int
    attraction_id: str


class MarkAsDoneAttraction(BaseModel):
    user_id: int
    attraction_id: str


class LikeAttraction(BaseModel):
    user_id: int
    attraction_id: str


class AddRating(BaseModel):
    user_id: int
    attraction_id: str
    rating: int


class AddComment(BaseModel):
    user_id: int
    attraction_id: str
    comment: str


class DeleteComment(BaseModel):
    comment_id: int


class UpdateComment(BaseModel):
    comment_id: int
    new_comment: str


class SearchAttractionsByText(BaseModel):
    query: str


class AutocompleteAttractions(BaseModel):
    query: str


class ScheduleAttraction(BaseModel):
    user_id: int
    attraction_id: str
    datetime: datetime


class UnscheduleAttraction(BaseModel):
    schedule_id: int


class UpdateSchedule(BaseModel):
    schedule_id: int
    new_datetime: datetime


class Comment(BaseModel):
    comment_id: int
    user_id: int
    comment: str
    user_name: str


class Location(BaseModel):
    latitude: float
    longitude: float


class AttractionsFilter(BaseModel):
    attraction_types: Optional[List[str]] = None


class AttractionWithCommentsByUser(BaseModel):
    attraction_id: str
    attraction_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    location: Optional[Location] = None
    photo: Optional[str] = None
    avg_rating: Optional[float] = None
    liked_count: int = 0
    types: List[str] = []
    formattedAddress: str = None
    googleMapsUri: str = None
    editorialSummary: str = None
    is_liked: bool = False
    is_saved: bool = False
    user_rating: int = None
    is_done: bool = False
    comments: List[Comment] = []


class Attraction(BaseModel):
    attraction_id: str
    attraction_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    location: Optional[Location] = None
    photo: Optional[str] = None
    avg_rating: Optional[float] = None
    liked_count: int = 0
    types: List[str] = []
    formattedAddress: str = None
    googleMapsUri: str = None
    editorialSummary: str = None


class AttractionWithComments(BaseModel):
    attraction_id: str
    attraction_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    location: Optional[Location] = None
    photo: Optional[str] = None
    avg_rating: Optional[float] = None
    liked_count: int = 0
    types: List[str] = []
    formattedAddress: str = None
    googleMapsUri: str = None
    editorialSummary: str = None
    comments: List[Comment] = []


class ScheduledAttraction(BaseModel):
    attraction_id: str
    attraction_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    location: Optional[Location] = None
    photo: Optional[str] = None
    avg_rating: Optional[float] = None
    liked_count: int = 0
    types: List[str] = []
    scheduled_day: datetime
    formattedAddress: str = None
    googleMapsUri: str = None
    editorialSummary: str = None


class UpdateRecommendations(BaseModel):
    user_id: int
    default_city: str
    preferences: List[str] = []


class CreatePlan(BaseModel):
    user_id: int
    city: str
    preferences: List[str] = []
