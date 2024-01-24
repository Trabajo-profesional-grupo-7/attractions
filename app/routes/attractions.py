from fastapi import APIRouter
from fastapi import Depends, HTTPException

from app.db import crud, schemas
from app.db.database import SessionLocal, get_db
from app.services.logger import Logger

router = APIRouter()


@router.post("/attractions/save", status_code=201, tags=["Attractions"])
def save_attraction(data: schemas.SaveAttraction, db: SessionLocal = Depends(get_db)):
    return crud.save_attraction(db=db, data=data)
