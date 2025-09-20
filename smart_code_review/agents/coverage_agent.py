from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent
from ..services.coverage_service import CoverageService
from ..analyzers.test_quality import analyze_test_quality

class CoverageAnalysisAgent(BaseAgent):
    """Agent for test coverage analysis"""
    
    def __init__(self):
        super().__init__("coverage")
        self.coverage_service = None
    
    def _init_services(self):
        """Initialize required services"""
        if self.coverage_service is None:
            self.coverage_service = CoverageService()
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process files for test coverage analysis"""
        self._init_services()
        
        # Run coverage analysis
        coverage_results = self.coverage_service.analyze_test_coverage(state["files_data"])
        missing_tests = self.coverage_service.analyze_missing_tests(state["files_data"], coverage_results)
        
        # Enhanced coverage analysis
        enhanced_coverage_results = []
        for i, result in enumerate(coverage_results):
            file_data = state["files_data"][i] if i < len(state["files_data"]) else {}
            content = file_data.get("content", "")
            
            if content:
                # Add test quality metrics
                filename = result["filename"]
                test_metrics = analyze_test_quality(content, filename)
                
                enhanced_result = {
                    **result,
                    "test_quality_score": test_metrics["test_quality_score"],
                    "missing_test_types": test_metrics["missing_test_types"],
                    "testability_score": test_metrics["testability_score"]
                }
                enhanced_coverage_results.append(enhanced_result)
        
        self.logger.info(f" Coverage analysis complete - {len(enhanced_coverage_results)} files analyzed")
        
        return {
            "coverage_results": enhanced_coverage_results,
            "missing_tests": missing_tests
        }