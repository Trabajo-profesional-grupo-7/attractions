import hashlib
from sqlalchemy.orm import Session
from . import models, schemas


def save_attraction(db: Session, data: schemas.SaveAttraction):
    existing_record = db.query(models.SaveAttractions).filter(
        models.SaveAttractions.user_id == data.user_id,
        models.SaveAttractions.attraction_id == data.attraction_id
    ).first()

    if existing_record:
        db.delete(existing_record)
        db.commit()
        db.flush()

        return "Existing record deleted successfully"
    else:
        new_record = models.SaveAttractions(
            user_id=data.user_id, attraction_id=data.attraction_id
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record

