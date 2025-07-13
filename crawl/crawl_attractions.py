#!/usr/bin/env python3
"""
把 Wikipedia「新竹市/縣旅遊景點」分類抓下來 → app/data/attractions.json
依賴：requests, python-slugify
"""

import json, re, unicodedata, requests
from pathlib import Path
from slugify import slugify

API_URL = "https://zh.wikipedia.org/w/api.php"
CATEGORIES = {
    "新竹市": "Category:新竹市旅遊景點",
    "新竹縣": "Category:新竹縣旅遊景點",
}

def normalize(s):                        # 去掉全形空白
    return unicodedata.normalize("NFKC", s).strip()

def fetch_category_members(cat_title):
    out, cont = [], ""
    while True:
        params = dict(
            action="query", list="categorymembers",
            cmtitle=cat_title, cmlimit="max",
            format="json", cmcontinue=cont
        )
        if not cont:
            params.pop("cmcontinue")
        r = requests.get(API_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        out.extend(data["query"]["categorymembers"])
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            break
    return out

def build_item(title, county):
    # 嘗試抓「區」字：例如 '北區', '竹北市'
    m = re.search(r"(東區|北區|香山區|竹北市|竹東鎮|[關新峨寶五橫北尖芎湖][西豐眉山峰山埔石林口]?(?:市|鎮|鄉)?)", title)
    area = m.group(1) if m else county
    return {
        "id"        : slugify(title, lowercase=False),
        "name"      : title,
        "area"      : area,
        "category"  : "photo",       # 先全部歸類拍照，可再細分
        "indoor"    : False,
        "open_time" : "00:00",
        "close_time": "23:59",
        "address"   : f"{county}{area}{title}",
        "lat"       : None,
        "lng"       : None,
    }

def main():
    all_spots = []
    for county, cat in CATEGORIES.items():
        members = fetch_category_members(cat)
        for m in members:
            all_spots.append(build_item(normalize(m["title"]), county))

    outfile = Path(__file__).parent.parent / "app" / "data" / "attractions.json"
    outfile.write_text(json.dumps(all_spots, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 寫入 {outfile}    共 {len(all_spots)} 筆")

if __name__ == "__main__":
    main()
