import requests
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class JiraService:
    """JIRA API client for fetching user activity"""
    
    def __init__(self):
        self.base_url = os.getenv('JIRA_BASE_URL')
        self.email = os.getenv('JIRA_EMAIL')
        self.api_token = os.getenv('JIRA_API_TOKEN')
        
        if not all([self.base_url, self.email, self.api_token]):
            logger.warning("JIRA configuration incomplete. Check environment variables.")
        
        self.session = requests.Session()
        self.session.auth = (self.email, self.api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to JIRA API"""
        try:
            url = f"{self.base_url}/rest/api/3{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    error_msg = "Authentication failed. Check JIRA credentials."
                elif e.response.status_code == 404:
                    error_msg = "User not found in JIRA."
                else:
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get('errorMessages', [error_msg])[0]
                    except:
                        pass
            
            logger.error(f"JIRA API error: {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def get_user_activity(self, username: str) -> Dict:
        """Get JIRA activity for a user"""
        try:
            # Find user
            user_search = self._find_user(username)
            if not user_search['success']:
                return user_search
            
            found_user = user_search['data']
            if not found_user:
                return {
                    'success': False,
                    'error': f"User '{username}' not found in JIRA. Please check the username or email address.",
                    'error_type': 'user_not_found'
                }
            
            user_id = found_user['account_id']
            user_display_name = found_user['display_name']
            
            # Get assigned issues
            current_issues = self._get_assigned_issues(user_id)
            recent_activity = self._get_recent_activity(user_id)
            
            # If no issues found at all, be explicit
            if not current_issues and not recent_activity:
                return {
                    'success': True,
                    'data': {
                        'user': {
                            'username': username,
                            'display_name': user_display_name,
                            'account_id': user_id
                        },
                        'summary': {
                            'total_assigned_issues': 0,
                            'recent_activity_count': 0,
                            'status_breakdown': {}
                        },
                        'current_issues': [],
                        'recent_activity': [],
                        'message': f"{user_display_name} has no assigned issues or recent activity in JIRA."
                    }
                }
            
            # Status breakdown
            status_counts = {}
            for issue in current_issues:
                status = issue['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'success': True,
                'data': {
                    'user': {
                        'username': username,
                        'display_name': user_display_name,
                        'account_id': user_id
                    },
                    'summary': {
                        'total_assigned_issues': len(current_issues),
                        'recent_activity_count': len(recent_activity),
                        'status_breakdown': status_counts
                    },
                    'current_issues': current_issues[:10],
                    'recent_activity': recent_activity[:5]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting JIRA user activity: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to get JIRA activity for '{username}': {str(e)}",
                'error_type': 'api_error'
            }
    
    def _find_user(self, username: str) -> Dict:
        """Find user by username, email, or display name"""
        result = self._make_request('/user/search', {'query': username})
        
        if not result['success']:
            return result
        
        users = result['data']
        if not users:
            return {'success': True, 'data': None}
        
        # Find exact match or best match
        for user in users:
            if (user.get('emailAddress', '').lower() == username.lower() or
                user.get('displayName', '').lower() == username.lower()):
                return {
                    'success': True,
                    'data': {
                        'account_id': user['accountId'],
                        'display_name': user['displayName'],
                        'email': user.get('emailAddress', ''),
                        'active': user['active']
                    }
                }
        
        # Return first active user
        for user in users:
            if user['active']:
                return {
                    'success': True,
                    'data': {
                        'account_id': user['accountId'],
                        'display_name': user['displayName'],
                        'email': user.get('emailAddress', ''),
                        'active': user['active']
                    }
                }
        
        return {'success': True, 'data': None}
    
    def _get_assigned_issues(self, user_id: str) -> List[Dict]:
        """Get issues assigned to user"""
        jql = f'assignee = "{user_id}" AND status != Done ORDER BY updated DESC'
        
        params = {
            'jql': jql,
            'maxResults': 20,
            'fields': 'key,summary,status,priority,updated,created'
        }
        
        result = self._make_request('/search', params)
        
        if not result['success']:
            return []
        
        issues = []
        for issue in result['data'].get('issues', []):
            fields = issue['fields']
            issues.append({
                'key': issue['key'],
                'summary': fields['summary'],
                'status': fields['status']['name'],
                'priority': fields.get('priority', {}).get('name', 'None'),
                'updated': fields['updated'],
                'created': fields['created']
            })
        
        return issues
    
    def _get_recent_activity(self, user_id: str) -> List[Dict]:
        """Get recent activity for user (last 7 days)"""
        jql = f'assignee = "{user_id}" AND updated >= -7d ORDER BY updated DESC'
        
        params = {
            'jql': jql,
            'maxResults': 10,
            'fields': 'key,summary,status,updated'
        }
        
        result = self._make_request('/search', params)
        
        if not result['success']:
            return []
        
        activity = []
        for issue in result['data'].get('issues', []):
            fields = issue['fields']
            activity.append({
                'key': issue['key'],
                'summary': fields['summary'],
                'status': fields['status']['name'],
                'updated': fields['updated']
            })
        
        return activity
    
    def test_connection(self) -> Dict:
        """Test JIRA API connection"""
        result = self._make_request('/myself')
        
        if not result['success']:
            return result
        
        user = result['data']
        return {
            'success': True,
            'data': {
                'display_name': user['displayName'],
                'email': user['emailAddress'],
                'account_id': user['accountId']
            }
        }