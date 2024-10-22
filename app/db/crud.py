import datetime
from datetime import date
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from . import models


# ATTRACTIONS TABLE
def get_attraction_by_id(db: Session, attraction_id: str):
    attraction = (
        db.query(models.Attractions)
        .filter(models.Attractions.attraction_id == attraction_id)
        .first()
    )

    return attraction


def add_attraction(db: Session, attraction_db: models.Attractions):
    db.add(attraction_db)
    db.commit()
    db.refresh(attraction_db)

    return attraction_db


def get_attractions_by_ids(db: Session, attractions_ids: List[str]):
    attractions = []
    for attraction_id in attractions_ids:
        attractions.append(get_attraction_by_id(db=db, attraction_id=attraction_id))
    return attractions


# SAVED TABLE
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

    attraction = get_attraction_by_id(db=db, attraction_id=attraction_id)

    attraction.saved_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def unsave_attraction(db: Session, attraction_to_unsave: models.Saved):
    db.delete(attraction_to_unsave)
    db.commit()
    db.flush()

    attraction = get_attraction_by_id(
        db=db, attraction_id=attraction_to_unsave.attraction_id
    )

    attraction.saved_count -= 1

    db.commit()
    db.refresh(attraction)


def get_user_saved_attractions(db: Session, user_id: int, page: int, size: int):
    saved_attractions_list = (
        db.query(models.Saved)
        .filter(models.Saved.user_id == user_id)
        .offset(page)
        .limit(size)
        .all()
    )

    return get_attractions_by_ids(
        db=db, attractions_ids=[x.attraction_id for x in saved_attractions_list]
    )


def user_saved_attraction(db: Session, attraction_id: str, user_id: int):
    if (
        db.query(models.Saved)
        .filter(
            models.Saved.attraction_id == attraction_id,
            models.Saved.user_id == user_id,
        )
        .first()
    ):
        return True
    return False


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

    attraction = get_attraction_by_id(db=db, attraction_id=attraction_id)

    attraction.likes_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def unlike_attraction(db: Session, attraction_to_unlike: models.Likes):
    db.delete(attraction_to_unlike)
    db.commit()
    db.flush()

    attraction = get_attraction_by_id(
        db=db, attraction_id=attraction_to_unlike.attraction_id
    )

    attraction.likes_count -= 1

    db.commit()
    db.refresh(attraction)


def get_user_liked_attractions(db: Session, attraction_id: str, user_id: int):
    if (
        db.query(models.Likes)
        .filter(
            models.Likes.attraction_id == attraction_id,
            models.Likes.user_id == user_id,
        )
        .first()
    ):
        return True
    return False


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

    attraction = get_attraction_by_id(db=db, attraction_id=attraction_id)

    attraction.done_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def mark_as_undone_attraction(db: Session, attraction_to_mark_as_undone: models.Done):
    db.delete(attraction_to_mark_as_undone)
    db.commit()
    db.flush()

    attraction = get_attraction_by_id(
        db=db, attraction_id=attraction_to_mark_as_undone.attraction_id
    )

    attraction.done_count -= 1

    db.commit()
    db.refresh(attraction)


def get_user_done_attractions(db: Session, user_id: int, page: int, size: int):
    done_list = (
        db.query(models.Done)
        .filter(models.Done.user_id == user_id)
        .offset(page)
        .limit(size)
        .all()
    )

    return get_attractions_by_ids(
        db=db, attractions_ids=[x.attraction_id for x in done_list]
    )


def user_did_attraction(db: Session, attraction_id: str, user_id: int):
    if (
        db.query(models.Done)
        .filter(
            models.Done.attraction_id == attraction_id,
            models.Done.user_id == user_id,
        )
        .first()
    ):
        return True
    return False


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

    attraction = get_attraction_by_id(db=db, attraction_id=attraction_id)

    attraction.rating_count += 1
    attraction.rating_total += float(rating)

    db.commit()
    db.refresh(attraction)

    return new_record


def get_user_rating(db: Session, attraction_id: str, user_id: int):
    user_rating = (
        db.query(models.Ratings)
        .filter(
            models.Ratings.attraction_id == attraction_id,
            models.Ratings.user_id == user_id,
        )
        .first()
    )
    if not user_rating:
        return None
    return user_rating.rating


def number_of_interactions_of_user(db: Session, user_id: int, city=None):
    df_ratings = db.query(
        models.Ratings.user_id,
        models.Ratings.attraction_id,
    ).filter(
        models.Ratings.user_id == user_id,
    )
    df_likes = db.query(models.Likes.user_id, models.Likes.attraction_id).filter(
        models.Likes.user_id == user_id,
    )
    df_saved = db.query(models.Saved.user_id, models.Saved.user_id).filter(
        models.Saved.user_id == user_id,
    )
    df_done = db.query(models.Done.user_id, models.Done.attraction_id).filter(
        models.Done.user_id == user_id,
    )
    df_comments = db.query(
        models.Comments.user_id, models.Comments.attraction_id
    ).filter(
        models.Comments.user_id == user_id,
    )

    if city:
        df_attractions = pd.DataFrame(
            (
                db.query(models.Attractions.attraction_id, models.Attractions.city)
                .filter(
                    models.Attractions.city == city,
                )
                .all()
            ),
            columns=["attraction_id", "city"],
        )

        df_ratings = pd.DataFrame(
            df_ratings.all(), columns=["user_id", "attraction_id"]
        )
        df_ratings["attraction_id"] = df_ratings["attraction_id"].astype(str)
        df_ratings = pd.merge(
            df_attractions,
            df_ratings,
            on=["attraction_id"],
            how="inner",
        )

        df_likes = pd.DataFrame(df_likes.all(), columns=["user_id", "attraction_id"])
        df_likes["attraction_id"] = df_likes["attraction_id"].astype(str)
        df_likes = pd.merge(
            df_attractions,
            df_likes,
            on=["attraction_id"],
            how="inner",
        )

        df_saved = pd.DataFrame(df_saved.all(), columns=["user_id", "attraction_id"])
        df_saved["attraction_id"] = df_saved["attraction_id"].astype(str)
        df_saved = pd.merge(
            df_attractions,
            df_saved,
            on=["attraction_id"],
            how="inner",
        )

        df_done = pd.DataFrame(df_done.all(), columns=["user_id", "attraction_id"])
        df_done["attraction_id"] = df_done["attraction_id"].astype(str)
        df_done = pd.merge(
            df_attractions,
            df_done,
            on=["attraction_id"],
            how="inner",
        )

        df_comments = pd.DataFrame(
            df_comments.all(), columns=["user_id", "attraction_id"]
        )
        df_comments["attraction_id"] = df_comments["attraction_id"].astype(str)
        df_comments = pd.merge(
            df_attractions,
            df_comments,
            on=["attraction_id"],
            how="inner",
        )

        return (
            df_ratings.shape[0]
            + df_likes.shape[0]
            + df_saved.shape[0]
            + df_done.shape[0]
            + df_comments.shape[0]
        )

    return (
        df_ratings.count()
        + df_likes.count()
        + df_saved.count()
        + df_done.count()
        + df_comments.count()
    )


# COMMENT


def add_comment(
    db: Session, user_id: int, attraction_id: str, comment: str, sentiment_metric: float
):
    new_record = models.Comments(
        user_id=user_id,
        attraction_id=attraction_id,
        comment=comment,
        sentiment_metric=sentiment_metric,
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


def update_comment(
    db: Session,
    comment_to_edit: models.Comments,
    updated_comment: str,
    updated_sentiment_metric: float,
):
    comment_to_edit.comment = updated_comment
    comment_to_edit.sentiment_metric = updated_sentiment_metric

    db.commit()
    db.refresh(comment_to_edit)

    return comment_to_edit


def delete_comment(db: Session, comment_to_delete: models.Comments):
    db.delete(comment_to_delete)
    db.commit()
    db.flush()


def get_attraction_comments(db: Session, attraction_id: str):
    return (
        db.query(models.Comments)
        .filter(models.Comments.attraction_id == attraction_id)
        .all()
    )


# SCHEDULE


def get_scheduled_attraction_by_id(db: Session, schedule_id: int):
    return (
        db.query(models.Scheduled)
        .filter(
            models.Scheduled.schedule_id == schedule_id,
        )
        .first()
    )


def check_if_schedule_is_valid(
    db: Session, user_id: int, attraction_id: str, datetime: datetime.datetime
):
    scheduled_attraction = (
        db.query(models.Scheduled)
        .filter(
            models.Scheduled.user_id == user_id,
            models.Scheduled.attraction_id == attraction_id,
            models.Scheduled.day == datetime,
        )
        .first()
    )

    if scheduled_attraction:
        return False
    return True


def schedule_attraction(
    db: Session, user_id: int, attraction_id: str, datetime: datetime.datetime
):
    new_record = models.Scheduled(
        user_id=user_id, attraction_id=attraction_id, day=datetime
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    attraction = get_attraction_by_id(db=db, attraction_id=attraction_id)

    attraction.scheduled_count += 1

    db.commit()
    db.refresh(attraction)

    return new_record


def update_scheduled_attraction(
    db: Session, scheduled_to_update: models.Scheduled, new_datetime: datetime.datetime
):
    scheduled_to_update.day = new_datetime

    db.commit()
    db.refresh(scheduled_to_update)

    return scheduled_to_update


def unschedule_attraction(db: Session, attraction_to_unschedule: models.Scheduled):
    db.delete(attraction_to_unschedule)
    db.commit()
    db.flush()

    attraction = get_attraction_by_id(
        db=db, attraction_id=attraction_to_unschedule.attraction_id
    )

    attraction.scheduled_count -= 1

    db.commit()
    db.refresh(attraction)


def get_user_scheduled_list(db: Session, user_id: int, page: int, size: int):
    scheduled_list = (
        db.query(models.Scheduled)
        .filter(models.Scheduled.user_id == user_id)
        .offset(page)
        .limit(size)
        .all()
    )

    return get_attractions_by_ids(
        db=db, attractions_ids=[x.attraction_id for x in scheduled_list]
    ), [x.day for x in scheduled_list]
