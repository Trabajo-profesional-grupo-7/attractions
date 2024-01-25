from fastapi import APIRouter
from fastapi import Depends, HTTPException

from app.db import crud, schemas
from app.db.database import SessionLocal, get_db
from app.services.logger import Logger

router = APIRouter()


@router.get("/attractions/save-list", status_code=201, tags=["Attractions"])
def get_saved_attractions(
    data: schemas.GetSavedAttractions, db: SessionLocal = Depends(get_db)
):
    return crud.get_saved_attractions(db=db, data=data)


@router.post("/attractions/save", status_code=201, tags=["Attractions"])
def save_attraction(data: schemas.SaveAttraction, db: SessionLocal = Depends(get_db)):
    return crud.save_attraction(db=db, data=data)


@router.get("/attractions/like-list", status_code=201, tags=["Attractions"])
def get_liked_attractions(
    data: schemas.GetLikedAttractions, db: SessionLocal = Depends(get_db)
):
    return crud.get_liked_attractions(db=db, data=data)


@router.post("/attractions/like", status_code=201, tags=["Attractions"])
def like_attraction(data: schemas.LikeAttraction, db: SessionLocal = Depends(get_db)):
    return crud.like_attraction(db=db, data=data)


@router.get("/attractions/done-list", status_code=201, tags=["Attractions"])
def get_done_attractions(
    data: schemas.GetDoneAttractions, db: SessionLocal = Depends(get_db)
):
    return crud.get_done_attractions(db=db, data=data)


@router.post("/attractions/done", status_code=201, tags=["Attractions"])
def mark_as_done(
    data: schemas.MarkAsDoneAttraction, db: SessionLocal = Depends(get_db)
):
    return crud.mark_as_done(db=db, data=data)
