import re
from typing import Optional, Tuple, Dict, Any, List

def validate_repo_url(repo_url: str) -> Tuple[bool, Optional[str]]:
    """Validate GitHub repository URL format"""
    # GitHub URL patterns
    patterns = [
        r'https?://github\.com/([^/]+)/([^/]+)/?.*',
        r'https?://api\.github\.com/repos/([^/]+)/([^/]+)/?.*',
        r'git@github\.com:([^/]+)/([^/]+)\.git'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            return True, None
    
    return False, "Invalid GitHub repository URL format"

def parse_repo_url(repo_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse GitHub repository URL and extract owner and name"""
    # Remove '/tree/' and everything after if present in the URL
    if '/tree/' in repo_url:
        repo_url = repo_url.split('/tree/')[0]
        
    # Remove '/blob/' and everything after if present in the URL
    if '/blob/' in repo_url:
        repo_url = repo_url.split('/blob/')[0]
        
    patterns = [
        r'https?://github\.com/([^/]+)/([^/]+)/?.*',
        r'https?://api\.github\.com/repos/([^/]+)/([^/]+)/?.*',
        r'git@github\.com:([^/]+)/([^/]+)\.git'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            return match.group(1), match.group(2)
    
    return None, None

def validate_file_paths(file_paths: List[str]) -> List[str]:
    """Validate file paths and return only valid Python files"""
    import os
    
    valid_files = []
    for file_path in file_paths:
        if os.path.exists(file_path) and file_path.endswith('.py'):
            valid_files.append(file_path)
            
    return valid_files

def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate application configuration"""
    required_keys = [
        "GITHUB_TOKEN",
        "GEMINI_API_KEY",
        "EMAIL_FROM",
        "EMAIL_PASSWORD",
        "EMAIL_TO"
    ]
    
    missing_keys = []
    for key in required_keys:
        if key not in config or not config[key]:
            missing_keys.append(key)
    
    return len(missing_keys) == 0, missing_keys