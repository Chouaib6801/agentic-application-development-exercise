# Agentic Application Development Exercise

A minimal agentic application with SQLite job queue and LLM integration.

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Submit a job

```bash
python main.py submit --text "What is the capital of France?"
```

With optional image and context directory:

```bash
python main.py submit --text "Describe this" --image path/to/image.png --context-dir ./docs
```

### 4. Run the worker

```bash
python main.py worker
```

The worker will:
- Continuously poll for pending jobs
- Process each job and generate `outputs/<job_id>/report.md`
- Write logs to `outputs/<job_id>/run.log`
- Update job status (RUNNING → DONE or FAILED)

Press `Ctrl+C` for graceful shutdown.

### 5. Check job status

```bash
python main.py status <job_id>
```

## Project Structure

```
├── main.py              # Entry point
├── data/                # SQLite database (auto-created)
│   └── jobs.db
├── outputs/             # Job results (auto-created)
│   └── <job_id>/
│       ├── report.md    # Generated report
│       └── run.log      # Processing log
├── app/
│   ├── cli.py           # Typer CLI commands
│   ├── db.py            # SQLite job queue
│   ├── worker.py        # Job processor
│   ├── agent.py         # Agent orchestration
│   ├── llm.py           # OpenAI API client
│   ├── context.py       # Conversation context
│   └── tools/
│       └── wikipedia.py # Wikipedia search tool
```

## Job Lifecycle

1. **PENDING** - Job created via `submit`
2. **RUNNING** - Worker claimed the job
3. **DONE** - Processing completed, `result_path` set
4. **FAILED** - Error occurred, `error` field set
