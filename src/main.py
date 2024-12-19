from datetime import datetime
from typing import Annotated, Optional 
from sqlalchemy.orm import Session
from src.db_config.fonte.models import Data
from fastapi import FastAPI, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from src.db_config.fonte.database import Base, engine, SessionLocal
from starlette import status


app = FastAPI()

Base.metadata.create_all(bind=engine)

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


@app.get('/data', status_code=status.HTTP_200_OK)
async def read_all(
    db: db_dependency,
    start_date: Optional[str] = Query("2024-12-19T17:00:00+00:00", alias="start"),
    end_date: Optional[str] = Query("2024-12-29T16:59:00+00:00", alias="end"),
    ):
    query = db.query(Data)

    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)  # Usando fromisoformat para tratar datas no formato ISO 8601
        query = query.filter(Data.timestamp >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)  # Usando fromisoformat para tratar datas no formato ISO 8601
        query = query.filter(Data.timestamp <= end_date_obj)
    
    return query.all()


@app.get('/data/{data_id}', status_code=status.HTTP_200_OK)
async def read_data(db: db_dependency, data_id: int = Path(gt=0)):
    data_model = db.query(Data).filter(Data.id == data_id).first()
    if data_model is not None:
        return data_model
    raise HTTPException(status_code=404, detail='Data not found')


@app.post('/data', status_code=status.HTTP_201_CREATED)
async def create_data(db: db_dependency, data_request: DataRequest):
    data_model = Data(**data_request.model_dump())
    db.add(data_model)
    db.commit()


@app.delete('/{data_id}', status_code = status.HTTP_204_NO_CONTENT)
async def delete_data(db: db_dependency, data_id: int = Path(gt=0)):
    data_model = db.query(Data).filter(Data.id == data_id).first()
    if data_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Data not found')
    db.query(Data).filter(Data.id == data_id).delete()
    db.commit()
