# Orion Starter

This is the workshop starter repo for Orion, an AI data analyst agent built with FastAPI, LangChain, LangGraph, and Vertex AI. The backend scaffold is in place, but four core files are intentionally stubbed so attendees can implement the agent step by step.

## What You Will Build

By the end of the workshop, this repo will:

- initialize a model through a provider-aware `get_llm()` factory
- expose dataset analysis tools for the agent
- define Orion's system prompt
- run a LangGraph ReAct agent behind a FastAPI API

## Workshop Scope

This starter is backend-only on purpose. The frontend is not included here so the workshop can stay focused on agent architecture, tools, tracing, and deployment.

## Prerequisites

- Python 3.12
- A GCP project with Vertex AI enabled
- Application Default Credentials for local Vertex AI access
- A LangSmith account and API key

## Local Setup

1. Create and activate a virtual environment:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your local environment file:
   ```bash
   cp .env.example .env
   ```
4. Update `.env` with your project-specific settings:
   - `LLM_PROVIDER=vertexai`
   - `LLM_MODEL=gemini-2.5-flash`
   - `GOOGLE_CLOUD_PROJECT=<your-project-id>`
   - `GOOGLE_CLOUD_LOCATION=us-central1`
   - `GOOGLE_GENAI_USE_VERTEXAI=true`
   - `LANGCHAIN_API_KEY=<your-langsmith-key>`
5. Authenticate for local Vertex AI access:
   ```bash
   gcloud auth application-default login
   ```

## Workshop Files to Implement

These files are intentionally incomplete:

- `app/config/llm.py`
- `app/agent/tools.py`
- `app/agent/prompts.py`
- `app/agent/agent.py`

Use [WORKSHOP.md](/home/osen/projects/orion-starter/WORKSHOP.md) as your guide. It maps each TODO to a workshop phase, includes hints, and gives you verification commands after every step.

## Run the Starter

Once you have implemented the TODOs, start the API with:

```bash
uvicorn app.main:app --reload --port 8080
```

Then verify:

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"question":"How many orders are in the dataset?"}'
```

## Deployment Note

For production deployment, Orion runs on Cloud Run using a service account for Vertex AI authentication. `GOOGLE_API_KEY` is not needed in Cloud Run when `LLM_PROVIDER=vertexai`.
