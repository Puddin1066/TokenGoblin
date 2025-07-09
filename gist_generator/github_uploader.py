"""
GitHub Gist uploader for Claude Token Resale System
"""

import os
import logging
from typing import Optional
from github import Github
from github.GithubException import GithubException

logger = logging.getLogger(__name__)


class GitHubUploader:
    """Upload gists to GitHub"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_PAT")
        self.github = None
        
        if self.github_token:
            try:
                self.github = Github(self.github_token)
                # Test authentication
                user = self.github.get_user()
                logger.info(f"GitHub authenticated as: {user.login}")
            except GithubException as e:
                logger.error(f"GitHub authentication failed: {e}")
                self.github = None
        else:
            logger.warning("No GitHub token provided. GitHub upload disabled.")
    
    def upload_gist(self, filename: str, content: str, description: str = "", 
                   public: bool = True) -> Optional[str]:
        """Upload content as a GitHub Gist"""
        if not self.github:
            raise ValueError("GitHub not initialized. Check your GITHUB_PAT token.")
        
        try:
            files = {filename: {"content": content}}
            
            gist = self.github.get_user().create_gist(
                public=public,
                files=files,
                description=description
            )
            
            logger.info(f"Gist created: {gist.html_url}")
            return gist.html_url
            
        except GithubException as e:
            logger.error(f"Failed to create gist: {e}")
            raise
    
    def update_gist(self, gist_id: str, filename: str, content: str, 
                   description: Optional[str] = None) -> Optional[str]:
        """Update existing GitHub Gist"""
        if not self.github:
            raise ValueError("GitHub not initialized. Check your GITHUB_PAT token.")
        
        try:
            gist = self.github.get_gist(gist_id)
            
            files = {filename: {"content": content}}
            
            if description:
                gist.edit(description=description, files=files)
            else:
                gist.edit(files=files)
            
            logger.info(f"Gist updated: {gist.html_url}")
            return gist.html_url
            
        except GithubException as e:
            logger.error(f"Failed to update gist: {e}")
            raise
    
    def delete_gist(self, gist_id: str) -> bool:
        """Delete GitHub Gist"""
        if not self.github:
            raise ValueError("GitHub not initialized. Check your GITHUB_PAT token.")
        
        try:
            gist = self.github.get_gist(gist_id)
            gist.delete()
            logger.info(f"Gist deleted: {gist_id}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to delete gist: {e}")
            return False
    
    def list_gists(self) -> list:
        """List all gists for authenticated user"""
        if not self.github:
            raise ValueError("GitHub not initialized. Check your GITHUB_PAT token.")
        
        try:
            gists = self.github.get_user().get_gists()
            return [{"id": g.id, "description": g.description, "url": g.html_url} for g in gists]
            
        except GithubException as e:
            logger.error(f"Failed to list gists: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if GitHub upload is available"""
        return self.github is not None