from src.db_config.fonte.database import Base
from sqlalchemy import Column, Float, DateTime, Integer


class Data(Base):
    __tablename__ = 'data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    ambient_temperature = Column(Float)
    power = Column(Float)
    wind_speed = Column(Float)
