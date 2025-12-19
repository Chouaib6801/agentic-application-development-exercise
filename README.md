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

### 5. Check job status

```bash
python main.py status <job_id>
```

## Project Structure

```
├── main.py              # Entry point
├── data/                # SQLite database (auto-created)
├── outputs/             # Job results
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
