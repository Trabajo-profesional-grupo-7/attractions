from datetime import datetime
from pydantic import BaseModel


class SaveAttraction(BaseModel):
    user_id: int
    attraction_id: str


class GetSavedAttractions(BaseModel):
    user_id: int
    size: int
    page: int


class MarkAsDoneAttraction(BaseModel):
    user_id: int
    attraction_id: str


class GetDoneAttractions(BaseModel):
    user_id: int
    size: int
    page: int


class LikeAttraction(BaseModel):
    user_id: int
    attraction_id: str


class GetLikedAttractions(BaseModel):
    user_id: int
    size: int
    page: int


class GetLikes(BaseModel):
    attraction_id: str


class RateAttraction(BaseModel):
    user_id: int
    attraction_id: str
    rating: int


class GetAvgAttractionRating(BaseModel):
    attraction_id: str


class CommentAttraction(BaseModel):
    user_id: int
    attraction_id: str
    comment: str


class DeleteCommentAttraction(BaseModel):
    comment_id: int


class UpdateComment(BaseModel):
    comment_id: int
    new_comment: str


class Comment(BaseModel):
    comment_id: int
    user_id: int
    attraction_id: str
    comment: str


class SearchTextRequest(BaseModel):
    textQuery: str
