import os
from typing import List, Optional

import boto3
import requests
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.db import crud, schemas
from app.db.database import get_db
from app.services.logger import Logger

router = APIRouter()


# ATTRACTIONS


@router.get(
    "/attractions/byid/{attraction_id}",
    status_code=201,
    tags=["Get Attractions"],
    description="Gets an attraction given its ID",
)
def get_attraction(
    attraction_id: str = Path(
        ..., title="Attraction ID", description="The ID of the attraction to get"
    ),
    db=Depends(get_db),
):
    url = f"https://places.googleapis.com/v1/places/{attraction_id}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
        "X-Goog-FieldMask": "displayName,id,addressComponents,photos",
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    response = response.json()

    return crud.format_attraction(db=db, attraction=response)


@router.post(
    "/attractions/nearby/{latitude}/{longitude}/{radius}",
    status_code=201,
    tags=["Get Attractions"],
    description="Gets nearby attractions given a latitude and longitude. Can filter by a list of attraction types.",
)
def get_nearby_attractions(
    latitude: float = Path(
        ..., title="Latitude", description="Center latitude for search"
    ),
    longitude: float = Path(
        ..., title="Longitude", description="Center longitude for search"
    ),
    radius: float = Path(..., title="Radius", description="Search radius in meters"),
    attraction_types: List[str] = Query(
        None,
        title="Attraction Types",
        description="Filter by attraction types",
    ),
    db=Depends(get_db),
):
    url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
        "X-Goog-FieldMask": "places.displayName,places.id,places.addressComponents,places.photos",
    }

    data = {
        "includedTypes": attraction_types,
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius,
            }
        },
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    formatted_response = []

    if "places" in response.json().keys():
        for attraction in response.json()["places"]:
            formatted_response.append(
                crud.format_attraction(db=db, attraction=attraction)
            )

    return formatted_response


@router.post(
    "/attractions/search",
    status_code=201,
    tags=["Get Attractions"],
    description="Searches attractions given a text query. Can filter by a certain attraction type.",
)
def search_attractions(
    data: schemas.SearchAttractionsByText,
    type: Optional[str] = None,
    db=Depends(get_db),
):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
        "X-Goog-FieldMask": "places.displayName,places.id,places.addressComponents,places.photos",
    }

    response = requests.post(
        url, json={"textQuery": data.query, "includedType": type}, headers=headers
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    crud.add_search(db=db, user_id=data.user_id, query=data.query)

    formatted_response = []

    if "places" in response.json().keys():
        for attraction in response.json()["places"]:
            formatted_response.append(
                crud.format_attraction(db=db, attraction=attraction)
            )

    return formatted_response


@router.get(
    "/attractions/recommendations/{attraction_id}",
    status_code=201,
    tags=["Get Attractions"],
    description="Gets similar attractions given an attraction ID",
)
def get_attraction_recommendations(
    attraction_id: str = Path(
        ..., title="Attraction ID", description="The ID of the attraction"
    ),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
):

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    dynamodb = session.resource("dynamodb", region_name="us-east-2")

    table_name = "attractions"
    table = dynamodb.Table(table_name)

    key = {"attraction_id": attraction_id}
    response = table.get_item(Key=key)
    recommendations = response.get("Item")

    if not recommendations:
        Logger().info("No similar attractions were found")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "No similar attractions were found",
            },
        )

    return recommendations["similar_attractions"][page * size : (page + 1) * size]


# SAVE


@router.post(
    "/attractions/save",
    status_code=201,
    tags=["Save Attraction"],
    description="Saves an attraction for a user",
)
def save_attraction(data: schemas.SaveAttraction, db=Depends(get_db)):
    if crud.get_saved_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    ):
        Logger().info("Attraction already saved by user")
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Attraction already saved by user"},
        )
    return crud.save_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )


@router.delete(
    "/attractions/unsave",
    status_code=204,
    tags=["Save Attraction"],
    description="Unsaves an attraction for a user",
)
def unsave_attraction(data: schemas.SaveAttraction, db=Depends(get_db)):
    saved_attraction = crud.get_saved_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )
    if not saved_attraction:
        Logger().info("Attraction has not been saved by user")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Attraction has not been saved by user",
            },
        )
    crud.unsave_attraction(db=db, attraction_to_unsave=saved_attraction)


@router.get(
    "/attractions/save-list",
    status_code=200,
    tags=["Save Attraction"],
    description="Returns a list of the attractions saved by an user",
)
def get_saved_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db=Depends(get_db),
):
    return crud.get_saved_attractions_list(db=db, user_id=user_id, page=page, size=size)


# LIKE


@router.post(
    "/attractions/like",
    status_code=201,
    tags=["Like Attraction"],
    description="Likes an attraction for a user",
)
def like_attraction(data: schemas.LikeAttraction, db=Depends(get_db)):
    if crud.get_liked_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    ):
        Logger().info("Attraction already liked by user")
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Attraction already liked by user"},
        )
    return crud.like_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )


@router.delete(
    "/attractions/unlike",
    status_code=204,
    tags=["Like Attraction"],
    description="Unlikes an attraction for a user",
)
def unlike_attraction(data: schemas.LikeAttraction, db=Depends(get_db)):
    liked_attraction = crud.get_liked_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )
    if not liked_attraction:
        Logger().info("Attraction has not been liked by user")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Attraction has not been liked by user",
            },
        )
    crud.unlike_attraction(db=db, attraction_to_unlike=liked_attraction)


@router.get(
    "/attractions/like-list",
    status_code=200,
    tags=["Like Attraction"],
    description="Returns a list of the attractions liked by an user",
)
def get_liked_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db=Depends(get_db),
):
    return crud.get_liked_attractions_list(db=db, user_id=user_id, page=page, size=size)


# DONE


@router.post(
    "/attractions/done",
    status_code=201,
    tags=["Done Attraction"],
    description="Marks as done a attraction for a user",
)
def mark_as_done_attraction(data: schemas.MarkAsDoneAttraction, db=Depends(get_db)):
    if crud.get_done_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    ):
        Logger().info("Attraction already marked as done by user")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Attraction already marked as done by user",
            },
        )
    return crud.mark_as_done_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )


@router.delete(
    "/attractions/undone",
    status_code=204,
    tags=["Done Attraction"],
    description="Marks as undone an attraction for a user",
)
def mark_as_undone_attraction(data: schemas.MarkAsDoneAttraction, db=Depends(get_db)):
    done_attraction = crud.get_done_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )
    if not done_attraction:
        Logger().info("Attraction has not been marked as done by user")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Attraction has not been marked as done by user",
            },
        )
    crud.mark_as_undone_attraction(db=db, attraction_to_mark_as_undone=done_attraction)


@router.get(
    "/attractions/done-list",
    status_code=200,
    tags=["Done Attraction"],
    description="Returns a list of the attractions done by an user",
)
def get_done_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db=Depends(get_db),
):
    return crud.get_done_attractions_list(db=db, user_id=user_id, page=page, size=size)


# RATE


@router.post(
    "/attractions/rate",
    status_code=201,
    tags=["Rate Attraction"],
    description="Rates an attraction by an user",
)
def rate_attraction(data: schemas.AddRating, db=Depends(get_db)):
    if not 1 <= data.rating <= 5:
        Logger().info("Rating must be between 1 and 5")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Rating must be between 1 and 5",
            },
        )

    rating = crud.get_rating(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )

    if not rating:
        return crud.rate_attraction(
            db=db,
            user_id=data.user_id,
            attraction_id=data.attraction_id,
            rating=data.rating,
        )

    return crud.update_rating(db=db, rating_to_update=rating, new_rating=data.rating)


# COMMENT


@router.post(
    "/attractions/comment",
    status_code=201,
    tags=["Comment Attraction"],
    description="Comments an attraction for an user",
)
def comment_attraction(data: schemas.AddComment, db=Depends(get_db)):
    return crud.add_comment(
        db=db,
        user_id=data.user_id,
        attraction_id=data.attraction_id,
        comment=data.comment,
    )


@router.delete(
    "/attractions/comment",
    status_code=204,
    tags=["Comment Attraction"],
    description="Deletes a comment by comment_id",
)
def delete_comment(data: schemas.DeleteComment, db=Depends(get_db)):
    comment = crud.get_comment_by_id(db, comment_id=data.comment_id)
    if not comment:
        Logger().info("Comment not found")
        raise HTTPException(
            status_code=404, detail={"status": "error", "message": "Comment not found"}
        )
    crud.delete_comment(db=db, comment_to_delete=comment)


@router.put(
    "/attractions/comment",
    status_code=201,
    tags=["Comment Attraction"],
    description="Edits a comment by comment_id",
)
def update_comment(
    data: schemas.UpdateComment,
    db=Depends(get_db),
):
    comment = crud.get_comment_by_id(db, comment_id=data.comment_id)
    if not comment:
        Logger().info("Comment not found")
        raise HTTPException(
            status_code=404, detail={"status": "error", "message": "Comment not found"}
        )
    return crud.update_comment(
        db=db, comment_to_edit=comment, updated_comment=data.new_comment
    )


# SCHEDULE


@router.post(
    "/attractions/schedule",
    status_code=201,
    tags=["Schedule Attraction"],
    description="Schedules an attraction for a user at a certain timestamp",
)
def schedule_attraction(data: schemas.ScheduleAttraction, db=Depends(get_db)):
    if not crud.check_if_schedule_is_valid(
        db=db,
        user_id=data.user_id,
        attraction_id=data.attraction_id,
        day=data.day,
    ):
        Logger().info(
            "Attraction has already been scheduled by user for specified date"
        )
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Attraction has already been scheduled by user for specified date",
            },
        )

    return crud.schedule_attraction(
        db=db,
        user_id=data.user_id,
        attraction_id=data.attraction_id,
        day=data.day,
    )


@router.delete(
    "/attractions/unschedule",
    status_code=204,
    tags=["Schedule Attraction"],
    description="Unschedules an attraction for a user",
)
def unschedule_attraction(data: schemas.UnscheduleAttraction, db=Depends(get_db)):
    scheduled_attraction = crud.get_scheduled_attraction_by_id(
        db=db, schedule_id=data.schedule_id
    )
    if not scheduled_attraction:
        Logger().info("Attraction has not been scheduled by user")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Attraction has not been scheduled by user",
            },
        )
    crud.unschedule_attraction(db=db, attraction_to_unschedule=scheduled_attraction)


@router.get(
    "/attractions/scheduled-list",
    status_code=200,
    tags=["Schedule Attraction"],
    description="Returns a list of the attractions scheduled by an user",
)
def get_scheduled_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db=Depends(get_db),
):
    return crud.get_scheduled_attractions_list(
        db=db, user_id=user_id, page=page, size=size
    )


@router.put(
    "/attractions/schedule",
    status_code=201,
    tags=["Schedule Attraction"],
    description="Edits a scheduled attraction by schedule_id",
)
def update_schedule(
    data: schemas.UpdateSchedule,
    db=Depends(get_db),
):
    scheduled_attraction = crud.get_scheduled_attraction_by_id(
        db=db, schedule_id=data.schedule_id
    )
    if not scheduled_attraction:
        Logger().info("Scheduled attraction not found")
        raise HTTPException(
            status_code=404, detail={"status": "error", "message": "Comment not found"}
        )
    return crud.update_scheduled_attraction(
        db=db,
        scheduled_to_update=scheduled_attraction,
        new_day=data.new_day,
    )
