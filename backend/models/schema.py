# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from backend.database import Base

class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    location_x = Column(Float, nullable=False)
    location_y = Column(Float, nullable=False)
    species = Column(String, default="Unknown", index=True)
    last_watered = Column(DateTime, nullable=True)

class WateringEvent(Base):
    __tablename__ = "watering_events"
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, index=True) # Basit bir ForeignKey referansı
    timestamp = Column(DateTime, default=datetime.utcnow)
    moisture_before = Column(Float)
    moisture_after = Column(Float)
    water_volume_ml = Column(Float)

class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String, index=True) # INFO, WARNING, ERROR
    module = Column(String)
    message = Column(String)
