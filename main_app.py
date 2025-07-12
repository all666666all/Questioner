from typing import Optional, Dict, Any, List, Tuple
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import AssessmentSession, DomainAssessment, DomainStatus
from assessment_flow import AssessmentFlowManager
from question_flow import QuestionFlowManager
from ai_service import AIService
from config import CONFIG

class StartAssessmentRequest(BaseModel):
    topic: str
    num_domains: int

class StartDomainRequest(BaseModel):
    domain_index: int

class SubmitAnswerRequest(BaseModel):
    answer_index: int
    confidence: float

class KnowledgeAssessmentApp:
    def __init__(self):
        self.assessment_flow = AssessmentFlowManager()
        self.question_flow = QuestionFlowManager()
        self.ai_service = AIService()
        self.current_session: Optional[AssessmentSession] = None
        self.current_domain_index: int = 0
        self.current_question = None

    def start_assessment(self, topic: str, num_domains: int) -> Dict[str, Any]:
        """
        Handles the "Start Assessment" API endpoint.
        """
        if not topic or not topic.strip():
            raise HTTPException(status_code=400, detail="Please enter a valid topic.")
        
        if num_domains < CONFIG["assessment"]["min_domains"] or num_domains > CONFIG["assessment"]["max_domains"]:
            raise HTTPException(status_code=400, detail=f"Number of domains must be between {CONFIG['assessment']['min_domains']} and {CONFIG['assessment']['max_domains']}.")
        
        self.current_session = self.assessment_flow.start_assessment_session(topic.strip(), num_domains)
        self.current_domain_index = 0
        
        domains_info = []
        if self.current_session:
            for i, domain in enumerate(self.current_session.domain_list):
                domains_info.append({
                    "index": i,
                    "name": domain.domain_name,
                    "description": domain.description,
                    "difficulty": domain.estimated_difficulty,
                    "accessible": self.assessment_flow.can_access_domain(i),
                    "status": self.current_session.domain_assessments[i].status.value
                })
        
        return {
            "message": "Assessment started successfully!",
            "session_id": id(self.current_session),
            "topic": topic.strip(),
            "domains": domains_info
        }

    def start_domain_assessment(self, domain_index: int) -> Dict[str, Any]:
        """
        Handles the API request when the user starts a domain assessment.
        """
        print(f"DEBUG: start_domain_assessment called with domain_index={domain_index}")
        print(f"DEBUG: self.current_session is None: {self.current_session is None}")
        if not self.current_session:
            raise HTTPException(status_code=400, detail="No active assessment session.")
        
        if not self.assessment_flow.can_access_domain(domain_index):
            raise HTTPException(status_code=400, detail="This domain is not accessible yet.")
        
        success = self.assessment_flow.start_domain_assessment(domain_index)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start domain assessment.")
        
        self.current_domain_index = domain_index
        domain_assessment = self.current_session.domain_assessments[domain_index]
        print(f"DEBUG: domain_assessment retrieved: {domain_assessment.domain_name}")
        
        self.question_flow.start_domain_assessment(domain_assessment)
        print(f"DEBUG: question_flow.start_domain_assessment completed")
        question = self.question_flow.generate_question()
        print(f"DEBUG: question generated: {question is not None}")
        self.current_question = question
        
        if question:
            print(f"DEBUG: About to access domain_assessment.progress")
            progress_value = getattr(domain_assessment, 'progress', 0)
            print(f"DEBUG: progress_value = {progress_value}")
            return {
                "message": "Domain assessment started!",
                "domain_name": domain_assessment.domain_name,
                "question": {
                    "question": question.question,
                    "options": question.options,
                    "knowledge_tag": question.knowledge_tag,
                    "difficulty_level": question.difficulty_level,
                    "estimated_time": question.estimated_time
                },
                "progress": progress_value
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate question.")

    def submit_answer(self, answer_index: int, confidence: float) -> Dict[str, Any]:
        """
        Handles the API request when the user submits an answer.
        """
        if not self.current_session or not self.current_question:
            raise HTTPException(status_code=400, detail="No active question.")
        
        result = self.question_flow.submit_answer(answer_index, confidence)
        
        self.current_session.total_questions += 1
        if result.get("is_correct", False):
            self.current_session.total_correct += 1
        
        response_data = {
            "message": "Answer submitted successfully!",
            "feedback": result.get("feedback", ""),
            "is_correct": result.get("is_correct", False),
            "progress": result.get("progress", 0),
            "domain_complete": result.get("domain_complete", False),
            "confidence_quality": result.get("confidence_quality", 0.0),
            "current_difficulty": result.get("current_difficulty", 50)
        }
        
        if result.get("next_question"):
            self.current_question = result["next_question"]
            response_data["question"] = {
                "question": self.current_question.question,
                "options": self.current_question.options,
                "knowledge_tag": self.current_question.knowledge_tag,
                "difficulty_level": self.current_question.difficulty_level,
                "estimated_time": self.current_question.estimated_time
            }
        else:
            self.current_question = None
        
        return response_data

    def generate_final_summary(self) -> Dict[str, Any]:
        """
        Handles the API request to generate the final assessment summary.
        """
        if not self.current_session:
            raise HTTPException(status_code=400, detail="No assessment session found.")
        
        total_time = (datetime.now() - self.current_session.start_time).total_seconds()
        
        summary = self.ai_service.generate_assessment_summary(
            self.current_session.main_topic,
            self.current_session.domain_assessments,
            total_time
        )
        
        radar_data = self.generate_radar_chart_data()
        
        return {
            "message": "Summary generated successfully!",
            "summary": summary,
            "radar_data": radar_data,
            "session_stats": {
                "total_questions": self.current_session.total_questions,
                "total_correct": self.current_session.total_correct,
                "overall_score": self.current_session.overall_score,
                "total_time_minutes": round(total_time / 60, 1)
            }
        }

    def generate_radar_chart_data(self) -> List[Dict[str, Any]]:
        """
        Generates radar chart data for the frontend.
        """
        if not self.current_session:
            return []
        
        radar_data = []
        for assessment in self.current_session.domain_assessments:
            if assessment.questions_attempted > 0:
                score = (assessment.questions_correct / assessment.questions_attempted) * 100
                radar_data.append({
                    "category": assessment.domain_name,
                    "score": round(score, 1)
                })
        
        return radar_data

    def get_assessment_progress(self) -> Dict[str, Any]:
        """
        Returns the current assessment progress.
        """
        if not self.current_session:
            return {"completed_domains": 0, "total_domains": 0}
        
        completed_domains = sum(1 for assessment in self.current_session.domain_assessments 
                              if assessment.status in [DomainStatus.COMPLETED, DomainStatus.MASTERED])
        
        return {
            "completed_domains": completed_domains,
            "total_domains": len(self.current_session.domain_assessments),
            "overall_score": self.current_session.overall_score,
            "session_start": self.current_session.start_time.isoformat()
        }

app = FastAPI(title="AI-Powered Adaptive Testing System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "https://assessment-fix-app-gmztnrwd.devinapps.com",
        "https://app-eyhhqswk.fly.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assessment_app_instance = KnowledgeAssessmentApp()

@app.post("/start-assessment")
async def start_assessment_endpoint(request: StartAssessmentRequest):
    """Start a new assessment session."""
    try:
        result = assessment_app_instance.start_assessment(request.topic, request.num_domains)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/start-domain")
async def start_domain_endpoint(request: StartDomainRequest):
    """Start assessment for a specific domain."""
    try:
        result = assessment_app_instance.start_domain_assessment(request.domain_index)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/submit-answer")
async def submit_answer_endpoint(request: SubmitAnswerRequest):
    """Submit an answer for the current question."""
    try:
        result = assessment_app_instance.submit_answer(request.answer_index, request.confidence)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/generate-summary")
async def generate_summary_endpoint():
    """Generate the final assessment summary."""
    try:
        result = assessment_app_instance.generate_final_summary()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "AI-Powered Adaptive Testing System is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
