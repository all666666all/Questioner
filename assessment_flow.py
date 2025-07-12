from typing import List, Tuple, Optional
from datetime import datetime
from models import AssessmentSession, AssessmentDomain, DomainAssessment, DomainStatus
from ai_service import AIService
from config import CONFIG

class AssessmentFlowManager:
    def __init__(self):
        self.ai_service = AIService()
        self.current_session: Optional[AssessmentSession] = None

    def start_assessment_session(self, topic: str, num_domains: int) -> AssessmentSession:
        """
        Calls the AI service to generate domains and initializes AssessmentSession.
        """
        min_domains = CONFIG["assessment"]["min_domains"]
        max_domains = CONFIG["assessment"]["max_domains"]
        
        if num_domains < min_domains or num_domains > max_domains:
            raise ValueError(f"Number of domains must be between {min_domains} and {max_domains}")
        
        domain_list = self.ai_service.generate_assessment_domains(topic, num_domains)
        
        domain_assessments = []
        for domain in domain_list:
            domain_assessment = DomainAssessment(
                domain_name=domain.domain_name,
                status=DomainStatus.NOT_STARTED,
                current_difficulty=domain.estimated_difficulty
            )
            domain_assessments.append(domain_assessment)
        
        self.current_session = AssessmentSession(
            main_topic=topic,
            domain_list=domain_list,
            current_domain_index=0,
            domain_assessments=domain_assessments,
            overall_score=0.0,
            start_time=datetime.now(),
            total_questions=0,
            total_correct=0
        )
        
        return self.current_session

    def start_domain_assessment(self, domain_index: int) -> bool:
        """
        Sets the status of the current active domain to IN_PROGRESS.
        """
        if not self.current_session:
            raise ValueError("No active assessment session")
        
        if domain_index < 0 or domain_index >= len(self.current_session.domain_assessments):
            raise ValueError("Invalid domain index")
        
        if not self.can_access_domain(domain_index):
            return False
        
        self.current_session.domain_assessments[domain_index].status = DomainStatus.IN_PROGRESS
        self.current_session.current_domain_index = domain_index
        
        return True

    def can_access_domain(self, domain_index: int) -> bool:
        """
        Checks if the user can access a domain (the first domain is always accessible, 
        subsequent domains require the previous one to be completed).
        """
        if not self.current_session:
            return False
        
        if domain_index < 0 or domain_index >= len(self.current_session.domain_assessments):
            return False
        
        if domain_index == 0:
            return True
        
        previous_domain = self.current_session.domain_assessments[domain_index - 1]
        completed_statuses = [DomainStatus.COMPLETED, DomainStatus.MASTERED, DomainStatus.STRUGGLING]
        
        return previous_domain.status in completed_statuses

    def get_assessment_progress(self) -> Tuple[int, int]:
        """
        Returns the number of completed domains and the total number of domains.
        """
        if not self.current_session:
            return (0, 0)
        
        completed_count = 0
        completed_statuses = [DomainStatus.COMPLETED, DomainStatus.MASTERED, DomainStatus.STRUGGLING]
        
        for domain_assessment in self.current_session.domain_assessments:
            if domain_assessment.status in completed_statuses:
                completed_count += 1
        
        total_domains = len(self.current_session.domain_assessments)
        
        return (completed_count, total_domains)

    def calculate_overall_score(self) -> float:
        """
        Calculates the overall score for the entire assessment.
        """
        if not self.current_session:
            return 0.0
        
        if not self.current_session.domain_assessments:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for i, domain_assessment in enumerate(self.current_session.domain_assessments):
            if domain_assessment.questions_attempted > 0:
                domain_score = (domain_assessment.questions_correct / domain_assessment.questions_attempted) * 100
                
                domain_difficulty = self.current_session.domain_list[i].estimated_difficulty
                weight = domain_difficulty / 100.0  # Normalize to 0-1 range
                
                total_weighted_score += domain_score * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score = total_weighted_score / total_weight
        else:
            overall_score = 0.0
        
        self.current_session.overall_score = overall_score
        
        return overall_score

    def get_current_session(self) -> Optional[AssessmentSession]:
        """
        Returns the current assessment session.
        """
        return self.current_session

    def get_domain_assessment(self, domain_index: int) -> DomainAssessment:
        """
        Returns the domain assessment for the specified index.
        """
        if not self.current_session:
            raise ValueError("No active assessment session")
        
        if domain_index < 0 or domain_index >= len(self.current_session.domain_assessments):
            raise ValueError("Invalid domain index")
        
        return self.current_session.domain_assessments[domain_index]

    def update_session_totals(self, questions_attempted: int, questions_correct: int):
        """
        Updates the total questions and correct answers for the session.
        """
        if not self.current_session:
            return
        
        self.current_session.total_questions += questions_attempted
        self.current_session.total_correct += questions_correct

    def is_assessment_complete(self) -> bool:
        """
        Checks if all domains in the assessment have been completed.
        """
        if not self.current_session:
            return False
        
        completed_count, total_domains = self.get_assessment_progress()
        return completed_count == total_domains

    def get_next_available_domain(self) -> int:
        """
        Returns the index of the next available domain, or -1 if none available.
        """
        if not self.current_session:
            return -1
        
        for i, domain_assessment in enumerate(self.current_session.domain_assessments):
            if domain_assessment.status == DomainStatus.NOT_STARTED and self.can_access_domain(i):
                return i
        
        return -1

    def get_assessment_summary_data(self) -> dict:
        """
        Prepares data for generating the final assessment summary.
        """
        if not self.current_session:
            return {}
        
        total_time = (datetime.now() - self.current_session.start_time).total_seconds()
        
        return {
            "main_topic": self.current_session.main_topic,
            "domain_assessments": self.current_session.domain_assessments,
            "total_time": total_time,
            "overall_score": self.calculate_overall_score(),
            "total_questions": self.current_session.total_questions,
            "total_correct": self.current_session.total_correct
        }
