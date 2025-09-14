import os
import json
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class UserMapping:
    """Simple user mapping for demo purposes"""
    
    def __init__(self):
        self.mapping_file = os.getenv('USER_MAPPING_FILE', 'config/users.json')
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, Dict]:
        """Load user mapping from file"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default mapping if file doesn't exist
                default_users = {
                    "john": {
                        "name": "John Doe",
                        "email": "john@company.com",
                        "github": "johndoe"
                    },
                    "sarah": {
                        "name": "Sarah Smith", 
                        "email": "sarah@company.com",
                        "github": "sarahsmith"
                    },
                    "mike": {
                        "name": "Mike Johnson",
                        "email": "mike@company.com", 
                        "github": "mikejohnson"
                    }
                }
                self._save_users(default_users)
                return default_users
        except Exception as e:
            logger.error(f"Error loading user mapping: {e}")
            return {}
    
    def _save_users(self, users: Dict):
        """Save users to file"""
        try:
            os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)
            with open(self.mapping_file, 'w') as f:
                json.dump(users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user mapping: {e}")
    
    def find_user(self, identifier: str) -> Optional[Dict]:
        """Find user by name, email, or key"""
        identifier = identifier.lower().strip()
        
        # Direct key match
        if identifier in self.users:
            return self.users[identifier]
        
        # Search by name or email
        for user_data in self.users.values():
            if (identifier == user_data.get('name', '').lower() or
                identifier == user_data.get('email', '').lower() or
                identifier in user_data.get('name', '').lower()):
                return user_data
        
        return None
    
    def get_jira_identifier(self, identifier: str) -> Optional[str]:
        """Get JIRA identifier (email) for a user"""
        user = self.find_user(identifier)
        return user.get('email') if user else None
    
    def get_github_identifier(self, identifier: str) -> Optional[str]:
        """Get GitHub username for a user"""
        user = self.find_user(identifier)
        return user.get('github') if user else None
    
    def list_users(self) -> List[str]:
        """List all available users"""
        return [f"{key}: {data['name']}" for key, data in self.users.items()]