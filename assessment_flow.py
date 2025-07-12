"""
Assessment Flow System - Outer layer managing knowledge assessment and domain progression
"""
from typing import List, Optional, Tuple
from models import (
    AssessmentSession, AssessmentDomain, DomainStatus, DomainAssessment, AssessmentSummary
)
from ai_service import AIService
from config import Config

class AssessmentFlowManager:
    def __init__(self):
        self.ai_service = AIService()
        self.current_session: Optional[AssessmentSession] = None
        
    def start_assessment_session(self, main_topic: str, num_domains: int = None) -> AssessmentSession:
        """
        Start a new knowledge assessment session for a given topic
        """
        if not main_topic.strip():
            raise ValueError("Topic cannot be empty")
        
        if num_domains is None:
            num_domains = Config.DEFAULT_NUM_DOMAINS
        
        # Validate number of domains
        if num_domains < Config.MIN_DOMAINS or num_domains > Config.MAX_DOMAINS:
            raise ValueError(f"Number of domains must be between {Config.MIN_DOMAINS} and {Config.MAX_DOMAINS}")
        
        try:
            # Generate assessment domains using AI
            domain_list = self.ai_service.generate_assessment_domains(main_topic, num_domains)
            
            # Initialize domain assessments
            domain_assessments = []
            for domain in domain_list:
                assessment = DomainAssessment(
                    domain_name=domain.domain_name,
                    status=DomainStatus.NOT_STARTED,
                    current_difficulty=domain.estimated_difficulty
                )
                domain_assessments.append(assessment)
            
            # Create new assessment session
            self.current_session = AssessmentSession(
                main_topic=main_topic,
                domain_list=domain_list,
                current_domain_index=0,
                domain_assessments=domain_assessments
            )
            
            return self.current_session
            
        except Exception as e:
            raise Exception(f"Failed to start assessment session: {str(e)}")
    
    def get_current_session(self) -> Optional[AssessmentSession]:
        """Get the current assessment session"""
        return self.current_session
    
    def can_access_domain(self, domain_index: int) -> bool:
        """Check if a domain can be accessed for assessment (sequential progression)"""
        if not self.current_session:
            return False

        if domain_index < 0 or domain_index >= len(self.current_session.domain_list):
            return False

        # Sequential progression: can only access first domain or domains after completed ones
        if domain_index == 0:
            return True

        # Check if all previous domains are completed
        for i in range(domain_index):
            prev_status = self.current_session.domain_assessments[i].status
            if prev_status == DomainStatus.NOT_STARTED or prev_status == DomainStatus.IN_PROGRESS:
                return False

        return True
    
    def start_domain_assessment(self, domain_index: int) -> str:
        """Start assessment for a specific domain"""
        if not self.current_session:
            raise ValueError("No active assessment session")
        
        if not self.can_access_domain(domain_index):
            raise ValueError(f"Cannot access domain {domain_index}")
        
        # Update current domain
        self.current_session.current_domain_index = domain_index
        
        # Update domain status
        domain_assessment = self.current_session.domain_assessments[domain_index]
        domain_assessment.status = DomainStatus.IN_PROGRESS
        
        return self.current_session.domain_list[domain_index].domain_name
    
    def complete_domain_assessment(self, domain_index: int) -> DomainAssessment:
        """Complete assessment for a domain and determine status"""
        if not self.current_session:
            raise ValueError("No active assessment session")
        
        domain_assessment = self.current_session.domain_assessments[domain_index]
        
        # Calculate accuracy
        accuracy = domain_assessment.questions_correct / max(domain_assessment.questions_attempted, 1)
        
        # Determine final status based on performance
        if accuracy >= Config.MASTERY_THRESHOLD:
            domain_assessment.status = DomainStatus.MASTERED
        elif accuracy <= Config.STRUGGLE_THRESHOLD:
            domain_assessment.status = DomainStatus.STRUGGLING
        else:
            domain_assessment.status = DomainStatus.COMPLETED
        
        return domain_assessment
    
    def is_assessment_complete(self) -> bool:
        """Check if the entire assessment is complete"""
        if not self.current_session:
            return False
        
        # Assessment is complete when all domains have been assessed
        for assessment in self.current_session.domain_assessments:
            if assessment.status == DomainStatus.NOT_STARTED:
                return False
        
        return True
    
    def get_next_domain_index(self) -> Optional[int]:
        """Get the index of the next domain to assess"""
        if not self.current_session:
            return None
        
        for i, assessment in enumerate(self.current_session.domain_assessments):
            if assessment.status == DomainStatus.NOT_STARTED:
                return i
        
        return None
    
    def calculate_overall_score(self) -> float:
        """Calculate overall assessment score"""
        if not self.current_session:
            return 0.0
        
        total_questions = 0
        total_correct = 0
        
        for assessment in self.current_session.domain_assessments:
            total_questions += assessment.questions_attempted
            total_correct += assessment.questions_correct
        
        if total_questions == 0:
            return 0.0
        
        return (total_correct / total_questions) * 100
    
    def generate_final_summary(self) -> AssessmentSummary:
        """Generate a comprehensive assessment summary"""
        if not self.current_session:
            raise ValueError("No active assessment session")
        
        # Calculate total time
        total_time = time.time() - self.current_session.start_time
        
        try:
            summary = self.ai_service.generate_assessment_summary(
                self.current_session.main_topic,
                self.current_session.domain_assessments,
                total_time
            )
            return summary
        except Exception as e:
            raise Exception(f"Failed to generate assessment summary: {str(e)}")
    
    def get_assessment_progress(self) -> Tuple[int, int]:
        """Get assessment progress (completed domains, total domains)"""
        if not self.current_session:
            return 0, 0
        
        completed = sum(1 for assessment in self.current_session.domain_assessments 
                       if assessment.status != DomainStatus.NOT_STARTED)
        total = len(self.current_session.domain_assessments)
        
        return completed, total
