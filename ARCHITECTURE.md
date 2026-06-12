# Orion — Architecture

## Full System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                │
│                    orion.web.app (Firebase)                         │
│                                                                     │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────────┐  │
│  │  Dataset    │    │   Chat Interface  │    │     Header        │  │
│  │  Sidebar    │    │                   │    │  model + LangSmith│  │
│  │             │    │  MessageBubble    │    │  link             │  │
│  │ sales.csv ✓ │    │  ┌─────────────┐ │    └───────────────────┘  │
│  │ my_data.csv │    │  │ Answer text │ │                           │
│  │             │    │  │ ▼ Reasoning │ │                           │
│  │ [Drop CSV]  │    │  │   Steps     │ │                           │
│  └──────┬──────┘    │  └─────────────┘ │                           │
│         │           └────────┬─────────┘                           │
│         │                    │                                     │
│  localStorage: orion_session_id (UUID)                             │
└─────────┼────────────────────┼─────────────────────────────────────┘
          │                    │
          │  POST /upload      │  POST /analyze
          │  PATCH /active     │  { question, session_id }
          ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GCP CLOUD RUN                                    │
│         https://orion-925134145115.us-central1.run.app             │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   FastAPI (app/main.py)                     │   │
│  │                                                             │   │
│  │  In-Memory Session Store                                    │   │
│  │  sessions: { session_id → SessionData }                     │   │
│  │                                                             │   │
│  │  SessionData:                                               │   │
│  │  ├── datasets: { filename → pd.DataFrame }                  │   │
│  │  ├── active_dataset: str                                    │   │
│  │  ├── conversation_history: [{role, content}, ...]           │   │
│  │  └── created_at: datetime (TTL: 2 hours)                    │   │
│  │                                                             │   │
│  │  Routes:                                                    │   │
│  │  POST   /session          → create session                  │   │
│  │  POST   /upload           → add CSV to session              │   │
│  │  GET    /session/{id}/datasets → list datasets              │   │
│  │  PATCH  /session/{id}/active-dataset → switch dataset       │   │
│  │  POST   /analyze          → run agent                       │   │
│  │  GET    /health           → health check                    │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                │                                   │
│  ┌─────────────────────────────▼───────────────────────────────┐   │
│  │              LangGraph Agent (app/agent/agent.py)           │   │
│  │                                                             │   │
│  │  run_agent(question, session_id, df, conversation_history)  │   │
│  │                                                             │   │
│  │  1. set_active_dataframe(df)   ← session's active df        │   │
│  │  2. inject conversation_history as prior messages           │   │
│  │  3. invoke create_react_agent                               │   │
│  │  4. return answer + steps                                   │   │
│  └──────────────┬──────────────────────────────────────────────┘   │
│                 │                                                   │
│  ┌──────────────▼──────────────────────────────────────────────┐   │
│  │                Tools (app/agent/tools.py)                   │   │
│  │                                                             │   │
│  │  _current_df ← set by set_active_dataframe() per request    │   │
│  │                                                             │   │
│  │  get_dataset_info() → columns, dtypes, shape, sample rows   │   │
│  │  python_repl(code)  → exec code with df in context          │   │
│  │                       returns stdout or "ERROR: ..."        │   │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Vertex AI (LLM)                                 │  │
│  │         ChatVertexAI(model=gemini-2.5-flash, temp=0)        │  │
│  │         Auth: Cloud Run service account (no API key)        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ auto-trace (env vars only)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LANGSMITH CLOUD                                │
│                    smith.langchain.com                              │
│                    Project: orion                                   │
│                                                                     │
│  Every agent run traced:                                            │
│  • User question + conversation history                             │
│  • Tool calls (get_dataset_info, python_repl)                       │
│  • Code written by agent + execution result                         │
│  • Self-correction loops                                            │
│  • Final answer + token count + latency + cost                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Session Lifecycle

```
Browser opens orion.web.app
        │
        ▼
localStorage.getItem('orion_session_id')
        │
        ├── EXISTS → use it
        └── NOT FOUND → uuid() → localStorage.setItem(...)
        │
        ▼
POST /session { session_id }
Backend: sessions[session_id] = SessionData(
    datasets={"sales_data.csv": default_df},
    active_dataset="sales_data.csv",
    conversation_history=[],
    created_at=now()
)
        │
        ▼
Chat interface ready — sales_data.csv active

Per question:
        │
        ▼
POST /analyze { question, session_id }
        │
Backend:
  session = sessions[session_id]
  df = session.datasets[session.active_dataset]
  history = session.conversation_history
  set_active_dataframe(df)
  result = run_agent(question, session_id, df, history)
  session.conversation_history.append({role:user, content:question})
  session.conversation_history.append({role:assistant, content:result.answer})
  return AnalyzeResponse(dataset_used=session.active_dataset, ...)
        │
        ▼
Frontend: message added to chat with reasoning steps

Session dies:
  - User closes browser (localStorage persists but backend session expires after 2h)
  - Next visit: new session_id → fresh session
```

---

## Multi-File Flow

```
User drops custom_data.csv onto FileUpload component
        │
        ▼
POST /upload
  multipart: file=custom_data.csv, session_id=abc-123
        │
Backend:
  df = pd.read_csv(file)
  session.datasets["custom_data.csv"] = df
  return UploadResponse(filename, rows, columns, column_names)
        │
        ▼
DatasetSidebar updates:
  [sales_data.csv]  (default badge)
  [custom_data.csv] ← new, not yet active
        │
User clicks custom_data.csv
        │
        ▼
PATCH /session/abc-123/active-dataset { filename: "custom_data.csv" }
Backend: session.active_dataset = "custom_data.csv"
        │
        ▼
Header shows: "custom_data.csv"
Next question analyzes custom_data.csv
```

---

## ReAct Agent Loop (unchanged from original)

```
User Question + Conversation History
      │
      ▼
┌─────────────┐
│   THINK     │  "I should check the dataset structure first"
└──────┬──────┘
       ▼
┌─────────────┐
│     ACT     │  get_dataset_info()
└──────┬──────┘
       ▼
┌─────────────┐
│   OBSERVE   │  columns, dtypes, sample rows
└──────┬──────┘
       ▼
┌─────────────┐
│   THINK     │  "I'll write pandas code to answer this"
└──────┬──────┘
       ▼
┌─────────────┐
│     ACT     │  python_repl(code)
└──────┬──────┘
       │
       ├── OK → ANSWER
       └── ERROR → THINK (fix code) → ACT again (up to 3x)
```

---

## Frontend Component Tree

```
app/page.tsx  (session state, messages state)
├── Header.tsx  (model name, LangSmith link)
├── DatasetSidebar.tsx  (dataset list, active indicator)
│   └── FileUpload.tsx  (drag-drop CSV uploader)
└── ChatInterface.tsx  (messages, input)
    ├── SuggestedQuestions.tsx  (shown when messages=[])
    └── MessageBubble.tsx  (per message)
        └── ReasoningSteps.tsx  (collapsible steps)
```

---

## LLM Provider Swap

```
.env
LLM_PROVIDER=vertexai   →  ChatVertexAI   (default, GCP auth, no API key)
LLM_PROVIDER=gemini     →  ChatGoogleGenerativeAI  (needs GOOGLE_API_KEY)
LLM_PROVIDER=openai     →  ChatOpenAI     (needs OPENAI_API_KEY)
LLM_PROVIDER=anthropic  →  ChatAnthropic  (needs ANTHROPIC_API_KEY)
LLM_PROVIDER=groq       →  ChatGroq       (needs GROQ_API_KEY)

LLM_MODEL=gemini-2.5-flash  → passed to whichever provider is active
```

---

## Infrastructure Map

```
Firebase Hosting (orion.web.app)
  └── Next.js static export (/out)
      └── calls → GCP Cloud Run (orion service, us-central1)
                    └── Vertex AI (gemini-2.5-flash, same region)
                    └── LangSmith (traces, external)
                    └── GCP Secret Manager (LANGCHAIN_API_KEY)
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Session storage | In-memory Python dict | Simple, fast, no infra. Swap for Redis at scale. |
| Session ID | Client-generated UUID in localStorage | No accounts, no server state on init |
| Multi-file | Dict per session | Clean isolation, easy to switch active df |
| Conversation memory | Injected as prior messages | LangGraph handles the context window |
| Frontend export | Static (Next.js output: export) | Firebase Hosting, no server needed |
| Tool df access | Module-level var + setter | Simple, works for low concurrency demo |
| Vertex AI auth | Service account (Cloud Run) | No API key management on GCP |
| CORS | Explicit origins list | Security — only Firebase + localhost |
