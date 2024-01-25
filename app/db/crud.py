import hashlib
from sqlalchemy.orm import Session
from . import models, schemas


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
        .filter(models.SavedAttractions.user_id == data.user_id)
        .offset(data.offset)
        .limit(data.limit)
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
        new_record = models.SavedAttractions(
            user_id=data.user_id, attraction_id=data.attraction_id
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record
