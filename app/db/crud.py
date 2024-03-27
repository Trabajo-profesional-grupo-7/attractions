import datetime

from sqlalchemy.orm import Session

from . import models

# ATTRACTIONS


def get_attraction(db: Session, attraction_id: str):
    return (
        db.query(models.Attractions)
        .filter(
            models.Attractions.attraction_id == attraction_id,
        )
        .first()
    )


# SAVE


def get_saved_attraction(db: Session, user_id: int, attraction_id: str):
    return (
        db.query(models.Saved)
        .filter(
            models.Saved.user_id == user_id,
            models.Saved.attraction_id == attraction_id,
        )
        .first()
    )


def save_attraction(db: Session, user_id: int, attraction_id: str):
    new_record = models.Saved(user_id=user_id, attraction_id=attraction_id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=attraction_id)
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


def get_saved_attractions_list(db: Session, user_id: int, page: int, size: int):
    return (
        db.query(models.Saved)
        .filter(models.Saved.user_id == user_id)
        .offset(page)
        .limit(size)
        .all()
    )


# LIKE


def get_liked_attraction(db: Session, user_id: int, attraction_id: str):
    return (
        db.query(models.Likes)
        .filter(
            models.Likes.user_id == user_id,
            models.Likes.attraction_id == attraction_id,
        )
        .first()
    )


def like_attraction(db: Session, user_id: int, attraction_id: str):
    new_record = models.Likes(user_id=user_id, attraction_id=attraction_id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=attraction_id)
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


def get_liked_attractions_list(db: Session, user_id: int, page: int, size: int):
    return (
        db.query(models.Likes)
        .filter(models.Likes.user_id == user_id)
        .offset(page)
        .limit(size)
        .all()
    )


# DONE


def get_done_attraction(db: Session, user_id: int, attraction_id: str):
    return (
        db.query(models.Done)
        .filter(
            models.Done.user_id == user_id,
            models.Done.attraction_id == attraction_id,
        )
        .first()
    )


def mark_as_done_attraction(db: Session, user_id: int, attraction_id: str):
    new_record = models.Done(user_id=user_id, attraction_id=attraction_id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=attraction_id)
        db.add(attraction)
        db.commit()
        db.refresh(attraction)

    attraction.done_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def mark_as_undone_attraction(db: Session, attraction_to_mark_as_undone: models.Done):
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


def get_done_attractions_list(db: Session, user_id: int, page: int, size: int):
    return (
        db.query(models.Done)
        .filter(models.Done.user_id == user_id)
        .offset(page)
        .limit(size)
        .all()
    )


# RATE


def get_rating(db: Session, user_id: int, attraction_id: str):
    return (
        db.query(models.Ratings)
        .filter(models.Ratings.user_id == user_id)
        .filter(models.Ratings.attraction_id == attraction_id)
        .first()
    )


def update_rating(db: Session, rating_to_update: models.Ratings, new_rating: float):
    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == rating_to_update.attraction_id)
        .first()
    )

    attraction.rating_total -= float(rating_to_update.rating)
    attraction.rating_total += float(new_rating)
    db.commit()
    db.refresh(attraction)

    rating_to_update.rating = new_rating
    db.commit()
    db.refresh(rating_to_update)

    return rating_to_update


def rate_attraction(db: Session, user_id: int, attraction_id: str, rating: float):
    new_record = models.Ratings(
        user_id=user_id, attraction_id=attraction_id, rating=rating
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=attraction_id)
        db.add(attraction)
        db.commit()
        db.refresh(attraction)

    attraction.rating_count += 1
    attraction.rating_total += float(rating)

    db.commit()
    db.refresh(attraction)

    return new_record


# COMMENT


def add_comment(db: Session, user_id: int, attraction_id: str, comment: str):
    new_record = models.Comments(
        user_id=user_id, attraction_id=attraction_id, comment=comment
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


def update_comment(db: Session, comment_to_edit: models.Comments, updated_comment: str):
    comment_to_edit.comment = updated_comment

    db.commit()
    db.refresh(comment_to_edit)

    return comment_to_edit


def delete_comment(db: Session, comment_to_delete: models.Comments):
    db.delete(comment_to_delete)
    db.commit()
    db.flush()


# SEARCH


def add_search(db: Session, user_id: int, query: str):
    new_record = models.Searches(user_id=user_id, query=query)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


# SCHEDULE


def get_scheduled_attraction(db: Session, user_id: int, attraction_id: str):
    return (
        db.query(models.Scheduled)
        .filter(
            models.Scheduled.user_id == user_id,
            models.Scheduled.attraction_id == attraction_id,
        )
        .first()
    )


def schedule_attraction(
    db: Session, user_id: int, attraction_id: str, scheduled_time: datetime
):
    new_record = models.Scheduled(
        user_id=user_id, attraction_id=attraction_id, scheduled_time=scheduled_time
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_id)
        .first()
    )

    if not attraction:
        attraction = models.Attractions(attraction_id=attraction_id)
        db.add(attraction)
        db.commit()
        db.refresh(attraction)

    attraction.scheduled_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record
