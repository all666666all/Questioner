import os
from typing import Dict, Any

OPENAI_API_KEY = "sk-proj-CP7WLP-5Kd5606O61-Y9SS_e9pOHtl4nq9oqgtrbVEu6oeCaXFWSSIx50QLgVI1oouJYl3dCAT3BlbkFJQ01WxieRk-r2Hdal9d64MDDUsQuYrkGP_ViuNqjvrDs4ldAshdLddXm4IS1l2pnVtC5IZ4kFgA"
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 2000

DEFAULT_NUM_DOMAINS = 5
MIN_DOMAINS = 2
MAX_DOMAINS = 10

DEFAULT_DIFFICULTY = 50
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 100
DIFFICULTY_ADJUSTMENT_RATE = 0.1
MAX_DIFFICULTY_CHANGE = 15

DOMAIN_COMPLETION_THRESHOLD = 100.0
MASTERY_THRESHOLD = 85.0
STRUGGLING_THRESHOLD = 40.0
MIN_QUESTIONS_FOR_ASSESSMENT = 5
MAX_QUESTIONS_PER_DOMAIN = 20

CONFIDENCE_HISTORY_SIZE = 100
CONFIDENCE_BINS = 10
MIN_SAMPLES_PER_BIN = 3
CALIBRATION_SMOOTHING_FACTOR = 0.1

CORRELATION_HISTORY_SIZE = 50
BASE_CONFIDENCE_WEIGHT = 1.0
CALIBRATION_QUALITY_WEIGHT = 0.3
CORRELATION_WEIGHT = 0.2
TIME_CONSISTENCY_WEIGHT = 0.25
DIFFICULTY_ADAPTABILITY_WEIGHT = 0.25

EXPECTED_TIME_BASE = 30  # seconds
TIME_DIFFICULTY_MULTIPLIER = 0.5
FAST_RESPONSE_THRESHOLD = 0.7  # 70% of expected time
SLOW_RESPONSE_THRESHOLD = 1.5  # 150% of expected time

QUALITY_METRICS_HISTORY_SIZE = 100
HIGH_CONFIDENCE_THRESHOLD = 0.7
LOW_CONFIDENCE_THRESHOLD = 0.3
OVERCONFIDENCE_PENALTY = 0.2
CONSISTENCY_WEIGHT = 0.4
CALIBRATION_ERROR_WEIGHT = 0.4

PERFORMANCE_HISTORY_SIZE = 10
CONSECUTIVE_BONUS_MULTIPLIER = 1.2
STABILITY_THRESHOLD = 0.2
MAX_STABILITY_FACTOR = 1.5
MIN_STABILITY_FACTOR = 0.5

CONFIDENCE_SLIDER_STEP = 0.1
PROGRESS_BAR_ANIMATION_DURATION = 500  # milliseconds
QUESTION_TRANSITION_DELAY = 1000  # milliseconds

CORRECT_ANSWER_BASE_POINTS = 10
DIFFICULTY_BONUS_MULTIPLIER = 0.1
CONFIDENCE_BONUS_MULTIPLIER = 0.05
TIME_BONUS_THRESHOLD = 0.8  # 80% of expected time
HONESTY_REWARD = 2  # points for honest low confidence on incorrect answers

DOMAIN_MASTERED_SCORE = 90.0
DOMAIN_COMPLETED_SCORE = 70.0
DOMAIN_STRUGGLING_SCORE = 40.0

DOMAIN_GENERATION_TEMPERATURE = 0.8
QUESTION_GENERATION_TEMPERATURE = 0.7
SUMMARY_GENERATION_TEMPERATURE = 0.6

MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
FALLBACK_TO_MOCK = True

DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

CONFIG: Dict[str, Any] = {
    "openai": {
        "api_key": OPENAI_API_KEY,
        "model": OPENAI_MODEL,
        "temperature": OPENAI_TEMPERATURE,
        "max_tokens": OPENAI_MAX_TOKENS,
    },
    "assessment": {
        "default_num_domains": DEFAULT_NUM_DOMAINS,
        "min_domains": MIN_DOMAINS,
        "max_domains": MAX_DOMAINS,
        "completion_threshold": DOMAIN_COMPLETION_THRESHOLD,
        "mastery_threshold": MASTERY_THRESHOLD,
        "struggling_threshold": STRUGGLING_THRESHOLD,
        "min_questions": MIN_QUESTIONS_FOR_ASSESSMENT,
        "max_questions": MAX_QUESTIONS_PER_DOMAIN,
    },
    "difficulty": {
        "default": DEFAULT_DIFFICULTY,
        "min": MIN_DIFFICULTY,
        "max": MAX_DIFFICULTY,
        "adjustment_rate": DIFFICULTY_ADJUSTMENT_RATE,
        "max_change": MAX_DIFFICULTY_CHANGE,
    },
    "confidence": {
        "history_size": CONFIDENCE_HISTORY_SIZE,
        "bins": CONFIDENCE_BINS,
        "min_samples_per_bin": MIN_SAMPLES_PER_BIN,
        "smoothing_factor": CALIBRATION_SMOOTHING_FACTOR,
        "correlation_history_size": CORRELATION_HISTORY_SIZE,
        "weights": {
            "base": BASE_CONFIDENCE_WEIGHT,
            "calibration_quality": CALIBRATION_QUALITY_WEIGHT,
            "correlation": CORRELATION_WEIGHT,
            "time_consistency": TIME_CONSISTENCY_WEIGHT,
            "difficulty_adaptability": DIFFICULTY_ADAPTABILITY_WEIGHT,
        },
    },
    "timing": {
        "expected_base": EXPECTED_TIME_BASE,
        "difficulty_multiplier": TIME_DIFFICULTY_MULTIPLIER,
        "fast_threshold": FAST_RESPONSE_THRESHOLD,
        "slow_threshold": SLOW_RESPONSE_THRESHOLD,
    },
    "ui": {
        "confidence_step": CONFIDENCE_SLIDER_STEP,
        "progress_animation": PROGRESS_BAR_ANIMATION_DURATION,
        "transition_delay": QUESTION_TRANSITION_DELAY,
    },
    "scoring": {
        "base_points": CORRECT_ANSWER_BASE_POINTS,
        "difficulty_bonus": DIFFICULTY_BONUS_MULTIPLIER,
        "confidence_bonus": CONFIDENCE_BONUS_MULTIPLIER,
        "time_bonus_threshold": TIME_BONUS_THRESHOLD,
        "honesty_reward": HONESTY_REWARD,
    },
    "development": {
        "debug": DEBUG_MODE,
        "log_level": LOG_LEVEL,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
        "fallback_to_mock": FALLBACK_TO_MOCK,
    },
}
