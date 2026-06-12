# Orion Workshop Guide

This guide maps each starter TODO to the workshop phase where attendees implement it. Work through the phases in order and run the verification commands after each section before moving on.

## Phase 1 — Configuration Layer

### File
`app/config/llm.py`

### TODO
Implement `get_llm()` so Orion can create the right LangChain chat model from environment settings.

### Hints

- Read `settings.LLM_PROVIDER` and `settings.LLM_MODEL`.
- Vertex AI is the default path for this workshop:
  - provider: `vertexai`
  - class: `ChatVertexAI`
  - use `project=settings.GOOGLE_CLOUD_PROJECT`
  - use `location=settings.GOOGLE_CLOUD_LOCATION`
- Keep support for the other providers listed in the starter comments.
- Set `temperature=0` for every model.
- Raise a helpful `ValueError` for unsupported providers.

### Verification

```bash
python -c "from app.config.settings import settings; print(settings.LLM_PROVIDER)"
python -c "from app.config.llm import get_llm; llm = get_llm(); print(type(llm).__name__)"
```

Expected direction:
- the first command prints `vertexai`
- the second command prints a LangChain chat model class such as `ChatVertexAI`

## Phase 2 — Agent Tools

### File
`app/agent/tools.py`

### TODOs

1. Implement `get_dataset_info()`
2. Implement `python_repl(code: str)`

### Hints

- Keep the module-level `df = pd.read_csv(settings.DATA_PATH)` as-is.
- `get_dataset_info()` should return:
  - dataset shape
  - column names and dtypes
  - first 3 rows
- `python_repl()` should execute code with these already available:
  - `df`
  - `pd`
  - `np`
- Capture stdout with `io.StringIO` and `contextlib.redirect_stdout`.
- Return exceptions as strings prefixed with `ERROR: ` so the agent can self-correct.
- Enforce the 30-second timeout with a thread-based approach.

### Verification

```bash
python -c "from app.agent.tools import get_dataset_info; print(get_dataset_info.invoke({}))"
python -c "from app.agent.tools import python_repl; print(python_repl.invoke({'code': 'print(df.shape)'}))"
```

Expected direction:
- the dataset info command prints schema and sample rows
- the REPL command prints `(1000, 13)`

## Phase 3 — Prompt Design

### File
`app/agent/prompts.py`

### TODO
Write the `SYSTEM_PROMPT` string that governs Orion's behavior.

### Hints

Make sure the prompt tells the agent to:

- act as a data analyst assistant
- use the already-loaded DataFrame named `df`
- always call `get_dataset_info` first
- use `python_repl` for analysis code
- self-correct up to 3 times on errors
- return concise, human-readable answers
- format currency and large numbers clearly

### Verification

```bash
python -c "from app.agent.prompts import SYSTEM_PROMPT; print(SYSTEM_PROMPT)"
```

Expected direction:
- the printed prompt should clearly mention the tool order and self-correction behavior

## Phase 3 — Agent Core

### File
`app/agent/agent.py`

### TODO
Implement `run_agent(question: str, session_id: str) -> dict`.

### Hints

- Import and initialize the LLM once at module level.
- Reuse the `tools` list and `SYSTEM_PROMPT`.
- Build the executor with `langgraph.prebuilt.create_react_agent`.
- Generate a new session ID with `uuid.uuid4()` when one is not provided.
- Return a dictionary with:
  - `answer`
  - `session_id`
  - `steps`
  - `model_used`
- `steps` should be a non-empty list built from tool calls and tool results.

### Verification

```bash
python -c "from app.agent.agent import run_agent; result = run_agent('How many orders are in the dataset?', ''); print(result['answer']); print(result['steps'])"
```

Expected direction:
- the answer should say there are 1000 orders
- `steps` should show at least one tool call and one tool result

## Final API Verification

After all TODOs are complete:

```bash
uvicorn app.main:app --reload --port 8080
curl http://localhost:8080/health
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"question":"Which region generated the most revenue?"}'
```

Expected direction:
- `/health` returns status `ok`
- `/analyze` returns an answer, session ID, reasoning steps, and model name

## If You Want a Quick Failure Check First

Before implementing anything, you can confirm the starter is truly incomplete:

```bash
python -c "from app.agent.agent import run_agent; run_agent('test', '')"
```

Expected result:
- a `NotImplementedError` pointing to one of the stubbed workshop files
