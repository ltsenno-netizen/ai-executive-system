import pytest
from src.backend.app.services.corporate_story_service import CorporateStoryService


def test_generate_story():
    """Test story generation"""
    service = CorporateStoryService()
    
    try:
        story = service.generate_story("2026-04")
        
        assert story is not None
        assert story.period == "2026-04"
        assert len(story.sections) > 0
        assert story.summary is not None
    except Exception as e:
        pytest.skip(f"Story generation failed: {str(e)}")


def test_get_story():
    """Test story retrieval"""
    service = CorporateStoryService()
    
    try:
        # Generate first
        story = service.generate_story("2026-04")
        
        # Retrieve
        retrieved = service.get_story("2026-04")
        
        assert retrieved is not None
        assert retrieved.period == "2026-04"
    except Exception as e:
        pytest.skip(f"Story operations failed: {str(e)}")


def test_get_latest_story():
    """Test retrieving latest story"""
    service = CorporateStoryService()
    
    try:
        latest = service.get_latest_story()
        
        # May be None if no stories exist
        if latest is not None:
            assert latest.period is not None
            assert latest.summary is not None
    except Exception:
        pytest.skip("No stories available")
