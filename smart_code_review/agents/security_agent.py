from typing import Dict, Any, List
import logging
from .base_agent import BaseAgent
from ..analyzers.security_analyzer import detect_security_vulnerabilities

class SecurityAnalysisAgent(BaseAgent):
    """Agent for security vulnerability analysis"""
    
    def __init__(self):
        super().__init__("security")
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process files for security vulnerabilities"""
        security_results = []
        
        for file_data in state["files_data"]:
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                self.logger.info(f" Security scanning {filename}...")
                security_issues = detect_security_vulnerabilities(content, filename)
                security_results.append({
                    "filename": filename,
                    "security_score": security_issues["security_score"],
                    "vulnerabilities": security_issues["vulnerabilities"],
                    "severity_counts": security_issues["severity_counts"],
                    "recommendations": security_issues["recommendations"]
                })
        
        return {
            "security_results": security_results
        }