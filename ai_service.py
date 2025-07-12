"""
AI Service for generating assessment domains, questions, and analysis
"""
import json
import openai
from typing import List, Optional
from config import Config
from models import AssessmentDomain, Question, AssessmentSummary, DomainAssessment

class AIService:
    def __init__(self):
        Config.validate()
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL

    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """Make a call to OpenAI API"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"AI API call failed: {str(e)}")

    def generate_assessment_domains(self, main_topic: str, num_domains: int = None) -> List[AssessmentDomain]:
        """
        Prompt 1: Assessment Domain Planning AI
        Generate knowledge domains for comprehensive assessment of a topic
        """
        if num_domains is None:
            num_domains = Config.DEFAULT_NUM_DOMAINS

        prompt = f"""# Role and Objective
You are an expert knowledge assessor. Your task is to break down a subject into {num_domains} distinct knowledge domains for comprehensive assessment. Focus on identifying core areas that would reveal someone's true understanding and competency level. Your response must be a pure JSON array.

# Input
1. `mainTopic` (string): {main_topic}
2. `numDomains` (number): {num_domains}

# Task
1. Analyze the `mainTopic` from an assessment perspective.
2. Identify the core knowledge domains that define expertise in this area.
3. Arrange these domains to cover the breadth and depth of the subject.
4. For each domain, provide a name and description focused on what knowledge/skills will be assessed.
5. Estimate the relative difficulty of each domain (1-100 scale).

# Output Format (strictly follow, no extra text)
[
  {{
    "domain_name": "Domain 1 Name (e.g., 'Fundamental Concepts')",
    "description": "What knowledge/skills this domain assesses (e.g., 'Assesses understanding of core principles and basic terminology.')",
    "estimated_difficulty": 30
  }},
  {{
    "domain_name": "Domain 2 Name (e.g., 'Applied Problem Solving')",
    "description": "What knowledge/skills this domain assesses (e.g., 'Evaluates ability to apply concepts to solve real-world problems.')",
    "estimated_difficulty": 70
  }}
]"""

        try:
            response = self._call_openai(prompt, temperature=0.3)
            # Parse JSON response
            domains_data = json.loads(response)
            return [AssessmentDomain(
                domain_name=domain["domain_name"],
                description=domain["description"],
                estimated_difficulty=domain.get("estimated_difficulty", 50)
            ) for domain in domains_data]
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate assessment domains: {str(e)}")

    def generate_assessment_question(self, domain: str, difficulty: int, knowledge_gaps: List[str] = None) -> Question:
        """
        Prompt 2: Assessment Question Generation AI
        Generate a multiple choice question for knowledge assessment
        """
        if knowledge_gaps is None:
            knowledge_gaps = []

        gaps_str = json.dumps(knowledge_gaps, ensure_ascii=False)

        prompt = f"""# Role and Objective
You are an expert assessment designer. Your task is to create a high-quality multiple-choice question that accurately measures knowledge in a specific domain at a precise difficulty level. Your response must be a pure JSON object.

# Input
1. `domain` (string): {domain}
2. `difficulty` (number): {difficulty} (1-100 scale, where 1=very basic, 100=expert level)
3. `knowledgeGaps` (array): {gaps_str}

# Task
1. Create a question that precisely matches the difficulty level (not too easy, not too hard).
2. If `knowledgeGaps` is provided, focus on assessing those specific areas.
3. Design 4-5 options with exactly one correct answer.
4. Include plausible distractors that reveal common misconceptions.
5. Provide a knowledge tag and clear explanation.
6. Estimate the time a knowledgeable person would need to answer.

# Difficulty Guidelines
- 1-20: Basic definitions and simple recall
- 21-40: Understanding and simple application
- 41-60: Analysis and moderate application
- 61-80: Synthesis and complex problem-solving
- 81-100: Expert-level evaluation and advanced concepts

# Output Format (strictly follow, no extra text)
{{
  "question": "Clear, precise question text that tests the intended knowledge",
  "options": [
    "Option A - plausible but incorrect",
    "Option B - correct answer",
    "Option C - plausible but incorrect",
    "Option D - plausible but incorrect"
  ],
  "correct_answer_index": 1,
  "knowledge_tag": "Specific knowledge area being tested",
  "explanation": "Clear explanation of why the correct answer is right and why others are wrong",
  "difficulty_level": {difficulty},
  "estimated_time": 30
}}"""

        try:
            response = self._call_openai(prompt, temperature=0.7)
            question_data = json.loads(response)
            return Question(**question_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse question response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate assessment question: {str(e)}")

    def generate_assessment_summary(self, main_topic: str, domain_assessments: List[DomainAssessment], total_time: float) -> AssessmentSummary:
        """
        Prompt 3: Assessment Analysis AI
        Generate a comprehensive assessment summary based on user performance
        """
        assessment_data = []
        total_questions = 0
        total_correct = 0

        for assessment in domain_assessments:
            accuracy = assessment.questions_correct / max(assessment.questions_attempted, 1)
            assessment_data.append({
                "domainName": assessment.domain_name,
                "status": assessment.status.value,
                "accuracy": round(accuracy, 2),
                "questionsAttempted": assessment.questions_attempted,
                "questionsCorrect": assessment.questions_correct,
                "knowledgeGaps": assessment.knowledge_gaps,
                "masteryAreas": assessment.mastery_areas,
                "averageResponseTime": round(assessment.average_response_time, 1),
                "confidenceScore": round(assessment.confidence_score, 2)
            })
            total_questions += assessment.questions_attempted
            total_correct += assessment.questions_correct

        overall_accuracy = total_correct / max(total_questions, 1)
        assessment_str = json.dumps(assessment_data, ensure_ascii=False, indent=2)

        prompt = f"""# Role and Objective
You are an expert knowledge assessor and analyst. Your task is to analyze a user's performance across multiple knowledge domains and generate a comprehensive assessment report. Your response must be a pure JSON object.

# Input
1. `mainTopic` (string): {main_topic}
2. `assessmentData` (array): {assessment_str}
3. `totalTimeMinutes` (number): {round(total_time / 60, 1)}
4. `overallAccuracy` (number): {round(overall_accuracy, 2)}

# Task
1. Determine the user's overall knowledge level (Beginner/Intermediate/Advanced/Expert).
2. Identify their strongest domains and specific mastery areas.
3. Identify areas needing improvement and specific knowledge gaps.
4. Provide actionable recommendations for further development.
5. Create a detailed breakdown of performance by domain.

# Knowledge Level Guidelines
- Beginner (0-40% accuracy): Basic understanding, needs foundational work
- Intermediate (41-70% accuracy): Solid grasp of fundamentals, ready for application
- Advanced (71-85% accuracy): Strong competency, can handle complex scenarios
- Expert (86-100% accuracy): Mastery level, can teach and innovate

# Output Format (strictly follow, no extra text)
{{
  "title": "Knowledge Assessment Report: {main_topic}",
  "overall_score": {round(overall_accuracy * 100, 1)},
  "total_time_minutes": {round(total_time / 60, 1)},
  "domains_assessed": {len(domain_assessments)},
  "knowledge_level": "Determine based on overall performance",
  "strengths": [
    "List specific domains and knowledge areas where user excelled"
  ],
  "areas_for_improvement": [
    "List specific domains and knowledge gaps that need attention"
  ],
  "recommendations": [
    "Provide 3-5 specific, actionable recommendations for improvement"
  ],
  "detailed_breakdown": {{
    "domain_name_1": {{
      "score": 85.5,
      "status": "mastered",
      "key_strengths": ["specific strength 1", "specific strength 2"],
      "improvement_areas": ["specific gap 1"]
    }}
  }}
}}"""

        try:
            response = self._call_openai(prompt, temperature=0.5)
            summary_data = json.loads(response)
            return AssessmentSummary(**summary_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse assessment summary response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate assessment summary: {str(e)}")
