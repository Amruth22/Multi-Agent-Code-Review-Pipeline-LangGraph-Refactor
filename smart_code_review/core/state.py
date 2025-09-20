from typing import Dict, Any, List, Optional, TypeVar, Generic, Callable
from datetime import datetime
import uuid
import logging
from ..models.review_state import ReviewState

logger = logging.getLogger("state_manager")

T = TypeVar('T')

class StateManager:
    """Centralized state management for review workflows"""
    
    @staticmethod
    def create_initial_state(repo_owner: str, repo_name: str, pr_number: int) -> ReviewState:
        """Create initial review state"""
        review_id = f"REV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        return ReviewState(
            review_id=review_id,
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_number=pr_number,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stage="started",
            
            pr_details={},
            files_data=[],
            
            agents_completed=[],
            
            security_results=[],
            pylint_results=[],
            coverage_results=[],
            ai_reviews=[],
            documentation_results=[],
            missing_tests=[],
            
            pr_summary={},
            has_critical_issues=False,
            critical_reason="",
            decision="",
            decision_metrics={},
            
            emails_sent=[],
            
            next="",
            error="",
            workflow_complete=False,
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    @staticmethod
    def update_stage(state: ReviewState, new_stage: str) -> ReviewState:
        """Update review stage with timestamp"""
        state_copy = state.copy()
        state_copy["stage"] = new_stage
        state_copy["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"State stage updated: {new_stage}")
        return state_copy
    
    @staticmethod
    def add_email_sent(state: ReviewState, email_type: str) -> ReviewState:
        """Track emails sent"""
        state_copy = state.copy()
        email_entry = {
            "type": email_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if "emails_sent" not in state_copy:
            state_copy["emails_sent"] = []
            
        state_copy["emails_sent"] = state_copy["emails_sent"] + [email_entry]
        return state_copy
    
    @staticmethod
    def check_all_agents_completed(state: ReviewState) -> bool:
        """Check if all expected agents have completed"""
        expected_agents = {"security", "quality", "coverage", "ai_review", "documentation"}
        completed_agents = set(state.get("agents_completed", []))
        return expected_agents.issubset(completed_agents)
    
    @staticmethod
    def add_error(state: ReviewState, error_message: str) -> ReviewState:
        """Add error to state"""
        state_copy = state.copy()
        state_copy["error"] = error_message
        state_copy["next"] = "error_handler"
        return state_copy