from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import func


def save_attraction(db: Session, data: schemas.SaveAttraction):
    existing_record = (
        db.query(models.SavedAttractions)
        .filter(
            models.SavedAttractions.user_id == data.user_id,
            models.SavedAttractions.attraction_id == data.attraction_id,
        )
        .first()
    )

    if existing_record:
        db.delete(existing_record)
        db.commit()
        db.flush()

        return "Existing record deleted successfully"
    else:
        new_record = models.SavedAttractions(
            user_id=data.user_id, attraction_id=data.attraction_id
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record


def get_saved_attractions(db: Session, data: schemas.GetSavedAttractions):
    return (
        db.query(models.SavedAttractions)
        .filter(models.SavedAttractions.user_id == data["user_id"])
        .offset(data["page"])
        .limit(data["size"])
        .all()
    )


def mark_as_done(db: Session, data: schemas.MarkAsDoneAttraction):
    existing_record = (
        db.query(models.DoneAttractions)
        .filter(
            models.DoneAttractions.user_id == data.user_id,
            models.DoneAttractions.attraction_id == data.attraction_id,
        )
        .first()
    )

    if existing_record:
        db.delete(existing_record)
        db.commit()
        db.flush()

        return "Existing record deleted successfully"
    else:
        new_record = models.DoneAttractions(
            user_id=data.user_id, attraction_id=data.attraction_id
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record


def get_done_attractions(db: Session, data: schemas.GetDoneAttractions):
    return (
        db.query(models.DoneAttractions)
        .filter(models.DoneAttractions.user_id == data["user_id"])
        .offset(data["page"])
        .limit(data["size"])
        .all()
    )


def like_attraction(db: Session, data: schemas.LikeAttraction):
    existing_record = (
        db.query(models.AttractionLikes)
        .filter(
            models.AttractionLikes.user_id == data.user_id,
            models.AttractionLikes.attraction_id == data.attraction_id,
        )
        .first()
    )

    if existing_record:
        db.delete(existing_record)
        db.commit()
        db.flush()

        return "Existing record deleted successfully"
    else:
        new_record = models.AttractionLikes(
            user_id=data.user_id, attraction_id=data.attraction_id
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record


def get_liked_attractions(db: Session, data: schemas.GetLikedAttractions):
    return (
        db.query(models.AttractionLikes)
        .filter(models.AttractionLikes.user_id == data["user_id"])
        .offset(data["page"])
        .limit(data["size"])
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
