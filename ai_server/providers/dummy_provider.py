# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

from typing import List
import random
from ai_server.providers.base_provider import BaseInferenceProvider
from shared.models.common import DetectionResult, BoundingBox, Point2D

class DummyProvider(BaseInferenceProvider):
    def load_model(self):
        print("Dummy AI Model loaded (MOCK)")

    def infer(self, image_bytes: bytes) -> List[DetectionResult]:
        # Sahte bitki bulma simülasyonu
        detections = []
        if random.random() > 0.3: # %70 bitki buldu
            det = DetectionResult(
                class_name="Plant",
                confidence=round(random.uniform(0.60, 0.99), 2),
                bbox=BoundingBox(x_min=100, y_min=100, x_max=200, y_max=200),
                center_point=Point2D(x=150, y=150)
            )
            detections.append(det)
        return detections
