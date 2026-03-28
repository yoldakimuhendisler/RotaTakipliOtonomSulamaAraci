# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

from fastapi import FastAPI, UploadFile, File
import traceback
import sys
from pathlib import Path

# Ortak modeller için root_dir ekleyelim
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from shared.models.common import AIInferenceResponse
from shared.utils.logger import get_logger
from ai_server.providers.dummy_provider import DummyProvider

logger = get_logger("AIServer")
app = FastAPI(title="Otonom Bitki Sulama AI Inference Server")

provider = DummyProvider()
provider.load_model()

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Inference Server is Running on port 9937"}

@app.post("/infer", response_model=AIInferenceResponse)
async def infer(file: UploadFile = File(...)):
    """
    Kameradan gelen görüntüyü (bytes) alarak AI işleminden geçirir.
    Simülasyon modunda ya da gerçek modda DummyProvider veya YOLO çalışabilir.
    """
    try:
        image_bytes = await file.read()
        detections = provider.infer(image_bytes)
        return AIInferenceResponse(
            success=True,
            message="Inference successful",
            detections=detections
        )
    except Exception as e:
        logger.error(f"Inference hatası: {e}\n{traceback.format_exc()}")
        return AIInferenceResponse(
            success=False,
            message=str(e),
            detections=[]
        )
