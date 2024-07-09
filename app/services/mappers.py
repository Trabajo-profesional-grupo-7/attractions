import json
import os

import requests
from fastapi import HTTPException
from sqlalchemy import DateTime
from sqlalchemy.orm import Session

from app.db import crud, models
from app.routes import schemas
from app.services.constants import ATTRACTION_TYPES


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
        types=json.loads(attraction_db.types),
        avg_rating=attraction_db.external_rating,
    )

    if attraction_db.editorialSummary:
        attraction_schema.editorial_summary = attraction_db.editorialSummary
    if attraction_db.formattedAddress:
        attraction_schema.formatted_address = attraction_db.formattedAddress
    if attraction_db.googleMapsUri:
        attraction_schema.google_maps_uri = attraction_db.googleMapsUri

    return attraction_schema


def map_to_attraction_schema_with_comments(
    db: Session, attraction_db: models.Attractions
) -> schemas.Attraction:

    attraction_schema = schemas.AttractionWithComments(
        attraction_id=attraction_db.attraction_id,
        attraction_name=attraction_db.attraction_name,
        location=schemas.Location(
            latitude=attraction_db.latitude, longitude=attraction_db.longitude
        ),
        country=attraction_db.country,
        city=attraction_db.city,
        photo=attraction_db.photo,
        liked_count=attraction_db.likes_count,
        types=json.loads(attraction_db.types),
        avg_rating=attraction_db.external_rating,
    )

    if attraction_db.editorialSummary:
        attraction_schema.editorial_summary = attraction_db.editorialSummary
    if attraction_db.formattedAddress:
        attraction_schema.formatted_address = attraction_db.formattedAddress
    if attraction_db.googleMapsUri:
        attraction_schema.google_maps_uri = attraction_db.googleMapsUri

    comments = crud.get_attraction_comments(
        db=db, attraction_id=attraction_db.attraction_id
    )
    if comments:
        for comment in comments:
            user_name, avatar_link = get_user_name_and_avatar(user_id=comment.user_id)
            attraction_schema.comments.append(
                schemas.Comment(
                    comment_id=comment.comment_id,
                    user_id=comment.user_id,
                    comment=comment.comment,
                    user_name=user_name,
                    avatar_link=avatar_link,
                )
            )

    return attraction_schema


def map_to_scheduled_attraction_schema(
    attraction_db: models.Attractions, scheduled_day: DateTime
) -> schemas.ScheduledAttraction:

    attraction_schema = schemas.ScheduledAttraction(
        attraction_id=attraction_db.attraction_id,
        attraction_name=attraction_db.attraction_name,
        location=schemas.Location(
            latitude=attraction_db.latitude, longitude=attraction_db.longitude
        ),
        country=attraction_db.country,
        city=attraction_db.city,
        photo=attraction_db.photo,
        liked_count=attraction_db.likes_count,
        types=json.loads(attraction_db.types),
        scheduled_day=scheduled_day,
        avg_rating=attraction_db.external_rating,
    )

    if attraction_db.editorialSummary:
        attraction_schema.editorial_summary = attraction_db.editorialSummary
    if attraction_db.formattedAddress:
        attraction_schema.formatted_address = attraction_db.formattedAddress
    if attraction_db.googleMapsUri:
        attraction_schema.google_maps_uri = attraction_db.googleMapsUri

    return attraction_schema


def map_to_attraction_with_comments_by_user_schema(
    db: Session, attraction_db: models.Attractions, user_id: int
) -> schemas.AttractionWithCommentsByUser:

    attraction_id = attraction_db.attraction_id

    attraction_by_user_schema = schemas.AttractionWithCommentsByUser(
        attraction_id=attraction_id,
        attraction_name=attraction_db.attraction_name,
        location=schemas.Location(
            latitude=attraction_db.latitude, longitude=attraction_db.longitude
        ),
        country=attraction_db.country,
        city=attraction_db.city,
        photo=attraction_db.photo,
        liked_count=attraction_db.likes_count,
        types=json.loads(attraction_db.types),
        avg_rating=attraction_db.external_rating,
    )

    comments = crud.get_attraction_comments(
        db=db, attraction_id=attraction_db.attraction_id
    )
    if comments:
        for comment in comments:
            user_name, avatar_link = get_user_name_and_avatar(user_id=comment.user_id)
            attraction_by_user_schema.comments.append(
                schemas.Comment(
                    comment_id=comment.comment_id,
                    user_id=comment.user_id,
                    comment=comment.comment,
                    user_name=user_name,
                    avatar_link=avatar_link,
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

    if attraction_db.editorialSummary:
        attraction_by_user_schema.editorial_summary = attraction_db.editorialSummary
    if attraction_db.formattedAddress:
        attraction_by_user_schema.formatted_address = attraction_db.formattedAddress
    if attraction_db.googleMapsUri:
        attraction_by_user_schema.google_maps_uri = attraction_db.googleMapsUri

    return attraction_by_user_schema


def map_to_attraction_db(attraction: dict) -> models.Attractions:
    attraction_db = models.Attractions(
        attraction_id=attraction["id"],
        attraction_name=attraction["displayName"]["text"],
        latitude=attraction["location"]["latitude"],
        longitude=attraction["location"]["longitude"],
    )

    attraction_types = []
    for type in attraction["types"]:
        if type in ATTRACTION_TYPES:
            attraction_types.append(type)
    attraction_db.types = json.dumps(attraction_types)

    for element in attraction["addressComponents"]:
        if "locality" in element["types"]:
            attraction_db.city = element["longText"]
        elif "country" in element["types"]:
            attraction_db.country = element["longText"]

    if "photos" in attraction.keys():
        photo_url = attraction["photos"][0]["name"]
        url = f"https://places.googleapis.com/v1/{photo_url}/media?maxHeightPx=400&maxWidthPx=400&key={os.getenv('ATTRACTIONS_API_KEY')}"
        attraction_db.photo = url

    if "rating" in attraction.keys():
        attraction_db.external_rating = attraction["rating"]

    if "formattedAddress" in attraction.keys():
        attraction_db.formattedAddress = attraction["formattedAddress"]

    if "googleMapsUri" in attraction.keys():
        attraction_db.googleMapsUri = attraction["googleMapsUri"]

    if "editorialSummary" in attraction.keys():
        attraction_db.editorialSummary = attraction["editorialSummary"]["text"]

    return attraction_db
