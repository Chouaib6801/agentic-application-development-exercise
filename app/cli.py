"""Command-line interface for the agentic application."""

from typing import Optional
import typer

app = typer.Typer(help="Agentic application CLI")


@app.command()
def submit(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text prompt"),
    image: Optional[str] = typer.Option(None, "--image", "-i", help="Path to image file"),
    context_dir: Optional[str] = typer.Option(None, "--context-dir", "-c", help="Context directory path"),
):
    """Submit a new job for processing."""
    from app.db import init_db, create_job
    
    if not text and not image:
        typer.echo("Error: At least --text or --image is required", err=True)
        raise typer.Exit(1)
    
    # Build payload
    payload = {}
    if text:
        payload["text"] = text
    if image:
        payload["image"] = image
    if context_dir:
        payload["context_dir"] = context_dir
    
    db_path = init_db()
    typer.echo(f"Using DB: {db_path}")
    
    job_id = create_job(payload)
    typer.echo(job_id)


@app.command()
def status(job_id: str = typer.Argument(..., help="The job ID to check")):
    """Check the status of a job."""
    from app.db import init_db, get_job
    
    db_path = init_db()
    typer.echo(f"Using DB: {db_path}")
    
    job = get_job(job_id)
    
    if job is None:
        typer.echo("Job not found", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"Status: {job['status']}")
    
    if job.get("result_path"):
        typer.echo(f"Result: {job['result_path']}")
    
    if job.get("error"):
        typer.echo(f"Error: {job['error']}")


@app.command()
def worker():
    """Run the worker to process pending jobs."""
    from app.worker import run_worker
    
    typer.echo("Starting worker...")
    run_worker()


if __name__ == "__main__":
    app()
