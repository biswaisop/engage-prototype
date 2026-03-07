
Routes · MD
Copy

# API Routes Reference — Front Desk AI

## Base URL
```
https://api.yourdomain.com
```

---

## Health

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Ping MongoDB, Redis, ChromaDB — returns status of all services |

---

## Orgs

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/orgs/signup` | Register a new organization |
| GET | `/api/orgs/{org_id}` | Get org details |
| PATCH | `/api/orgs/{org_id}` | Update org info (name, email, phone, etc.) |
| DELETE | `/api/orgs/{org_id}` | Deactivate an org |

---

## Settings

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/settings/{org_id}` | Get all settings for an org |
| PATCH | `/api/settings/{org_id}/bot` | Update bot name, welcome message, allowed intents |
| PATCH | `/api/settings/{org_id}/redis` | Update memory TTL and max messages |
| PATCH | `/api/settings/{org_id}/llm` | Switch LLM model (groq/gemini), update temperature |

---

## Chat

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/chat/` | Send a message, get bot response |
| GET | `/api/chat/history?thread_id=` | Get conversation history from Redis |

---

## Documents (RAG / Knowledge Base)

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/docs/upload` | Upload PDF or DOCX → chunk → embed into ChromaDB |
| GET | `/api/docs/{org_id}` | List all ingested documents for an org |
| DELETE | `/api/docs/{org_id}/{doc_id}` | Remove a document from the vector store |

---

## Leads

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/leads/submit` | Submit lead from shadow DOM form |
| GET | `/api/leads/{org_id}` | List all leads for an org |
| GET | `/api/leads/{org_id}/{lead_id}` | Get a single lead |
| PATCH | `/api/leads/{org_id}/{lead_id}` | Update lead status (NEW → CONTACTED → CONVERTED / LOST) |

---

## Issues

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/issues/{org_id}` | List all issues for an org |
| GET | `/api/issues/{org_id}/{issue_id}` | Get a single issue |
| PATCH | `/api/issues/{org_id}/{issue_id}` | Update issue status |

---

## Handoff

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/handoff/trigger` | Called internally by `handoff_node` when HANDOFF_REQUEST intent is detected |
| GET | `/api/handoff/{org_id}` | List active handoff queue (for staff dashboard in Next.js) |
| PATCH | `/api/handoff/{thread_id}/claim` | Staff claims a handoff session |
| PATCH | `/api/handoff/{thread_id}/close` | Staff closes/resolves a handoff session |

---

## Conversations (MongoDB)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/conversations/{org_id}` | List all conversations for an org |
| GET | `/api/conversations/{org_id}/{thread_id}` | Get full conversation record from MongoDB |

---

## Message Flow Summary

```
Guest Message
      ↓
POST /api/chat/
      ↓
LangGraph → Intent Router
      ↓
┌─────────────────────────────────────────┐
│ INFORMATION_RETRIEVAL → RAG Node        │
│ LEAD_CAPTURE          → Lead Node       │  → Bot confirms → Shadow DOM form → POST /api/leads/submit
│ ISSUE_COMPLAINT       → Issue Node      │
│ HANDOFF_REQUEST       → Handoff Node    │  → POST /api/handoff/trigger → Next.js WebSocket → Staff
│ CHAT                  → Chat Node       │
└─────────────────────────────────────────┘
      ↓
Save to Redis + MongoDB
      ↓
Response to Guest
```

---

## Route File Structure

```
routes/
├── chat_service.py       # POST /api/chat/
├── chat_history.py       # GET  /api/chat/history
├── org.py                # /api/orgs/*
├── settings.py           # /api/settings/*
├── docs.py               # /api/docs/*
├── leads.py              # /api/leads/*
├── issues.py             # /api/issues/*
├── handoff.py            # /api/handoff/*
└── conversations.py      # /api/conversations/*
```
