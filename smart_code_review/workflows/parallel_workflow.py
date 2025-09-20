from typing import Dict, Any, List, Callable, Union
import logging
from datetime import datetime
from langgraph.graph import StateGraph, END

from ..models.review_state import ReviewState
from ..core.state import StateManager
from ..agents.pr_detector import PRDetectorAgent
from ..agents.security_agent import SecurityAnalysisAgent
from ..agents.quality_agent import QualityAnalysisAgent
from ..agents.coverage_agent import CoverageAnalysisAgent
from ..agents.ai_review_agent import AIReviewAgent
from ..agents.documentation_agent import DocumentationAgent
from ..agents.agent_coordinator import AgentCoordinator
from ..utils.logging_utils import get_logger

logger = get_logger("parallel_workflow")

class ParallelMultiAgentWorkflow:
    """Parallel Multi-Agent Code Review Workflow using LangGraph"""
    
    def __init__(self):
        self.workflow = None
        self.logger = logger
    
    def create_workflow(self):
        """Create the parallel multi-agent workflow graph"""
        self.logger.info(" Building Parallel Multi-Agent Workflow...")
        
        # Create workflow graph with proper state schema
        workflow = StateGraph(ReviewState)
        
        # Initialize agents
        pr_detector = PRDetectorAgent()
        security_agent = SecurityAnalysisAgent()
        quality_agent = QualityAnalysisAgent()
        coverage_agent = CoverageAnalysisAgent()
        ai_review_agent = AIReviewAgent()
        documentation_agent = DocumentationAgent()
        agent_coordinator = AgentCoordinator()
        
        # Add nodes
        workflow.add_node("pr_detector", pr_detector.execute)
        workflow.add_node("security_agent", security_agent.execute)
        workflow.add_node("quality_agent", quality_agent.execute)
        workflow.add_node("coverage_agent", coverage_agent.execute)
        workflow.add_node("ai_review_agent", ai_review_agent.execute)
        workflow.add_node("documentation_agent", documentation_agent.execute)
        workflow.add_node("agent_coordinator", agent_coordinator.execute)
        workflow.add_node("decision_maker", self.decision_maker_node)
        workflow.add_node("report_generator", self.report_generator_node)
        workflow.add_node("error_handler", self.error_handler_node)
        
        # Set entry point
        workflow.set_entry_point("pr_detector")
        
        # Define routing logic
        workflow.add_conditional_edges("pr_detector", self.route_to_parallel_agents)
        
        # All parallel agents always route to coordinator
        workflow.add_edge("security_agent", "agent_coordinator")
        workflow.add_edge("quality_agent", "agent_coordinator")
        workflow.add_edge("coverage_agent", "agent_coordinator")
        workflow.add_edge("ai_review_agent", "agent_coordinator")
        workflow.add_edge("documentation_agent", "agent_coordinator")
        
        # Coordinator routes to decision maker only when all agents complete
        workflow.add_conditional_edges("agent_coordinator", self.route_after_coordination)
        
        # Decision maker routes to report generator
        workflow.add_conditional_edges("decision_maker", self.route_after_decision)
        
        # Report generator ends workflow
        workflow.add_conditional_edges("report_generator", self.route_final)
        
        # Error handler always ends
        workflow.add_edge("error_handler", END)
        
        self.logger.info(" Parallel Multi-Agent Workflow Created")
        self.logger.info(" Agents: PR Detector -> [Security, Quality, Coverage, AI Review, Documentation] -> Coordinator -> Decision -> Report")
        
        self.workflow = workflow.compile()
        return self.workflow
    
    def route_to_parallel_agents(self, state: ReviewState):
        """Route to parallel agents after PR detection"""
        next_step = state.get("next", "end")
        
        if next_step == "parallel_agents":
            # Launch all agents in parallel
            return ["security_agent", "quality_agent", "coverage_agent", "ai_review_agent", "documentation_agent"]
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    def route_after_coordination(self, state: ReviewState):
        """Route after coordination is complete"""
        # Check if all agents have completed before proceeding
        expected_agents = ["security", "quality", "coverage", "ai_review", "documentation"]
        completed_agents = state.get("agents_completed", [])
        
        if not all(agent in completed_agents for agent in expected_agents):
            missing_agents = [agent for agent in expected_agents if agent not in completed_agents]
            self.logger.info(f"Coordinator waiting for agents: {missing_agents}")
            return END  # Wait for more agents
        
        # All agents completed, proceed based on next step
        next_step = state.get("next", "end")
        
        if next_step == "decision_maker":
            return "decision_maker"
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    def route_after_decision(self, state: ReviewState):
        """Route after decision making"""
        next_step = state.get("next", "end")
        
        if next_step == "report_generator":
            return "report_generator"
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    def route_final(self, state: ReviewState):
        """Final routing logic"""
        next_step = state.get("next", "end")
        
        if next_step == "end":
            return END
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    def decision_maker_node(self, state: ReviewState) -> Dict[str, Any]:
        """Decision maker node implementation"""
        from ..core.config import get_config_value
        
        PYLINT_THRESHOLD = get_config_value("PYLINT_THRESHOLD", 7.0)
        COVERAGE_THRESHOLD = get_config_value("COVERAGE_THRESHOLD", 80.0) 
        AI_CONFIDENCE_THRESHOLD = get_config_value("AI_CONFIDENCE_THRESHOLD", 0.8)
        SECURITY_THRESHOLD = get_config_value("SECURITY_THRESHOLD", 8.0)
        DOCUMENTATION_THRESHOLD = get_config_value("DOCUMENTATION_THRESHOLD", 70.0)
        
        self.logger.info(f" DECISION MAKER: {state['review_id']}")
        
        try:
            # Extract results for decision making
            security_results = state.get("security_results", [])
            pylint_results = state.get("pylint_results", [])
            coverage_results = state.get("coverage_results", [])
            ai_reviews = state.get("ai_reviews", [])
            documentation_results = state.get("documentation_results", [])
            
            # Calculate average scores
            avg_security_score = sum(r.get('security_score', 0) for r in security_results) / len(security_results) if security_results else 0
            avg_pylint_score = sum(r.get('score', 0) for r in pylint_results) / len(pylint_results) if pylint_results else 0
            avg_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results) if coverage_results else 0
            avg_ai_score = sum(r.get('overall_score', 0) for r in ai_reviews) / len(ai_reviews) if ai_reviews else 0
            avg_doc_coverage = sum(r.get('documentation_coverage', 0) for r in documentation_results) / len(documentation_results) if documentation_results else 0
            
            # Check for critical security issues
            high_severity_count = sum(r.get('severity_counts', {}).get('HIGH', 0) for r in security_results)
            has_critical_security = (avg_security_score < SECURITY_THRESHOLD) or (high_severity_count > 0)
            
            # Check other quality thresholds
            has_quality_issues = (avg_pylint_score < PYLINT_THRESHOLD) or (avg_coverage < COVERAGE_THRESHOLD) or (avg_ai_score < AI_CONFIDENCE_THRESHOLD)
            has_doc_issues = avg_doc_coverage < DOCUMENTATION_THRESHOLD
            
            # Make decision
            has_critical_issues = False
            critical_reason = ""
            decision = "auto_approve"
            
            if has_critical_security:
                has_critical_issues = True
                critical_reason = f"Security issues detected: Score {avg_security_score:.1f}/{SECURITY_THRESHOLD} or {high_severity_count} high severity vulnerabilities"
                decision = "critical_escalation"
            elif has_quality_issues:
                has_critical_issues = True
                if avg_pylint_score < PYLINT_THRESHOLD:
                    critical_reason = f"PyLint score too low: {avg_pylint_score:.2f} < {PYLINT_THRESHOLD}"
                elif avg_coverage < COVERAGE_THRESHOLD:
                    critical_reason = f"Test coverage too low: {avg_coverage:.1f}% < {COVERAGE_THRESHOLD}%"
                elif avg_ai_score < AI_CONFIDENCE_THRESHOLD:
                    critical_reason = f"AI confidence too low: {avg_ai_score:.2f} < {AI_CONFIDENCE_THRESHOLD}"
                decision = "human_review"
            elif has_doc_issues:
                has_critical_issues = True
                critical_reason = f"Documentation coverage too low: {avg_doc_coverage:.1f}% < {DOCUMENTATION_THRESHOLD}%"
                decision = "documentation_review"
            
            self.logger.info(f" Decision made: {decision.upper()}")
            if has_critical_issues:
                self.logger.info(f" Critical issues: {critical_reason}")
            
            return {
                "has_critical_issues": has_critical_issues,
                "critical_reason": critical_reason,
                "decision": decision,
                "stage": "decision_complete",
                "next": "report_generator",
                "decision_metrics": {
                    "security_score": avg_security_score,
                    "pylint_score": avg_pylint_score,
                    "coverage": avg_coverage,
                    "ai_score": avg_ai_score,
                    "documentation_coverage": avg_doc_coverage,
                    "high_severity_issues": high_severity_count
                }
            }
            
        except Exception as e:
            self.logger.error(f" Decision maker error: {e}")
            return {
                "error": str(e),
                "next": "error_handler",
                "stage": "decision_error"
            }
    
    def report_generator_node(self, state: ReviewState) -> Dict[str, Any]:
        """Report generator node implementation"""
        from ..services.email_service import EmailService
        
        self.logger.info(f" REPORT GENERATOR: {state['review_id']}")
        
        try:
            # Initialize email service
            email_service = EmailService()
            
            # Generate final report
            pr_details = state.get("pr_details", {})
            decision = state.get("decision", "human_review")
            has_critical_issues = state.get("has_critical_issues", False)
            critical_reason = state.get("critical_reason", "")
            
            # Format report data
            report_data = {
                "decision": decision,
                "recommendation": decision.replace("_", " ").upper(),
                "priority": "HIGH" if has_critical_issues else "MEDIUM",
                "metrics": state.get("decision_metrics", {}),
                "key_findings": [critical_reason] if critical_reason else ["All quality thresholds met"],
                "action_items": self._generate_action_items(state),
                "approval_criteria": self._generate_approval_criteria(state)
            }
            
            # Send email
            email_service.send_final_report_email(pr_details, report_data, has_critical_issues)
            
            # Update state with report completion
            return {
                "report": report_data,
                "stage": "report_complete",
                "next": "end",
                "workflow_complete": True,
                "emails_sent": [{"type": "final_report", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]
            }
            
        except Exception as e:
            self.logger.error(f" Report generator error: {e}")
            return {
                "error": str(e),
                "next": "error_handler",
                "stage": "report_error"
            }
    
    def _generate_action_items(self, state: ReviewState) -> List[str]:
        """Generate action items based on decision and results"""
        action_items = []
        decision = state.get("decision", "human_review")
        metrics = state.get("decision_metrics", {})
        
        if decision == "critical_escalation":
            action_items.append("Address critical security vulnerabilities immediately")
            action_items.append("Follow security best practices for affected code")
            
        elif decision == "human_review":
            if metrics.get("pylint_score", 10) < 7.0:
                action_items.append("Address code quality issues flagged by PyLint")
            if metrics.get("coverage", 100) < 80.0:
                action_items.append("Improve test coverage for affected code")
            if metrics.get("ai_score", 1.0) < 0.8:
                action_items.append("Review AI suggestions for code improvements")
                
        elif decision == "documentation_review":
            action_items.append("Add missing documentation to functions and classes")
            action_items.append("Ensure all modules have proper docstrings")
            
        return action_items
    
    def _generate_approval_criteria(self, state: ReviewState) -> List[str]:
        """Generate approval criteria based on results"""
        criteria = []
        metrics = state.get("decision_metrics", {})
        
        from ..core.config import get_config_value
        PYLINT_THRESHOLD = get_config_value("PYLINT_THRESHOLD", 7.0)
        COVERAGE_THRESHOLD = get_config_value("COVERAGE_THRESHOLD", 80.0) 
        AI_CONFIDENCE_THRESHOLD = get_config_value("AI_CONFIDENCE_THRESHOLD", 0.8)
        SECURITY_THRESHOLD = get_config_value("SECURITY_THRESHOLD", 8.0)
        DOCUMENTATION_THRESHOLD = get_config_value("DOCUMENTATION_THRESHOLD", 70.0)
        
        if metrics.get("security_score", 10) < SECURITY_THRESHOLD:
            criteria.append(f"Security score must be at least {SECURITY_THRESHOLD}/10.0")
        if metrics.get("high_severity_issues", 0) > 0:
            criteria.append("All high-severity security vulnerabilities must be addressed")
            
        if metrics.get("pylint_score", 10) < PYLINT_THRESHOLD:
            criteria.append(f"PyLint score must be at least {PYLINT_THRESHOLD}/10.0")
            
        if metrics.get("coverage", 100) < COVERAGE_THRESHOLD:
            criteria.append(f"Test coverage must be at least {COVERAGE_THRESHOLD}%")
            
        if metrics.get("ai_score", 1.0) < AI_CONFIDENCE_THRESHOLD:
            criteria.append("AI-identified code issues must be resolved")
            
        if metrics.get("documentation_coverage", 100) < DOCUMENTATION_THRESHOLD:
            criteria.append(f"Documentation coverage must be at least {DOCUMENTATION_THRESHOLD}%")
            
        # If all thresholds are met
        if not criteria:
            criteria.append("All quality thresholds are met")
        
        return criteria
    
    def error_handler_node(self, state: ReviewState) -> Dict[str, Any]:
        """Error handler node implementation"""
        from ..services.email_service import EmailService
        
        error_message = state.get("error", "Unknown error")
        self.logger.error(f" ERROR HANDLER: {error_message}")
        
        try:
            # Initialize email service
            email_service = EmailService()
            
            # Send error notification
            pr_details = state.get("pr_details", {"pr_number": "unknown", "title": "unknown"})
            email_service.send_error_notification(pr_details, error_message)
            
            return {
                "stage": "error_handled",
                "workflow_complete": True,
                "emails_sent": [{"type": "error_notification", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]
            }
            
        except Exception as e:
            self.logger.error(f" Error handler failed: {e}")
            return {
                "stage": "error_handling_failed",
                "workflow_complete": True
            }
    
    def execute(self, repo_owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Execute the workflow for a specific PR"""
        self.logger.info(f" STARTING PARALLEL MULTI-AGENT CODE REVIEW WORKFLOW")
        self.logger.info(f" Repository: {repo_owner}/{repo_name}")
        self.logger.info(f" PR Number: {pr_number}")
        
        if not self.workflow:
            self.create_workflow()
        
        # Create initial state
        state = StateManager.create_initial_state(repo_owner, repo_name, pr_number)
        
        # Execute workflow
        self.logger.info(f" Executing PARALLEL MULTI-AGENT workflow...")
        final_state = self.workflow.invoke(state)
        
        # Display results
        self.logger.info("=" * 70)
        self.logger.info(" WORKFLOW COMPLETED")
        self.logger.info(f" Review: {final_state['review_id']}")
        self.logger.info(f" Status: {final_state['stage'].upper()}")
        
        # Display agent completion status
        if "agents_completed" in final_state:
            completed_agents = final_state["agents_completed"]
            self.logger.info(f" Agents Completed: {', '.join(set(completed_agents))}")
        
        if final_state.get("has_critical_issues"):
            self.logger.info(f" Critical Issues: {final_state.get('critical_reason', 'Unknown')}")
        else:
            self.logger.info(" No critical issues found")
        
        self.logger.info(f" Emails Sent: {len(final_state.get('emails_sent', []))}")
        
        # Display detailed metrics if available
        if "decision_metrics" in final_state:
            metrics = final_state["decision_metrics"]
            self.logger.info("\n" + "=" * 70)
            self.logger.info(" QUALITY METRICS SUMMARY")
            self.logger.info(f" Security Score: {metrics.get('security_score', 0):.2f}/10.0")
            self.logger.info(f" PyLint Score: {metrics.get('pylint_score', 0):.2f}/10.0")
            self.logger.info(f" Test Coverage: {metrics.get('coverage', 0):.1f}%")
            self.logger.info(f" AI Review Score: {metrics.get('ai_score', 0):.2f}/1.0")
            self.logger.info(f" Documentation: {metrics.get('documentation_coverage', 0):.1f}%")
        
        return final_state