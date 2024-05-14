import datetime
import json
import os
from typing import List, Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response

from app.db import crud
from app.db.database import get_db
from app.routes import schemas
from app.services import attractions_service, mappers, recommendations
from app.services.constants import ATTRACTION_TYPES, MINIMUM_NUMBER_OF_RATINGS
from app.services.logger import Logger

router = APIRouter()


# ATTRACTIONS


@router.get(
    "/metadata",
    status_code=200,
    tags=["Metadata"],
    description="Gets the application metadata",
)
def get_metadata():
    return {"attraction_types": ATTRACTION_TYPES}


@router.get(
    "/attractions/byid/{attraction_id}",
    status_code=200,
    tags=["Get Attractions"],
    description="Gets an attraction given its ID. Can optionally send user ID to get additional information.",
)
def get_attraction(
    attraction_id: str = Path(
        ..., title="Attraction ID", description="The ID of the attraction to get"
    ),
    user_id: Optional[int] = None,
    db=Depends(get_db),
):

    attraction_db = crud.get_attraction_by_id(db=db, attraction_id=attraction_id)

    if not attraction_db:
        attraction_db = attractions_service.get_attraction_by_id(
            attraction_id=attraction_id
        )

        crud.add_attraction(
            db=db,
            attraction_db=attraction_db,
        )

    if user_id != None:
        return mappers.map_to_attraction_by_user_schema(
            db=db, attraction_db=attraction_db, user_id=user_id
        )

    return mappers.map_to_attraction_schema(attraction_db=attraction_db)


@router.post(
    "/attractions/nearby/{latitude}/{longitude}/{radius}",
    status_code=201,
    tags=["Get Attractions"],
    description="Gets nearby attractions given a latitude, longitude and radius. Can optionally filter by a list of attraction types.",
)
def get_nearby_attractions(
    attractions_filter: Optional[
        schemas.AttractionsFilter
    ] = schemas.AttractionsFilter(),
    latitude: float = Path(
        ..., title="Latitude", description="Center latitude for search"
    ),
    longitude: float = Path(
        ..., title="Longitude", description="Center longitude for search"
    ),
    radius: float = Path(
        ..., title="Radius", description="Search radius in meters", le=50000
    ),
    db=Depends(get_db),
):
    attractions = attractions_service.get_nearby_attractions(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        attraction_types=attractions_filter.attraction_types,
    )

    formatted_response = []

    for attraction in attractions:

        attraction_db = crud.get_attraction_by_id(
            db=db, attraction_id=attraction.attraction_id
        )

        if not attraction_db:
            attraction_db = crud.add_attraction(
                db=db,
                attraction_db=attraction,
            )

        formatted_response.append(
            mappers.map_to_attraction_schema(attraction_db=attraction_db)
        )

    return attractions_service.sort_attractions_by_rating(formatted_response)


@router.post(
    "/attractions/search",
    status_code=201,
    tags=["Get Attractions"],
    description="Searches attractions given a text query. Can optionally filter by a certain attraction type.",
)
def search_attractions(
    data: schemas.SearchAttractionsByText,
    type: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    db=Depends(get_db),
):
    attractions = attractions_service.search_attractions(
        query=data.query, type=type, latitude=latitude, longitude=longitude
    )

    formatted_response = []

    for attraction in attractions:

        attraction_db = crud.get_attraction_by_id(
            db=db, attraction_id=attraction.attraction_id
        )

        if not attraction_db:
            attraction_db = crud.add_attraction(
                db=db,
                attraction_db=attraction,
            )

        formatted_response.append(
            mappers.map_to_attraction_schema(attraction_db=attraction_db)
        )

    return attractions_service.sort_attractions_by_rating(formatted_response)


@router.get(
    "/attractions/location",
    status_code=200,
    tags=["Get attractions location"],
)
def get_attraction_location(text: str):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("ATTRACTIONS_API_KEY"),
        "X-Goog-FieldMask": "places.location",
    }

    response = requests.post(url, json={"textQuery": text}, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": f"External API error: {response.status_code}",
            },
        )

    return response.json()


@router.post(
    "/attractions/autocomplete",
    status_code=201,
    tags=["Get Attractions"],
    description="Returns attractions predictions given a substring. Can optionally filter by a list of attraction types.",
)
def autocomplete_attractions(
    data: schemas.AutocompleteAttractions,
    attraction_types: List[str] = Query(
        None,
        title="Attraction Types",
        description="Filter by attraction types",
    ),
):
    return attractions_service.autocomplete(
        query=data.query, attraction_types=attraction_types
    )


@router.get(
    "/attractions/recommendations/{user_id}",
    status_code=200,
    tags=["Recommendations"],
    description="Gets recommended attractions for a given user ID",
)
def get_feed(
    user_id: int = Path(..., title="User ID", description="The ID of the user"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db=Depends(get_db),
):

    feed = attractions_service.get_feed(user_id=user_id, page=page, size=size)

    formatted_response = []

    for attraction_id in feed:
        attraction_db = crud.get_attraction_by_id(db=db, attraction_id=attraction_id)

        if not attraction_db:
            attraction_db = crud.add_attraction(
                db=db,
                attraction_db=attractions_service.get_attraction_by_id(
                    attraction_id=attraction_id
                ),
            )

        formatted_response.append(
            mappers.map_to_attraction_schema(attraction_db=attraction_db)
        )

    return attractions_service.sort_attractions_by_rating(formatted_response)


@router.post(
    "/attractions/run-recommendation-system",
    status_code=201,
    tags=["Recommendations"],
    description="Runs the recommendation system",
)
def run_recommendation_system(db=Depends(get_db)):
    recommendations.run_recommendation_system(db=db)


@router.put(
    "/update_recommendations/",
    status_code=201,
    tags=["Recommendations"],
    description="Updates the recommendations for a certain user given preferences and default city",
)
def update_recommendations(request: schemas.UpdateRecommendations, db=Depends(get_db)):
    n = crud.number_of_interactions_of_user(db=db, user_id=request.user_id)
    Logger().info(f"User {request.user_id} has {n} interactions")
    if (
        crud.number_of_interactions_of_user(db=db, user_id=request.user_id)
        < MINIMUM_NUMBER_OF_RATINGS
    ):
        attractions = []

        for preference in request.preferences:
            for attraction in attractions_service.search_attractions(
                query=f"{preference} in {request.default_city}"
            ):
                attractions.append(attraction)

        for attraction in attractions:
            attraction_db = crud.get_attraction_by_id(
                db=db, attraction_id=attraction.attraction_id
            )

            if not attraction_db:
                attraction_db = crud.add_attraction(
                    db=db,
                    attraction_db=attraction,
                )

        attractions = sorted(
            attractions,
            key=lambda x: (x.external_rating if x.external_rating is not None else 0),
            reverse=True,
        )

        recommendations.update_recommendations(
            user_id=request.user_id,
            attractions_ids=[x.attraction_id for x in attractions],
        )

        response = Response(status_code=200)
        response.headers["X-Message"] = (
            f"Recommendations for user {request.user_id} updated successfully"
        )
        return response

    response = Response(status_code=422)
    response.headers["message"] = (
        f"Recommendations were not updated because user {request.user_id} does not yet have a sufficient number of ratings made"
    )
    return response


@router.put(
    "/create_plan/",
    status_code=201,
    tags=["Recommendations"],
    description="Returns recommended attractions to visit a city for a certain user",
)
def create_plan(
    data: schemas.CreatePlan,
    db=Depends(get_db),
):

    attractions_ids = recommendations.get_recommendations_for_user_in_city(
        db=db, user_id=data.user_id, city=data.city
    )

    formatted_response = []

    for attraction_id in attractions_ids:
        attraction_db = crud.get_attraction_by_id(db=db, attraction_id=attraction_id)

        if not attraction_db:
            attraction_db = crud.add_attraction(
                db=db,
                attraction_db=attractions_service.get_attraction_by_id(
                    attraction_id=attraction_id
                ),
            )

        formatted_response.append(
            mappers.map_to_attraction_schema(attraction_db=attraction_db)
        )

    return formatted_response


# SAVE


@router.post(
    "/attractions/save",
    status_code=201,
    tags=["Save Attraction"],
    description="Saves an attraction for a user",
)
def save_attraction(data: schemas.SaveAttraction, db=Depends(get_db)):
    attraction_db = crud.get_attraction_by_id(db=db, attraction_id=data.attraction_id)

    if not attraction_db:
        attraction_db = crud.add_attraction(
            db=db,
            attraction_db=attractions_service.get_attraction_by_id(
                attraction_id=data.attraction_id
            ),
        )

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
    attractions = crud.get_user_saved_attractions(
        db=db, user_id=user_id, page=page, size=size
    )

    formatted_response = []

    for attraction_db in attractions:
        formatted_response.append(
            mappers.map_to_attraction_schema(attraction_db=attraction_db)
        )
    return formatted_response


# LIKE


@router.post(
    "/attractions/like",
    status_code=201,
    tags=["Like Attraction"],
    description="Likes an attraction for a user",
)
def like_attraction(data: schemas.LikeAttraction, db=Depends(get_db)):
    attraction_db = crud.get_attraction_by_id(db=db, attraction_id=data.attraction_id)

    if not attraction_db:
        attraction_db = crud.add_attraction(
            db=db,
            attraction_db=attractions_service.get_attraction_by_id(
                attraction_id=data.attraction_id
            ),
        )

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


# DONE


@router.post(
    "/attractions/done",
    status_code=201,
    tags=["Done Attraction"],
    description="Marks as done a attraction for a user",
)
def mark_as_done_attraction(data: schemas.MarkAsDoneAttraction, db=Depends(get_db)):
    attraction_db = crud.get_attraction_by_id(db=db, attraction_id=data.attraction_id)

    if not attraction_db:
        attraction_db = crud.add_attraction(
            db=db,
            attraction_db=attractions_service.get_attraction_by_id(
                attraction_id=data.attraction_id
            ),
        )

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
    attractions = crud.get_user_done_attractions(
        db=db, user_id=user_id, page=page, size=size
    )

    formatted_response = []

    for attraction_db in attractions:
        formatted_response.append(
            mappers.map_to_attraction_schema(attraction_db=attraction_db)
        )
    return formatted_response


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

    attraction_db = crud.get_attraction_by_id(db=db, attraction_id=data.attraction_id)

    if not attraction_db:
        attraction_db = crud.add_attraction(
            db=db,
            attraction_db=attractions_service.get_attraction_by_id(
                attraction_id=data.attraction_id
            ),
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
    attraction_db = crud.get_attraction_by_id(db=db, attraction_id=data.attraction_id)

    if not attraction_db:
        attraction_db = crud.add_attraction(
            db=db,
            attraction_db=attractions_service.get_attraction_by_id(
                attraction_id=data.attraction_id
            ),
        )

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
    if data.datetime < datetime.datetime.now(datetime.timezone.utc):
        Logger().info("Cannot schedule an attraction for a date before today")
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Cannot schedule an attraction for a date before today",
            },
        )

    attraction_db = crud.get_attraction_by_id(db=db, attraction_id=data.attraction_id)

    if not attraction_db:
        attraction_db = crud.add_attraction(
            db=db,
            attraction_db=attractions_service.get_attraction_by_id(
                attraction_id=data.attraction_id
            ),
        )

    if not crud.check_if_schedule_is_valid(
        db=db,
        user_id=data.user_id,
        attraction_id=data.attraction_id,
        datetime=data.datetime,
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
        datetime=data.datetime,
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
    attractions = crud.get_user_scheduled_list(
        db=db, user_id=user_id, page=page, size=size
    )

    formatted_response = []

    for attraction_db in attractions:
        formatted_response.append(
            mappers.map_to_attraction_schema(attraction_db=attraction_db)
        )
    return formatted_response


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
        new_datetime=data.new_datetime,
    )
