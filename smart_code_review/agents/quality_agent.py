from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent
from ..services.pylint_service import PylintService
from ..analyzers.code_complexity import analyze_code_complexity

class QualityAnalysisAgent(BaseAgent):
    """Agent for code quality analysis"""
    
    def __init__(self):
        super().__init__("quality")
        self.pylint_service = None
    
    def _init_services(self):
        """Initialize required services"""
        if self.pylint_service is None:
            self.pylint_service = PylintService()
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process files for code quality analysis"""
        self._init_services()
        
        # Run PyLint analysis
        pylint_results = self.pylint_service.analyze_multiple_files(state["files_data"])
        
        # Add custom quality metrics
        enhanced_quality_results = []
        for i, result in enumerate(pylint_results):
            file_data = state["files_data"][i] if i < len(state["files_data"]) else {}
            content = file_data.get("content", "")
            
            # Add custom quality metrics
            if content:
                filename = result["filename"]
                custom_metrics = analyze_code_complexity(content, filename)
                
                enhanced_result = {
                    **result,
                    "complexity_score": custom_metrics["complexity_score"],
                    "maintainability_index": custom_metrics["maintainability_index"],
                    "code_smells": custom_metrics["code_smells"],
                    "technical_debt": custom_metrics["technical_debt"]
                }
                enhanced_quality_results.append(enhanced_result)
        
        self.logger.info(f" Quality analysis complete - {len(enhanced_quality_results)} files analyzed")
        
        return {
            "pylint_results": enhanced_quality_results
        }