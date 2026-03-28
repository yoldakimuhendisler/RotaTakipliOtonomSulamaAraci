# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

from abc import ABC, abstractmethod
from typing import List

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from shared.models.common import DetectionResult

class BaseInferenceProvider(ABC):
    @abstractmethod
    def load_model(self):
        """Modeli yükler."""
        pass

    @abstractmethod
    def infer(self, image_bytes: bytes) -> List[DetectionResult]:
        """Byte formatındaki resmi alıp List[DetectionResult] döner."""
        pass
