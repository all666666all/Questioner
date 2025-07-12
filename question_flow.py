from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import time
from models import (
    DomainAssessment, Question, QuestionResponse, DomainStatus,
    ImprovedAdaptiveDifficultyEngine, ConfidenceQualityMetrics
)
from ai_service import AIService
from config import CONFIG

class QuestionFlowManager:
    def __init__(self):
        self.ai_service = AIService()
        self.current_domain_assessment: Optional[DomainAssessment] = None
        self.difficulty_engine: Optional[ImprovedAdaptiveDifficultyEngine] = None
        self.confidence_metrics: Optional[ConfidenceQualityMetrics] = None
        self.current_question: Optional[Question] = None
        self.question_start_time: Optional[float] = None
        self.domain_progress: float = 0.0

    def start_domain_assessment(self, domain_assessment: DomainAssessment) -> bool:
        """
        Initializes an in-domain question session and sets the initial difficulty of the difficulty engine.
        """
        try:
            self.current_domain_assessment = domain_assessment
            
            self.difficulty_engine = ImprovedAdaptiveDifficultyEngine(
                initial_difficulty=domain_assessment.current_difficulty
            )
            
            self.confidence_metrics = ConfidenceQualityMetrics(
                history_size=CONFIG["confidence"]["history_size"]
            )
            
            self.domain_progress = 0.0
            
            domain_assessment.status = DomainStatus.IN_PROGRESS
            
            return True
        except Exception as e:
            print(f"Error starting domain assessment: {e}")
            return False

    def generate_question(self) -> Optional[Question]:
        """
        Calls the AI service to generate a question that matches the current difficulty and knowledge gaps.
        """
        if not self.current_domain_assessment or not self.difficulty_engine:
            return None
        
        try:
            current_difficulty = int(self.difficulty_engine.current_difficulty)
            
            question = self.ai_service.generate_assessment_question(
                domain=self.current_domain_assessment.domain_name,
                difficulty=current_difficulty,
                knowledge_gaps=self.current_domain_assessment.knowledge_gaps
            )
            
            self.current_question = question
            self.question_start_time = time.time()
            
            return question
        except Exception as e:
            print(f"Error generating question: {e}")
            return None

    def submit_answer(self, answer_index: int, confidence: float) -> Dict[str, Any]:
        """
        Handles answer submission with all required functionality:
        1. Records response time and determines if the answer is correct
        2. Adds the (confidence, is_correct) data point to ConfidenceQualityMetrics
        3. Calls the update_difficulty method of ImprovedAdaptiveDifficultyEngine
        4. Calls calculate_enhanced_progress_increment to calculate the progress increment
        5. If the answer is incorrect, records the knowledge tag to the weakness list
        6. Generates answer feedback including confidence quality feedback
        7. Checks domain progress; if 100%, completes the domain assessment; otherwise, generates the next question
        """
        if not self.current_question or not self.current_domain_assessment or not self.difficulty_engine or not self.confidence_metrics:
            return {"error": "No active question or assessment"}
        
        response_time = time.time() - self.question_start_time if self.question_start_time else 30.0
        is_correct = answer_index == self.current_question.correct_answer_index
        
        question_response = QuestionResponse(
            question_id=f"{self.current_domain_assessment.domain_name}_{len(self.current_domain_assessment.response_history)}",
            user_answer_index=answer_index,
            is_correct=is_correct,
            response_time=response_time,
            confidence_level=confidence,
            timestamp=datetime.now()
        )
        
        self.current_domain_assessment.response_history.append(question_response)
        self.current_domain_assessment.questions_attempted += 1
        
        if is_correct:
            self.current_domain_assessment.questions_correct += 1
        
        # Calculate system-determined confidence
        system_confidence = self.difficulty_engine.calculate_system_confidence(is_correct, response_time)
        
        self.confidence_metrics.add_data_point(system_confidence, is_correct)
        
        self.difficulty_engine.update_difficulty(is_correct, response_time, system_confidence)
        
        self.current_domain_assessment.current_difficulty = int(self.difficulty_engine.current_difficulty)
        
        progress_increment = self.calculate_enhanced_progress_increment(
            is_correct, system_confidence, self.current_question.difficulty_level, response_time
        )
        
        self.domain_progress += progress_increment
        self.domain_progress = min(100.0, self.domain_progress)  # Cap at 100%
        
        if not is_correct:
            knowledge_tag = self.current_question.knowledge_tag
            if knowledge_tag not in self.current_domain_assessment.knowledge_gaps:
                self.current_domain_assessment.knowledge_gaps.append(knowledge_tag)
        else:
            knowledge_tag = self.current_question.knowledge_tag
            if knowledge_tag not in self.current_domain_assessment.mastery_areas:
                self.current_domain_assessment.mastery_areas.append(knowledge_tag)
        
        total_time = sum(r.response_time for r in self.current_domain_assessment.response_history)
        self.current_domain_assessment.average_response_time = total_time / len(self.current_domain_assessment.response_history)
        
        self.current_domain_assessment.confidence_score = self.confidence_metrics.get_confidence_quality_score()
        
        feedback = self.generate_enhanced_answer_feedback(
            is_correct, self.current_question.explanation, system_confidence
        )
        
        result = {
            "is_correct": is_correct,
            "correct_answer": self.current_question.options[self.current_question.correct_answer_index],
            "explanation": self.current_question.explanation,
            "feedback": feedback,
            "progress": self.domain_progress,
            "confidence_quality": self.confidence_metrics.get_confidence_quality_score(),
            "current_difficulty": self.difficulty_engine.current_difficulty,
            "domain_complete": False,
            "next_question": None,
            "response_time": response_time,
            "knowledge_tag": self.current_question.knowledge_tag
        }
        
        if self.domain_progress >= 100.0:
            completion_result = self.complete_domain_assessment()
            result["domain_complete"] = True
            result["domain_status"] = completion_result["status"]
            result["final_stats"] = completion_result["stats"]
        else:
            next_question = self.generate_question()
            result["next_question"] = next_question
        
        return result

    def calculate_enhanced_progress_increment(self, is_correct: bool, confidence: float, 
                                            difficulty: int, response_time: float) -> float:
        """
        Calculates the progress bar increment after a single question.
        For correct answers, the base increment is boosted based on question difficulty, confidence, and confidence quality.
        For incorrect answers, progress does not increase, but honest low-confidence assessments may receive a small 'honesty reward.'
        """
        if not self.confidence_metrics:
            return 0.0
        
        base_increment = CONFIG["scoring"]["base_points"]  # Base 10 points
        
        if is_correct:
            increment = base_increment
            
            difficulty_bonus = (difficulty / 100) * CONFIG["scoring"]["difficulty_bonus"] * base_increment
            increment += difficulty_bonus
            
            confidence_bonus = confidence * CONFIG["scoring"]["confidence_bonus"] * base_increment
            increment += confidence_bonus
            
            quality_score = self.confidence_metrics.get_confidence_quality_score()
            quality_bonus = quality_score * 0.1 * base_increment
            increment += quality_bonus
            
            expected_time = CONFIG["timing"]["expected_base"] + (difficulty / 100) * 30
            if response_time < expected_time * CONFIG["scoring"]["time_bonus_threshold"]:
                time_bonus = 0.2 * base_increment
                increment += time_bonus
            
        else:
            increment = 0.0
            
            if confidence < 0.4:  # Low confidence threshold
                honesty_reward = CONFIG["scoring"]["honesty_reward"]
                increment += honesty_reward
        
        max_questions = CONFIG["assessment"]["max_questions"]
        percentage_increment = (increment / (base_increment * max_questions)) * 100
        
        return min(percentage_increment, 20.0)  # Cap individual increments at 20%

    def generate_enhanced_answer_feedback(self, is_correct: bool, explanation: str, confidence: float) -> str:
        """
        Generates answer feedback and appends a statement about the quality of the user's confidence assessment.
        """
        if not self.confidence_metrics:
            return explanation
        
        if is_correct:
            feedback = f"✅ Correct! {explanation}"
        else:
            feedback = f"❌ Incorrect. {explanation}"
        
        quality_score = self.confidence_metrics.get_confidence_quality_score()
        
        if is_correct and confidence > 0.8:
            feedback += "\n\n🎯 Excellent confidence calibration! You were highly confident and correct."
        elif is_correct and confidence < 0.5:
            feedback += "\n\n🤔 You were correct but had low confidence. Trust your knowledge more!"
        elif not is_correct and confidence > 0.8:
            feedback += "\n\n⚠️ You were very confident but incorrect. Consider reviewing this topic."
        elif not is_correct and confidence < 0.4:
            feedback += "\n\n👍 Good self-awareness! You correctly identified uncertainty on a difficult question."
        
        if quality_score > 0.8:
            feedback += f"\n\n📊 Your confidence assessment quality is excellent ({quality_score:.1%})."
        elif quality_score > 0.6:
            feedback += f"\n\n📊 Your confidence assessment quality is good ({quality_score:.1%})."
        elif quality_score > 0.4:
            feedback += f"\n\n📊 Your confidence assessment quality is fair ({quality_score:.1%}). Try to better match your confidence to your actual knowledge."
        else:
            feedback += f"\n\n📊 Your confidence assessment needs improvement ({quality_score:.1%}). Focus on being more honest about your certainty level."
        
        return feedback

    def complete_domain_assessment(self) -> Dict[str, Any]:
        """
        Called when domain progress is full. Calculates final statistics, determines domain status 
        (MASTERED, COMPLETED, STRUGGLING), and updates the DomainAssessment object.
        """
        if not self.current_domain_assessment:
            return {"error": "No active domain assessment"}
        
        total_questions = self.current_domain_assessment.questions_attempted
        correct_answers = self.current_domain_assessment.questions_correct
        accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        if accuracy >= CONFIG["scoring"]["domain_mastered_score"]:
            status = DomainStatus.MASTERED
        elif accuracy >= CONFIG["scoring"]["domain_completed_score"]:
            status = DomainStatus.COMPLETED
        else:
            status = DomainStatus.STRUGGLING
        
        self.current_domain_assessment.status = status
        
        avg_confidence = sum(r.confidence_level for r in self.current_domain_assessment.response_history) / len(self.current_domain_assessment.response_history)
        avg_difficulty = 0.5
        if self.difficulty_engine and self.difficulty_engine.recent_performance:
            avg_difficulty = sum(self.difficulty_engine.recent_performance) / len(self.difficulty_engine.recent_performance)
        
        final_stats = {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "accuracy": accuracy,
            "average_confidence": avg_confidence,
            "average_response_time": self.current_domain_assessment.average_response_time,
            "confidence_quality": self.current_domain_assessment.confidence_score,
            "final_difficulty": self.current_domain_assessment.current_difficulty,
            "knowledge_gaps": len(self.current_domain_assessment.knowledge_gaps),
            "mastery_areas": len(self.current_domain_assessment.mastery_areas)
        }
        
        return {
            "status": status.value,
            "stats": final_stats
        }

    def get_current_progress(self) -> float:
        """
        Returns the current progress percentage for the domain.
        """
        return self.domain_progress

    def get_current_difficulty(self) -> int:
        """
        Returns the current difficulty level.
        """
        if self.difficulty_engine:
            return int(self.difficulty_engine.current_difficulty)
        return CONFIG["difficulty"]["default"]

    def reset_session(self):
        """
        Resets the current question flow session.
        """
        self.current_domain_assessment = None
        self.difficulty_engine = None
        self.confidence_metrics = None
        self.current_question = None
        self.question_start_time = None
        self.domain_progress = 0.0
