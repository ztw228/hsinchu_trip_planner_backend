from pathlib import Path
from slugify import slugify
import json, pathlib
# 取得 data 目錄路徑
DATA_DIR = Path(__file__).parent

def load_attractions():
    """讀取 attractions.json → list[dict]"""
    with open(DATA_DIR / "attractions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_hotels():
    raw = json.loads((DATA_DIR / "hotels.json").read_text(encoding="utf-8"))
    for h in raw:
        if "id" not in h or not h["id"]:
            h["id"] = slugify(h["name"], lowercase=False)
    return raw