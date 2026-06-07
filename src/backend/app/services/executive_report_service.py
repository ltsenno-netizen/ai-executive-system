import os
import re
from typing import Dict, List, Optional

from ..models.executive_report_model import ExecutiveReport
from .executive_report_engine import ExecutiveReportEngine


class ExecutiveReportService:
    def __init__(self, data_path: Optional[str] = None):
        self.root_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../..')
        ) if data_path is None else os.path.abspath(data_path)
        self.reports_path = os.path.join(self.root_path, 'reports')
        os.makedirs(self.reports_path, exist_ok=True)
        self.engine = ExecutiveReportEngine()

    def generate_and_store_report(
        self,
        period: str,
        narrative: object,
        financials: Dict[str, object],
        market_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> ExecutiveReport:
        report = self.engine.build_monthly_report(
            period=period,
            narrative=narrative,
            financials=financials,
            market_state=market_state,
            org_state=org_state,
            meeting_state=meeting_state,
        )
        markdown = self.engine.render_report_markdown(report)
        file_path = os.path.join(self.reports_path, f"{period}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        return report

    def get_report(self, period: str) -> str:
        file_path = os.path.join(self.reports_path, f"{period}.md")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Report not found for period: {period}')
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_reports(self, limit: int = 6) -> List[Dict[str, str]]:
        if limit < 1:
            raise ValueError('limit must be 1 or greater')

        report_files = [
            file for file in os.listdir(self.reports_path)
            if file.endswith('.md')
        ]
        report_files.sort()
        reports = []
        for file_name in report_files[-limit:]:
            period = file_name.replace('.md', '')
            file_path = os.path.join(self.reports_path, file_name)
            title = self._extract_title(file_path)
            summary = self._extract_management_summary(file_path)
            reports.append({'period': period, 'title': title, 'summary': summary})
        return reports[::-1]

    def get_latest_report(self) -> Optional[ExecutiveReport]:
        reports = self.list_reports(limit=1)
        if not reports:
            return None

        latest = reports[0]
        return ExecutiveReport(
            period=latest['period'],
            title=latest['title'],
            management_summary=latest['summary'],
            sections=[],
        )

    def _extract_title(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    return line.lstrip('# ').strip()
        return os.path.basename(file_path).replace('.md', '')

    def _extract_management_summary(self, file_path: str) -> str:
        summary_lines = []
        section_started = False
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('## 1. マネジメントサマリ'):
                    section_started = True
                    continue
                if section_started:
                    if line.startswith('## '):
                        break
                    if line.strip():
                        summary_lines.append(line.strip())
        if not summary_lines:
            return ''
        return ' '.join(summary_lines)[:200]
