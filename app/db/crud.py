import hashlib
from sqlalchemy.orm import Session
from . import models, schemas


def save_attraction(db: Session, data: schemas.SaveAttraction):
    db_saved_attractions = models.SaveAttractions(
        user_id=data.user_id, attraction_id=data.attraction_id
    )
    db.add(db_saved_attractions)
    db.commit()
    db.refresh(db_saved_attractions)
    return db_saved_attractions
