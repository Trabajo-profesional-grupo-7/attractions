import json
import os

import requests
from fastapi import HTTPException


def get_user_name_and_avatar(user_id: int):
    url = f"{os.getenv('USERS_URL')}/{user_id}"

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )
    response = json.loads(response.content)
    return response["username"], response["avatar_link"]
