import json
import openai
from typing import List, Dict, Any, Optional
import time
import random
from config import CONFIG
from models import AssessmentDomain, Question

class AIService:
    def __init__(self):
        self.api_key = CONFIG["openai"]["api_key"]
        
        self.model = "gpt-4o"
        self.temperature = CONFIG["openai"]["temperature"]
        self.max_tokens = CONFIG["openai"]["max_tokens"]
        
        if self.api_key and self.api_key.startswith("sk-"):
            self.client = openai.OpenAI(api_key=self.api_key)
            self.use_mock = False
            print("OpenAI client initialized successfully with GPT-4o")
        else:
            self.client = None
            self.use_mock = True
            print("Warning: No valid OpenAI API key found. Using mock data for demonstration.")

    def _call_openai(self, prompt: str, temperature: Optional[float] = None) -> str:
        if self.use_mock or self.client is None:
            return self._generate_mock_response(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational assessment designer. Generate high-quality, accurate educational content in proper JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise e  # Re-raise the exception to trigger proper fallback handling

    def generate_assessment_domains(self, main_topic: str, num_domains: int) -> List[AssessmentDomain]:
        prompt = f"""# Role and Objective

You are an expert knowledge assessor and educational designer. Your task is to break down a subject into {num_domains} distinct knowledge domains for comprehensive assessment. Focus on creating a logical learning progression that reveals someone's true understanding and competency level. Your response must be a pure JSON array.


1. `mainTopic` (string): {main_topic}

2. `numDomains` (number): {num_domains}


1. Analyze the `mainTopic` from both assessment and learning progression perspectives.

2. Identify the core knowledge domains that define expertise in this area, arranged from foundational to advanced.

3. Create domains that build upon each other logically (prerequisites → applications → mastery).

4. For each domain, provide a clear English name and detailed description focused on what knowledge/skills will be assessed.

5. Estimate the relative difficulty of each domain (1-100 scale), ensuring a good distribution.


- Start with foundational concepts (difficulty 20-40)
- Progress to application and analysis (difficulty 40-70) 
- End with synthesis and evaluation (difficulty 70-90)
- Each domain should have 8-12 questions for thorough assessment
- Focus on practical, real-world applications where possible


[

  {{

    "domain_name": "Fundamental Concepts and Principles",

    "description": "Assesses understanding of core concepts, basic terminology, and foundational principles that form the basis for advanced learning.",

    "estimated_difficulty": 25

  }},

  {{

    "domain_name": "Practical Application and Problem Solving",

    "description": "Evaluates the ability to apply theoretical knowledge to real-world scenarios and solve specific problems.",

    "estimated_difficulty": 65

  }}

]"""

        try:
            response = self._call_openai(prompt, CONFIG["ai_prompt"]["domain_generation_temperature"] if "ai_prompt" in CONFIG else 0.8)
            domains_data = json.loads(response)
            
            domains = []
            for domain_data in domains_data:
                domain = AssessmentDomain(
                    domain_name=domain_data["domain_name"],
                    description=domain_data["description"],
                    estimated_difficulty=domain_data["estimated_difficulty"]
                )
                domains.append(domain)
            
            return domains
        except Exception as e:
            print(f"Error generating domains: {e}")
            return self._generate_mock_domains(main_topic, num_domains)

    def generate_assessment_question(self, domain: str, difficulty: int, knowledge_gaps: List[str]) -> Question:
        print(f"DEBUG: generate_assessment_question called with domain='{domain}', difficulty={difficulty}")
        print(f"DEBUG: self.use_mock={self.use_mock}, self.client is None={self.client is None}")
        
        gaps_str = json.dumps(knowledge_gaps) if knowledge_gaps else "[]"
        
        prompt = f"""# Role and Objective

You are an expert assessment designer and educational psychologist. Your task is to create a high-quality, engaging multiple-choice question that accurately measures knowledge in a specific domain at a precise difficulty level. Focus on creating questions that are both challenging and fair. Your response must be a pure JSON object.


1. `domain` (string): {domain}

2. `difficulty` (number): {difficulty} (1-100 scale, where 1=very basic, 100=expert level)

3. `knowledgeGaps` (array): {gaps_str}


1. Create a question that precisely matches the difficulty level and is engaging to answer.

2. If `knowledgeGaps` is provided, prioritize assessing those specific areas to help the learner improve.

3. Design 4 options with exactly one correct answer and three carefully crafted distractors.

4. Include plausible distractors that reveal common misconceptions or partial understanding.

5. Provide a specific knowledge tag and comprehensive explanation with learning tips.

6. Estimate realistic time needed based on question complexity.


- Use clear, unambiguous English language
- Avoid trick questions or overly complex wording
- Include real-world context when possible
- Make distractors educational (reveal common mistakes)
- Provide explanations that teach, not just correct


- 1-20: Basic definitions, simple recall, fundamental concepts
- 21-40: Understanding relationships, simple application, basic analysis
- 41-60: Moderate application, comparison, pattern recognition
- 61-80: Complex synthesis, multi-step problem solving, evaluation
- 81-100: Expert-level analysis, advanced synthesis, cutting-edge concepts


{{

  "question": "Clear, precise question text that tests the intended knowledge",

  "options": [

    "Option A - plausible but incorrect answer",

    "Option B - correct answer", 

    "Option C - common misconception answer",

    "Option D - partially correct but incomplete answer"

  ],

  "correct_answer_index": 1,

  "knowledge_tag": "Specific knowledge area label",

  "explanation": "Detailed explanation of why the correct answer is right, why other options are wrong, and relevant learning points and recommendations.",

  "difficulty_level": {difficulty},

  "estimated_time": 45

}}"""

        if self.use_mock or self.client is None:
            print("DEBUG: Taking mock path - calling _generate_mock_question")
            return self._generate_mock_question(domain, difficulty)

        try:
            print("DEBUG: Taking OpenAI API path")
            response = self._call_openai(prompt, CONFIG["ai_prompt"]["question_generation_temperature"] if "ai_prompt" in CONFIG else 0.7)
            question_data = json.loads(response)
            
            question = Question(
                question=question_data["question"],
                options=question_data["options"],
                correct_answer_index=question_data["correct_answer_index"],
                knowledge_tag=question_data["knowledge_tag"],
                explanation=question_data["explanation"],
                difficulty_level=question_data["difficulty_level"],
                estimated_time=question_data["estimated_time"]
            )
            
            return question
        except Exception as e:
            print(f"Error generating question: {e}")
            print("DEBUG: Falling back to _generate_mock_question due to error")
            return self._generate_mock_question(domain, difficulty)

    def generate_assessment_summary(self, main_topic: str, domain_assessments: List[Any], total_time: float) -> Dict[str, Any]:
        overall_accuracy = 0.0
        if domain_assessments:
            total_correct = sum(da.questions_correct for da in domain_assessments)
            total_attempted = sum(da.questions_attempted for da in domain_assessments)
            overall_accuracy = total_correct / total_attempted if total_attempted > 0 else 0.0

        assessment_str = json.dumps([{
            "domain_name": da.domain_name,
            "questions_attempted": da.questions_attempted,
            "questions_correct": da.questions_correct,
            "accuracy": da.questions_correct / da.questions_attempted if da.questions_attempted > 0 else 0.0,
            "status": da.status.value,
            "knowledge_gaps": da.knowledge_gaps,
            "mastery_areas": da.mastery_areas,
            "average_response_time": da.average_response_time,
            "confidence_score": da.confidence_score
        } for da in domain_assessments])

        weakness_summary = []
        for da in domain_assessments:
            accuracy = da.questions_correct / da.questions_attempted if da.questions_attempted > 0 else 0.0
            if accuracy < 0.7 and da.knowledge_gaps:
                weakness_summary.extend(da.knowledge_gaps)

        prompt = f"""# Role and Objective

You are an expert knowledge assessor and analyst. Your task is to analyze a user's performance across multiple knowledge domains and generate a comprehensive assessment report with AI-generated weakness summaries. Your response must be a pure JSON object.


1. `mainTopic` (string): {main_topic}

2. `assessmentData` (array): {assessment_str}

3. `totalTimeMinutes` (number): {round(total_time / 60, 1)}

4. `overallAccuracy` (number): {round(overall_accuracy, 2)}

5. `weaknessAreas` (array): {weakness_summary}


1. Determine the user's overall knowledge level (Beginner/Intermediate/Advanced/Expert).

2. Identify their strongest domains and specific mastery areas.

3. Generate AI-powered weakness summaries based on knowledge gaps and poor performance areas.

4. Provide actionable recommendations for addressing weaknesses and further development.

5. Create a detailed breakdown of performance by domain with specific improvement strategies.


- Beginner (0-40% accuracy): Basic understanding, needs foundational work
- Intermediate (41-70% accuracy): Solid grasp of fundamentals, ready for application
- Advanced (71-85% accuracy): Strong competency, can handle complex scenarios
- Expert (86-100% accuracy): Mastery level, can teach and innovate


{{

  "title": "Knowledge Assessment Report: {main_topic}",

  "overall_score": {round(overall_accuracy * 100, 1)},

  "total_time_minutes": {round(total_time / 60, 1)},

  "domains_assessed": {len(domain_assessments)},

  "knowledge_level": "Determine based on overall performance",

  "strengths": [

    "List specific domains and knowledge areas where user excelled"

  ],

  "weakness_summary": "AI-generated comprehensive analysis of the user's main weaknesses, learning gaps, and areas requiring focused attention based on their performance patterns",

  "areas_for_improvement": [

    "List specific domains and knowledge gaps that need attention"

  ],

  "recommendations": [

    "Provide 3-5 specific, actionable recommendations for improvement with learning resources"

  ],

  "detailed_breakdown": {{

    "domain_name_1": {{

      "score": 85.5,

      "status": "mastered",

      "key_strengths": ["specific strength 1", "specific strength 2"],

      "improvement_areas": ["specific gap 1"],

      "learning_strategy": "Specific strategy for this domain"

    }}

  }}

}}"""

        try:
            response = self._call_openai(prompt, CONFIG["ai_prompt"]["summary_generation_temperature"] if "ai_prompt" in CONFIG else 0.6)
            summary_data = json.loads(response)
            return summary_data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing summary response: {e}")
            return self._generate_mock_summary(main_topic, domain_assessments, total_time, overall_accuracy)

    def _generate_mock_response(self, prompt: str) -> str:
        if "domain" in prompt.lower() and "assessment" in prompt.lower():
            return self._get_mock_domains_response()
        elif "question" in prompt.lower():
            return self._get_mock_question_response()
        elif "summary" in prompt.lower():
            return self._get_mock_summary_response()
        return "{}"

    def _generate_mock_domains(self, main_topic: str, num_domains: int) -> List[AssessmentDomain]:
        mock_domains = [
            AssessmentDomain("Fundamental Concepts", f"Core principles and basic terminology of {main_topic}", 25),
            AssessmentDomain("Applied Knowledge", f"Practical application of {main_topic} concepts", 45),
            AssessmentDomain("Advanced Techniques", f"Complex methods and advanced strategies in {main_topic}", 65),
            AssessmentDomain("Problem Solving", f"Critical thinking and problem-solving skills in {main_topic}", 75),
            AssessmentDomain("Expert Analysis", f"Expert-level analysis and evaluation in {main_topic}", 85)
        ]
        return mock_domains[:num_domains]

    def _generate_mock_question(self, domain: str, difficulty: int) -> Question:
        questions_pool = [
            {
                "question": f"What is a fundamental concept in {domain}?",
                "options": ["Option A", "Option B (Correct)", "Option C", "Option D"],
                "correct_answer_index": 1,
                "knowledge_tag": f"{domain} Fundamentals",
                "explanation": "This tests basic understanding of core concepts.",
                "difficulty_level": difficulty,
                "estimated_time": 30
            },
            {
                "question": f"How would you apply {domain} principles to solve a complex problem?",
                "options": ["Approach A", "Approach B", "Approach C (Correct)", "Approach D"],
                "correct_answer_index": 2,
                "knowledge_tag": f"{domain} Application",
                "explanation": "This evaluates practical application skills.",
                "difficulty_level": difficulty,
                "estimated_time": 45
            }
        ]
        
        selected = random.choice(questions_pool)
        print(f"DEBUG: Mock question data: {selected}")
        print(f"DEBUG: correct_answer_index type: {type(selected['correct_answer_index'])}")
        question = Question(**selected)
        print(f"DEBUG: Question object correct_answer_index type: {type(question.correct_answer_index)}")
        return question

    def _get_mock_domains_response(self) -> str:
        return '''[
  {
    "domain_name": "Fundamental Concepts",
    "description": "Assesses understanding of core principles and basic terminology",
    "estimated_difficulty": 25
  },
  {
    "domain_name": "Applied Knowledge",
    "description": "Evaluates ability to apply concepts to practical scenarios",
    "estimated_difficulty": 45
  },
  {
    "domain_name": "Advanced Techniques",
    "description": "Tests mastery of complex methods and strategies",
    "estimated_difficulty": 65
  }
]'''

    def _get_mock_question_response(self) -> str:
        return '''{
  "question": "What is the primary purpose of adaptive testing systems?",
  "options": [
    "To make tests harder for everyone",
    "To personalize difficulty based on user performance",
    "To reduce the number of questions",
    "To eliminate multiple choice questions"
  ],
  "correct_answer_index": 1,
  "knowledge_tag": "Adaptive Testing Fundamentals",
  "explanation": "Adaptive testing systems adjust difficulty in real-time based on user responses to provide personalized assessment experiences.",
  "difficulty_level": 40,
  "estimated_time": 30
}'''

    def _get_mock_summary_response(self) -> str:
        return '''{
  "title": "Knowledge Assessment Report: Sample Topic",
  "overall_score": 75.0,
  "total_time_minutes": 15.5,
  "domains_assessed": 3,
  "knowledge_level": "Advanced",
  "strengths": [
    "Strong grasp of fundamental concepts",
    "Excellent problem-solving abilities"
  ],
  "areas_for_improvement": [
    "Advanced techniques need more practice",
    "Time management could be improved"
  ],
  "recommendations": [
    "Focus on practicing advanced problem-solving scenarios",
    "Review complex theoretical concepts",
    "Work on speed and accuracy balance"
  ],
  "detailed_breakdown": {
    "Fundamental Concepts": {
      "score": 85.0,
      "status": "mastered",
      "key_strengths": ["terminology", "basic principles"],
      "improvement_areas": []
    }
  }
}'''

    def _generate_mock_summary(self, main_topic: str, domain_assessments: List[Any], 
                             total_time: float, overall_accuracy: float) -> Dict[str, Any]:
        knowledge_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
        level_index = min(3, int(overall_accuracy * 4))
        
        return {
            "title": f"Knowledge Assessment Report: {main_topic}",
            "overall_score": round(overall_accuracy * 100, 1),
            "total_time_minutes": round(total_time / 60, 1),
            "domains_assessed": len(domain_assessments),
            "knowledge_level": knowledge_levels[level_index],
            "strengths": ["Strong analytical thinking", "Good foundational knowledge"],
            "areas_for_improvement": ["Advanced concepts", "Application skills"],
            "recommendations": [
                "Practice more complex problems",
                "Review theoretical foundations",
                "Focus on real-world applications"
            ],
            "detailed_breakdown": {
                domain.domain_name: {
                    "score": round((domain.questions_correct / max(1, domain.questions_attempted)) * 100, 1),
                    "status": domain.status.value,
                    "key_strengths": domain.mastery_areas[:2],
                    "improvement_areas": domain.knowledge_gaps[:2]
                } for domain in domain_assessments
            }
        }
