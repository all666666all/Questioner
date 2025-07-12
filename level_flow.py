"""
Level Flow System - Outer layer managing learning paths and level progression
"""
from typing import List, Optional, Tuple
from models import (
    LearningSession, Level, LevelStatus, LevelReport, LearningSummary
)
from ai_service import AIService
from config import Config

class LevelFlowManager:
    def __init__(self):
        self.ai_service = AIService()
        self.current_session: Optional[LearningSession] = None
        
    def start_new_learning_session(self, main_topic: str, num_levels: int = None) -> LearningSession:
        """
        Start a new learning session by generating a learning path
        """
        if num_levels is None:
            num_levels = Config.DEFAULT_NUM_LEVELS
        
        # Validate input
        if not main_topic.strip():
            raise ValueError("Main topic cannot be empty")
        
        if num_levels < Config.MIN_LEVELS or num_levels > Config.MAX_LEVELS:
            raise ValueError(f"Number of levels must be between {Config.MIN_LEVELS} and {Config.MAX_LEVELS}")
        
        try:
            # Generate learning path using AI
            level_list = self.ai_service.generate_learning_path(main_topic, num_levels)
            
            # Initialize level statuses (first level unlocked, others locked)
            level_statuses = [LevelStatus.UNLOCKED] + [LevelStatus.LOCKED] * (len(level_list) - 1)
            
            # Create new learning session
            self.current_session = LearningSession(
                main_topic=main_topic,
                level_list=level_list,
                current_level_index=0,
                level_statuses=level_statuses,
                history=[]
            )
            
            return self.current_session
            
        except Exception as e:
            raise Exception(f"Failed to start learning session: {str(e)}")
    
    def get_current_session(self) -> Optional[LearningSession]:
        """Get the current learning session"""
        return self.current_session
    
    def get_level_info(self, level_index: int) -> Tuple[Level, LevelStatus]:
        """Get information about a specific level"""
        if not self.current_session:
            raise ValueError("No active learning session")
        
        if level_index < 0 or level_index >= len(self.current_session.level_list):
            raise ValueError("Invalid level index")
        
        level = self.current_session.level_list[level_index]
        status = self.current_session.level_statuses[level_index]
        
        return level, status
    
    def can_access_level(self, level_index: int) -> bool:
        """Check if a level can be accessed by the user"""
        if not self.current_session:
            return False
        
        if level_index < 0 or level_index >= len(self.current_session.level_list):
            return False
        
        status = self.current_session.level_statuses[level_index]
        return status in [LevelStatus.UNLOCKED, LevelStatus.PASSED, LevelStatus.FAILED]
    
    def start_level(self, level_index: int) -> str:
        """
        Start a specific level if it's accessible
        Returns the level name for the question flow
        """
        if not self.can_access_level(level_index):
            raise ValueError("Level is not accessible")
        
        self.current_session.current_level_index = level_index
        level = self.current_session.level_list[level_index]
        
        return level.level_name
    
    def complete_level(self, level_index: int, level_report: LevelReport) -> bool:
        """
        Complete a level and update the session state
        Returns True if all levels are completed
        """
        if not self.current_session:
            raise ValueError("No active learning session")
        
        if level_index < 0 or level_index >= len(self.current_session.level_list):
            raise ValueError("Invalid level index")
        
        # Add report to history
        self.current_session.history.append(level_report)
        
        # Update level status
        self.current_session.level_statuses[level_index] = level_report.final_status
        
        # If level passed, unlock next level
        if (level_report.final_status == LevelStatus.PASSED and 
            level_index + 1 < len(self.current_session.level_list)):
            self.current_session.level_statuses[level_index + 1] = LevelStatus.UNLOCKED
        
        # Check if all levels are completed
        return self._all_levels_completed()
    
    def _all_levels_completed(self) -> bool:
        """Check if all levels have been attempted"""
        for status in self.current_session.level_statuses:
            if status in [LevelStatus.LOCKED, LevelStatus.UNLOCKED]:
                return False
        return True
    
    def generate_final_summary(self) -> LearningSummary:
        """Generate a final learning summary"""
        if not self.current_session:
            raise ValueError("No active learning session")
        
        if not self._all_levels_completed():
            raise ValueError("Not all levels have been completed")
        
        try:
            summary = self.ai_service.generate_learning_summary(
                self.current_session.main_topic,
                self.current_session.history
            )
            return summary
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def get_progress_stats(self) -> dict:
        """Get overall progress statistics"""
        if not self.current_session:
            return {"total_levels": 0, "completed_levels": 0, "passed_levels": 0}
        
        total_levels = len(self.current_session.level_list)
        completed_levels = sum(1 for status in self.current_session.level_statuses 
                             if status in [LevelStatus.PASSED, LevelStatus.FAILED])
        passed_levels = sum(1 for status in self.current_session.level_statuses 
                          if status == LevelStatus.PASSED)
        
        return {
            "total_levels": total_levels,
            "completed_levels": completed_levels,
            "passed_levels": passed_levels,
            "completion_rate": completed_levels / total_levels if total_levels > 0 else 0,
            "pass_rate": passed_levels / completed_levels if completed_levels > 0 else 0
        }
    
    def reset_session(self):
        """Reset the current learning session"""
        self.current_session = None
