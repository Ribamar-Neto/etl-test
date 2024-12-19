from datetime import datetime
from typing import Annotated 
from sqlalchemy.orm import Session
from src.db_config.models import Fonte
from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from src.db_config.models import Base
from src.db_config.database import engine_for_source_db, SessionLocal
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
async def create_data(db: db_dependency, data_request: DataRequest):
    data_model = Fonte(**data_request.model_dump())
    db.add(data_model)
    db.commit()


@app.delete('/{data_id}', status_code = status.HTTP_204_NO_CONTENT)
async def delete_data(db: db_dependency, data_id: int = Path(gt=0)):
    data_model = db.query(Fonte).filter(Fonte.id == data_id).first()
    if data_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Data not found')
    db.query(Fonte).filter(Fonte.id == data_id).delete()
    db.commit()
