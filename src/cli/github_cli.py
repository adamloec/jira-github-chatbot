import click
import requests
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def github():
    """GitHub-related commands"""
    pass

@github.command()
@click.option('--port', default=5000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def test(port, host):
    """Test GitHub connection"""
    try:
        url = f"http://{host}:{port}/api/github/test-connection"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            console.print("[green]GitHub connection successful![/green]")
            console.print(f"Connected as: {data['user']['login']}")
            if data['user']['name']:
                console.print(f"Name: {data['user']['name']}")
            console.print(f"Public repos: {data['user']['public_repos']}")
        else:
            error_data = response.json()
            console.print(f"[red]GitHub connection failed:[/red] {error_data.get('error', 'Unknown error')}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

@github.command()
@click.argument('username')
@click.option('--port', default=5000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def activity(username, port, host):
    """Get comprehensive GitHub activity for a user"""
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
                    console.print(f"  [cyan]{commit['sha']}[/cyan] - {commit['repository']}")
                    console.print(f"    {commit['message']}")
                console.print()
            
            # Active repositories
            if data['repositories']:
                table = Table(title="Active Repositories")
                table.add_column("Name", style="cyan")
                table.add_column("Language", style="yellow")
                table.add_column("Description", style="white")
                table.add_column("Updated", style="green")
                
                for repo in data['repositories'][:5]:
                    table.add_row(
                        repo['name'],
                        repo['language'],
                        repo['description'][:50] + "..." if len(repo['description']) > 50 else repo['description'],
                        repo['updated_at'][:10]  # Just the date part
                    )
                
                console.print(table)
            
            # Pull requests
            if data['pull_requests']:
                console.print()
                console.print("[bold]Recent Pull Requests:[/bold]")
                for pr in data['pull_requests'][:3]:
                    status_color = "green" if pr['state'] == 'open' else "red"
                    console.print(f"  [cyan]#{pr['number']}[/cyan] [{status_color}]{pr['state']}[/{status_color}] - {pr['repository']}")
                    console.print(f"    {pr['title'][:80]}")
        
        else:
            error_data = response.json()
            console.print(f"[red]Error:[/red] {error_data.get('error', 'Unknown error')}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")