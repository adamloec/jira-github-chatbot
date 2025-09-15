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