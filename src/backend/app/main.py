# src/backend/app/main.py
# FastAPIベースのエントリポイント。将来拡張を意識した構造。

from fastapi import FastAPI
from .routes.weekly_report import router as weekly_report_router
from .routes.oneonone import router as oneonone_router
from .routes.agenda import router as agenda_router
from .routes.recommendation import router as recommendation_router
from .routes.development import router as development_router
from .routes.development_progress import router as development_progress_router
from .routes.assessment import router as assessment_router
from .routes.pl import router as pl_router
from .routes.dashboard import router as dashboard_router
from .routes.leadership import router as leadership_router

app = FastAPI(title="AI Executive System - Phase 1: AI Secretary")

# ルートをインクルード（将来的に拡張）
app.include_router(weekly_report_router, prefix="/api")
app.include_router(oneonone_router, prefix="/api")
app.include_router(agenda_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")
app.include_router(development_router, prefix="/api")
app.include_router(development_progress_router, prefix="/api")
app.include_router(assessment_router, prefix="/api")
app.include_router(pl_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(leadership_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=12000)