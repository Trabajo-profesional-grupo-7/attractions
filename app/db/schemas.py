from datetime import date, datetime

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
    user_id: int
    query: str


class AutocompleteAttractions(BaseModel):
    query: str


class ScheduleAttraction(BaseModel):
    user_id: int
    attraction_id: str
    day: date


class UnscheduleAttraction(BaseModel):
    schedule_id: int


class UpdateSchedule(BaseModel):
    schedule_id: int
    new_day: date
