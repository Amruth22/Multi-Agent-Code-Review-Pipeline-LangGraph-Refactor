from typing import Dict, Any, List
import textwrap
import re
from datetime import datetime

def format_code_block(code: str, language: str = "python") -> str:
    """Format code as a Markdown code block"""
    return f"```{language}\n{code}\n```"

def format_list_items(items: List[str], bullet: str = "•") -> str:
    """Format a list of items with consistent bullet points"""
    if not items:
        return "None"
    return "\n".join(f"{bullet} {item}" for item in items)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_timestamp(timestamp: str = None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return timestamp

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage with specified decimal places"""
    return f"{value:.{decimals}f}%"

def format_score(value: float, max_score: float = 10.0, decimals: int = 1) -> str:
    """Format score with specified decimal places and maximum score"""
    return f"{value:.{decimals}f}/{max_score:.{decimals}f}"

def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    return re.sub(r'<[^>]+>', '', text)