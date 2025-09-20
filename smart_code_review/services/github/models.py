from typing import Optional
from dataclasses import dataclass

@dataclass
class PullRequest:
    """Pull request data model"""
    pr_number: int
    title: str
    author: str
    head_branch: str
    base_branch: str
    state: str
    created_at: str
    updated_at: str

@dataclass
class FileChange:
    """File change in a pull request"""
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    content: Optional[str] = None