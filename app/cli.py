"""Command-line interface for the agentic application."""

import typer

app = typer.Typer(help="Agentic application CLI")


@app.command()
def submit(prompt: str = typer.Argument(..., help="The prompt to process")):
    """Submit a new job for processing."""
    from app.db import create_job
    
    job_id = create_job(prompt)
    typer.echo(f"Job submitted: {job_id}")


@app.command()
def status(job_id: str = typer.Argument(..., help="The job ID to check")):
    """Check the status of a job."""
    from app.db import get_job
    
    job = get_job(job_id)
    if job:
        typer.echo(f"Status: {job['status']}")
        if job.get("result"):
            typer.echo(f"Result: {job['result']}")
    else:
        typer.echo("Job not found", err=True)
        raise typer.Exit(1)


@app.command()
def worker():
    """Run the worker to process pending jobs."""
    from app.worker import run_worker
    
    typer.echo("Starting worker...")
    run_worker()


if __name__ == "__main__":
    app()

