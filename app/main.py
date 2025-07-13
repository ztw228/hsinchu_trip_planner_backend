from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from .schemas import PlanRequest, PlanResponse
from .planner import build_plan
from .data import load_attractions, load_hotels

app = FastAPI(title="Hsinchu Trip Planner API")

# ★ 把前端網域加進 allow_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hsinchu-trip-planner-front-320837244860.asia-east1.run.app",
        "http://localhost:5500",          # ← 本機測試時可用 (可刪)
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False
)


ATTRACTIONS = load_attractions()
HOTELS      = load_hotels()
PLANS: dict[str, dict] = {}

@app.post("/api/plan", response_model=PlanResponse)
def create_plan(req: PlanRequest):
    plan_data = build_plan(req, ATTRACTIONS, HOTELS)
    plan_id   = str(uuid4())
    PLANS[plan_id] = plan_data
    return PlanResponse(id=plan_id, **plan_data)

@app.get("/api/plan/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: str):
    if plan_id not in PLANS:
        raise HTTPException(404, "Plan not found")
    return PlanResponse(id=plan_id, **PLANS[plan_id])

@app.put("/api/plan/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: str, plan: PlanResponse):
    if plan_id not in PLANS:
        raise HTTPException(404, "Plan not found")
    PLANS[plan_id] = plan.dict(exclude={"id"})
    return plan

