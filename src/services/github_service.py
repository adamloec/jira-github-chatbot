import requests
import os
from typing import Dict, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GitHubService:
    """GitHub API client for fetching user activity"""
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        
        if not self.token:
            logger.warning("GitHub token not found. Check GITHUB_TOKEN environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'JIRA-GitHub-Chatbot'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to GitHub API"""
        try:
            url = f"https://api.github.com{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    error_msg = "GitHub authentication failed. Check token."
                elif e.response.status_code == 404:
                    error_msg = "GitHub user not found."
                elif e.response.status_code == 403:
                    error_msg = "GitHub API rate limit exceeded."
                else:
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get('message', error_msg)
                    except:
                        pass
            
            logger.error(f"GitHub API error: {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def get_user_activity(self, username: str) -> Dict:
        """Get GitHub activity for a user"""
        try:
            # Get user profile
            profile_result = self._make_request(f'/users/{username}')
            if not profile_result['success']:
                return profile_result
            
            profile = profile_result['data']
            
            # Get repositories
            repos = self._get_user_repositories(username)
            
            # Get recent commits
            commits = self._get_recent_commits(username)
            
            # Get pull requests
            prs = self._get_user_pull_requests(username)
            
            # Recent activity (last 7 days)
            recent_commits = [c for c in commits if self._is_recent(c['date'], 7)]
            recent_prs = [pr for pr in prs if self._is_recent(pr['updated_at'], 7)]
            
            return {
                'success': True,
                'data': {
                    'user': {
                        'username': username,
                        'name': profile.get('name', username),
                        'company': profile.get('company', ''),
                        'public_repos': profile.get('public_repos', 0)
                    },
                    'summary': {
                        'total_repositories': len(repos),
                        'total_commits': len(commits),
                        'total_pull_requests': len(prs),
                        'recent_commits_7d': len(recent_commits),
                        'recent_prs_7d': len(recent_prs)
                    },
                    'recent_commits': commits[:10],
                    'repositories': repos[:10],
                    'pull_requests': prs[:5]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting GitHub user activity: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to get GitHub activity: {str(e)}"
            }
    
    def _get_user_repositories(self, username: str) -> List[Dict]:
        """Get user repositories"""
        result = self._make_request(f'/users/{username}/repos', {
            'sort': 'updated',
            'per_page': 20
        })
        
        if not result['success']:
            return []
        
        repositories = []
        for repo in result['data']:
            repositories.append({
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description', '')[:100] if repo.get('description') else 'No description',
                'language': repo.get('language', 'Unknown'),
                'updated_at': repo['updated_at'],
                'private': repo['private']
            })
        
        return repositories
    
    def _get_recent_commits(self, username: str) -> List[Dict]:
        """Get recent commits by user"""
        result = self._make_request(f'/users/{username}/events', {
            'per_page': 30
        })
        
        if not result['success']:
            return []
        
        commits = []
        for event in result['data']:
            if event['type'] == 'PushEvent':
                repo_name = event['repo']['name']
                for commit in event['payload'].get('commits', []):
                    commits.append({
                        'sha': commit['sha'][:7],
                        'message': commit['message'][:100],
                        'repository': repo_name,
                        'date': event['created_at']
                    })
        
        return commits[:20]
    
    def _get_user_pull_requests(self, username: str) -> List[Dict]:
        """Get user pull requests"""
        result = self._make_request('/search/issues', {
            'q': f'type:pr author:{username}',
            'sort': 'updated',
            'per_page': 15
        })
        
        if not result['success']:
            return []
        
        pull_requests = []
        for pr in result['data'].get('items', []):
            pull_requests.append({
                'number': pr['number'],
                'title': pr['title'],
                'state': pr['state'],
                'repository': pr['repository_url'].split('/')[-1],
                'created_at': pr['created_at'],
                'updated_at': pr['updated_at']
            })
        
        return pull_requests
    
    def _is_recent(self, date_str: str, days: int) -> bool:
        """Check if date is within the last N days"""
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            cutoff = datetime.now().replace(tzinfo=date.tzinfo) - timedelta(days=days)
            return date > cutoff
        except:
            return False
    
    def test_connection(self) -> Dict:
        """Test GitHub API connection"""
        result = self._make_request('/user')
        
        if not result['success']:
            return result
        
        user = result['data']
        return {
            'success': True,
            'data': {
                'login': user['login'],
                'name': user.get('name', ''),
                'email': user.get('email', ''),
                'public_repos': user.get('public_repos', 0)
            }
        }