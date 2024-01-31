from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import func


# SAVE


def get_saved_attraction(db: Session, user_id: int, attraction_id: int):
    return (
        db.query(models.Saved)
        .filter(
            models.Saved.user_id == user_id,
            models.Saved.attraction_id == attraction_id,
        )
        .first()
    )


def save_attraction(db: Session, data: schemas.SaveAttraction):
    new_record = models.Saved(
        user_id=data.user_id, attraction_id=data.attraction_id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == data.attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=data.attraction_id)
        db.add(attraction)
        db.commit()
        db.refresh(attraction)

    attraction.saved_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def unsave_attraction(db: Session, attraction_to_unsave: models.Saved):
    db.delete(attraction_to_unsave)
    db.commit()
    db.flush()

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_to_unsave.attraction_id)
        .first()
    )

    attraction.saved_count -= 1

    db.commit()
    db.refresh(attraction)


def get_saved_attractions_list(db: Session, data: schemas.GetSavedAttractions):
    return (
        db.query(models.Saved)
        .filter(models.Saved.user_id == data.user_id)
        .offset(data.page)
        .limit(data.size)
        .all()
    )


# LIKE


def get_liked_attraction(db: Session, user_id: int, attraction_id: int):
    return (
        db.query(models.Likes)
        .filter(
            models.Likes.user_id == user_id,
            models.Likes.attraction_id == attraction_id,
        )
        .first()
    )


def like_attraction(db: Session, data: schemas.LikeAttraction):
    new_record = models.Likes(
        user_id=data.user_id, attraction_id=data.attraction_id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == data.attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=data.attraction_id)
        db.add(attraction)
        db.commit()
        db.refresh(attraction)

    attraction.likes_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def unlike_attraction(db: Session, attraction_to_unlike: models.Likes):
    db.delete(attraction_to_unlike)
    db.commit()
    db.flush()

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_to_unlike.attraction_id)
        .first()
    )

    attraction.likes_count -= 1

    db.commit()
    db.refresh(attraction)


def get_liked_attractions_list(db: Session, data: schemas.GetLikedAttractions):
    return (
        db.query(models.Likes)
        .filter(models.Likes.user_id == data.user_id)
        .offset(data.page)
        .limit(data.size)
        .all()
    )


# DONE


def get_done_attraction(db: Session, user_id: int, attraction_id: int):
    return (
        db.query(models.Done)
        .filter(
            models.Done.user_id == user_id,
            models.Done.attraction_id == attraction_id,
        )
        .first()
    )


def mark_as_done_attraction(db: Session, data: schemas.MarkAsDoneAttraction):
    new_record = models.Done(
        user_id=data.user_id, attraction_id=data.attraction_id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == data.attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=data.attraction_id)
        db.add(attraction)
        db.commit()
        db.refresh(attraction)

    attraction.done_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def mark_as_undone_attraction(
    db: Session, attraction_to_mark_as_undone: models.Done
):
    db.delete(attraction_to_mark_as_undone)
    db.commit()
    db.flush()

    attraction = (
        db.query(models.Attractions)
        .filter(
            models.Attractions.attraction_id
            == attraction_to_mark_as_undone.attraction_id
        )
        .first()
    )

    attraction.done_count -= 1

    db.commit()
    db.refresh(attraction)


def get_done_attractions_list(db: Session, data: schemas.GetDoneAttractions):
    return (
        db.query(models.Done)
        .filter(models.Done.user_id == data["user_id"])
        .offset(data["page"])
        .limit(data["size"])
        .all()
    )


# RATE


def rate_attraction(db: Session, data: schemas.RateAttraction):
    new_record = models.Ratings(
        user_id=data.user_id, attraction_id=data.attraction_id, rating=data.rating
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == data.attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=data.attraction_id)
        db.add(attraction)
        db.commit()
        db.refresh(attraction)

    attraction.rating_count += 1
    attraction.rating_total += float(data.rating)

    db.commit()
    db.refresh(attraction)

    return new_record


# COMMENT


def add_comment(db: Session, data: schemas.CommentAttraction):
    new_record = models.Comments(
        user_id=data.user_id, attraction_id=data.attraction_id, comment=data.comment
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


def get_comment_by_id(db: Session, comment_id: int):
    return (
        db.query(models.Comments)
        .filter(
            models.Comments.comment_id == comment_id,
        )
        .first()
    )


def update_comment(db: Session, comment_to_edit: schemas.Comment, updated_comment: str):
    comment_to_edit.comment = updated_comment

    db.commit()
    db.refresh(comment_to_edit)

    return comment_to_edit
