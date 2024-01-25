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