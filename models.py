"""
Data models for the Knowledge Assessment Tool
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import time

class DomainStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"
    STRUGGLING = "struggling"

class AssessmentDomain(BaseModel):
    domain_name: str = Field(..., description="Name of the knowledge domain")
    description: str = Field(..., description="Brief description of what this domain covers")
    estimated_difficulty: int = Field(50, description="Estimated difficulty level (1-100)")

class Question(BaseModel):
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of answer options")
    correct_answer_index: int = Field(..., description="Index of the correct answer (0-based)")
    knowledge_tag: str = Field(..., description="Knowledge point tag for this question")
    explanation: str = Field(..., description="Explanation of the correct answer")
    difficulty_level: int = Field(..., description="Difficulty level of this question (1-100)")
    estimated_time: int = Field(30, description="Estimated time to answer in seconds")

class QuestionResponse(BaseModel):
    question_id: str
    user_answer_index: int
    is_correct: bool
    response_time: float = Field(..., description="Time taken to answer in seconds")
    confidence_level: float = Field(0.5, description="User's confidence in their answer (0-1)")
    timestamp: float = Field(default_factory=time.time)

class DomainAssessment(BaseModel):
    domain_name: str
    status: DomainStatus = DomainStatus.NOT_STARTED
    current_difficulty: int = 50
    questions_attempted: int = 0
    questions_correct: int = 0
    response_history: List[QuestionResponse] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)
    mastery_areas: List[str] = Field(default_factory=list)
    average_response_time: float = 0.0
    confidence_score: float = 0.5

class AssessmentSession(BaseModel):
    main_topic: str
    domain_list: List[AssessmentDomain] = Field(default_factory=list)
    current_domain_index: int = 0
    domain_assessments: List[DomainAssessment] = Field(default_factory=list)
    overall_score: float = 0.0
    start_time: float = Field(default_factory=time.time)
    total_questions: int = 0
    total_correct: int = 0

class AdaptiveDifficultyEngine(BaseModel):
    current_difficulty: int = 50
    recent_performance: List[bool] = Field(default_factory=list)  # Recent correct/incorrect
    recent_response_times: List[float] = Field(default_factory=list)
    consecutive_correct: int = 0
    consecutive_incorrect: int = 0
    confidence_trend: List[float] = Field(default_factory=list)

    def update_difficulty(self, is_correct: bool, response_time: float, confidence: float) -> int:
        """Update difficulty based on performance metrics"""
        from config import Config

        # Update tracking variables
        self.recent_performance.append(is_correct)
        self.recent_response_times.append(response_time)
        self.confidence_trend.append(confidence)

        # Keep only recent history
        window = Config.MOVING_AVERAGE_WINDOW
        if len(self.recent_performance) > window:
            self.recent_performance = self.recent_performance[-window:]
            self.recent_response_times = self.recent_response_times[-window:]
            self.confidence_trend = self.confidence_trend[-window:]

        # Update streaks
        if is_correct:
            self.consecutive_correct += 1
            self.consecutive_incorrect = 0
        else:
            self.consecutive_incorrect += 1
            self.consecutive_correct = 0

        # Calculate difficulty adjustment
        adjustment = self._calculate_difficulty_adjustment(is_correct, response_time, confidence)

        # Apply adjustment
        self.current_difficulty = max(
            Config.MIN_DIFFICULTY,
            min(Config.MAX_DIFFICULTY, self.current_difficulty + adjustment)
        )

        return self.current_difficulty

    def _calculate_difficulty_adjustment(self, is_correct: bool, response_time: float, confidence: float) -> int:
        """Calculate the difficulty adjustment based on multiple factors"""
        from config import Config

        base_adjustment = Config.DIFFICULTY_STEP_SIZE

        # Performance-based adjustment
        if is_correct:
            adjustment = base_adjustment
            # Increase more if answered quickly and confidently
            if response_time < 15 and confidence > 0.8:
                adjustment *= 1.5
            # Apply streak multiplier
            if self.consecutive_correct > 2:
                adjustment *= Config.STREAK_MULTIPLIER
        else:
            adjustment = -base_adjustment
            # Decrease more if answered slowly or with low confidence
            if response_time > 45 or confidence < 0.3:
                adjustment *= 1.5
            # Apply streak multiplier
            if self.consecutive_incorrect > 1:
                adjustment *= Config.STREAK_MULTIPLIER

        # Response time factor
        if len(self.recent_response_times) > 0:
            avg_time = sum(self.recent_response_times) / len(self.recent_response_times)
            time_factor = (30 - avg_time) / 30 * Config.RESPONSE_TIME_FACTOR
            adjustment += time_factor * base_adjustment

        # Confidence factor
        if len(self.confidence_trend) > 0:
            avg_confidence = sum(self.confidence_trend) / len(self.confidence_trend)
            confidence_factor = (avg_confidence - 0.5) * 2  # Scale to -1 to 1
            adjustment += confidence_factor * base_adjustment * 0.5

        return int(adjustment)

class AssessmentSummary(BaseModel):
    title: str
    overall_score: float
    total_time_minutes: float
    domains_assessed: int
    strengths: List[str]
    areas_for_improvement: List[str]
    knowledge_level: str  # "Beginner", "Intermediate", "Advanced", "Expert"
    recommendations: List[str]
    detailed_breakdown: Dict[str, Dict[str, Any]]
