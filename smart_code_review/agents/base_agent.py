from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
from datetime import datetime
from ..utils.error_handling import safe_execute, detailed_error

class BaseAgent(ABC):
    """Abstract base class for all agents in the code review system"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method with standardized error handling and logging"""
        review_id = state.get("review_id", "unknown")
        self.logger.info(f"{self.agent_name.upper()} AGENT: {review_id}")
        
        try:
            # Execute agent-specific analysis
            result = self.process(state)
            
            # Always add agent to completed list
            if "agents_completed" not in result:
                result["agents_completed"] = [self._get_agent_id()]
                
            self.logger.info(f" {self.agent_name.capitalize()} analysis complete")
            return result
            
        except Exception as e:
            self.logger.error(f" {self.agent_name.capitalize()} agent error: {e}")
            # Capture detailed error information
            error_info = detailed_error(e)
            # Return minimal result with agent marked as completed
            return {
                f"{self._get_result_key()}": [],
                "agents_completed": [self._get_agent_id()],
                "agent_errors": [{
                    "agent": self.agent_name,
                    "error": str(e),
                    "details": error_info
                }]
            }
    
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Agent-specific processing logic to be implemented by subclasses"""
        pass
    
    def _get_agent_id(self) -> str:
        """Get the agent identifier for completion tracking"""
        return self.agent_name.lower().replace("_agent", "")
    
    def _get_result_key(self) -> str:
        """Get the state key for storing this agent's results"""
        agent_id = self._get_agent_id()
        return f"{agent_id}_results"