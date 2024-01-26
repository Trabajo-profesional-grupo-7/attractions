from fastapi import APIRouter
from fastapi import Depends, HTTPException, Query
from app.db import crud, schemas
from app.db.database import SessionLocal, get_db
from app.services.logger import Logger


router = APIRouter()


# SAVE


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
            detail={
                "status": "error",
                "message": "Attraction has not been saved by user",
            },
        )
    crud.unsave_attraction(db=db, attraction_to_unsave=saved_attraction)


@router.get(
    "/attractions/save-list",
    status_code=200,
    tags=["Attractions"],
    description="Returns a list of the attractions saved by an user",
)
def get_saved_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: SessionLocal = Depends(get_db),
):
    data = schemas.GetSavedAttractions(user_id=user_id, page=page, size=size)
    return crud.get_saved_attractions_list(db=db, data=data)


# LIKE


@router.post(
    "/attractions/like",
    status_code=201,
    tags=["Attractions"],
    description="Likes an attraction for a user",
)
def like_attraction(data: schemas.LikeAttraction, db: SessionLocal = Depends(get_db)):
    if crud.get_liked_attraction(
        db=db, user_id=data.user_id, attraction_id=data.attraction_id
    ):
        Logger().info("Attraction already liked by user")
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Attraction already liked by user"},
        )
    return crud.like_attraction(db=db, data=data)


@router.delete(
    "/attractions/unlike",
    status_code=204,
    tags=["Attractions"],
    description="Unlikes an attraction for a user",
)
def unlike_attraction(data: schemas.LikeAttraction, db: SessionLocal = Depends(get_db)):
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
    tags=["Attractions"],
    description="Returns a list of the attractions liked by an user",
)
def get_liked_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: SessionLocal = Depends(get_db),
):
    data = schemas.GetLikedAttractions(user_id=user_id, page=page, size=size)
    return crud.get_liked_attractions_list(db=db, data=data)


# DONE


@router.post(
    "/attractions/done",
    status_code=201,
    tags=["Attractions"],
    description="Marks as done a attraction for a user",
)
def mark_as_done_attraction(
    data: schemas.MarkAsDoneAttraction, db: SessionLocal = Depends(get_db)
):
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
    return crud.mark_as_done_attraction(db=db, data=data)


@router.delete(
    "/attractions/undone",
    status_code=204,
    tags=["Attractions"],
    description="Marks as undone an attraction for a user",
)
def mark_as_undone_attraction(
    data: schemas.MarkAsDoneAttraction, db: SessionLocal = Depends(get_db)
):
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
    tags=["Attractions"],
    description="Returns a list of the attractions done by an user",
)
def get_done_attractions_list(
    user_id: int = Query(..., description="User ID"),
    page: int = Query(0, description="Page number", ge=0),
    size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: SessionLocal = Depends(get_db),
):
    data = {"user_id": user_id, "page": page, "size": size}
    return crud.get_done_attractions_list(db=db, data=data)


# RATE


@router.post(
    "/attractions/rate",
    status_code=201,
    tags=["Attractions"],
    description="Rates an attraction by an user",
)
def rate_attraction(data: schemas.RateAttraction, db: SessionLocal = Depends(get_db)):
    return crud.rate_attraction(db=db, data=data)


# COMMENT


@router.post(
    "/attractions/comment",
    status_code=201,
    tags=["Attractions"],
    description="Comments an attraction for an user",
)
def comment_attraction(
    data: schemas.CommentAttraction, db: SessionLocal = Depends(get_db)
):
    return crud.add_comment(db=db, data=data)


@router.delete(
    "/attractions/comment",
    status_code=204,
    tags=["Attractions"],
    description="Deletes a comment by comment_id",
)
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


@router.put(
    "/attractions/comment",
    status_code=201,
    tags=["Attractions"],
    description="Edits a comment by comment_id",
)
def update_comment(
    data: schemas.UpdateComment,
    db: SessionLocal = Depends(get_db),
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
