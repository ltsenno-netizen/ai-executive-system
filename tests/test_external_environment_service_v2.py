import os
import sys
import tempfile
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.external_environment_service_v2 import ExternalEnvironmentServiceV2


def test_generate_and_store_environment_saves_and_loads():
    with tempfile.TemporaryDirectory() as temp_dir:
        service = ExternalEnvironmentServiceV2(environment_root=temp_dir)

        with patch('app.services.external_environment_engine_v2.random.random', return_value=1.0):
            environment = service.generate_and_store_environment('2026-01')

        assert environment.period == '2026-01'

        loaded = service.get_environment('2026-01')
        assert loaded is not None
        assert loaded.period == environment.period
        assert loaded.pest.economic == environment.pest.economic
        assert loaded.market_growth_modifier == environment.market_growth_modifier

        latest = service.get_latest_environment()
        assert latest is not None
        assert latest.period == '2026-01'
