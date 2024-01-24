from pydantic import BaseModel


class PostAttraction(BaseModel):
    user_id: int
    attraction_id: int
