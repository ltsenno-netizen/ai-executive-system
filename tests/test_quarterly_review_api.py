import os
import sys
import tempfile
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.routes.quarterly_review import router
from app.models.quarterly_review_model import QuarterlyReview, QuarterlyFinancialSummary, QuarterlyExecutionSummary, QuarterlyBoardReview
from fastapi.testclient import TestClient
from fastapi import FastAPI


def test_get_latest_quarterly_review():
    """Test GET /api/reviews/quarterly/latest"""
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        with patch('app.routes.quarterly_review.service.get_latest_quarterly_review') as mock_get:
            # Test successful retrieval
            mock_review = QuarterlyReview(
                quarter='2026-Q1',
                financial=QuarterlyFinancialSummary(
                    quarter='2026-Q1',
                    revenue_total=3200000.0,
                    operating_profit_total=410000.0,
                    cash_end=1800000.0,
                    revenue_vs_plan=0.04,
                    profit_vs_plan=-0.02,
                ),
                execution=QuarterlyExecutionSummary(
                    initiatives_completed=12,
                    initiatives_delayed=3,
                    org_load_index=0.62,
                ),
                gap_analysis='Test analysis',
                next_quarter_focus=['制作費の最適化'],
                board_review=QuarterlyBoardReview(
                    status='conditional',
                    rationale='利益率の改善が必要',
                    conditions='Q2 で利益率 1.5pt 改善を必須とする',
                ),
            )
            mock_get.return_value = mock_review

            response = client.get('/api/reviews/quarterly/latest')
            assert response.status_code == 200
            assert response.json()['quarter'] == '2026-Q1'

            # Test no review available
            mock_get.return_value = None
            response = client.get('/api/reviews/quarterly/latest')
            assert response.status_code == 200
            assert response.json() is None


def test_get_quarterly_review():
    """Test GET /api/reviews/quarterly/{quarter}"""
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        with patch('app.routes.quarterly_review.service.get_quarterly_review') as mock_get:
            # Test successful retrieval
            mock_review = QuarterlyReview(
                quarter='2026-Q1',
                financial=QuarterlyFinancialSummary(
                    quarter='2026-Q1',
                    revenue_total=3200000.0,
                    operating_profit_total=410000.0,
                    cash_end=1800000.0,
                    revenue_vs_plan=0.04,
                    profit_vs_plan=-0.02,
                ),
                execution=QuarterlyExecutionSummary(
                    initiatives_completed=12,
                    initiatives_delayed=3,
                    org_load_index=0.62,
                ),
                gap_analysis='Test analysis',
                next_quarter_focus=['制作費の最適化'],
                board_review=QuarterlyBoardReview(
                    status='conditional',
                    rationale='利益率の改善が必要',
                    conditions='Q2 で利益率 1.5pt 改善を必須とする',
                ),
            )
            mock_get.return_value = mock_review

            response = client.get('/api/reviews/quarterly/2026-Q1')
            assert response.status_code == 200
            assert response.json()['quarter'] == '2026-Q1'

            # Test review not found
            mock_get.return_value = None
            response = client.get('/api/reviews/quarterly/2026-Q2')
            assert response.status_code == 404
            assert 'not found' in response.json()['detail'].lower()


def test_generate_quarterly_review():
    """Test POST /api/reviews/quarterly/{quarter}/generate"""
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        with patch('app.routes.quarterly_review.service.generate_quarterly_review') as mock_generate:
            mock_review = QuarterlyReview(
                quarter='2026-Q1',
                financial=QuarterlyFinancialSummary(
                    quarter='2026-Q1',
                    revenue_total=3200000.0,
                    operating_profit_total=410000.0,
                    cash_end=1800000.0,
                    revenue_vs_plan=0.04,
                    profit_vs_plan=-0.02,
                ),
                execution=QuarterlyExecutionSummary(
                    initiatives_completed=12,
                    initiatives_delayed=3,
                    org_load_index=0.62,
                ),
                gap_analysis='Test analysis',
                next_quarter_focus=['制作費の最適化'],
                board_review=QuarterlyBoardReview(
                    status='conditional',
                    rationale='利益率の改善が必要',
                    conditions='Q2 で利益率 1.5pt 改善を必須とする',
                ),
            )
            mock_generate.return_value = mock_review

            response = client.post('/api/reviews/quarterly/2026-Q1/generate')
            assert response.status_code == 200
            assert response.json()['quarter'] == '2026-Q1'


def test_error_handling():
    """Test error handling in API endpoints"""
    app = FastAPI()
    app.include_router(router)

    with TestClient(app) as client:
        with patch('app.routes.quarterly_review.service.get_latest_quarterly_review') as mock_get:
            # Test exception handling
            mock_get.side_effect = Exception('Database error')

            response = client.get('/api/reviews/quarterly/latest')
            assert response.status_code == 500
            assert 'Failed to get latest quarterly review' in response.json()['detail']

        with patch('app.routes.quarterly_review.service.get_quarterly_review') as mock_get:
            mock_get.side_effect = Exception('File error')

            response = client.get('/api/reviews/quarterly/2026-Q1')
            assert response.status_code == 500
            assert 'Failed to get quarterly review' in response.json()['detail']

        with patch('app.routes.quarterly_review.service.generate_quarterly_review') as mock_generate:
            mock_generate.side_effect = Exception('Generation error')

            response = client.post('/api/reviews/quarterly/2026-Q1/generate')
            assert response.status_code == 500
            assert 'Failed to generate quarterly review' in response.json()['detail']