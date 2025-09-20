from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent
from ..analyzers.documentation_analyzer import analyze_documentation_quality

class DocumentationAgent(BaseAgent):
    """Agent for documentation analysis and generation"""
    
    def __init__(self):
        super().__init__("documentation")
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process files for documentation analysis"""
        documentation_results = []
        
        for file_data in state["files_data"]:
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                self.logger.info(f" Analyzing documentation for {filename}...")
                doc_analysis = analyze_documentation_quality(content, filename)
                documentation_results.append(doc_analysis)
        
        self.logger.info(f" Documentation analysis complete - {len(documentation_results)} files analyzed")
        
        return {
            "documentation_results": documentation_results
        }