# Orion — AI Data Analyst Agent — Master Project Documentation

## Overview

Orion is a full-stack, production-grade AI data analyst agent. Users upload any CSV file
and ask natural language questions about their data. The agent uses LangChain and LangGraph
to reason over the data, writes and executes Python/pandas code, self-corrects on errors,
and returns clear human-readable answers. All agent activity is fully traced in LangSmith.

The system consists of:
- A FastAPI backend deployed on GCP Cloud Run
- A Next.js frontend deployed on Firebase Hosting at orion.web.app
- In-memory session management (no accounts required)
- Multi-file support — analyze multiple CSVs in one session
- Conversation memory — the agent remembers previous questions in a session

This project is built as both a working production system and a teaching demo for a
2-hour hands-on workshop targeting mid-level engineers.

---

## Goals

1. Demonstrate what an AI agent is versus a simple LLM call
2. Show how LangChain tools, memory, and agent loops work in practice
3. Show how LangSmith gives full observability into agent reasoning
4. Deploy a working full-stack AI product end to end
5. Leave attendees with a real project they can extend and deploy

---

## Tech Stack

### Backend
| Component | Technology | Version | Reason |
|---|---|---|---|
| Language | Python | 3.12 | Latest stable |
| Agent Framework | LangChain | 0.3.x | Most widely known, model-agnostic |
| Agent Runtime | LangGraph | 0.2.x | LangChain's recommended ReAct agent runtime |
| LLM | Vertex AI Gemini 2.5 Flash | latest | GCP-native, no API key needed on Cloud Run |
| LLM Abstraction | langchain-google-vertexai | latest | Vertex AI support in LangChain |
| Observability | LangSmith | latest | Native LangChain tracing |
| API Framework | FastAPI | 0.115.x | Lightweight, async, auto docs |
| ASGI Server | Uvicorn | latest | FastAPI runtime |
| Containerization | Docker | latest | GCP Cloud Run requirement |
| Deployment | GCP Cloud Run | latest | Serverless, scales to zero |

### Frontend
| Component | Technology | Version | Reason |
|---|---|---|---|
| Framework | Next.js | 14.x (App Router) | Production-grade, TypeScript, familiar to JS devs |
| Language | TypeScript | 5.x | Type safety, better DX |
| Styling | Tailwind CSS | 3.x | Utility-first, fast to build with |
| Icons | Lucide React | latest | Clean icon set |
| HTTP Client | Axios | latest | Clean API calls with interceptors |
| Deployment | Firebase Hosting | latest | Fast CDN, free tier, orion.web.app domain |

---

## Model-Agnostic LLM Design

The agent is designed so the LLM can be swapped by changing two environment variables.
A single `get_llm()` factory function in `app/config/llm.py` reads `LLM_PROVIDER` and
`LLM_MODEL` and returns the correct LangChain `BaseChatModel` instance.

Supported providers:
- `vertexai` → uses `langchain-google-vertexai` ChatVertexAI (default, no API key on GCP)
- `gemini` → uses `langchain-google-genai` ChatGoogleGenerativeAI (needs GOOGLE_API_KEY)
- `openai` → uses `langchain-openai` ChatOpenAI (needs OPENAI_API_KEY)
- `anthropic` → uses `langchain-anthropic` ChatAnthropic (needs ANTHROPIC_API_KEY)
- `groq` → uses `langchain-groq` ChatGroq (needs GROQ_API_KEY)

All models use temperature=0 for deterministic analytical responses.

---

## Dataset

**File:** `data/sales_data.csv`
**Rows:** 1,000 orders
**Date range:** 2024-01-01 to 2024-12-30
**Total revenue:** ~$286,936

### Columns

| Column | Type | Description |
|---|---|---|
| order_id | string | Unique order identifier e.g. ORD-0001 |
| order_date | date (YYYY-MM-DD) | Date the order was placed |
| product_name | string | Name of the product sold |
| category | string | Electronics, Office, Stationery, Accessories |
| unit_price | float | Price per unit in USD |
| quantity | int | Number of units ordered |
| discount_pct | int | Discount percentage: 0, 5, 10, 15, or 20 |
| total_amount | float | Final order value after discount |
| region | string | African region (5 regions) |
| country | string | Country within the region (25 countries) |
| sales_rep | string | Sales representative name (10 reps) |
| channel | string | Online, Retail, Wholesale, Direct Sales |
| status | string | Completed, Returned, Pending |

---

## Full Project Folder Structure

```
orion/
│
├── app/                              # FastAPI backend
│   ├── __init__.py
│   ├── main.py                       # App entry point, routes, CORS, session store
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py                  # LangGraph agent, run_agent(), conversation memory
│   │   ├── tools.py                  # get_dataset_info, python_repl (session-aware)
│   │   └── prompts.py                # System prompt
│   ├── config/
│   │   ├── __init__.py
│   │   ├── llm.py                    # get_llm() model-agnostic factory
│   │   └── settings.py               # Pydantic settings from env vars
│   └── schemas/
│       ├── __init__.py
│       └── models.py                 # All Pydantic request/response models
│
├── data/
│   └── sales_data.csv                # Default preloaded dataset
│
├── frontend/                         # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx                # Root layout, fonts, metadata
│   │   ├── page.tsx                  # Landing/main page
│   │   ├── globals.css               # Global styles, Tailwind directives
│   │   └── api/
│   │       └── analyze/
│   │           └── route.ts          # Next.js API route proxying to FastAPI backend
│   ├── components/
│   │   ├── ChatInterface.tsx         # Main chat area with message history
│   │   ├── MessageBubble.tsx         # Individual message with reasoning steps
│   │   ├── DatasetSidebar.tsx        # Sidebar: dataset list, switcher, upload zone
│   │   ├── FileUpload.tsx            # Drag-and-drop CSV upload component
│   │   ├── ReasoningSteps.tsx        # Collapsible agent reasoning trace
│   │   ├── Header.tsx                # Top bar: logo, model info, LangSmith link
│   │   └── SuggestedQuestions.tsx    # Sample questions shown before first message
│   ├── lib/
│   │   ├── api.ts                    # Axios client, all API call functions
│   │   ├── session.ts                # Session ID management via localStorage
│   │   └── types.ts                  # All TypeScript interfaces and types
│   ├── public/
│   │   └── orion-logo.svg            # Orion logo
│   ├── .env.local.example            # Frontend env var template
│   ├── .firebaserc                   # Firebase project config
│   ├── firebase.json                 # Firebase hosting config
│   ├── next.config.ts                # Next.js config
│   ├── package.json                  # Dependencies
│   ├── tailwind.config.ts            # Tailwind config
│   └── tsconfig.json                 # TypeScript config
│
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── cloudbuild.yaml
├── requirements.txt
└── README.md
```

---

## Backend File-by-File Specifications

### `app/main.py`

FastAPI application with session management. Responsibilities:
- Create FastAPI app with CORS enabled for the Firebase frontend domain and localhost:3000
- Define in-memory session store: a dict mapping session_id → SessionData
- SessionData contains:
  - `datasets: dict[str, pd.DataFrame]` — filename → DataFrame for all uploaded files
  - `active_dataset: str` — filename of currently selected dataset
  - `conversation_history: list[dict]` — list of {role, content} message dicts
  - `created_at: datetime`
- On startup: load `sales_data.csv` as the default dataset into a shared default store
- Routes:
  - `GET /health` → HealthResponse
  - `POST /session` → creates new session, preloads sales_data, returns session_id
  - `POST /upload` → accepts multipart CSV upload, stores in session, returns file metadata
  - `GET /session/{session_id}/datasets` → returns list of datasets in the session
  - `PATCH /session/{session_id}/active-dataset` → switches active dataset
  - `POST /analyze` → accepts AnalyzeRequest (question + session_id + optional filename),
    runs agent against active dataset with conversation history, returns AnalyzeResponse
  - `DELETE /session/{session_id}` → clears session data
- Session cleanup: remove sessions older than 2 hours using a background task
- CORS origins: `["https://orion.web.app", "http://localhost:3000"]`

### `app/agent/agent.py`

LangGraph agent with conversation memory. Key changes from Phase 3:
- `run_agent(question, session_id, df, conversation_history)` — now accepts the active
  DataFrame and conversation history as parameters (passed in from main.py)
- Conversation history is injected into the agent as prior messages so the agent
  has context of what was asked before in the session
- The tools receive the DataFrame via a closure or context variable — see tools.py spec
- Returns dict: answer, session_id, steps, model_used

### `app/agent/tools.py`

Session-aware tools. Key change: tools must operate on the session's active DataFrame,
not a globally loaded one. Implementation approach:
- Define a module-level variable `_current_df: pd.DataFrame = None`
- Expose a `set_active_dataframe(df: pd.DataFrame)` function that sets `_current_df`
- Both tools (`get_dataset_info` and `python_repl`) use `_current_df` internally
- In `main.py`'s `/analyze` route, call `set_active_dataframe(session_df)` before
  calling `run_agent()` — this sets the correct DataFrame for that request
- Note: this is not thread-safe for high concurrency but is correct for a workshop/demo
  with low concurrent users. Document this limitation in a comment.
- The default dataset (sales_data.csv) is loaded at startup and set as the initial df

### `app/schemas/models.py`

Updated Pydantic models:

`SessionResponse`:
- `session_id: str`
- `datasets: list[str]` — list of loaded dataset filenames
- `active_dataset: str`

`UploadResponse`:
- `filename: str`
- `rows: int`
- `columns: int`
- `column_names: list[str]`
- `session_id: str`

`DatasetSwitchRequest`:
- `filename: str`

`AnalyzeRequest`:
- `question: str` — min 5, max 500 chars
- `session_id: str` — required (created by POST /session on app load)
- `filename: Optional[str]` — if provided, analyze this specific file; else use active

`AnalyzeResponse`:
- `answer: str`
- `session_id: str`
- `steps: list[str]`
- `model_used: str`
- `dataset_used: str` — which filename was analyzed

`HealthResponse`:
- `status: str`
- `model: str`

### `app/config/settings.py`

Add these new fields:
- `CORS_ORIGINS: str` — default `"https://orion.web.app,http://localhost:3000"`
- `SESSION_TTL_HOURS: int` — default `2`
- `MAX_FILE_SIZE_MB: int` — default `10`
- `MAX_FILES_PER_SESSION: int` — default `5`

---

## Frontend Specifications

### Design Language

Clean, dark-mode-first professional UI. Think: a data tool that engineers would
actually use. Not colorful or playful — minimal, focused, fast-feeling.

Color palette:
- Background: `#0f0f0f` (near black)
- Surface: `#1a1a1a` (card backgrounds)
- Border: `#2a2a2a`
- Primary accent: `#6366f1` (indigo — buttons, active states)
- Text primary: `#f4f4f5`
- Text secondary: `#a1a1aa`
- Success: `#22c55e`
- Code background: `#111827`

Typography: Inter font (Google Fonts)

### `frontend/lib/types.ts`

Define all interfaces:
```
Message: { id, role ('user'|'assistant'), content, steps?, dataset_used?, timestamp }
Dataset: { filename, rows, columns, column_names, is_default }
Session: { session_id, datasets: Dataset[], active_dataset: string }
AnalyzeRequest: { question, session_id, filename? }
AnalyzeResponse: { answer, session_id, steps, model_used, dataset_used }
```

### `frontend/lib/session.ts`

- `getOrCreateSessionId()` — reads from localStorage key `orion_session_id`,
  creates and stores a new UUID if not found
- `clearSession()` — removes from localStorage
- Session ID is generated client-side and sent with every API request

### `frontend/lib/api.ts`

Axios instance pointing to the FastAPI backend URL (from env var `NEXT_PUBLIC_API_URL`).
Functions:
- `createSession(sessionId)` → POST /session with session_id, returns SessionResponse
- `uploadFile(sessionId, file)` → POST /upload multipart, returns UploadResponse
- `switchDataset(sessionId, filename)` → PATCH /session/{id}/active-dataset
- `analyzeQuestion(request)` → POST /analyze, returns AnalyzeResponse
- `getDatasets(sessionId)` → GET /session/{id}/datasets
- All functions handle errors and throw with meaningful messages

### `frontend/app/page.tsx`

Main page — orchestrates the full UI. State managed here:
- `session: Session | null` — initialized on mount via createSession()
- `messages: Message[]` — full conversation history displayed in chat
- `isLoading: boolean` — shows typing indicator while agent is running
- `isSidebarOpen: boolean` — mobile sidebar toggle

On mount:
- Call `getOrCreateSessionId()` from session.ts
- Call `createSession(sessionId)` to initialize backend session
- Set session state with preloaded sales_data.csv as default dataset

Layout: full viewport height, flex row
- Left: `DatasetSidebar` (fixed width 260px, collapsible on mobile)
- Right: flex column — `Header` on top, `ChatInterface` fills remaining space

### `frontend/components/ChatInterface.tsx`

The main chat area. Props: session, messages, isLoading, onSendMessage.
- Messages list: scrollable, auto-scrolls to bottom on new message
- Empty state: shows `SuggestedQuestions` component with 4 sample questions
- Each message rendered by `MessageBubble`
- Bottom: text input with send button, disabled while isLoading
- Input: pressing Enter sends, Shift+Enter adds newline
- Shows "Orion is analyzing..." typing indicator when isLoading

### `frontend/components/MessageBubble.tsx`

Renders a single message. Props: message: Message.
- User messages: right-aligned, indigo background, rounded bubble
- Assistant messages: left-aligned, surface background
  - Answer text rendered with basic markdown (bold, newlines)
  - If steps exist: `ReasoningSteps` component below the answer
  - Small footer: dataset_used filename + timestamp

### `frontend/components/ReasoningSteps.tsx`

Collapsible section showing agent reasoning. Props: steps: string[].
- Toggle button: "Show reasoning (N steps)" / "Hide reasoning"
- When expanded: each step shown as a monospace code-style block
- Tool calls highlighted differently from tool results
- This is a KEY teaching component — show it prominently in the demo

### `frontend/components/DatasetSidebar.tsx`

Left sidebar. Props: session, onDatasetSwitch, onFileUpload.
- Header: "Datasets" title
- List of loaded datasets — each shows filename, row count
- Active dataset highlighted with indigo border
- Clicking a dataset calls onDatasetSwitch
- Bottom: `FileUpload` component
- Shows "Default" badge on sales_data.csv

### `frontend/components/FileUpload.tsx`

Drag-and-drop CSV uploader. Props: sessionId, onUploadSuccess.
- Dashed border drop zone: "Drop CSV here or click to browse"
- Only accepts .csv files, max 10MB
- On upload: shows progress, then calls onUploadSuccess with the new dataset info
- Shows error message if file is too large or wrong type

### `frontend/components/Header.tsx`

Top navigation bar.
- Left: Orion logo + name
- Center: active dataset name (subtle, secondary text)
- Right: model name badge (e.g. "gemini-2.5-flash") + link to LangSmith project

### `frontend/components/SuggestedQuestions.tsx`

Shown when chat is empty. Props: onSelect: (question: string) => void.
Displays 4 clickable question chips:
- "Which region generated the most revenue?"
- "Who is the top performing sales rep?"
- "What is the return rate by category?"
- "Show monthly revenue trend for 2024"

### `frontend/app/api/analyze/route.ts`

Next.js API route that proxies requests to the FastAPI backend.
Handles CORS for the frontend → backend communication.
Forwards the request body to `NEXT_PUBLIC_API_URL/analyze` and returns the response.
This avoids CORS issues when the frontend and backend are on different domains.

---

## Session Flow

```
Browser loads orion.web.app
    │
    ▼
getOrCreateSessionId() → reads/creates UUID in localStorage
    │
    ▼
POST /session { session_id }
Backend creates session with sales_data.csv preloaded
    │
    ▼
User sees chat interface with sales_data.csv active in sidebar
SuggestedQuestions shown
    │
    ├── User types question → POST /analyze
    │   Backend: set_active_dataframe(session.active_df)
    │             inject conversation_history into agent
    │             run agent → return answer + steps
    │   Frontend: add message to chat, show reasoning steps
    │             save to conversation_history
    │
    ├── User uploads CSV → POST /upload (multipart)
    │   Backend: parse CSV → store in session.datasets
    │   Frontend: new dataset appears in sidebar
    │             user clicks it → PATCH /active-dataset
    │             subsequent questions use new dataset
    │
    └── User switches dataset → PATCH /session/{id}/active-dataset
        Backend: updates session.active_dataset
        Frontend: header shows new active dataset name
```

---

## Environment Variables

### Backend `.env`
```
# LLM — Vertex AI (default, no API key needed on GCP Cloud Run)
LLM_PROVIDER=vertexai
LLM_MODEL=gemini-2.5-flash

# Optional providers
GOOGLE_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=orion

# App
DATA_PATH=data/sales_data.csv
PORT=8080
CORS_ORIGINS=https://orion.web.app,http://localhost:3000
SESSION_TTL_HOURS=2
MAX_FILE_SIZE_MB=10
MAX_FILES_PER_SESSION=5
```

### Frontend `frontend/.env.local`
```
NEXT_PUBLIC_API_URL=https://orion-925134145115.us-central1.run.app
NEXT_PUBLIC_LANGSMITH_PROJECT_URL=https://smith.langchain.com/your-project-url
```

---

## Firebase Hosting Configuration

### `frontend/firebase.json`
```json
{
  "hosting": {
    "public": "out",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [{ "source": "**", "destination": "/index.html" }]
  }
}
```

### `frontend/.firebaserc`
```json
{
  "projects": {
    "default": "your-firebase-project-id"
  }
}
```

### Next.js Static Export
In `next.config.ts`, set `output: 'export'` for static site generation.
All pages must be compatible with static export (no server-side runtime needed
since the API proxy is handled by the FastAPI backend directly).

### Deploy Commands
```bash
cd frontend
npm run build          # generates /out folder
firebase deploy        # deploys /out to Firebase Hosting
```

---

## GCP Cloud Run — Updated Configuration

Backend URL: `https://orion-925134145115.us-central1.run.app`

The Cloud Run service uses Vertex AI authentication via the attached service account.
No API key required for Vertex AI. Only LangSmith key stored in Secret Manager.

Updated deploy command if redeploying:
```bash
gcloud run deploy orion \
  --image gcr.io/YOUR_PROJECT_ID/orion \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=vertexai,LLM_MODEL=gemini-2.5-flash \
  --set-env-vars LANGCHAIN_TRACING_V2=true,LANGCHAIN_PROJECT=orion \
  --set-env-vars CORS_ORIGINS="https://orion.web.app,http://localhost:3000" \
  --set-secrets LANGCHAIN_API_KEY=langsmith-api-key:latest \
  --memory 1Gi \
  --cpu 1 \
  --timeout 120 \
  --min-instances 0 \
  --max-instances 3
```

---

## Self-Correction Demo (Workshop Key Moment)

Ask: "What is the total revenue for the Electronics categry?" (deliberate typo)
The agent handles this gracefully via self-correction — visible in LangSmith traces
and in the reasoning steps shown in the UI.

---

## Starter Repo Guide

See Phase 7 in PHASES.md. The starter repo (orion-starter/) stubs out:
- app/config/llm.py
- app/agent/tools.py
- app/agent/prompts.py
- app/agent/agent.py

Frontend is provided complete — attendees focus on the backend agent logic.
