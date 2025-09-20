from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent
from ..services.gemini.client import GeminiClient
from ..core.config import get_config_value

class AIReviewAgent(BaseAgent):
    """Agent for AI-powered code review"""
    
    def __init__(self):
        super().__init__("ai_review")
        self.gemini_client = None
    
    def _init_services(self):
        """Initialize required services"""
        if self.gemini_client is None:
            api_key = get_config_value("GEMINI_API_KEY")
            model = get_config_value("GEMINI_MODEL")
            self.gemini_client = GeminiClient(api_key, model)
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process files for AI-powered code review"""
        self._init_services()
        
        # Get results from other agents (if available)
        pylint_results = state.get("pylint_results", [])
        coverage_results = state.get("coverage_results", [])
        security_results = state.get("security_results", [])
        
        # Run AI reviews with enhanced context
        ai_reviews = []
        for i, file_data in enumerate(state["files_data"]):
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                self.logger.info(f" AI reviewing {filename}...")
                
                # Get corresponding analysis results
                pylint_result = self._get_result_for_file(pylint_results, filename, i)
                coverage_result = self._get_result_for_file(coverage_results, filename, i)
                security_result = self._get_result_for_file(security_results, filename, i)
                
                # Create context for AI review
                context = {}
                if pylint_result:
                    context["pylint"] = pylint_result
                if coverage_result:
                    context["coverage"] = coverage_result
                if security_result:
                    context["security"] = security_result
                
                # Generate AI review
                ai_review = self.gemini_client.review_code(content, filename, context)
                
                # Add security context if available
                if security_result:
                    ai_review['security_context'] = {
                        'security_score': security_result.get('security_score', 0),
                        'vulnerability_count': len(security_result.get('vulnerabilities', [])),
                        'high_severity_issues': security_result.get('severity_counts', {}).get('HIGH', 0)
                    }
                
                ai_reviews.append(ai_review)
        
        self.logger.info(f" AI review complete - {len(ai_reviews)} files analyzed")
        
        # Generate comprehensive PR summary with all agent results
        pr_summary = None
        if state.get("pr_details") and pylint_results and coverage_results and ai_reviews:
            pr_summary = self.gemini_client.generate_pr_summary(
                state.get("pr_details", {}),
                pylint_results,
                coverage_results,
                ai_reviews
            )
            self.logger.info(" PR summary generated")
        
        result = {
            "ai_reviews": ai_reviews
        }
        
        if pr_summary:
            result["pr_summary"] = pr_summary
        
        return result
    
    def _get_result_for_file(self, results: List[Dict[str, Any]], filename: str, index: int) -> Optional[Dict[str, Any]]:
        """Get the result for a specific file, first by name then by index"""
        # Try to match by filename
        for result in results:
            if result.get("filename") == filename:
                return result
        
        # Fallback to index if available
        if index < len(results):
            return results[index]
        
        return None