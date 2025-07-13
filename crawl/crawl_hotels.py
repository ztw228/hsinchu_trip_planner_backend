#!/usr/bin/env python3
"""
交通部觀光署「臺灣旅宿網」CSV → app/data/hotels.json
依賴：requests, python-slugify
"""

import csv, json, requests
from pathlib import Path
from slugify import slugify

CSV_URL   = "https://media.taiwan.net/CSVDownload.ashx?type=Hotel"
COUNTIES  = {"新竹市", "新竹縣"}

def fetch_csv_lines():
    r = requests.get(CSV_URL, timeout=30)
    r.raise_for_status()
    return r.text.splitlines()

def parse_hotels(lines):
    rdr = csv.DictReader(lines)
    data = []
    for row in rdr:
        if row["縣市"] not in COUNTIES:
            continue
        price = int(row.get("最低房價", "0") or 0)
        data.append({
            "id"     : slugify(row["旅宿名稱"], lowercase=False),
            "name"   : row["旅宿名稱"],
            "price"  : price,
            "address": row["地址"],
            "lat"    : float(row["緯度"]) if row["緯度"] else None,
            "lng"    : float(row["經度"]) if row["經度"] else None,
        })
    return data

def main():
    lines = fetch_csv_lines()
    hotels = parse_hotels(lines)
    outfile = Path(__file__).parent.parent / "app" / "data" / "hotels.json"
    outfile.write_text(json.dumps(hotels, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 寫入 {outfile}    共 {len(hotels)} 筆")

if __name__ == "__main__":
    main()
