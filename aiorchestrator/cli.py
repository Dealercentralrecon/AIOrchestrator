import json
import sys

import click

from .orchestrator import orchestrator


@click.group()
def cli():
    """AI Orchestrator Command Line Interface"""
    pass


@cli.command()
def start():
    """Start core services"""
    from .core import initialize

    initialize()
    click.echo("Services initialized")


@cli.command()
@click.option("--task", help="Natural language task description")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def execute(task, verbose):
    """Execute a task through the orchestrator"""
    try:
        result = orchestrator.execute_task(task)
        if verbose:
            click.echo(f"Detailed results:\n{json.dumps(result, indent=2)}")
        else:
            click.echo(f"Success: {result['summary']}")
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
