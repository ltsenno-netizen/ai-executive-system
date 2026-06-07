from typing import List, Optional
from pydantic import BaseModel


class CorporateStorySection(BaseModel):
    """ストーリーの一章"""
    title: str
    content: str


class CorporateStory(BaseModel):
    """企業の統合ストーリー"""
    period: str
    sections: List[CorporateStorySection]
    summary: str
    markdown_path: Optional[str] = None
