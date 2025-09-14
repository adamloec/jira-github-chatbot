from typing import Dict, List, Any
from .jira_service import JiraService
from .github_service import GitHubService
from .user_mapping import UserMapping
import logging

logger = logging.getLogger(__name__)

# Initialize services
jira_service = JiraService()
github_service = GitHubService()
user_mapping = UserMapping()

# Updated tools that handle name mapping
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_jira_activity",
            "description": "Get JIRA activity for a user. Can use person's name (e.g., 'John', 'Sarah'), email, or display name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Name, username, or email of the person to look up in JIRA"
                    }
                },
                "required": ["identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_github_activity",
            "description": "Get GitHub activity for a user. Can use person's name (e.g., 'John', 'Sarah') or GitHub username.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Name or GitHub username of the person to look up"
                    }
                },
                "required": ["identifier"]
            }
        }
    }
]


class ToolExecutor:
    """Execute OpenAI function calls with user mapping"""
    
    def __init__(self):
        self.jira = jira_service
        self.github = github_service
        self.mapping = user_mapping
    
    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict:
        """Execute a function call from OpenAI"""
        try:
            identifier = arguments['identifier']
            
            if function_name == "get_jira_activity":
                jira_id = self.mapping.get_jira_identifier(identifier)
                if not jira_id:
                    return {
                        'success': False,
                        'error': f"Could not find JIRA information for '{identifier}'. Available users: {', '.join(self.mapping.list_users())}",
                        'error_type': 'user_not_found'
                    }
                return self.jira.get_user_activity(jira_id)
            
            elif function_name == "get_github_activity":
                github_id = self.mapping.get_github_identifier(identifier)
                if not github_id:
                    return {
                        'success': False,
                        'error': f"Could not find GitHub information for '{identifier}'. Available users: {', '.join(self.mapping.list_users())}",
                        'error_type': 'user_not_found'
                    }
                return self.github.get_user_activity(github_id)
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown function: {function_name}'
                }
        
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {str(e)}")
            return {
                'success': False,
                'error': f'Function execution failed: {str(e)}'
            }
    
    def get_available_tools(self) -> List[Dict]:
        """Get list of available tools for OpenAI"""
        return TOOLS