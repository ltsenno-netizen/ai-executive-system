import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.quarterly_review_service import QuarterlyReviewService
from app.models.quarterly_review_model import QuarterlyReview


def test_generate_quarterly_review():
    """Test generating a quarterly review"""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = QuarterlyReviewService()
        service.data_path = temp_dir
        service.reviews_path = os.path.join(temp_dir, 'reviews', 'quarterly')
        os.makedirs(service.reviews_path, exist_ok=True)

        # Mock dependencies
        with patch.object(service, '_get_quarterly_monthly_results') as mock_monthly, \
             patch.object(service.mid_term_service, 'load_latest_plan') as mock_plan, \
             patch.object(service.ceo_service, 'get_current_persona') as mock_persona, \
             patch.object(service, '_get_board_members') as mock_board:

            # Mock monthly results
            mock_monthly.return_value = [
                Mock(
                    financials={'revenue': 1000000, 'operating_profit': 100000, 'cash_balance': 2000000},
                    execution={'completed_initiatives': ['init1'], 'delayed_initiatives': []},
                    org_state={'avg_workload_index': 0.7}
                )
            ]

            # Mock mid-term plan
            mock_plan.return_value = Mock(
                quarterly_targets={'2026-Q1': {'revenue': 1000000, 'profit': 100000}}
            )

            # Mock CEO persona
            mock_persona.return_value = Mock(aggressiveness=0.5, brand_priority=0.5)

            # Mock board members
            mock_board.return_value = []  # Empty for simplicity

            review = service.generate_quarterly_review('2026-Q1')

            assert isinstance(review, QuarterlyReview)
            assert review.quarter == '2026-Q1'

            # Check files were created
            json_file = os.path.join(service.reviews_path, '2026-Q1.json')
            md_file = os.path.join(service.reviews_path, '2026-Q1.md')

            assert os.path.exists(json_file)
            assert os.path.exists(md_file)


def test_get_quarterly_review():
    """Test getting a quarterly review"""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = QuarterlyReviewService()
        service.data_path = temp_dir
        service.reviews_path = os.path.join(temp_dir, 'reviews', 'quarterly')
        os.makedirs(service.reviews_path, exist_ok=True)

        # Create a test review file
        test_review = QuarterlyReview(
            quarter='2026-Q1',
            financial=Mock(revenue_total=1000000, operating_profit_total=100000, cash_end=2000000,
                          revenue_vs_plan=0.0, profit_vs_plan=0.0),
            execution=Mock(initiatives_completed=5, initiatives_delayed=1, org_load_index=0.7),
            gap_analysis='Test analysis',
            next_quarter_focus=['Focus 1', 'Focus 2'],
            board_review=Mock(status='approved', rationale='Good', conditions=None, member_opinions=[])
        )

        json_file = os.path.join(service.reviews_path, '2026-Q1.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(test_review.model_dump_json(indent=2, ensure_ascii=False))

        # Test retrieval
        retrieved = service.get_quarterly_review('2026-Q1')
        assert retrieved is not None
        assert retrieved.quarter == '2026-Q1'

        # Test non-existent review
        non_existent = service.get_quarterly_review('2026-Q2')
        assert non_existent is None


def test_get_latest_quarterly_review():
    """Test getting the latest quarterly review"""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = QuarterlyReviewService()
        service.data_path = temp_dir
        service.reviews_path = os.path.join(temp_dir, 'reviews', 'quarterly')
        os.makedirs(service.reviews_path, exist_ok=True)

        # Create multiple review files
        quarters = ['2026-Q1', '2026-Q2', '2026-Q3']
        for quarter in quarters:
            json_file = os.path.join(service.reviews_path, f'{quarter}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write('{"quarter": "' + quarter + '"}')

        latest = service.get_latest_quarterly_review()
        assert latest is not None
        assert latest.quarter == '2026-Q3'  # Should be the latest


def test_save_review():
    """Test saving a review"""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = QuarterlyReviewService()
        service.data_path = temp_dir
        service.reviews_path = os.path.join(temp_dir, 'reviews', 'quarterly')
        os.makedirs(service.reviews_path, exist_ok=True)

        review = QuarterlyReview(
            quarter='2026-Q1',
            financial=Mock(revenue_total=1000000, operating_profit_total=100000, cash_end=2000000,
                          revenue_vs_plan=0.0, profit_vs_plan=0.0),
            execution=Mock(initiatives_completed=5, initiatives_delayed=1, org_load_index=0.7),
            gap_analysis='Test analysis',
            next_quarter_focus=['Focus 1'],
            board_review=Mock(status='approved', rationale='Good', conditions=None, member_opinions=[])
        )

        service._save_review(review)

        # Check JSON file
        json_file = os.path.join(service.reviews_path, '2026-Q1.json')
        assert os.path.exists(json_file)

        with open(json_file, 'r', encoding='utf-8') as f:
            data = f.read()
            assert '"quarter": "2026-Q1"' in data

        # Check Markdown file
        md_file = os.path.join(service.reviews_path, '2026-Q1.md')
        assert os.path.exists(md_file)

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '# 四半期レビュー（2026-Q1）' in content
            assert '売上合計' in content
            assert '取締役会レビュー' in content


def test_generate_markdown():
    """Test markdown generation"""
    service = QuarterlyReviewService()

    review = QuarterlyReview(
        quarter='2026-Q1',
        financial=Mock(revenue_total=3200000, operating_profit_total=410000, cash_end=1800000,
                      revenue_vs_plan=0.04, profit_vs_plan=-0.02),
        execution=Mock(initiatives_completed=12, initiatives_delayed=3, org_load_index=0.62),
        gap_analysis='利益率が計画を下回った要因は、舞台制作費の増加と広告費の前倒し。',
        next_quarter_focus=['制作費の最適化', 'ライブ事業の追加投資判断'],
        board_review=Mock(
            status='conditional',
            rationale='利益率の改善が必要',
            conditions='Q2 で利益率 1.5pt 改善を必須とする',
            member_opinions=[
                Mock(member_role='financial', rationale='キャッシュ残高が不足', risk_flag=True),
                Mock(member_role='brand', rationale='ブランド価値向上の機会', risk_flag=False)
            ]
        )
    )

    markdown = service._generate_markdown(review)

    assert '# 四半期レビュー（2026-Q1）' in markdown
    assert '¥3,200M' in markdown  # Formatted revenue
    assert '¥410M' in markdown    # Formatted profit
    assert '¥1,800M' in markdown  # Formatted cash
    assert '+4%' in markdown      # Revenue vs plan
    assert '-2%' in markdown      # Profit vs plan
    assert '12' in markdown       # Completed initiatives
    assert '3' in markdown        # Delayed initiatives
    assert '0.62' in markdown     # Org load index
    assert '利益率が計画を下回った' in markdown
    assert '制作費の最適化' in markdown
    assert 'ライブ事業の追加投資判断' in markdown
    assert '条件付き承認' in markdown
    assert '利益率の改善が必要' in markdown
    assert 'Q2 で利益率 1.5pt 改善を必須とする' in markdown
    assert 'financial' in markdown
    assert 'brand' in markdown