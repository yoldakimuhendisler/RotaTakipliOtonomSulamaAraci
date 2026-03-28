# Yoldaki Mühendisler - Rota Takipli Otonom Sulama Aracı
# Bu kod Aras Coşkun - github.com/arascoskun0 tarafından yapılmıştır.

import os
from pathlib import Path

def is_sim_mode() -> bool:
    """
    Kök dizinde .sim_mode dosyası olup olmadığını kontrol eder.
    Var ise True döner ve tüm donanım işlemleri simüle edilir/mocklanır.
    """
    # Proje kök dizinini bulmak için (shared/utils/env_checker.py konumuna göre iki üst dizin)
    current_dir = Path(__file__).resolve().parent
    try:
        project_root = current_dir.parent.parent
        sim_file = project_root / ".sim_mode"
        return sim_file.exists() or os.environ.get("SIM_MODE", "0") == "1"
    except Exception:
        # Eğer bir nedenden ötürü bulamazsak güvenli varsayım olarak sim modunu kapalı varsay veya environmenta bak
        return os.environ.get("SIM_MODE", "0") == "1"

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent
