from typing import Dict, Optional
from .company_operating_service import CompanyOperatingService
from .annual_operations_service import AnnualOperationsService
from .corporate_fundamentals_service import CorporateFundamentalsService
from .external_environment_service import ExternalEnvironmentService
from .organization_service import OrganizationService
from .executive_report_service import ExecutiveReportService

class CompanyOperationsIntegrationService:
    def __init__(self):
        self.company_service = CompanyOperatingService()
        self.operations_service = AnnualOperationsService()
        self.environment_service = ExternalEnvironmentService()
        self.fundamentals_service = CorporateFundamentalsService()
        self.organization_service = OrganizationService()

    def simulate_month_full(
        self,
        month: int,
        year: int = 2026,
        environment_state: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        self.company_service.load_company_model()
        self.operations_service.load_operations_model()

        environment_state = environment_state or self.environment_service.build_environment_state(month, year)
        org_state = self.organization_service.load_organization_state(month=month)
        pl_result = self.company_service.simulate_month(
            month,
            environment_state=environment_state,
            org_state=org_state,
        )
        operations_result = self.operations_service.simulate_month_operations(month)
        fundamentals = self.fundamentals_service.load_fundamentals()
        pl_with_fundamentals = self.company_service.apply_corporate_fundamentals_to_result(
            pl_result.model_dump(), fundamentals
        )

        from .financial_service import FinancialService
        financials = FinancialService().load_financials()
        financials.monthly_revenue = sum(pl_result.revenue.values())
        financials = FinancialService().calculate_monthly_free_cash_flow(pl_result.model_dump(), financials)

        return {
            'financials': financials.model_dump(),
            'month': month,
            'year': year,
            'pl': pl_result.model_dump(),
            'pl_with_fundamentals': pl_with_fundamentals,
            'operations': operations_result,
            'environment': environment_state,
            'fundamentals': fundamentals.model_dump(),
            'strategy': {},
        }

    def store_executive_report(
        self,
        period: str,
        narrative: object,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> object:
        report_service = ExecutiveReportService()
        return report_service.generate_and_store_report(
            period=period,
            narrative=narrative,
            financials=financials,
            market_state=market_state,
            org_state=org_state,
            meeting_state=meeting_state,
        )
