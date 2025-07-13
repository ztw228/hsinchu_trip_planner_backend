#!/usr/bin/env python
"""
把多個 CSV 轉成 JSON
用法：
    python csv2json.py app/data/hotels.csv app/data/hotels_hsinchu_county.csv
"""

import sys, json, pandas as pd
from pathlib import Path
from slugify import slugify

def csv_to_json(csv_path: Path):
    df = pd.read_csv(csv_path)

    # 根據你的 CSV 欄名調整
    df = df.rename(columns={
        "旅宿名稱": "name",
        "縣市": "county",
        "鄉鎮": "area",
        "地址": "address",
        "電話或手機": "phone"
    })

    # 產生 id、(若無價格欄) price
    df["id"] = df["name"].apply(lambda s: slugify(s, lowercase=False))
    if "price" not in df.columns:
        df["price"] = 0

    records = df.to_dict(orient="records")

    out_path = csv_path.with_suffix(".json")
    out_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),    # ← 用標準 json
        encoding="utf-8"
    )
    print(f"✅ {csv_path.name} → {out_path.name} ({len(df)} rows)")

def main():
    if len(sys.argv) < 2:
        print("請帶入一個或多個 CSV 檔，例如：csv2json.py file1.csv file2.csv")
        sys.exit(1)
    for path_str in sys.argv[1:]:
        csv_to_json(Path(path_str))

if __name__ == "__main__":
    main()

