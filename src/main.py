from datetime import datetime
from typing import Annotated 
from sqlalchemy.orm import Session
from src.models import Fonte
from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from src.models import Base
from src.database import engine_for_source_db, SessionLocal
from starlette import status


app = FastAPI()

Base.metadata.create_all(bind=engine_for_source_db)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]



class DataRequest(BaseModel):
	timestamp: datetime
	ambient_temperature: float
	power: float
	wind_speed: float


@app.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Fonte).all()


@app.post('/data', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, data_request: DataRequest):
    data_model = Fonte(**data_request.model_dump())
    db.add(data_model)
    db.commit()
