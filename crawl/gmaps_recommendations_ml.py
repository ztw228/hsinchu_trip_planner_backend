
#!/usr/bin/env python3
# coding: utf-8
"""
gmaps_recommendations_ml.py
---------------------------
不依賴 OpenAI API，而是在本地使用 scikit‑learn 建立一個
簡易的評論分類模型（美食 / 拍照 / 遊玩 / 飯店）。

步驟：
1. 透過 Google Places API 抓取候選景點
2. 用關鍵字 + 小型標註語料訓練 One‑Vs‑Rest Logistic Regression
3. 作用於所有評論 → 取眾數決定景點標籤
4. 輸出符合格式的 JSON 檔 (hsinchu_recommended_places.json)

依賴：
  pip install scikit-learn joblib requests

環境變數：
  GOOGLE_API_KEY  - Google Cloud Places API 金鑰

執行：
  python gmaps_recommendations_ml.py
"""

import os, json, time, requests
from typing import List, Dict, Any
from collections import Counter

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression

# === 設定 ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CENTER = "24.8013,120.9715"   # 新竹火車站座標
RADIUS = 5000
KEYWORD = "旅遊 美食 景點 新竹"
LANGUAGE = "zh-TW"
RATING_THRESHOLD = 3.5
PRICE_LEVEL_MAP = {0: "免費", 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}

MODEL_PATH = "review_tag_model.joblib"
VEC_PATH   = "review_tfidf.joblib"
LABELS = ["美食", "拍照", "遊玩", "飯店"]

# --- Google API ---
def google_request(url: str) -> Dict[str, Any]:
    for _ in range(3):
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        time.sleep(1)
    raise RuntimeError(f"Google API error: {r.status_code} {r.text}")

def nearby_search() -> List[Dict[str, Any]]:
    out, url = [], (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={CENTER}&radius={RADIUS}&keyword={KEYWORD}"
        f"&language={LANGUAGE}&key={GOOGLE_API_KEY}"
    )
    while url:
        data = google_request(url)
        out.extend(data.get("results", []))
        token = data.get("next_page_token")
        url = (f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
               f"?pagetoken={token}&language={LANGUAGE}&key={GOOGLE_API_KEY}") if token else None
        if token: time.sleep(2)
    return out

def place_details(pid: str) -> Dict[str, Any]:
    fields = "name,rating,price_level,formatted_address,opening_hours,reviews"
    url = ("https://maps.googleapis.com/maps/api/place/details/json"
           f"?place_id={pid}&fields={fields}&language={LANGUAGE}&key={GOOGLE_API_KEY}")
    return google_request(url)["result"]

# --- ML 模型 ---
def seed_corpus():
    samples = [
        ("這家牛肉麵超好吃，湯頭濃郁",   "美食"),
        ("排隊小吃，蚵仔煎必點",       "美食"),
        ("蛋糕精緻，適合下午茶打卡",     "美食"),
        ("夜景漂亮，非常適合拍照",       "拍照"),
        ("彩虹屋外觀繽紛，怎麼拍都好看", "拍照"),
        ("每年花季必朝聖，賞花拍照人潮多","拍照"),
        ("動物園親子遊玩好去處",        "遊玩"),
        ("園區有溜滑梯和草地，孩子玩瘋","遊玩"),
        ("水上活動刺激又有趣",          "遊玩"),
        ("飯店服務周到，房間乾淨",      "飯店"),
        ("早餐豐盛，住宿體驗佳",        "飯店"),
        ("地點便利，CP值高的住宿",      "飯店"),
    ]
    texts, labels = zip(*samples)
    y = [[1 if l == tag else 0 for tag in LABELS] for l in labels]
    return list(texts), y

def train_model():
    texts, y = seed_corpus()
    vec = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    X = vec.fit_transform(texts)
    clf = OneVsRestClassifier(LogisticRegression(max_iter=1000))
    clf.fit(X, y)
    joblib.dump(vec, VEC_PATH)
    joblib.dump(clf, MODEL_PATH)
    return vec, clf

def load_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH):
        return joblib.load(VEC_PATH), joblib.load(MODEL_PATH)
    return train_model()

VEC, CLF = load_model()

def predict_tags(reviews: List[str]) -> List[str]:
    if not reviews:
        return ["遊玩"]
    X = VEC.transform(reviews)
    preds = CLF.predict(X)
    counts = Counter()
    for row in preds:
        for idx, val in enumerate(row):
            if val: counts[LABELS[idx]] += 1
    if not counts:
        return ["遊玩"]
    top = [tag for tag, _ in counts.most_common(2)]
    return top

# --- 主程式 ---
def main():
    if not GOOGLE_API_KEY:
        raise EnvironmentError("請先設定 GOOGLE_API_KEY")
    print("抓取候選地點…")
    places = nearby_search()
    print("共", len(places), "筆；開始篩選", RATING_THRESHOLD, "星以上")
    results = []
    for p in places:
        if p.get("rating",0) < RATING_THRESHOLD: continue
        det = place_details(p["place_id"])
        reviews = [r.get("text","") for r in det.get("reviews", []) if r.get("text")]
        entry = {
            "name": det["name"],
            "address": det["formatted_address"],
            "rating": det.get("rating"),
            "price": PRICE_LEVEL_MAP.get(det.get("price_level"), "不明"),
            "opening_hours": "；".join(det.get("opening_hours", {}).get("weekday_text", [])),
            "popular_review": reviews[0] if reviews else "",
            "tags": predict_tags(reviews)
        }
        results.append(entry)
        print("✔", entry["name"], entry["tags"])
        time.sleep(0.2)
    with open("hsinchu_recommended_places.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("輸出完成：hsinchu_recommended_places.json")

if __name__ == "__main__":
    main()
