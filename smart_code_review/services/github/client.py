import requests
import logging
import base64
from typing import Dict, Any, List, Optional, Union
from .models import PullRequest, FileChange
from ...utils.error_handling import GitHubError

logger = logging.getLogger("github_service")

class GitHubClient:
    """GitHub API client implementation"""
    
    def __init__(self, token: str, api_url: str = "https://api.github.com"):
        self.token = token
        self.api_url = api_url
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_pr_details(self, repo_owner: str, repo_name: str, pr_number: int) -> Optional[PullRequest]:
        """Get pull request details"""
        url = f"{self.api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
        
        try:
            logger.info(f"Fetching PR details for {repo_owner}/{repo_name}#{pr_number}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            pr_data = response.json()
            return PullRequest(
                pr_number=pr_number,
                title=pr_data.get('title', ''),
                author=pr_data.get('user', {}).get('login', ''),
                head_branch=pr_data.get('head', {}).get('ref', ''),
                base_branch=pr_data.get('base', {}).get('ref', ''),
                state=pr_data.get('state', ''),
                created_at=pr_data.get('created_at', ''),
                updated_at=pr_data.get('updated_at', '')
            )
            
        except Exception as e:
            logger.error(f"Error fetching PR details: {e}")
            return None
    
    def get_pr_files(self, repo_owner: str, repo_name: str, pr_number: int) -> List[FileChange]:
        """Get files changed in a pull request"""
        url = f"{self.api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        results = []
        
        try:
            logger.info(f"Fetching PR files for {repo_owner}/{repo_name}#{pr_number}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            files_data = response.json()
            
            # Process only Python files
            for file_data in files_data:
                filename = file_data.get('filename', '')
                
                if filename.endswith('.py'):
                    results.append(FileChange(
                        filename=filename,
                        status=file_data.get('status', ''),
                        additions=file_data.get('additions', 0),
                        deletions=file_data.get('deletions', 0),
                        changes=file_data.get('changes', 0),
                        content=None  # Content will be fetched separately
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching PR files: {e}")
            return []
    
    def get_file_content(self, repo_owner: str, repo_name: str, file_path: str, ref: str = "main") -> Optional[str]:
        """Get content of a specific file"""
        url = f"{self.api_url}/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        params = {"ref": ref}
        
        try:
            logger.info(f"Fetching file content: {file_path} (ref: {ref})")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            content_data = response.json()
            if 'content' in content_data and content_data.get('encoding') == 'base64':
                content = base64.b64decode(content_data['content']).decode('utf-8')
                return content
                
            return None
            
        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            return None
    
    def get_repo_details(self, repo_owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get repository details"""
        url = f"{self.api_url}/repos/{repo_owner}/{repo_name}"
        
        try:
            logger.info(f"Fetching repository details for {repo_owner}/{repo_name}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching repository details: {e}")
            return None