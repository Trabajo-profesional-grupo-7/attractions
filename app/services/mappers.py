import os

from sqlalchemy.orm import Session

from app.db import crud, models
from app.routes import schemas


def map_to_attraction_schema(attraction_db: models.Attractions) -> schemas.Attraction:

    attraction_schema = schemas.Attraction(
        attraction_id=attraction_db.attraction_id,
        attraction_name=attraction_db.attraction_name,
        location=schemas.Location(
            latitude=attraction_db.latitude, longitude=attraction_db.longitude
        ),
        country=attraction_db.country,
        city=attraction_db.city,
        photo=attraction_db.photo,
        liked_count=attraction_db.likes_count,
    )

    if attraction_db.rating_count > 0:
        attraction_schema.avg_rating = (
            attraction_db.rating_total / attraction_db.rating_count
        )

    return attraction_schema


def map_to_attraction_by_user_schema(
    db: Session, attraction_db: models.Attractions, user_id: int
) -> schemas.AttractionByUser:

    attraction_id = attraction_db.attraction_id

    attraction_by_user_schema = schemas.AttractionByUser(
        attraction_id=attraction_id,
        attraction_name=attraction_db.attraction_name,
        location=schemas.Location(
            latitude=attraction_db.latitude, longitude=attraction_db.longitude
        ),
        country=attraction_db.country,
        city=attraction_db.city,
        photo=attraction_db.photo,
        liked_count=attraction_db.likes_count,
    )

    comments = crud.get_attraction_comments(
        db=db, attraction_id=attraction_db.attraction_id
    )
    if comments:
        for comment in comments:
            attraction_by_user_schema.comments.append(
                schemas.Comment(
                    comment_id=comment.comment_id,
                    user_id=comment.user_id,
                    comment=comment.comment,
                )
            )

    attraction_by_user_schema.is_liked = crud.get_user_liked_attractions(
        db=db, attraction_id=attraction_id, user_id=user_id
    )

    attraction_by_user_schema.is_done = crud.user_did_attraction(
        db=db, attraction_id=attraction_id, user_id=user_id
    )

    attraction_by_user_schema.is_saved = crud.user_saved_attraction(
        db=db, attraction_id=attraction_id, user_id=user_id
    )

    attraction_by_user_schema.user_rating = crud.get_user_rating(
        db=db, attraction_id=attraction_id, user_id=user_id
    )

    if attraction_db.rating_count > 0:
        attraction_by_user_schema.avg_rating = (
            attraction_db.rating_total / attraction_db.rating_count
        )

    return attraction_by_user_schema


def map_to_attraction_db(attraction: dict) -> models.Attractions:
    attraction_db = models.Attractions(
        attraction_id=attraction["id"],
        attraction_name=attraction["displayName"]["text"],
        latitude=attraction["location"]["latitude"],
        longitude=attraction["location"]["longitude"],
    )

    for element in attraction["addressComponents"]:
        if "locality" in element["types"]:
            attraction_db.city = element["longText"]
        elif "country" in element["types"]:
            attraction_db.country = element["longText"]

    if "photos" in attraction.keys():
        photo_url = attraction["photos"][0]["name"]
        url = f"https://places.googleapis.com/v1/{photo_url}/media?maxHeightPx=400&maxWidthPx=400&key={os.getenv('ATTRACTIONS_API_KEY')}"
        attraction_db.photo = url

    return attraction_db