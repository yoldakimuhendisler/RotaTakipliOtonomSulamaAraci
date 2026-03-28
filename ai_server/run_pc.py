# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import uvicorn

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from shared.utils.logger import get_logger

logger = get_logger("PC_Runner")

if __name__ == "__main__":
    logger.info("AI Inference Server (Saf Python Kodu) Başlatılıyor...")
    uvicorn.run("main:app", host="0.0.0.0", port=9937, reload=False)
