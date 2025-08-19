#!/usr/bin/env python3
"""
Memory Manager CLI - Interactive tool for managing Claude's memory database
"""

import click
import requests
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import print as rprint
from pathlib import Path

console = Console()
API_URL = "http://localhost:8080"

@click.group()
def cli():
    """Claude Memory Manager - Curate and manage your AI's memories"""
    pass

@cli.command()
def health():
    """Check memory database health and get recommendations"""
    with console.status("[bold green]Analyzing memory health..."):
        try:
            response = requests.get(f"{API_URL}/api/curator/health", timeout=30)
            if response.status_code == 200:
                data = response.json()['data']
                
                # Create summary panel
                summary = f"""
[bold cyan]Memory Database Health Report[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Total Memories: {data.get('total_memories', 0)}
📁 Duplicates: {len(data.get('duplicates', {}).get('exact', []))} exact, {len(data.get('duplicates', {}).get('near', []))} near
🗓️ Stale Memories: {len(data.get('stale_memories', []))}
⚠️ Error Rate: {data.get('error_patterns', {}).get('error_rate', 0):.1%}
                """
                console.print(Panel(summary, title="Summary", border_style="green"))
                
                # Show quality distribution
                quality = data.get('quality_distribution', {})
                quality_table = Table(title="Memory Quality Distribution")
                quality_table.add_column("Quality", style="cyan")
                quality_table.add_column("Count", style="magenta")
                quality_table.add_column("Percentage")
                
                total = sum(quality.values())
                for level, count in quality.items():
                    pct = (count/total*100) if total > 0 else 0
                    quality_table.add_row(level.capitalize(), str(count), f"{pct:.1f}%")
                
                console.print(quality_table)
                
                # Show technology distribution
                tech = data.get('technology_distribution', {})
                if tech:
                    tech_table = Table(title="Top Technologies")
                    tech_table.add_column("Technology", style="cyan")
                    tech_table.add_column("Count", style="magenta")
                    
                    for tech_name, count in list(tech.items())[:5]:
                        tech_table.add_row(tech_name, str(count))
                    
                    console.print(tech_table)
                
                # Show recommendations
                recommendations = data.get('recommendations', [])
                if recommendations:
                    console.print("\n[bold yellow]Recommendations:[/bold yellow]")
                    for i, rec in enumerate(recommendations, 1):
                        console.print(f"  {i}. {rec}")
            else:
                console.print("[red]Failed to get health report[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option('--execute', is_flag=True, help='Actually remove duplicates (default is dry run)')
def deduplicate(execute):
    """Find and remove duplicate memories"""
    dry_run = not execute
    
    with console.status(f"[bold green]{'Analyzing' if dry_run else 'Removing'} duplicates..."):
        try:
            response = requests.post(f"{API_URL}/api/curator/deduplicate", 
                                    json={'dry_run': dry_run})
            
            if response.status_code == 200:
                data = response.json()['data']
                
                if dry_run:
                    console.print(f"[yellow]DRY RUN - No changes made[/yellow]")
                
                console.print(f"Found {data['duplicates_found']} duplicate memories")
                
                if data['duplicate_ids']:
                    console.print("\nSample duplicate IDs:")
                    for dup_id in data['duplicate_ids'][:5]:
                        console.print(f"  • {dup_id}")
                
                if dry_run and data['duplicates_found'] > 0:
                    console.print("\n[cyan]Run with --execute to remove these duplicates[/cyan]")
                elif not dry_run:
                    console.print(f"[green]✓ Removed {data['removed']} duplicates[/green]")
            else:
                console.print("[red]Deduplication failed[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option('--days', default=90, help='Archive memories older than N days')
@click.option('--execute', is_flag=True, help='Actually archive (default is dry run)')
def archive(days, execute):
    """Archive old memories"""
    dry_run = not execute
    
    with console.status(f"[bold green]{'Finding' if dry_run else 'Archiving'} old memories..."):
        try:
            response = requests.post(f"{API_URL}/api/curator/archive",
                                    json={'days': days, 'dry_run': dry_run})
            
            if response.status_code == 200:
                data = response.json()['data']
                
                if dry_run:
                    console.print(f"[yellow]DRY RUN - No changes made[/yellow]")
                
                console.print(f"Found {data['found']} memories older than {days} days")
                
                if data.get('sample'):
                    console.print("\nSample memories to archive:")
                    for mem in data['sample']:
                        console.print(f"  • [{mem['date']}] {mem['title']}")
                
                if dry_run and data['found'] > 0:
                    console.print(f"\n[cyan]Run with --execute to archive these memories[/cyan]")
                elif not dry_run and data['archived'] > 0:
                    console.print(f"[green]✓ Archived {data['archived']} memories to {data['archive_path']}[/green]")
            else:
                console.print("[red]Archival failed[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.argument('memory_ids', nargs=-1, required=True)
@click.option('--title', help='Title for consolidated memory')
def consolidate(memory_ids, title):
    """Consolidate multiple memories into one"""
    memory_list = list(memory_ids)
    
    console.print(f"Consolidating {len(memory_list)} memories...")
    
    try:
        response = requests.post(f"{API_URL}/api/curator/consolidate",
                                json={'memory_ids': memory_list, 'title': title})
        
        if response.status_code == 200:
            data = response.json()['data']
            
            if data['success']:
                console.print(f"[green]✓ Successfully consolidated {data['original_count']} memories[/green]")
                console.print(f"  New memory ID: {data['consolidated_id']}")
                console.print(f"  Title: {data['new_title']}")
            else:
                console.print(f"[red]Consolidation failed: {data.get('error')}[/red]")
        else:
            console.print("[red]Consolidation request failed[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
def analyze():
    """Analyze patterns and insights from memories"""
    with console.status("[bold green]Analyzing memory patterns..."):
        try:
            response = requests.get(f"{API_URL}/api/curator/analyze")
            
            if response.status_code == 200:
                data = response.json()['data']
                
                # Show key insights
                if data.get('key_insights'):
                    console.print("\n[bold cyan]Key Insights:[/bold cyan]")
                    for insight in data['key_insights']:
                        console.print(f"  💡 {insight}")
                
                # Show error patterns
                error_data = data.get('error_patterns', {})
                if error_data.get('common_patterns'):
                    console.print("\n[bold yellow]Common Error Patterns:[/bold yellow]")
                    for pattern in error_data['common_patterns'][:5]:
                        console.print(f"  • {pattern}")
                
                # Show temporal patterns
                temporal = data.get('temporal_patterns', {})
                if temporal:
                    console.print("\n[bold green]Memory Age Distribution:[/bold green]")
                    age_table = Table()
                    age_table.add_column("Period", style="cyan")
                    age_table.add_column("Count", style="magenta")
                    
                    for period, count in temporal.items():
                        age_table.add_row(period.replace('_', ' ').title(), str(count))
                    
                    console.print(age_table)
            else:
                console.print("[red]Analysis failed[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.option('--execute', is_flag=True, help='Actually perform curation (default is dry run)')
def auto_curate(execute):
    """Automatically curate memories based on best practices"""
    dry_run = not execute
    
    with console.status(f"[bold green]{'Planning' if dry_run else 'Performing'} auto-curation..."):
        try:
            response = requests.post(f"{API_URL}/api/curator/auto-curate",
                                    json={'dry_run': dry_run})
            
            if response.status_code == 200:
                data = response.json()['data']
                
                if dry_run:
                    console.print("[yellow]DRY RUN - Showing what would be done:[/yellow]\n")
                else:
                    console.print("[green]Auto-curation complete:[/green]\n")
                
                for action in data['actions_taken']:
                    console.print(f"  ✓ {action}")
                
                console.print(f"\n{data['summary']}")
                
                if dry_run and data['actions_taken']:
                    console.print("\n[cyan]Run with --execute to perform these actions[/cyan]")
            else:
                console.print("[red]Auto-curation failed[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
def search():
    """Interactive memory search"""
    query = click.prompt("Enter search query")
    
    with console.status("[bold green]Searching memories..."):
        try:
            response = requests.post(f"{API_URL}/api/search",
                                    json={'query': query, 'max_results': 10})
            
            if response.status_code == 200:
                data = response.json()['data']
                results = data.get('results', [])
                
                if results:
                    console.print(f"\n[green]Found {len(results)} results:[/green]\n")
                    
                    for i, result in enumerate(results, 1):
                        similarity = result.get('similarity', 0)
                        title = result.get('title', 'Untitled')
                        date = result.get('date', 'Unknown')
                        preview = result.get('preview', '')[:150]
                        
                        # Color code by similarity
                        if similarity > 0.7:
                            color = "green"
                        elif similarity > 0.5:
                            color = "yellow"
                        else:
                            color = "red"
                        
                        console.print(f"[{color}]{i}. [{similarity:.2f}] {title} ({date})[/{color}]")
                        console.print(f"   {preview}...\n")
                else:
                    console.print("[yellow]No results found[/yellow]")
            else:
                console.print("[red]Search failed[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
def stats():
    """Show memory database statistics"""
    with console.status("[bold green]Gathering statistics..."):
        try:
            # Get health data for statistics
            response = requests.get(f"{API_URL}/api/curator/health")
            
            if response.status_code == 200:
                data = response.json()['data']
                
                stats_panel = f"""
[bold cyan]Memory Database Statistics[/bold cyan]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Total Memories: {data.get('total_memories', 0)}
📝 High Quality: {data.get('quality_distribution', {}).get('high', 0)}
📝 Medium Quality: {data.get('quality_distribution', {}).get('medium', 0)}
📝 Low Quality: {data.get('quality_distribution', {}).get('low', 0)}

🔄 Consolidation Opportunities: {len(data.get('consolidation_opportunities', []))}
📁 Duplicate Memories: {len(data.get('duplicates', {}).get('exact', []))}
🗓️ Stale Memories (>90 days): {len(data.get('stale_memories', []))}

⚠️ Error Memories: {data.get('error_patterns', {}).get('total_error_memories', 0)}
⚠️ Error Rate: {data.get('error_patterns', {}).get('error_rate', 0):.1%}
                """
                
                console.print(Panel(stats_panel, border_style="cyan"))
                
                # Show top error types if any
                error_types = data.get('error_patterns', {}).get('error_types', {})
                if error_types:
                    console.print("\n[bold yellow]Error Types:[/bold yellow]")
                    for error_type, count in error_types.items():
                        console.print(f"  • {error_type}: {count}")
            else:
                console.print("[red]Failed to get statistics[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@cli.command()
def interactive():
    """Interactive memory management mode"""
    console.print("[bold cyan]Claude Memory Manager - Interactive Mode[/bold cyan]")
    console.print("Type 'help' for available commands, 'exit' to quit\n")
    
    commands = {
        'health': 'Check memory health',
        'stats': 'Show statistics',
        'search': 'Search memories',
        'dedupe': 'Remove duplicates (dry run)',
        'archive': 'Archive old memories (dry run)',
        'auto': 'Auto-curate (dry run)',
        'help': 'Show this help',
        'exit': 'Exit interactive mode'
    }
    
    while True:
        try:
            command = console.input("[bold green]memory>[/bold green] ").strip().lower()
            
            if command == 'exit':
                console.print("Goodbye!")
                break
            elif command == 'help':
                console.print("\n[bold]Available commands:[/bold]")
                for cmd, desc in commands.items():
                    console.print(f"  {cmd:10} - {desc}")
                console.print()
            elif command == 'health':
                ctx = cli.make_context('', ['health'])
                cli.invoke(ctx)
            elif command == 'stats':
                ctx = cli.make_context('', ['stats'])
                cli.invoke(ctx)
            elif command == 'search':
                ctx = cli.make_context('', ['search'])
                cli.invoke(ctx)
            elif command == 'dedupe':
                ctx = cli.make_context('', ['deduplicate'])
                cli.invoke(ctx)
            elif command == 'archive':
                ctx = cli.make_context('', ['archive'])
                cli.invoke(ctx)
            elif command == 'auto':
                ctx = cli.make_context('', ['auto-curate'])
                cli.invoke(ctx)
            elif command:
                console.print(f"[red]Unknown command: {command}[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == '__main__':
    cli()