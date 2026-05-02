# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

from fastapi import FastAPI, Depends, WebSocket
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio

# Modülleri absolute import formatında çağırmak projede daha stabil olur.
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from backend.database import engine, Base, get_db
from backend.models import schema
from shared.models.common import TelemetryData
from shared.utils.logger import get_logger

logger = get_logger("BackendServer")

# Veritabanı tablolarını senkron bir şekilde oluştur (Alembic'e ihtiyaç duyulmadan)
schema.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Otonom Bitki Sulama Aracı Backend API")

active_connections = []

import os

# app.mount will be at the bottom to avoid shadowing api routes

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Sadece bağlantıyı tutmak için
            data = await websocket.receive_text()
    except Exception as e:
        logger.info(f"Websocket bağlantısı koptu: {e}")
        active_connections.remove(websocket)

@app.post("/api/telemetry")
async def post_telemetry(data: TelemetryData):
    """ROS 2 veya arabadan gelen telemetri datasını Web'e Broadcast eder."""
    msg = data.json()
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(msg)
        except Exception:
            disconnected.append(connection)
    
    for c in disconnected:
        if c in active_connections:
            active_connections.remove(c)
    return {"status": "success"}

@app.get("/api/plants")
def get_plants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plants = db.query(schema.Plant).offset(skip).limit(limit).all()
    # ORM objelerini basitçe dict'e çevirelim
    return [{"id": p.id, "location_x": p.location_x, "location_y": p.location_y, "species": p.species} for p in plants]

class PlantCreate(BaseModel):
    location_x: float
    location_y: float
    species: str = "Unknown"

@app.post("/api/plants")
def create_plant(plant: PlantCreate, db: Session = Depends(get_db)):
    db_plant = schema.Plant(location_x=plant.location_x, location_y=plant.location_y, species=plant.species)
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return {"id": db_plant.id, "status": "created"}

# Mount the static files for the React Dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    logger.warning("Static directory not found! Dashboard won't be served.")

