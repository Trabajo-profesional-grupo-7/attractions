from datetime import datetime
from pydantic import BaseModel


class SaveAttraction(BaseModel):
    user_id: int
    attraction_id: int
