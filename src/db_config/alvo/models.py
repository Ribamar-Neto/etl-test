from src.db_config.fonte.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Float, DateTime, Integer, String, ForeignKey


class Signal(Base):
    __tablename__ = 'signal'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)    
    data = relationship("DataTarget", back_populates="signal")


class Data(Base):
    __tablename__ = 'data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    signal_id = Column(Integer, ForeignKey('signal.id'))
    value = Column(Float)
    signal = relationship("Signal", back_populates="data")
