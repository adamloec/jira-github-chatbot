#!/usr/bin/env python3

import click
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich import print as rprint
import sys
import os
from jira_cli import jira

# Rich console for beautiful output
console = Console()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """JIRA-GitHub Chatbot CLI"""
    pass

# Add JIRA commands
cli.add_command(jira)

@cli.command()
@click.option('--port', default=8000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def test(port, host):
    """Test connection to the backend server"""
    try:
        url = f"http://{host}:{port}/health"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        console.print("[green]Backend connection successful![/green]")
        console.print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        console.print("[red]Backend connection failed![/red]")
        console.print("Make sure the server is running with: uv run src/app.py")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--port', default=8000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def chat(port, host):
    """Start interactive chat mode"""
    console.print("[blue]JIRA-GitHub Chatbot CLI[/blue]")
    console.print("[dim]Type 'exit' to quit[/dim]\n")
    
    base_url = f"http://{host}:{port}"
    
    # Test connection first
    try:
        requests.get(f"{base_url}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        console.print("[red]Cannot connect to server![/red]")
        console.print("Make sure the server is running with: uv run src/app.py")
        return
    
    while True:
        try:
            query = Prompt.ask("[cyan]You[/cyan]")
            
            if query.lower() in ['exit', 'quit', 'bye']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            # Send query to backend
            response = requests.post(
                f"{base_url}/api/chat",
                json={'query': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"[green]Bot:[/green] {data['response']}")
            else:
                console.print(f"[red]Error:[/red] {response.status_code}")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")

@cli.command()
@click.argument('query')
@click.option('--port', default=8000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def ask(query, port, host):
    """Ask a single question"""
    try:
        url = f"http://{host}:{port}/api/chat"
        response = requests.post(
            url,
            json={'query': query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            console.print(f"[blue]Query:[/blue] {query}")
            console.print(f"[green]Response:[/green] {data['response']}")
        else:
            console.print(f"[red]Error:[/red] {response.status_code}")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

@cli.command()
@click.argument('username')
@click.option('--port', default=8000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def github(username, port, host):
    """Get GitHub activity for a user"""
    try:
        url = f"http://{host}:{port}/api/github/user/{username}/activity"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Display user info
            user = data['user']
            console.print(f"[bold cyan]GitHub Activity for {user['name'] or user['username']}[/bold cyan]")
            if user['company']:
                console.print(f"Company: {user['company']}")
            console.print(f"Public repos: {user['public_repos']}")
            console.print()
            
            # Display summary
            summary = data['summary']
            console.print("[bold]Summary:[/bold]")
            console.print(f"  Total repositories: {summary['total_repositories']}")
            console.print(f"  Total commits: {summary['total_commits']}")
            console.print(f"  Total pull requests: {summary['total_pull_requests']}")
            console.print(f"  Recent commits (7 days): {summary['recent_commits_7d']}")
            console.print(f"  Recent PRs (7 days): {summary['recent_prs_7d']}")
            console.print()
            
            # Recent commits
            if data['recent_commits']:
                console.print("[bold]Recent Commits:[/bold]")
                for commit in data['recent_commits'][:5]:
                    console.print(f"  {commit['sha']} - {commit['repository']}")
                    console.print(f"    {commit['message']}")
                console.print()
            
            # Repositories
            if data['repositories']:
                console.print("[bold]Repositories:[/bold]")
                for repo in data['repositories'][:5]:
                    console.print(f"  {repo['name']} ({repo['language']})")
                    if repo['description']:
                        console.print(f"    {repo['description']}")
                console.print()
            
        else:
            error_data = response.json()
            console.print(f"[red]Error:[/red] {error_data.get('error', 'Unknown error')}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

if __name__ == '__main__':
    cli()