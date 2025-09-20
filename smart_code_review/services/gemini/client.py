import logging
from typing import Dict, Any, List, Optional, Union
from .prompts import CODE_REVIEW_PROMPT, PR_SUMMARY_PROMPT, SECURITY_ENHANCEMENT_PROMPT, DOCUMENTATION_IMPROVEMENT_PROMPT
from .parser import parse_ai_review, create_fallback_ai_review, parse_pr_summary
from ...utils.error_handling import AIModelError
from ...core.config import get_config_value

logger = logging.getLogger("gemini_service")

class GeminiClient:
    """Client for Gemini AI API"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.client = None
        
    def _init_client(self):
        """Initialize the Gemini client if not already done"""
        if self.client is None:
            try:
                from google import genai
                from google.genai import types
                self.client = genai.Client(api_key=self.api_key)
                self.types = types
                logger.info(f"Initialized Gemini client with model: {self.model}")
            except ImportError:
                logger.error("Failed to import Google Generative AI library")
                raise AIModelError("Google Generative AI library not found. Please install with 'pip install google-generativeai'")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise AIModelError(f"Failed to initialize Gemini client: {e}")
    
    def generate_response(self, prompt: str) -> str:
        """Generate response from Gemini"""
        self._init_client()
        
        try:
            from google.genai import types
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
            response = ""
            
            for chunk in self.client.models.generate_content_stream(model=self.model, contents=contents):
                if chunk.text is not None:
                    response += chunk.text
                else:
                    logger.warning(f"Gemini chunk returned None text, skipping...")
                    
            return response.strip() if response else "Unable to generate AI response"
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise AIModelError(f"Failed to generate response from Gemini: {e}")
    
    def review_code(self, file_content: str, filename: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Review code with Gemini AI"""
        # Prepare context string
        context_str = f"Filename: {filename}\n"
        if context:
            if "pylint" in context:
                context_str += f"PyLint Score: {context['pylint'].get('score', 'N/A')}/10\n"
                context_str += f"Issues Found: {context['pylint'].get('total_issues', 0)}\n"
            
            if "coverage" in context:
                context_str += f"Test Coverage: {context['coverage'].get('coverage_percent', 0)}%\n"
            
            if "security" in context:
                context_str += f"Security Score: {context['security'].get('security_score', 'N/A')}/10\n"
                vuln_count = len(context['security'].get('vulnerabilities', []))
                context_str += f"Vulnerabilities Found: {vuln_count}\n"
        
        # Format the prompt with code and context
        prompt = CODE_REVIEW_PROMPT.format(
            context=context_str,
            code=file_content
        )
        
        # Generate and parse response
        try:
            response = self.generate_response(prompt)
            return parse_ai_review(response, filename)
        except Exception as e:
            logger.error(f"Failed to review code: {e}")
            return create_fallback_ai_review(filename, str(e))
    
    def generate_pr_summary(self, pr_details: Dict[str, Any], 
                          quality_results: List[Dict[str, Any]],
                          coverage_results: List[Dict[str, Any]],
                          ai_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall PR summary with AI"""
        # Calculate aggregate metrics
        overall_pylint_score = sum(r.get('score', 0) for r in quality_results) / len(quality_results) if quality_results else 0
        overall_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results) if coverage_results else 0
        overall_ai_score = sum(r.get('overall_score', 0) for r in ai_reviews) / len(ai_reviews) if ai_reviews else 0
        
        # Format the prompt with PR details and metrics
        prompt = PR_SUMMARY_PROMPT.format(
            title=pr_details.get('title', 'N/A'),
            author=pr_details.get('author', 'N/A'),
            files_count=len(quality_results) if quality_results else 0,
            pylint_score=f"{overall_pylint_score:.2f}",
            coverage=f"{overall_coverage:.1f}",
            ai_score=f"{overall_ai_score:.2f}"
        )
        
        # Generate and parse response
        try:
            response = self.generate_response(prompt)
            return parse_pr_summary(response)
        except Exception as e:
            logger.error(f"Failed to generate PR summary: {e}")
            return {
                "recommendation": "NEEDS_WORK",
                "priority": "MEDIUM",
                "key_findings": ["Unable to generate complete analysis"],
                "action_items": ["Review code manually"],
                "approval_criteria": ["Address all identified issues"],
                "raw_response": str(e)
            }
    
    def generate_security_enhancements(self, code: str, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate security enhancement recommendations"""
        vulnerabilities_text = "\n".join([
            f"• {vuln['description']} (Line {vuln['line']}, Severity: {vuln['severity']})" 
            for vuln in vulnerabilities
        ])
        
        prompt = SECURITY_ENHANCEMENT_PROMPT.format(
            code=code,
            vulnerabilities=vulnerabilities_text
        )
        
        try:
            response = self.generate_response(prompt)
            return self._parse_security_enhancements(response)
        except Exception as e:
            logger.error(f"Failed to generate security enhancements: {e}")
            return {
                "security_score": 5.0,
                "severity": "MEDIUM",
                "recommended_fixes": ["Manual security review required"],
                "secure_alternatives": [],
                "security_best_practices": ["Follow language-specific security guidelines"]
            }
    
    def generate_documentation_improvements(self, code: str, coverage: float) -> Dict[str, Any]:
        """Generate documentation improvement recommendations"""
        prompt = DOCUMENTATION_IMPROVEMENT_PROMPT.format(
            code=code,
            coverage=f"{coverage:.1f}"
        )
        
        try:
            response = self.generate_response(prompt)
            return self._parse_documentation_improvements(response)
        except Exception as e:
            logger.error(f"Failed to generate documentation improvements: {e}")
            return {
                "module_docstring": "# Documentation could not be generated automatically",
                "class_docstrings": {},
                "function_docstrings": {}
            }
    
    def _parse_security_enhancements(self, response: str) -> Dict[str, Any]:
        """Parse security enhancement response"""
        from .parser import extract_section, extract_list_section
        
        security_score = extract_section(response, r'SECURITY_SCORE:\s*([\d.]+)', float, 5.0)
        severity = extract_section(response, r'SEVERITY:\s*(\w+)', str, "MEDIUM")
        
        recommended_fixes = extract_list_section(response, r'RECOMMENDED_FIXES:(.*?)(?:SECURE_ALTERNATIVES:|$)')
        secure_alternatives = extract_list_section(response, r'SECURE_ALTERNATIVES:(.*?)(?:SECURITY_BEST_PRACTICES:|$)')
        security_best_practices = extract_list_section(response, r'SECURITY_BEST_PRACTICES:(.*?)$')
        
        return {
            "security_score": security_score,
            "severity": severity.upper(),
            "recommended_fixes": recommended_fixes,
            "secure_alternatives": secure_alternatives,
            "security_best_practices": security_best_practices,
            "raw_response": response
        }
    
    def _parse_documentation_improvements(self, response: str) -> Dict[str, Any]:
        """Parse documentation improvements response"""
        from .parser import extract_section
        import re
        
        # Extract module docstring
        module_match = re.search(r'MODULE_DOCSTRING:\s*"""\s*(.*?)\s*"""', response, re.DOTALL)
        module_docstring = module_match.group(1).strip() if module_match else ""
        
        # Extract class docstrings
        class_docstrings = {}
        class_pattern = r'class\s+(\w+):\s*"""\s*(.*?)\s*"""'
        for match in re.finditer(class_pattern, response, re.DOTALL):
            class_name = match.group(1)
            docstring = match.group(2).strip()
            class_docstrings[class_name] = docstring
        
        # Extract function docstrings
        function_docstrings = {}
        function_pattern = r'def\s+(\w+)\([^)]*\):\s*"""\s*(.*?)\s*"""'
        for match in re.finditer(function_pattern, response, re.DOTALL):
            function_name = match.group(1)
            docstring = match.group(2).strip()
            function_docstrings[function_name] = docstring
        
        return {
            "module_docstring": module_docstring,
            "class_docstrings": class_docstrings,
            "function_docstrings": function_docstrings,
            "raw_response": response
        }