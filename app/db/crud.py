from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import func


# SAVE


def get_saved_attraction(db: Session, user_id: int, attraction_id: int):
    return (
        db.query(models.SavedAttractions)
        .filter(
            models.SavedAttractions.user_id == user_id,
            models.SavedAttractions.attraction_id == attraction_id,
        )
        .first()
    )


def save_attraction(db: Session, data: schemas.SaveAttraction):
    new_record = models.SavedAttractions(
        user_id=data.user_id, attraction_id=data.attraction_id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def get_saved_attractions_list(db: Session, data: schemas.GetSavedAttractions):
    return (
        db.query(models.SavedAttractions)
        .filter(models.SavedAttractions.user_id == data.user_id)
        .offset(data.page)
        .limit(data.size)
        .all()
    )


# LIKE


def get_liked_attraction(db: Session, user_id: int, attraction_id: int):
    return (
        db.query(models.AttractionLikes)
        .filter(
            models.AttractionLikes.user_id == user_id,
            models.AttractionLikes.attraction_id == attraction_id,
        )
        .first()
    )


def like_attraction(db: Session, data: schemas.LikeAttraction):
    new_record = models.AttractionLikes(
        user_id=data.user_id, attraction_id=data.attraction_id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def get_liked_attractions_list(db: Session, data: schemas.GetLikedAttractions):
    return (
        db.query(models.AttractionLikes)
        .filter(models.AttractionLikes.user_id == data.user_id)
        .offset(data.page)
        .limit(data.size)
        .all()
    )


def get_likes(db: Session, data: schemas.GetLikes):
    result = (
        db.query(func.count(models.AttractionLikes.attraction_id).label("likes"))
        .filter(models.AttractionLikes.attraction_id == data.attraction_id)
        .group_by(models.AttractionLikes.attraction_id)
        .first()
    )

    likes = float(result[0]) if result else None

    return {"likes": likes}


# DONE


def get_done_attraction(db: Session, user_id: int, attraction_id: int):
    return (
        db.query(models.DoneAttractions)
        .filter(
            models.DoneAttractions.user_id == user_id,
            models.DoneAttractions.attraction_id == attraction_id,
        )
        .first()
    )


def mark_as_done_attraction(db: Session, data: schemas.MarkAsDoneAttraction):
    new_record = models.DoneAttractions(
        user_id=data.user_id, attraction_id=data.attraction_id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def get_done_attractions_list(db: Session, data: schemas.GetDoneAttractions):
    return (
        db.query(models.DoneAttractions)
        .filter(models.DoneAttractions.user_id == data["user_id"])
        .offset(data["page"])
        .limit(data["size"])
        .all()
    )


# RATE


def rate_attraction(db: Session, data: schemas.RateAttraction):
    new_record = models.AttractionRatings(
        user_id=data.user_id, attraction_id=data.attraction_id, rating=data.rating
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def get_avg_attraction_rating(db: Session, data: schemas.GetAvgAttractionRating):
    result = (
        db.query(func.avg(models.AttractionRatings.rating).label("average_rating"))
        .filter(models.AttractionRatings.attraction_id == data.attraction_id)
        .group_by(models.AttractionRatings.attraction_id)
        .first()
    )

    average_rating = float(result[0]) if result else None

    return {"average_rating": average_rating}


# COMMENT


def add_comment(db: Session, data: schemas.CommentAttraction):
    new_record = models.AttractionComments(
        user_id=data.user_id, attraction_id=data.attraction_id, comment=data.comment
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def get_comment_by_id(db: Session, comment_id: int):
    return (
        db.query(models.AttractionComments)
        .filter(
            models.AttractionComments.comment_id == comment_id,
        )
        .first()
    )


def update_comment(db: Session, comment_to_edit: schemas.Comment, updated_comment: str):
    comment_to_edit.comment = updated_comment

    db.commit()
    db.refresh(comment_to_edit)

    return comment_to_edit


# GENERIC METHODS


def delete_record(db: Session, record):
    db.delete(record)
    db.commit()
    db.flush()
