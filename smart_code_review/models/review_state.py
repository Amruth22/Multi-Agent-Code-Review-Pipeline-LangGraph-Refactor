from typing import TypedDict, List, Dict, Any, Optional, Union, Annotated
from datetime import datetime
import uuid

# Custom reducers for state updates
def add_to_list(existing: List, new: List) -> List:
    """Reducer function to safely add items to a list"""
    if existing is None:
        existing = []
    if new is None:
        new = []
    return existing + new

class AgentResult(TypedDict, total=False):
    """Base type for agent results"""
    filename: str

class SecurityResult(AgentResult):
    """Security analysis result"""
    security_score: float
    vulnerabilities: List[Dict[str, Any]]
    severity_counts: Dict[str, int]
    recommendations: List[str]

class QualityResult(AgentResult):
    """Quality analysis result"""
    score: float
    total_issues: int
    issues: List[Dict[str, Any]]
    complexity_score: float
    maintainability_index: float
    code_smells: List[str]
    technical_debt: float

class CoverageResult(AgentResult):
    """Test coverage analysis result"""
    coverage_percent: float
    missing_tests: List[str]
    test_quality_score: float
    missing_test_types: List[str]
    testability_score: float

class AIReviewResult(AgentResult):
    """AI review result"""
    overall_score: float
    confidence: float
    strengths: List[str]
    issues: List[str]
    recommendations: List[str]
    refactoring_suggestions: List[str]
    security_concerns: List[str]
    raw_response: str

class DocumentationResult(AgentResult):
    """Documentation analysis result"""
    documentation_coverage: float
    missing_documentation: List[str]
    total_items: int
    documented_items: int

class ReviewState(TypedDict, total=False):
    """Complete review state schema"""
    # Basic review information
    review_id: str
    repo_owner: str
    repo_name: str
    pr_number: int
    timestamp: str
    stage: str
    
    # PR and file data
    pr_details: Dict[str, Any]
    files_data: List[Dict[str, Any]]
    
    # Agent completion tracking - allows multiple concurrent updates
    agents_completed: Annotated[List[str], add_to_list]
    
    # Agent results - each agent updates its own key
    security_results: List[SecurityResult]
    pylint_results: List[QualityResult]
    coverage_results: List[CoverageResult]
    ai_reviews: List[AIReviewResult]
    documentation_results: List[DocumentationResult]
    missing_tests: List[Dict[str, Any]]
    
    # Coordination and decision
    pr_summary: Dict[str, Any]
    has_critical_issues: bool
    critical_reason: str
    decision: str
    decision_metrics: Dict[str, Any]
    
    # Email tracking - allows multiple concurrent updates
    emails_sent: Annotated[List[Dict[str, Any]], add_to_list]
    
    # Workflow control
    next: str
    error: str
    workflow_complete: bool
    updated_at: str