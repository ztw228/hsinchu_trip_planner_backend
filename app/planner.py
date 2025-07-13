import math, random
from collections import defaultdict
from datetime import date, timedelta
from typing import List, Dict

from .schemas import PlanRequest, Spot, Hotel

# ========= util =========
def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

# ========= 主入口 =========
def build_plan(req: PlanRequest,
               attractions: List[Dict],
               hotels: List[Dict]) -> Dict:
    """回傳 dict 給 PlanResponse"""

    # ---------- 1. 挑飯店 ----------
    hotellist = [
        Hotel(**h) for h in hotels
        if h["area"] in req.areas and h["price"] <= req.budget_hotel
    ] or [Hotel(**h) for h in hotels]          # 若沒符合 → 全域池隨機
    picked_hotel = random.choice(hotellist)

    # ---------- 2. 篩景點 ----------
    cand = [
        Spot(**a) for a in attractions
        if a["area"] in req.areas
        and a["category"] in req.categories
        and (req.indoor_outdoor == "mixed"
             or (req.indoor_outdoor == "indoor" and a["indoor"])
             or (req.indoor_outdoor == "outdoor" and not a["indoor"]))
    ]

    # 預算：先把貴票景點踢掉（可改權重計算）
    cand = [c for c in cand if c.ticket <= req.budget_play]

    # 簡單 shuffle + open_time 排序
    random.shuffle(cand)
    cand.sort(key=lambda s: s.open_time)

    # 景點池不足時自動放寬類型限制
    if len(cand) < req.spot_count:
        extra = [
            Spot(**a) for a in attractions
            if a["area"] in req.areas and a["id"] not in {c.id for c in cand}
        ]
        random.shuffle(extra)
        cand.extend(extra)

    spots = cand[:req.spot_count]

    # ---------- 3. 按天均分（Round-Robin） ----------
    n_days = (req.end_date - req.start_date).days + 1
    days: list[list[Spot]] = [[] for _ in range(n_days)]

    for idx, spot in enumerate(spots):
        days[idx % n_days].append(spot)   # idx=0→DAY1，idx=1→DAY2，idx=2→DAY1 …

    # ---------- 4. 也許你喜歡 ----------
    suggestions = cand[req.spot_count: req.spot_count + 6]

    return {
        "hotel": picked_hotel,
        "days":  days,
        "suggestions": suggestions
    }
