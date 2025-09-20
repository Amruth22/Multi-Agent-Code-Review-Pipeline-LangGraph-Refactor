from typing import Dict, Any, List
import logging
from datetime import datetime
from .base_agent import BaseAgent
from ..core.state import StateManager

class AgentCoordinator(BaseAgent):
    """Coordinator for aggregating results from all parallel agents"""
    
    def __init__(self):
        super().__init__("agent_coordinator")
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process and coordinate results from all agents"""
        # Log current agent completion status
        completed_agents = state.get("agents_completed", [])
        self.logger.info(f" Agents completed: {completed_agents}")
        
        # Check if all agents have completed
        all_completed = StateManager.check_all_agents_completed(state)
        
        if not all_completed:
            # Agents still running, wait for more
            expected_agents = ["security", "quality", "coverage", "ai_review", "documentation"]
            missing_agents = [agent for agent in expected_agents if agent not in completed_agents]
            self.logger.info(f"⏳ Coordinator waiting for agents: {missing_agents}")
            
            # Return minimal state update to avoid overwriting other agents' results
            return {
                "stage": "coordination_in_progress"
            }
        
        # All agents completed, aggregate results
        self.logger.info(f" All agents completed, aggregating results...")
        
        # If AI review agent already generated PR summary, use that
        pr_summary = state.get("pr_summary", {})
        
        # If not, generate summary here
        if not pr_summary:
            from ..services.gemini.client import GeminiClient
            from ..core.config import get_config_value
            
            # Initialize Gemini client
            api_key = get_config_value("GEMINI_API_KEY")
            model = get_config_value("GEMINI_MODEL")
            gemini_client = GeminiClient(api_key, model)
            
            # Generate PR summary
            pr_summary = self._generate_multi_agent_pr_summary(
                state.get("pr_details", {}),
                state.get("pylint_results", []),
                state.get("coverage_results", []),
                state.get("ai_reviews", []),
                state.get("security_results", []),
                state.get("documentation_results", []),
                gemini_client
            )
        
        self.logger.info(" Agent coordination complete - All results aggregated")
        
        # Return coordinator-specific updates
        return {
            "pr_summary": pr_summary,
            "stage": "coordination_complete",
            "next": "decision_maker",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_multi_agent_pr_summary(self, 
                                       pr_details: Dict[str, Any],
                                       pylint_results: List[Dict[str, Any]],
                                       coverage_results: List[Dict[str, Any]],
                                       ai_reviews: List[Dict[str, Any]],
                                       security_results: List[Dict[str, Any]],
                                       documentation_results: List[Dict[str, Any]],
                                       gemini_client) -> Dict[str, Any]:
        """Generate comprehensive PR summary from all agent results"""
        # Use existing PR summary generation as base
        base_summary = gemini_client.generate_pr_summary(
            pr_details, pylint_results, coverage_results, ai_reviews
        )
        
        # Enhance with multi-agent results
        if security_results:
            total_vulnerabilities = sum(len(result.get('vulnerabilities', [])) for result in security_results)
            high_severity_count = sum(result.get('severity_counts', {}).get('HIGH', 0) for result in security_results)
            
            base_summary['security_analysis'] = {
                'total_vulnerabilities': total_vulnerabilities,
                'high_severity_count': high_severity_count,
                'security_recommendation': 'CRITICAL' if high_severity_count > 0 else 'REVIEW' if total_vulnerabilities > 0 else 'APPROVED'
            }
        
        if documentation_results:
            avg_doc_coverage = sum(result.get('documentation_coverage', 0) for result in documentation_results) / len(documentation_results)
            base_summary['documentation_analysis'] = {
                'average_coverage': avg_doc_coverage,
                'documentation_recommendation': 'NEEDS_IMPROVEMENT' if avg_doc_coverage < 70 else 'GOOD'
            }
        
        return base_summary