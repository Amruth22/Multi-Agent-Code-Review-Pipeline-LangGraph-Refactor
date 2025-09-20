import re
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("gemini_parser")

def extract_section(text: str, pattern: str, data_type: type, default: Any) -> Any:
    """Extract a single value from text using regex"""
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return data_type(match.group(1))
        return default
    except Exception as e:
        logger.debug(f"Error extracting pattern {pattern}: {e}")
        return default

def extract_list_section(text: str, pattern: str) -> List[str]:
    """Extract list items from text using regex"""
    try:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1).strip()
            # Extract bullet points
            items = []
            for line in section_text.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    items.append(line[1:].strip())
            return items
        return []
    except Exception as e:
        logger.debug(f"Error extracting list section {pattern}: {e}")
        return []

def parse_ai_review(response: str, filename: str) -> Dict[str, Any]:
    """Parse Gemini AI review response"""
    try:
        overall_score = extract_section(response, r'OVERALL_SCORE:\s*([\d.]+)', float, 0.7)
        confidence = extract_section(response, r'CONFIDENCE:\s*([\d.]+)', float, 0.8)
        
        strengths = extract_list_section(response, r'STRENGTHS:(.*?)(?:ISSUES:|$)')
        issues = extract_list_section(response, r'ISSUES:(.*?)(?:RECOMMENDATIONS:|$)')
        recommendations = extract_list_section(response, r'RECOMMENDATIONS:(.*?)(?:REFACTORING_SUGGESTIONS:|$)')
        refactoring = extract_list_section(response, r'REFACTORING_SUGGESTIONS:(.*?)(?:SECURITY_CONCERNS:|$)')
        security = extract_list_section(response, r'SECURITY_CONCERNS:(.*?)$')
        
        return {
            "filename": filename,
            "overall_score": overall_score,
            "confidence": confidence,
            "strengths": strengths,
            "issues": issues,
            "recommendations": recommendations,
            "refactoring_suggestions": refactoring,
            "security_concerns": security,
            "raw_response": response
        }
    except Exception as e:
        logger.error(f"Failed to parse AI review: {e}")
        return create_fallback_ai_review(filename, response)

def create_fallback_ai_review(filename: str, raw_response: str) -> Dict[str, Any]:
    """Create fallback AI review when parsing fails"""
    return {
        "filename": filename,
        "overall_score": 0.7,
        "confidence": 0.6,
        "strengths": ["Code structure appears reasonable"],
        "issues": ["Unable to perform detailed analysis"],
        "recommendations": ["Manual code review recommended"],
        "refactoring_suggestions": [],
        "security_concerns": ["Manual security review needed"],
        "raw_response": raw_response,
        "note": "Fallback review due to parsing error"
    }

def parse_pr_summary(response: str) -> Dict[str, Any]:
    """Parse PR summary response"""
    try:
        recommendation = extract_section(response, r'OVERALL_RECOMMENDATION:\s*(\w+)', str, "NEEDS_WORK")
        priority = extract_section(response, r'PRIORITY:\s*(\w+)', str, "MEDIUM")
        
        key_findings = extract_list_section(response, r'KEY_FINDINGS:(.*?)(?:ACTION_ITEMS:|$)')
        action_items = extract_list_section(response, r'ACTION_ITEMS:(.*?)(?:APPROVAL_CRITERIA:|$)')
        approval_criteria = extract_list_section(response, r'APPROVAL_CRITERIA:(.*?)$')
        
        return {
            "recommendation": recommendation.upper(),
            "priority": priority.upper(),
            "key_findings": key_findings,
            "action_items": action_items,
            "approval_criteria": approval_criteria,
            "raw_response": response
        }
    except Exception as e:
        logger.error(f"Failed to parse PR summary: {e}")
        return {
            "recommendation": "NEEDS_WORK",
            "priority": "MEDIUM",
            "key_findings": ["Analysis completed with limitations"],
            "action_items": ["Manual review recommended"],
            "approval_criteria": ["Address identified issues"],
            "raw_response": response
        }