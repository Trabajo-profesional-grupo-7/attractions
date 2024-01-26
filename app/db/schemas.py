from datetime import datetime
from pydantic import BaseModel


class SaveAttraction(BaseModel):
    user_id: int
    attraction_id: int


class GetSavedAttractions(BaseModel):
    user_id: int
    size: int
    page: int


class MarkAsDoneAttraction(BaseModel):
    user_id: int
    attraction_id: int


class GetDoneAttractions(BaseModel):
    user_id: int
    size: int
    page: int


class LikeAttraction(BaseModel):
    user_id: int
    attraction_id: int


class GetLikedAttractions(BaseModel):
    user_id: int
    size: int
    page: int


class GetLikes(BaseModel):
    attraction_id: int


class RateAttraction(BaseModel):
    user_id: int
    attraction_id: int
    rating: int


class GetAvgAttractionRating(BaseModel):
    attraction_id: int


class CommentAttraction(BaseModel):
    user_id: int
    attraction_id: int
    comment: str


class DeleteCommentAttraction(BaseModel):
    comment_id: int