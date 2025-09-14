from typing import Dict, List, Any
from .jira_service import JiraService
from .github_service import GitHubService
import logging

logger = logging.getLogger(__name__)

# Initialize services
jira_service = JiraService()
github_service = GitHubService()

# Two simple tools for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_jira_activity",
            "description": "Get JIRA activity for a user including current issues, recent activity, and status breakdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username or email of the person to look up in JIRA"
                    }
                },
                "required": ["username"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_github_activity",
            "description": "Get GitHub activity for a user including recent commits, repositories, and pull requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username to look up"
                    }
                },
                "required": ["username"]
            }
        }
    }
]

class ToolExecutor:
    """Execute OpenAI function calls"""
    
    def __init__(self):
        self.jira = jira_service
        self.github = github_service
    
    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict:
        """Execute a function call from OpenAI"""
        try:
            if function_name == "get_jira_activity":
                return self.jira.get_user_activity(arguments['username'])
            
            elif function_name == "get_github_activity":
                return self.github.get_user_activity(arguments['username'])
            
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