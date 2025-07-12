from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import statistics
import math

class DomainStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"
    STRUGGLING = "struggling"

class LevelStatus(Enum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    PASSED = "passed"
    FAILED = "failed"

@dataclass
class AssessmentDomain:
    domain_name: str
    description: str
    estimated_difficulty: int  # 1-100

@dataclass
class Question:
    question: str
    options: List[str]
    correct_answer_index: int
    knowledge_tag: str
    explanation: str
    difficulty_level: int  # 1-100
    estimated_time: int  # seconds

@dataclass
class QuestionResponse:
    question_id: str
    user_answer_index: int
    is_correct: bool
    response_time: float  # seconds
    confidence_level: float  # 0-1
    timestamp: datetime

@dataclass
class DomainAssessment:
    domain_name: str
    status: DomainStatus = DomainStatus.NOT_STARTED
    current_difficulty: int = 50
    questions_attempted: int = 0
    questions_correct: int = 0
    response_history: List[QuestionResponse] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)
    mastery_areas: List[str] = field(default_factory=list)
    average_response_time: float = 0.0
    confidence_score: float = 0.0

@dataclass
class AssessmentSession:
    main_topic: str
    domain_list: List[AssessmentDomain] = field(default_factory=list)
    current_domain_index: int = 0
    domain_assessments: List[DomainAssessment] = field(default_factory=list)
    overall_score: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    total_questions: int = 0
    total_correct: int = 0

class ConfidenceCalibrationEngine:
    def __init__(self, history_size: int = 100):
        self.confidence_accuracy_pairs: List[tuple[float, bool]] = []
        self.calibration_curve: Dict[float, float] = {}
        self.history_size = history_size

    def update_calibration(self, confidence: float, is_correct: bool):
        self.confidence_accuracy_pairs.append((confidence, is_correct))
        
        if len(self.confidence_accuracy_pairs) > self.history_size:
            self.confidence_accuracy_pairs.pop(0)
        
        self.calculate_calibration_curve()

    def calculate_calibration_curve(self):
        if len(self.confidence_accuracy_pairs) < 10:
            return
        
        bins = {}
        for confidence, is_correct in self.confidence_accuracy_pairs:
            bin_key = round(confidence, 1)
            if bin_key not in bins:
                bins[bin_key] = []
            bins[bin_key].append(is_correct)
        
        self.calibration_curve = {}
        for bin_key, results in bins.items():
            if len(results) >= 3:
                accuracy = sum(results) / len(results)
                self.calibration_curve[bin_key] = accuracy

    def get_calibrated_confidence(self, raw_confidence: float) -> float:
        bin_key = round(raw_confidence, 1)
        
        if bin_key in self.calibration_curve:
            return self.calibration_curve[bin_key]
        
        return self.interpolate_confidence(raw_confidence)

    def interpolate_confidence(self, confidence: float) -> float:
        if not self.calibration_curve:
            return confidence
        
        sorted_bins = sorted(self.calibration_curve.keys())
        
        if confidence <= sorted_bins[0]:
            return self.calibration_curve[sorted_bins[0]]
        
        if confidence >= sorted_bins[-1]:
            return self.calibration_curve[sorted_bins[-1]]
        
        for i in range(len(sorted_bins) - 1):
            if sorted_bins[i] <= confidence <= sorted_bins[i + 1]:
                x1, y1 = sorted_bins[i], self.calibration_curve[sorted_bins[i]]
                x2, y2 = sorted_bins[i + 1], self.calibration_curve[sorted_bins[i + 1]]
                
                interpolated = y1 + (y2 - y1) * (confidence - x1) / (x2 - x1)
                return interpolated
        
        return confidence

class EnhancedConfidenceEngine:
    def __init__(self, history_size: int = 50):
        self.calibration_engine = ConfidenceCalibrationEngine()
        self.confidence_history: List[float] = []
        self.accuracy_history: List[float] = []
        self.confidence_accuracy_correlation: float = 0.0
        self.history_size = history_size

    def calculate_confidence_impact(self, confidence: float, is_correct: bool, 
                                  response_time: float, difficulty: int) -> float:
        calibrated_confidence = self.calibration_engine.get_calibrated_confidence(confidence)
        
        self.calibration_engine.update_calibration(confidence, is_correct)
        self.update_correlation(confidence, is_correct)
        
        return self.calculate_comprehensive_impact(
            calibrated_confidence, is_correct, response_time, difficulty, confidence
        )

    def update_correlation(self, confidence: float, is_correct: bool):
        self.confidence_history.append(confidence)
        self.accuracy_history.append(float(is_correct))
        
        if len(self.confidence_history) > self.history_size:
            self.confidence_history.pop(0)
            self.accuracy_history.pop(0)
        
        if len(self.confidence_history) >= 10:
            self.confidence_accuracy_correlation = self.calculate_correlation(
                self.confidence_history, self.accuracy_history
            )

    def calculate_correlation(self, x: List[float], y: List[float]) -> float:
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator

    def calculate_comprehensive_impact(self, calibrated_confidence: float, is_correct: bool,
                                     response_time: float, difficulty: int, raw_confidence: float) -> float:
        base_impact = calibrated_confidence if is_correct else -calibrated_confidence
        
        calibration_quality_weight = min(1.0, len(self.calibration_engine.confidence_accuracy_pairs) / 50)
        
        correlation_weight = abs(self.confidence_accuracy_correlation)
        
        expected_time = 30 + (difficulty / 100) * 30
        time_ratio = response_time / expected_time
        
        if is_correct and time_ratio < 0.8 and raw_confidence > 0.7:
            time_consistency_weight = 1.2
        elif not is_correct and time_ratio > 1.2 and raw_confidence < 0.4:
            time_consistency_weight = 1.1
        else:
            time_consistency_weight = 1.0
        
        if (difficulty > 70 and raw_confidence > 0.8) or (difficulty < 30 and raw_confidence < 0.3):
            difficulty_adaptability_weight = 1.15
        else:
            difficulty_adaptability_weight = 1.0
        
        comprehensive_impact = (
            base_impact * 
            (1 + 0.3 * calibration_quality_weight) *
            (1 + 0.2 * correlation_weight) *
            time_consistency_weight *
            difficulty_adaptability_weight
        )
        
        return comprehensive_impact

class ConfidenceQualityMetrics:
    def __init__(self, history_size: int = 100):
        self.confidence_accuracy_data: List[tuple[float, bool]] = []
        self.history_size = history_size

    def add_data_point(self, confidence: float, is_correct: bool):
        self.confidence_accuracy_data.append((confidence, is_correct))
        
        if len(self.confidence_accuracy_data) > self.history_size:
            self.confidence_accuracy_data.pop(0)

    def get_confidence_quality_score(self) -> float:
        if len(self.confidence_accuracy_data) < 10:
            return 0.5
        
        calibration_error = self.calculate_calibration_error()
        overconfidence = self.calculate_overconfidence()
        consistency = self.calculate_consistency()
        
        quality_score = (
            0.4 * (1 - calibration_error) +
            0.4 * (1 - overconfidence) +
            0.2 * consistency
        )
        
        return max(0.0, min(1.0, quality_score))

    def calculate_calibration_error(self) -> float:
        bins = {}
        for confidence, is_correct in self.confidence_accuracy_data:
            bin_key = round(confidence, 1)
            if bin_key not in bins:
                bins[bin_key] = []
            bins[bin_key].append(is_correct)
        
        total_error = 0.0
        total_weight = 0
        
        for bin_confidence, results in bins.items():
            if len(results) >= 3:
                actual_accuracy = sum(results) / len(results)
                error = abs(bin_confidence - actual_accuracy)
                weight = len(results)
                total_error += error * weight
                total_weight += weight
        
        return total_error / total_weight if total_weight > 0 else 0.0

    def calculate_overconfidence(self) -> float:
        high_confidence_incorrect = 0
        high_confidence_total = 0
        
        for confidence, is_correct in self.confidence_accuracy_data:
            if confidence > 0.7:
                high_confidence_total += 1
                if not is_correct:
                    high_confidence_incorrect += 1
        
        return high_confidence_incorrect / high_confidence_total if high_confidence_total > 0 else 0.0

    def calculate_consistency(self) -> float:
        correct_confidences = [conf for conf, correct in self.confidence_accuracy_data if correct]
        incorrect_confidences = [conf for conf, correct in self.confidence_accuracy_data if not correct]
        
        if len(correct_confidences) < 3 or len(incorrect_confidences) < 3:
            return 0.5
        
        correct_variance = statistics.variance(correct_confidences)
        incorrect_variance = statistics.variance(incorrect_confidences)
        
        avg_variance = (correct_variance + incorrect_variance) / 2
        consistency = 1 / (1 + avg_variance)
        
        return consistency

class ImprovedAdaptiveDifficultyEngine:
    def __init__(self, initial_difficulty: int = 50, history_size: int = 10):
        self.current_difficulty = float(initial_difficulty)
        self.recent_performance: List[bool] = []
        self.recent_response_times: List[float] = []
        self.consecutive_correct = 0
        self.consecutive_incorrect = 0
        self.history_size = history_size
        self.confidence_engine = EnhancedConfidenceEngine()

    def update_difficulty(self, is_correct: bool, response_time: float, confidence: float):
        self.recent_performance.append(is_correct)
        self.recent_response_times.append(response_time)
        
        if len(self.recent_performance) > self.history_size:
            self.recent_performance.pop(0)
            self.recent_response_times.pop(0)
        
        if is_correct:
            self.consecutive_correct += 1
            self.consecutive_incorrect = 0
        else:
            self.consecutive_incorrect += 1
            self.consecutive_correct = 0
        
        adjustment = self.calculate_enhanced_adjustment(is_correct, response_time, confidence)
        
        self.current_difficulty = max(1, min(100, self.current_difficulty + adjustment))

    def calculate_enhanced_adjustment(self, is_correct: bool, response_time: float, confidence: float) -> float:
        base_adjustment = 5 if is_correct else -5
        
        if self.consecutive_correct >= 3:
            base_adjustment *= 1.2
        elif self.consecutive_incorrect >= 3:
            base_adjustment *= 1.2
        
        confidence_impact = self.confidence_engine.calculate_confidence_impact(
            confidence, is_correct, response_time, int(self.current_difficulty)
        )
        
        time_impact = self.calculate_time_impact(response_time, is_correct)
        
        stability_factor = self.calculate_stability_factor()
        
        total_adjustment = (base_adjustment + confidence_impact + time_impact) * stability_factor
        
        return max(-15, min(15, total_adjustment))

    def calculate_time_impact(self, response_time: float, is_correct: bool) -> float:
        expected_time = 30 + (self.current_difficulty / 100) * 30
        time_ratio = response_time / expected_time
        
        if is_correct:
            if time_ratio < 0.7:
                return 2
            elif time_ratio > 1.5:
                return -1
        else:
            if time_ratio < 0.7:
                return -2
            elif time_ratio > 1.5:
                return 1
        
        return 0

    def calculate_stability_factor(self) -> float:
        if len(self.recent_performance) < 5:
            return 1.0
        
        recent_accuracy = sum(self.recent_performance) / len(self.recent_performance)
        
        changes = 0
        for i in range(1, len(self.recent_performance)):
            if self.recent_performance[i] != self.recent_performance[i-1]:
                changes += 1
        
        change_rate = changes / (len(self.recent_performance) - 1)
        
        if change_rate > 0.6:
            return 0.7
        elif change_rate < 0.2:
            return 1.3
        else:
            return 1.0
    
    def calculate_system_confidence(self, is_correct: bool, response_time: float) -> float:
        """
        Calculate system-determined confidence based on response patterns and timing.
        This replaces user-input confidence with intelligent system calculation.
        """
        base_confidence = 0.5
        
        if is_correct:
            base_confidence += 0.3
        else:
            base_confidence -= 0.2
        
        expected_time = 30.0 + (self.current_difficulty / 100) * 30.0
        time_ratio = response_time / expected_time
        
        if is_correct and time_ratio < 0.7:
            base_confidence += 0.2
        elif is_correct and time_ratio > 1.5:
            base_confidence -= 0.1
        elif not is_correct and time_ratio < 0.5:
            base_confidence -= 0.2
        
        if self.consecutive_correct >= 3:
            base_confidence += 0.1
        elif self.consecutive_incorrect >= 2:
            base_confidence -= 0.1
        
        if len(self.recent_performance) >= 3:
            recent_accuracy = sum(self.recent_performance[-3:]) / 3
            if recent_accuracy > 0.8 and self.current_difficulty < 70:
                base_confidence += 0.1
            elif recent_accuracy < 0.4 and self.current_difficulty > 50:
                base_confidence -= 0.1
        
        return max(0.1, min(0.9, base_confidence))
