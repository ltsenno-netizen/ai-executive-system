import pytest
from fastapi.testclient import TestClient
from src.backend.app.main import app  # Assuming main.py has the app


class TestMidTermPlanAPI:
    def test_get_latest_plan(self):
        client = TestClient(app)
        response = client.get('/api/plans/midterm/latest')
        # Assuming the endpoint returns 200 if plan exists, or appropriate response
        assert response.status_code in [200, 404]  # 404 if no plan