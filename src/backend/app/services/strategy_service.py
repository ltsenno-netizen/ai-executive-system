import json
from pathlib import Path
from typing import Optional
from ..models.strategy_model import StrategyRoadmap
from ..models.self_optimization_model import OptimizationObjective
from .strategy_engine import build_strategy_roadmap
from .self_optimization_service import SelfOptimizationService
from .corporate_story_service import CorporateStoryService


class StrategyService:
    """Service for generating and managing strategy roadmaps"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data" / "strategy"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.self_optimization_service = SelfOptimizationService()
        self.corporate_story_service = CorporateStoryService()
    
    def generate_strategy_roadmap(
        self,
        objective: OptimizationObjective
    ) -> Optional[StrategyRoadmap]:
        """Generate strategy roadmap for objective"""
        try:
            # Get latest optimization plan for objective
            plan = self.self_optimization_service.get_latest_plan(objective)
            if not plan:
                return None
            
            # Get latest corporate story
            story = self.corporate_story_service.get_latest_story()
            if not story:
                return None
            
            # Build roadmap
            roadmap = build_strategy_roadmap(plan, story)
            
            # Save to JSON
            filepath = self.data_dir / f"{objective.value}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(roadmap.model_dump(), f, ensure_ascii=False, indent=2)
            
            return roadmap
        except Exception as e:
            print(f"Error generating strategy roadmap: {str(e)}")
            return None
    
    def get_latest_strategy_roadmap(
        self,
        objective: Optional[OptimizationObjective] = None
    ) -> Optional[StrategyRoadmap]:
        """Get latest strategy roadmap"""
        try:
            if objective:
                # Get specific objective
                filepath = self.data_dir / f"{objective.value}.json"
                if filepath.exists():
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return StrategyRoadmap(**data)
                return None
            else:
                # Get most recent from any objective
                roadmaps = []
                for filepath in self.data_dir.glob("*.json"):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            roadmaps.append(StrategyRoadmap(**data))
                    except Exception:
                        pass
                
                return roadmaps[0] if roadmaps else None
        except Exception as e:
            print(f"Error retrieving strategy roadmap: {str(e)}")
            return None
    
    def get_all_strategy_roadmaps(self) -> list[StrategyRoadmap]:
        """Get all strategy roadmaps"""
        roadmaps = []
        try:
            for filepath in sorted(self.data_dir.glob("*.json")):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        roadmaps.append(StrategyRoadmap(**data))
                except Exception as e:
                    print(f"Error reading {filepath}: {str(e)}")
        except Exception as e:
            print(f"Error listing strategy roadmaps: {str(e)}")
        
        return roadmaps
