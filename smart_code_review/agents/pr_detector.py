from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent
from ..services.github.client import GitHubClient
from ..services.email_service import EmailService
from ..core.config import get_config_value
from ..utils.error_handling import GitHubError

class PRDetectorAgent(BaseAgent):
    """Agent for PR detection and file extraction"""
    
    def __init__(self):
        super().__init__("pr_detector")
        self.github_client = None
        self.email_service = None
    
    def _init_services(self):
        """Initialize required services"""
        if self.github_client is None:
            github_token = get_config_value("GITHUB_TOKEN")
            github_api_url = get_config_value("GITHUB_API_URL")
            self.github_client = GitHubClient(github_token, github_api_url)
        
        if self.email_service is None:
            self.email_service = EmailService()
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process PR detection and file extraction"""
        self._init_services()
        
        repo_owner = state["repo_owner"]
        repo_name = state["repo_name"]
        pr_number = state["pr_number"]
        
        # Get PR details
        pr_details = self.github_client.get_pr_details(repo_owner, repo_name, pr_number)
        if not pr_details:
            raise GitHubError("Failed to fetch PR details", {
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "pr_number": pr_number
            })
        
        # Get changed Python files
        files = self.github_client.get_pr_files(repo_owner, repo_name, pr_number)
        if not files:
            raise GitHubError("No Python files found in PR", {
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "pr_number": pr_number
            })
        
        # Get file contents from the PR head branch
        pr_head_branch = pr_details.head_branch
        self.logger.info(f" Fetching files from branch: {pr_head_branch}")
        
        files_with_content = []
        for file_info in files:
            if file_info.status != "deleted":  # Skip deleted files
                content = self.github_client.get_file_content(
                    repo_owner, repo_name, file_info.filename, ref=pr_head_branch
                )
                if content:
                    files_with_content.append({
                        "filename": file_info.filename,
                        "status": file_info.status,
                        "additions": file_info.additions,
                        "deletions": file_info.deletions,
                        "changes": file_info.changes,
                        "content": content
                    })
                else:
                    self.logger.warning(f" Could not fetch content for {file_info.filename} from branch {pr_head_branch}")
        
        if not files_with_content:
            raise GitHubError("Could not fetch content for any files", {
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "pr_number": pr_number,
                "branch": pr_head_branch
            })
        
        # Send initial email
        pr_details_dict = {
            "pr_number": pr_number,
            "title": pr_details.title,
            "author": pr_details.author,
            "head_branch": pr_details.head_branch,
            "base_branch": pr_details.base_branch,
            "created_at": pr_details.created_at,
            "updated_at": pr_details.updated_at
        }
        self.email_service.send_review_started_email(pr_details_dict, len(files_with_content))
        
        self.logger.info(f" PR detected: {len(files_with_content)} Python files to review")
        self.logger.info(f" Launching parallel agents: Security, Quality, Coverage, AI Review")
        
        # Return updated state
        return {
            "pr_details": pr_details_dict,
            "files_data": files_with_content,
            "stage": "parallel_analysis",
            "next": "parallel_agents",
            "emails_sent": [{"type": "review_started", "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]
        }