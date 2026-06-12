# Build Phases — Claude Code Prompt Guide

Each phase is a single focused Claude Code session.
Start every session with:

> "Read PROJECT.md and PHASES.md. We are working on Phase N: [Title].
>  Complete only the tasks listed under this phase. Do not proceed to the next phase."

---

## Phase 0 — Project Scaffold ✅ COMPLETE
## Phase 1 — Configuration Layer ✅ COMPLETE
## Phase 2 — Agent Tools ✅ COMPLETE
## Phase 3 — Agent Core ✅ COMPLETE
## Phase 4 — FastAPI Application ✅ COMPLETE
## Phase 5 — LangSmith Verification ✅ COMPLETE
## Phase 6 — Docker & GCP Deployment ✅ COMPLETE

Live backend URL: https://orion-925134145115.us-central1.run.app

---

## Phase 7 — Starter Repo

**Goal:** Create the workshop starter repo by stripping the working project.

**Tasks:**
1. Copy the entire working backend into a new folder `orion-starter/`
2. Stub out these 4 files with TODO comments:
   - `app/config/llm.py` — keep signature, stub body with provider list comment
   - `app/agent/tools.py` — keep imports and df loading, stub tool bodies
   - `app/agent/prompts.py` — keep variable name, stub prompt content
   - `app/agent/agent.py` — keep imports and function signature, stub body
3. Create `WORKSHOP.md` in orion-starter/ mapping each TODO to a workshop phase
   with hints and verification commands
4. Update orion-starter/README.md to be workshop-oriented

**Note:** The frontend is NOT included in the starter repo — attendees focus on
backend agent logic. Frontend is a bonus they take home from the full project.

**Verification:**
- Run starter and confirm NotImplementedError raised at right points
- Confirm WORKSHOP.md clearly guides an attendee through all 4 TODOs

---

## Phase 8 — Backend Updates for Full Stack

**Goal:** Update the FastAPI backend to support sessions, multi-file uploads,
and conversation memory. The backend already works — this phase extends it.

**Tasks:**

1. Update `app/schemas/models.py` — add new models as specified in PROJECT.md:
   - `SessionResponse`, `UploadResponse`, `DatasetSwitchRequest`
   - Update `AnalyzeRequest` to require `session_id` and add optional `filename`
   - Update `AnalyzeResponse` to add `dataset_used` field

2. Update `app/agent/tools.py` — make tools session-aware:
   - Remove the module-level hardcoded DataFrame load
   - Add `_current_df: pd.DataFrame = None` module-level variable
   - Add `set_active_dataframe(df: pd.DataFrame)` function
   - Update `get_dataset_info` and `python_repl` to use `_current_df`
   - Keep the default sales_data.csv load at startup as fallback

3. Update `app/agent/agent.py` — add conversation memory:
   - Update `run_agent` signature:
     `run_agent(question, session_id, df, conversation_history) -> dict`
   - Call `set_active_dataframe(df)` at the start of each run
   - Inject `conversation_history` as prior messages into the agent invocation
     so the agent has context of previous questions in the session
   - Return same dict structure: answer, session_id, steps, model_used

4. Update `app/main.py` — full session management:
   - Add in-memory session store: `sessions: dict[str, SessionData]`
   - SessionData is a dataclass/TypedDict with:
     datasets (dict filename→DataFrame), active_dataset (str),
     conversation_history (list of dicts), created_at (datetime)
   - Implement all routes from PROJECT.md:
     POST /session, POST /upload, GET /session/{id}/datasets,
     PATCH /session/{id}/active-dataset, DELETE /session/{id}
   - Update POST /analyze to:
     - Look up session by session_id (return 404 if not found)
     - Call set_active_dataframe with session's active DataFrame
     - Pass conversation_history to run_agent
     - Append question and answer to session's conversation_history after response
     - Return dataset_used in response
   - Add CORS middleware with origins from settings.CORS_ORIGINS
   - Add background task: every 30 minutes, remove sessions older than SESSION_TTL_HOURS
   - On startup: load sales_data.csv into a shared default_df variable

5. Update `requirements.txt`:
   - Add `python-multipart` (required for FastAPI file uploads)

**Verification:**
```bash
# Start server
uvicorn app.main:app --reload --port 8080

# Create session
curl -X POST http://localhost:8080/session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123"}'
# Expected: {"session_id":"test-123","datasets":["sales_data.csv"],"active_dataset":"sales_data.csv"}

# Ask a question
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"question":"How many orders are there?","session_id":"test-123"}'
# Expected: answer mentioning 1000 orders, dataset_used: "sales_data.csv"

# Ask a follow-up (tests conversation memory)
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"question":"Which of those are completed?","session_id":"test-123"}'
# Expected: agent understands "those" refers to orders from previous question

# Upload a file
curl -X POST http://localhost:8080/upload \
  -F "session_id=test-123" \
  -F "file=@data/sales_data.csv"
# Expected: {"filename":"sales_data.csv","rows":1000,"columns":13,...}
```

---

## Phase 9 — Next.js Frontend

**Goal:** Build the complete Next.js frontend as specified in PROJECT.md.

**Tasks:**

1. Initialize Next.js project inside `frontend/` folder:
   ```bash
   cd frontend
   npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
   ```

2. Install additional dependencies:
   ```bash
   npm install axios lucide-react
   npm install -D @types/node
   ```

3. Configure `next.config.ts`:
   - Set `output: 'export'` for Firebase static hosting
   - Set `images: { unoptimized: true }` (required for static export)
   - Set `trailingSlash: true`

4. Set up Tailwind with the dark theme color palette from PROJECT.md:
   - Extend colors in `tailwind.config.ts` with the exact hex values from PROJECT.md
   - Set dark mode as default (no class toggling needed)

5. Create `frontend/.env.local.example` with variables from PROJECT.md

6. Implement all files in this order:
   a. `lib/types.ts` — all TypeScript interfaces
   b. `lib/session.ts` — getOrCreateSessionId, clearSession
   c. `lib/api.ts` — Axios client + all API functions
   d. `components/Header.tsx`
   e. `components/SuggestedQuestions.tsx`
   f. `components/ReasoningSteps.tsx`
   g. `components/MessageBubble.tsx`
   h. `components/FileUpload.tsx`
   i. `components/DatasetSidebar.tsx`
   j. `components/ChatInterface.tsx`
   k. `app/globals.css` — dark background, Inter font import
   l. `app/layout.tsx` — root layout with Inter font and dark background
   m. `app/page.tsx` — main page orchestrating all components

7. Create `frontend/.env.local` with:
   ```
   NEXT_PUBLIC_API_URL=https://orion-925134145115.us-central1.run.app
   NEXT_PUBLIC_LANGSMITH_PROJECT_URL=https://smith.langchain.com
   ```

**Design requirements:**
- Dark background `#0f0f0f` as default — no white/light theme
- Sidebar fixed at 260px, chat area fills remaining width
- Mobile: sidebar hidden by default, toggle button in header
- Messages auto-scroll to bottom
- Typing indicator (animated dots) while agent is running
- Reasoning steps collapsible — collapsed by default, expand on click
- File upload zone with dashed border, drag-and-drop working
- All interactive elements have hover states
- Empty state shows 4 suggested question chips

**Verification:**
```bash
cd frontend
cp .env.local.example .env.local
# Fill in the API URL
npm run dev
# Open http://localhost:3000
# Verify:
# 1. Page loads with dark theme
# 2. Sidebar shows "sales_data.csv" as default dataset
# 3. Suggested questions appear in empty chat
# 4. Clicking a suggested question sends it and gets a response
# 5. Response shows answer + collapsible reasoning steps
# 6. Uploading a CSV adds it to the sidebar
# 7. Switching datasets works
# 8. Follow-up questions demonstrate conversation memory
npm run build
# Verify build succeeds and /out folder is generated
```

---

## Phase 10 — Firebase Deployment

**Goal:** Deploy the Next.js frontend to Firebase Hosting at orion.web.app

**Prerequisites:**
- Firebase project created at console.firebase.google.com
- Firebase project has Hosting enabled
- `firebase-tools` installed: `npm install -g firebase-tools`
- Logged in: `firebase login`
- Custom domain `orion.web.app` configured in Firebase Hosting (or use the
  auto-generated Firebase URL if custom domain not yet set up)

**Tasks:**

1. Create `frontend/firebase.json`:
   ```json
   {
     "hosting": {
       "public": "out",
       "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
       "rewrites": [{ "source": "**", "destination": "/index.html" }]
     }
   }
   ```

2. Create `frontend/.firebaserc`:
   ```json
   {
     "projects": {
       "default": "YOUR_FIREBASE_PROJECT_ID"
     }
   }
   ```

3. Build and deploy:
   ```bash
   cd frontend
   npm run build
   firebase deploy --only hosting
   ```

4. After deploy: visit the Firebase Hosting URL and verify the full flow works
   end to end against the live Cloud Run backend

5. Update `NEXT_PUBLIC_API_URL` in Firebase environment if needed and redeploy

6. Update Cloud Run CORS to include the Firebase Hosting URL:
   ```bash
   gcloud run services update orion \
     --update-env-vars CORS_ORIGINS="https://orion.web.app,https://YOUR-PROJECT.web.app,http://localhost:3000" \
     --region us-central1
   ```

**Verification:**
- Visit live Firebase URL
- Create session, ask a question, upload a file — all working against live backend
- Check LangSmith — traces appearing from real user on live URL
- Share the URL: orion.web.app (or Firebase auto URL)

**Final system verification checklist:**
- [ ] Frontend loads at orion.web.app
- [ ] Default sales dataset preloaded
- [ ] Can ask questions and get answers
- [ ] Reasoning steps visible and collapsible
- [ ] Can upload a custom CSV
- [ ] Can switch between datasets
- [ ] Conversation memory works (follow-up questions)
- [ ] LangSmith traces visible for all queries
- [ ] Backend health: curl https://orion-925134145115.us-central1.run.app/health
