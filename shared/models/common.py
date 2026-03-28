# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

from pydantic import BaseModel
from typing import List, Optional

class Point2D(BaseModel):
    x: float
    y: float

class BoundingBox(BaseModel):
    x_min: int
    y_min: int
    x_max: int
    y_max: int

class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: Optional[BoundingBox] = None
    center_point: Optional[Point2D] = None

class AIInferenceResponse(BaseModel):
    success: bool
    message: str
    detections: List[DetectionResult]

class TelemetryData(BaseModel):
    robot_x: float
    robot_y: float
    battery_level: float
    water_level: float
    current_state: str # ex: "SEARCHING", "WATERING"
    is_sim_mode: bool
