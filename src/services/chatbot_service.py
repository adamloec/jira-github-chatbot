import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from .ai_tools import ToolExecutor, TOOLS

logger = logging.getLogger(__name__)


class ChatbotService:
    """OpenAI-powered chatbot with JIRA and GitHub tools"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OpenAI API key not found. Check OPENAI_API_KEY environment variable.")
            return
        
        self.client = OpenAI(api_key=self.api_key)
        self.tool_executor = ToolExecutor()
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """Process user message and return response"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'OpenAI API key not configured'
                }
            
            # Create messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant that can answer questions about team member activities using JIRA and GitHub data.

You have access to two tools:
- get_jira_activity: Get JIRA issues, tasks, and recent activity for a user
- get_github_activity: Get GitHub commits, repositories, and pull requests for a user

IMPORTANT TOOL USAGE STRATEGY:
- For BROAD questions like "What is [name] working on?", "Show me [name]'s recent activity", or "What has [name] been doing?" → ALWAYS call BOTH tools to get a complete picture
- For SPECIFIC questions like "What JIRA tickets does [name] have?" → Call only get_jira_activity
- For SPECIFIC questions like "What repos has [name] worked on?" → Call only get_github_activity

When you have data from both tools, provide a comprehensive summary that covers:
1. JIRA work (current issues, recent activity)
2. GitHub work (recent commits, repositories, pull requests)
3. A brief overall assessment of their activity level

IMPORTANT ERROR HANDLING:
- If error_type is "user_not_found", clearly tell the user that the person was not found
- If error_type is "api_error", explain there was a technical issue
- If a user has no activity, mention this clearly
- Don't make up or hallucinate any information

Be helpful and provide comprehensive answers for broad questions."""
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
            
            # Call OpenAI with tools
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            
            # Check if the model wants to call tools
            if message.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Executing tool: {function_name} with args: {arguments}")
                    
                    # Execute the tool
                    result = self.tool_executor.execute_function(function_name, arguments)
                    
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": json.dumps(result)
                    })
                
                # Add tool call and results to conversation
                messages.append(message)
                messages.extend(tool_results)
                
                # Get final response with tool results
                final_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                final_message = final_response.choices[0].message.content
            else:
                # No tools needed, use direct response
                final_message = message.content
            
            return {
                'success': True,
                'response': final_message,
                'tools_used': [call.function.name for call in (message.tool_calls or [])]
            }
            
        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to process message: {str(e)}"
            }