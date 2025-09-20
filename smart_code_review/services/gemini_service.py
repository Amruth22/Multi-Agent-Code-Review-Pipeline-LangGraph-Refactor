from .gemini.client import GeminiClient
from ..core.config import get_config_value

class GeminiService:
    """Wrapper service for Gemini AI API to match expected interface in tests"""
    
    def __init__(self):
        api_key = get_config_value("GEMINI_API_KEY")
        model = get_config_value("GEMINI_MODEL", "gemini-2.0-flash")
        self.client = GeminiClient(api_key, model)
    
    def analyze_file(self, filename: str, content: str) -> dict:
        """Analyze a file with Gemini AI"""
        return self.client.review_code(content, filename)