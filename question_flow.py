"""
Question Flow System - Inner layer handling adaptive questioning within assessment domains
"""
import time
from typing import List, Optional, Tuple
from models import (
    DomainAssessment, Question, QuestionResponse, AdaptiveDifficultyEngine
)
from ai_service import AIService
from config import Config

class QuestionFlowManager:
    def __init__(self):
        self.ai_service = AIService()
        self.current_assessment: Optional[DomainAssessment] = None
        self.difficulty_engine: Optional[AdaptiveDifficultyEngine] = None
        self.question_start_time: float = 0
        
    def start_domain_assessment(self, domain_assessment: DomainAssessment) -> DomainAssessment:
        """
        Start a new question session for a specific domain assessment
        """
        if not domain_assessment.domain_name.strip():
            raise ValueError("Domain name cannot be empty")

        self.current_assessment = domain_assessment
        self.difficulty_engine = AdaptiveDifficultyEngine(
            current_difficulty=domain_assessment.current_difficulty
        )

        return self.current_assessment

    def get_current_assessment(self) -> Optional[DomainAssessment]:
        """Get the current domain assessment"""
        return self.current_assessment
    
    def generate_next_question(self) -> Question:
        """
        Generate the next question based on current difficulty and knowledge gaps
        """
        if not self.current_assessment:
            raise ValueError("No active domain assessment")

        if not self.difficulty_engine:
            raise ValueError("Difficulty engine not initialized")

        try:
            question = self.ai_service.generate_assessment_question(
                domain=self.current_assessment.domain_name,
                difficulty=self.difficulty_engine.current_difficulty,
                knowledge_gaps=self.current_assessment.knowledge_gaps
            )

            # Record question start time
            self.question_start_time = time.time()

            return question
        except Exception as e:
            raise Exception(f"Failed to generate assessment question: {str(e)}")
    
    def submit_answer(self, question: Question, user_answer_index: int, confidence: float = 0.5) -> Tuple[bool, str, bool]:
        """
        Submit an answer and update assessment state with adaptive difficulty
        Returns: (is_correct, explanation, is_domain_complete)
        """
        if not self.current_assessment:
            raise ValueError("No active domain assessment")

        if not self.difficulty_engine:
            raise ValueError("Difficulty engine not initialized")

        # Validate answer index
        if user_answer_index < 0 or user_answer_index >= len(question.options):
            raise ValueError("Invalid answer index")

        is_correct = user_answer_index == question.correct_answer_index
        response_time = time.time() - self.question_start_time

        # Create question response record
        response = QuestionResponse(
            question_id=f"{self.current_assessment.domain_name}_{self.current_assessment.questions_attempted}",
            user_answer_index=user_answer_index,
            is_correct=is_correct,
            response_time=response_time,
            confidence_level=confidence
        )

        # Update assessment statistics
        self.current_assessment.questions_attempted += 1
        if is_correct:
            self.current_assessment.questions_correct += 1

        # Record response
        self.current_assessment.response_history.append(response)

        # Update adaptive difficulty
        new_difficulty = self.difficulty_engine.update_difficulty(is_correct, response_time, confidence)
        self.current_assessment.current_difficulty = new_difficulty

        # Handle knowledge tracking
        if is_correct:
            self._handle_correct_answer(question.knowledge_tag)
        else:
            self._handle_incorrect_answer(question.knowledge_tag)

        # Update average response time and confidence
        self._update_assessment_metrics()

        # Check if domain assessment is complete
        is_domain_complete = self._is_domain_assessment_complete()

        return is_correct, question.explanation, is_domain_complete
    
    def _handle_correct_answer(self, knowledge_tag: str):
        """Handle logic when user answers correctly"""
        # Add to mastery areas if consistently correct
        if knowledge_tag not in self.current_assessment.mastery_areas:
            # Check recent performance for this knowledge area
            recent_correct = sum(1 for response in self.current_assessment.response_history[-5:]
                               if response.is_correct)
            if recent_correct >= 3:  # 3 out of last 5 correct
                self.current_assessment.mastery_areas.append(knowledge_tag)
                # Remove from knowledge gaps if present
                if knowledge_tag in self.current_assessment.knowledge_gaps:
                    self.current_assessment.knowledge_gaps.remove(knowledge_tag)

    def _handle_incorrect_answer(self, knowledge_tag: str):
        """Handle logic when user answers incorrectly"""
        # Add knowledge tag to gaps if not already present
        if knowledge_tag not in self.current_assessment.knowledge_gaps:
            self.current_assessment.knowledge_gaps.append(knowledge_tag)

        # Remove from mastery areas if present
        if knowledge_tag in self.current_assessment.mastery_areas:
            self.current_assessment.mastery_areas.remove(knowledge_tag)

    def _update_assessment_metrics(self):
        """Update average response time and confidence score"""
        if not self.current_assessment.response_history:
            return

        # Calculate average response time
        total_time = sum(response.response_time for response in self.current_assessment.response_history)
        self.current_assessment.average_response_time = total_time / len(self.current_assessment.response_history)

        # Calculate average confidence
        total_confidence = sum(response.confidence_level for response in self.current_assessment.response_history)
        self.current_assessment.confidence_score = total_confidence / len(self.current_assessment.response_history)

    def _is_domain_assessment_complete(self) -> bool:
        """Check if the domain assessment is complete"""
        if not self.current_assessment:
            return False

        # Domain is complete when target number of questions is reached
        target_questions = Config.QUESTIONS_PER_DOMAIN

        # Adjust based on performance - may end early if clearly mastered or struggling
        if self.current_assessment.questions_attempted >= Config.MIN_QUESTIONS_PER_DOMAIN:
            accuracy = self.current_assessment.questions_correct / self.current_assessment.questions_attempted

            # End early if clearly mastered (high accuracy with high difficulty)
            if (accuracy >= Config.MASTERY_THRESHOLD and
                self.current_assessment.current_difficulty >= 80 and
                self.current_assessment.questions_attempted >= 10):
                return True

            # End early if clearly struggling (low accuracy with low difficulty)
            if (accuracy <= Config.STRUGGLE_THRESHOLD and
                self.current_assessment.current_difficulty <= 30 and
                self.current_assessment.questions_attempted >= 10):
                return True

        # Standard completion
        return self.current_assessment.questions_attempted >= target_questions

    def get_assessment_progress(self) -> Tuple[int, int, float]:
        """Get current assessment progress (questions answered, target, accuracy)"""
        if not self.current_assessment:
            return 0, Config.QUESTIONS_PER_DOMAIN, 0.0

        accuracy = 0.0
        if self.current_assessment.questions_attempted > 0:
            accuracy = self.current_assessment.questions_correct / self.current_assessment.questions_attempted

        return (
            self.current_assessment.questions_attempted,
            Config.QUESTIONS_PER_DOMAIN,
            accuracy
        )
    
    def get_assessment_info(self) -> dict:
        """Get current assessment information"""
        if not self.current_assessment:
            return {
                "domain_name": "",
                "questions_attempted": 0,
                "questions_correct": 0,
                "accuracy": 0,
                "current_difficulty": Config.INITIAL_DIFFICULTY,
                "confidence_score": 0.5,
                "average_response_time": 0,
                "knowledge_gaps": [],
                "mastery_areas": []
            }

        accuracy = (self.current_assessment.questions_correct /
                   self.current_assessment.questions_attempted
                   if self.current_assessment.questions_attempted > 0 else 0)

        return {
            "domain_name": self.current_assessment.domain_name,
            "questions_attempted": self.current_assessment.questions_attempted,
            "questions_correct": self.current_assessment.questions_correct,
            "accuracy": accuracy * 100,
            "current_difficulty": self.current_assessment.current_difficulty,
            "confidence_score": self.current_assessment.confidence_score,
            "average_response_time": self.current_assessment.average_response_time,
            "knowledge_gaps": self.current_assessment.knowledge_gaps.copy(),
            "mastery_areas": self.current_assessment.mastery_areas.copy()
        }

    def complete_domain_assessment(self) -> DomainAssessment:
        """
        Complete the current domain assessment
        """
        if not self.current_assessment:
            raise ValueError("No active domain assessment")

        return self.current_assessment

    def reset_assessment(self):
        """Reset the current assessment session"""
        self.current_assessment = None
        self.difficulty_engine = None
        self.question_start_time = 0

    def get_assessment_summary(self) -> dict:
        """Get a summary of the current assessment"""
        if not self.current_assessment:
            return {}

        assessment_info = self.get_assessment_info()

        return {
            "domain_name": self.current_assessment.domain_name,
            "assessment_info": assessment_info,
            "recent_responses": self.current_assessment.response_history[-5:],  # Last 5 responses
            "is_complete": self._is_domain_assessment_complete()
        }
