# JIRA-GitHub Chatbot

AI-powered chatbot that answers questions about team member activities using JIRA and GitHub APIs.

- Using gpt-3.5-turbo

## Prerequisites

- UV package manager
- JIRA API token
- GitHub personal access token
- OpenAI API key

## Installation

```bash
git clone https://github.com/adamloec/jira-github-chatbot
cd jira-github-chatbot
uv sync
```

## Configuration

Create `.env` file:
```bash
# API Configuration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your-jira-api-token
GITHUB_TOKEN=your-github-personal-access-token
OPENAI_API_KEY=your-openai-api-key
PORT=8000
```

Edit `config/users.json` with your team members:
```json
{
  "john": {
    "name": "John Doe",
    "email": "john@company.com",
    "github": "johndoe"
  }
}
```

## Usage

### Start Server
```bash
uv run src/app.py
```

### Web Interface
Open http://localhost:8000

### CLI Commands
```bash
# Interactive chat
uv run src/cli/main.py chat

# Single question
uv run src/cli/main.py ask "What is John working on?"

# Test connections
uv run src/cli/main.py jira test
uv run src/cli/main.py github test

# Get activity
uv run src/cli/main.py jira activity john@company.com
uv run src/cli/main.py github activity johndoe
```

## API

- Health
  - `GET /health`
    - 200 OK:
      ```json
      {
        "status": "OK",
        "message": "Server is running",
        "timestamp": "2025-01-01T12:34:56.789012"
      }
      ```

- General API
  - `GET /api/test`
    - 200 OK:
      ```json
      { "message": "API is working!" }
      ```
  - `GET /api/status`
    - 200 OK:
      ```json
      {
        "api_status": "operational",
        "chatbot_configured": true,
        "endpoints": [
          {"path": "/test", "method": "GET"},
          {"path": "/chat", "method": "POST"},
          {"path": "/status", "method": "GET"}
        ]
      }
      ```
  - `POST /api/chat`
    - Request:
      ```json
      { "query": "What is John working on?" }
      ```
    - 200 OK:
      ```json
      {
        "query": "What is John working on?",
        "response": "Summary across JIRA and GitHub...",
        "tools_used": ["get_jira_activity", "get_github_activity"],
        "timestamp": "2025-01-01T12:34:56.789012",
        "status": "success"
      }
      ```
    - 400/500 error:
      ```json
      {
        "error": "Error message",
        "query": "What is John working on?",
        "timestamp": "2025-01-01T12:34:56.789012",
        "status": "error"
      }
      ```

- JIRA
  - `GET /api/jira/test-connection`
    - 200 OK:
      ```json
      {
        "status": "success",
        "message": "JIRA connection successful",
        "user": {
          "display_name": "Your Name",
          "email": "you@company.com",
          "account_id": "abc123"
        }
      }
      ```
  - `GET /api/jira/user/<username>/activity`
    - Path param `username`: email, display name, or mapped key (see `config/users.json`)
    - 200 OK:
      ```json
      {
        "user": {
          "username": "john@company.com",
          "display_name": "John Doe",
          "account_id": "abc123"
        },
        "summary": {
          "total_assigned_issues": 3,
          "recent_activity_count": 5,
          "status_breakdown": { "In Progress": 2, "To Do": 1 }
        },
        "current_issues": [ /* up to 10 */ ],
        "recent_activity": [ /* up to 5 */ ]
      }
      ```
    - 400 error:
      ```json
      { "error": "User 'john' not found in JIRA. Please check the username or email address." }
      ```

- GitHub
  - `GET /api/github/test-connection`
    - 200 OK:
      ```json
      {
        "status": "success",
        "message": "GitHub connection successful",
        "user": {
          "login": "your-login",
          "name": "Your Name",
          "email": "you@example.com",
          "public_repos": 12
        }
      }
      ```
  - `GET /api/github/user/<username>/activity`
    - Path param `username`: GitHub username or mapped key (see `config/users.json`)
    - 200 OK:
      ```json
      {
        "user": {
          "username": "johndoe",
          "name": "John Doe",
          "company": "ACME",
          "public_repos": 42
        },
        "summary": {
          "total_repositories": 10,
          "total_commits": 25,
          "total_pull_requests": 3,
          "recent_commits_7d": 5,
          "recent_prs_7d": 1
        },
        "recent_commits": [ /* up to 10 */ ],
        "repositories": [ /* up to 10 */ ],
        "pull_requests": [ /* up to 5 */ ]
      }
      ```
    - 400 error:
      ```json
      { "error": "GitHub user 'foo' not found. Please check the username." }
      ```