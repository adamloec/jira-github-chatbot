import click
import requests
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def jira():
    """JIRA-related commands"""
    pass

@jira.command()
@click.option('--port', default=8000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def test(port, host):
    """Test JIRA connection"""
    try:
        url = f"http://{host}:{port}/api/jira/test-connection"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            console.print("[green]JIRA connection successful![/green]")
            console.print(f"Connected as: {data['user']['display_name']}")
            console.print(f"Email: {data['user']['email']}")
        else:
            error_data = response.json()
            console.print(f"[red]JIRA connection failed:[/red] {error_data.get('error', 'Unknown error')}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

@jira.command()
@click.argument('username')
@click.option('--port', default=8000, help='Server port')
@click.option('--host', default='localhost', help='Server host')
def activity(username, port, host):
    """Get comprehensive activity for a user"""
    try:
        url = f"http://{host}:{port}/api/jira/user/{username}/activity"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Display user info
            user = data['user']
            console.print(f"[bold cyan]JIRA Activity for {user['display_name']}[/bold cyan]")
            console.print()
            
            # Display summary
            summary = data['summary']
            console.print("[bold]Summary:[/bold]")
            console.print(f"  Total assigned issues: {summary['total_assigned_issues']}")
            console.print(f"  Recent activity (7 days): {summary['recent_activity_count']}")
            console.print()
            
            # Status breakdown
            if summary['status_breakdown']:
                console.print("[bold]Status Breakdown:[/bold]")
                for status, count in summary['status_breakdown'].items():
                    console.print(f"  {status}: {count}")
                console.print()
            
            # Current issues
            if data['current_issues']:
                table = Table(title="Current Issues")
                table.add_column("Key", style="cyan")
                table.add_column("Summary", style="white")
                table.add_column("Status", style="green")
                table.add_column("Priority", style="yellow")
                
                for issue in data['current_issues']:
                    table.add_row(
                        issue['key'],
                        issue['summary'][:50] + "..." if len(issue['summary']) > 50 else issue['summary'],
                        issue['status'],
                        issue['priority']
                    )
                
                console.print(table)
            else:
                console.print("[yellow]No current issues found[/yellow]")
        
        else:
            error_data = response.json()
            console.print(f"[red]Error:[/red] {error_data.get('error', 'Unknown error')}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")