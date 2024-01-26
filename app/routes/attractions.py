from fastapi import APIRouter
from fastapi import Depends, HTTPException, Query

from app.db import crud, schemas
from app.db.database import SessionLocal, get_db
from app.services.logger import Logger

router = APIRouter()


@router.post(
    "/attractions/save",
    status_code=201,
    tags=["Attractions"],
    description="Saves an attraction for a user",
)
def save_attraction(data: schemas.SaveAttraction, db: SessionLocal = Depends(get_db)):
    if crud.get_saved_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    ):
        Logger().info("Attraction already saved by user")
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Attraction already saved by user"},
        )
    return crud.save_attraction(db=db, data=data)


@router.delete(
    "/attractions/unsave",
    status_code=204,
    tags=["Attractions"],
    description="Unsaves an attraction for a user",
)
def unsave_attraction(data: schemas.SaveAttraction, db: SessionLocal = Depends(get_db)):
    saved_attraction = crud.get_saved_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    )
    if not saved_attraction:
        Logger().info("Attraction has not been saved by user")
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Attraction has not been saved by user"},
        )
    crud.delete_record(db=db, record=saved_attraction)


@router.get(
    "/attractions/save-list",
    status_code=200,
    tags=["Attractions"],
    description="Returns a list of the saved attractions of an user",
)
def get_saved_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: SessionLocal = Depends(get_db),
):
    data = schemas.GetSavedAttractions(user_id=user_id, page=page, size=size)
    return crud.get_saved_attractions_list(db=db, data=data)


@router.get("/attractions/like-list", status_code=201, tags=["Attractions"])
def get_liked_attractions(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: SessionLocal = Depends(get_db),
):
    data = {"user_id": user_id, "page": page, "size": size}
    return crud.get_liked_attractions(db=db, data=data)


@router.post("/attractions/like", status_code=201, tags=["Attractions"])
def like_attraction(data: schemas.LikeAttraction, db: SessionLocal = Depends(get_db)):
    return crud.like_attraction(db=db, data=data)


@router.get("/attractions/likes", status_code=201, tags=["Attractions"])
def get_likes(
    attraction_id: int = Query(..., description="Attraction ID"),
    db: SessionLocal = Depends(get_db),
):
    data = schemas.GetLikes(attraction_id=attraction_id)
    return crud.get_likes(db=db, data=data)


@router.get("/attractions/done-list", status_code=201, tags=["Attractions"])
def get_done_attractions(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: SessionLocal = Depends(get_db),
):
    data = {"user_id": user_id, "page": page, "size": size}
    return crud.get_done_attractions(db=db, data=data)


@router.post("/attractions/done", status_code=201, tags=["Attractions"])
def mark_as_done(
    data: schemas.MarkAsDoneAttraction, db: SessionLocal = Depends(get_db)
):
    return crud.mark_as_done(db=db, data=data)


@router.post("/attractions/rate", status_code=201, tags=["Attractions"])
def rate_attraction(data: schemas.RateAttraction, db: SessionLocal = Depends(get_db)):
    return crud.rate_attraction(db=db, data=data)


@router.get("/attractions/avg-attraction-rating", status_code=201, tags=["Attractions"])
def get_avg_attraction_rating(
    attraction_id: int = Query(..., description="Attraction ID"),
    db: SessionLocal = Depends(get_db),
):
    data = schemas.GetAvgAttractionRating(attraction_id=attraction_id)
    return crud.get_avg_attraction_rating(db=db, data=data)


@router.post("/attractions/comment", status_code=201, tags=["Attractions"])
def comment_attraction(
    data: schemas.CommentAttraction, db: SessionLocal = Depends(get_db)
):
    return crud.comment_attraction(db=db, data=data)


@router.delete("/attractions/comment", status_code=204, tags=["Attractions"])
def delete_comment(
    data: schemas.DeleteCommentAttraction, db: SessionLocal = Depends(get_db)
):
    comment = crud.get_comment_by_id(db, comment_id=data.comment_id)
    if not comment:
        Logger().info("Comment not found")
        raise HTTPException(
            status_code=404, detail={"status": "error", "message": "Comment not found"}
        )
    crud.delete_record(db=db, record=comment)
