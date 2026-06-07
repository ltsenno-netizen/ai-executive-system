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
from .routes.business import router as business_router
from .routes.organization import router as organization_router
from .routes.business_strategy import router as business_strategy_router
from .routes.business_strategy_definition import router as business_strategy_definition_router
from .routes.company_operating import router as company_operating_router
from .routes.company_operations_integration import router as company_operations_integration_router
from .routes.external_environment import router as external_environment_router
from .routes.external_environment_v2 import router as external_environment_v2_router
from .routes.corporate_fundamentals import router as corporate_fundamentals_router
from .routes.business_portfolio import router as business_portfolio_router
from .routes.executive_dashboard import router as executive_dashboard_router
from .routes.executive_report import router as executive_report_router
from .routes.monthly_batch import router as monthly_batch_router
from .routes.financial import router as financial_router
from .routes.executive_meeting import router as executive_meeting_router
from .routes.executive_narrative import router as executive_narrative_router
from .routes.execution import router as execution_router
from .routes.improvement_cycle import router as improvement_cycle_router
from .routes.midterm_strategy import router as midterm_strategy_router
from .routes.operational_issues import router as operational_issues_router
from .routes.talent_management import router as talent_management_router
from .routes.talent_management_extended import router as talent_management_extended_router
from .routes.quarterly_review import router as quarterly_review_router
from .routes.ceo_succession import router as ceo_succession_router
from .routes.executive_agents import router as executive_agents_router
from .routes.narrative_intelligence import router as narrative_intelligence_router
from .routes.corporate_memory import router as corporate_memory_router
from .routes.scenario_simulation import router as scenario_simulation_router
from .routes.multi_company_comparative import router as multi_company_comparative_router
from .routes.strategy_engine_v2 import router as strategy_engine_v2_router
from .routes.executive_simulation import router as executive_simulation_router
from .routes.enterprise_autopilot import router as enterprise_autopilot_router

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
app.include_router(business_router, prefix="/api")
app.include_router(organization_router, prefix="/api")
app.include_router(business_strategy_router, prefix="/api")
app.include_router(business_strategy_definition_router, prefix="/api")
app.include_router(company_operating_router, prefix="/api")
app.include_router(company_operations_integration_router, prefix="/api")
app.include_router(external_environment_router, prefix="/api")
app.include_router(external_environment_v2_router, prefix="/api")
app.include_router(corporate_fundamentals_router, prefix="/api")
app.include_router(business_portfolio_router, prefix="/api")
app.include_router(executive_dashboard_router, prefix="/api")
app.include_router(executive_report_router, prefix="/api")
app.include_router(monthly_batch_router, prefix="/api")
app.include_router(financial_router, prefix="/api")
app.include_router(execution_router, prefix="/api")
app.include_router(executive_meeting_router, prefix="/api")
app.include_router(executive_narrative_router, prefix="/api")
app.include_router(improvement_cycle_router, prefix="/api")
app.include_router(midterm_strategy_router, prefix="/api")
app.include_router(operational_issues_router, prefix="/api")
app.include_router(talent_management_router, prefix="/api")
app.include_router(talent_management_extended_router, prefix="/api")
app.include_router(quarterly_review_router, prefix="/api")
app.include_router(ceo_succession_router, prefix="/api")
app.include_router(executive_agents_router, prefix="/api")
app.include_router(narrative_intelligence_router, prefix="/api")
app.include_router(corporate_memory_router, prefix="/api")
app.include_router(scenario_simulation_router, prefix="/api")
app.include_router(multi_company_comparative_router, prefix="/api")
app.include_router(strategy_engine_v2_router, prefix="/api")
app.include_router(executive_simulation_router, prefix="/api")
app.include_router(enterprise_autopilot_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=12000)