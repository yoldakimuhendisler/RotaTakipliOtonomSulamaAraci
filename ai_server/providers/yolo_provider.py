# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import cv2
import numpy as np
from typing import List
from ai_server.providers.base_provider import BaseInferenceProvider
from shared.models.common import DetectionResult, BoundingBox, Point2D

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

class YoloProvider(BaseInferenceProvider):
    def __init__(self):
        self.model = None

    def load_model(self):
        if YOLO is None:
            print("HATA: ultralytics kutuphanesi bulunamadi. Lutfen 'pip install ultralytics' komutunu calistirin.")
            return

        print("Gerçek YOLO Modeli Yükleniyor (yolov8n.pt)...")
        # Ilk calistirmada internetten yolov8n.pt dosyasini indirecektir
        self.model = YOLO("yolov8n.pt")
        print("YOLO Modeli Basariyla Yuklendi.")

    def infer(self, image_bytes: bytes) -> List[DetectionResult]:
        if self.model is None:
            print("Model yuklu degil!")
            return []

        # Byte dizisini OpenCV formatina (numpy array) donustur
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            print("Goruntu decode edilemedi.")
            return []

        # Inference islemini baslat (guven skoru %50 ve uzeri)
        results = self.model(img, conf=0.5, verbose=False)
        detections = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                # box.xyxy[0] -> [x_min, y_min, x_max, y_max]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = result.names[cls_id]

                # Sulama araci genelde 'potted plant' (saksi bitkisi) veya 'plant' arar.
                # COCO datasetindeki 'potted plant' ID'si 58'dir. 
                # Diger siniflari da test amacli loglayabiliriz ama ana odak bitki.
                
                # Model bitki disindaki seyleri de bulacaktir. Biz "Plant" ortak adi altinda toplayabiliriz.
                # Eger sinif ismi bitki/agac/saksi iceriyorsa filtrele:
                if class_name in ["potted plant", "vase"]:
                    final_name = "Plant"
                else:
                    final_name = class_name.capitalize() # Diger nesneleri de panele yollasin

                # Sadece bitkilere odaklanmak istiyorsak yukaridaki filtrelemeyi daraltabiliriz.
                # Ancak simdilik her nesneyi tespit ettigini gostermek havali olabilir.

                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                det = DetectionResult(
                    class_name=final_name,
                    confidence=round(conf, 2),
                    bbox=BoundingBox(x_min=x1, y_min=y1, x_max=x2, y_max=y2),
                    center_point=Point2D(x=center_x, y=center_y)
                )
                detections.append(det)

        return detections
