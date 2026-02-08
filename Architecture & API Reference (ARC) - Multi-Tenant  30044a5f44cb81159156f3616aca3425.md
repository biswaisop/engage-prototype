# Architecture & API Reference (ARC) - Multi-Tenant SaaS AI Chatbot Platform

# Architecture & API Reference (ARC) Document

## Multi-Tenant SaaS AI Chatbot Platform with Human Handoff

**Version:** 1.0  

**Target Vertical:** Hospitality Industry  

**Document Status:** Production-Grade Specification  

**Last Updated:** February 2026

---

## Table of Contents

1. High-Level Architecture
2. Conversation State Machine
3. API & Real-Time Specification
4. LangGraph Orchestration
5. RAG Architecture
6. Storage Design
7. Error Handling & Resilience
8. Security & Multi-Tenancy
9. Versioning Strategy

---

## 1. High-Level Architecture

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     VISITOR INTERFACE                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Website Chat Widget (JavaScript SDK)                │   │
│  │  - Embedded via <script> tag                         │   │
│  │  - WebSocket connection to backend                   │   │
│  │  - UI state management (local only)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WSS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND API GATEWAY                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Application                                 │   │
│  │  - WebSocket Handler (/ws/visitor, /ws/agent)        │   │
│  │  - REST API Endpoints                                │   │
│  │  - Authentication & Authorization                    │   │
│  │  - Multi-tenant org_id routing                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

The system consists of:

**Website Chat Widget (Embeddable)**

- Renders chat interface embedded on client website
- Manages WebSocket connection lifecycle
- Displays messages received from backend
- **DOES NOT:** Store conversation history, make routing decisions, call external APIs

**Agent Dashboard**

- Displays active conversation queue
- Manages agent availability status
- Renders multi-conversation interface
- **DOES NOT:** Route conversations, store persistent data, make handoff decisions

**Backend API Gateway (FastAPI)**

- Authenticates all connections (visitor + agent)
- Routes messages to appropriate handlers
- Maintains WebSocket connection registry
- Writes all events to persistent storage
- Invokes LangGraph for AI decisions
- Enforces multi-tenant isolation (org_id)
- **Authority:** Full control over all data flows

**LangGraph Orchestration**

- Analyzes user messages for intent
- Routes to appropriate handling node
- Queries RAG for knowledge-based responses
- Detects lead capture opportunities
- **Returns decisions to backend for execution**
- **DOES NOT:** Write to database, send WebSocket messages, manage state

**Vector Store (Pinecone/Qdrant)**

- Stores pre-ingested embeddings (hotel docs, FAQs, policies)
- Returns semantically relevant chunks for RAG
- **Ingestion happens offline via separate pipeline**
- **DOES NOT:** Store conversation data, track state, get written to at runtime

**Persistent Storage (PostgreSQL + Redis)**

PostgreSQL:

- Organizations, Conversations, Messages
- Agents, Leads, Issues, Callbacks

Redis:

- WebSocket connection mappings
- Agent availability status
- Active conversation assignments
- Rate limiting counters

---

## 2. Conversation State Machine

### 2.1 State Definitions

**States:**

- `AI_ACTIVE` - AI handling conversation (default)
- `HUMAN_REQUESTED` - Visitor/AI requested human, waiting for agent
- `HUMAN_CONNECTED` - Agent actively chatting with visitor
- `CLOSED` - Conversation ended, archived

### 2.2 State Transition Table

| Current State | Event | Next State | Trigger |
| --- | --- | --- | --- |
| AI_ACTIVE | REQUEST_HUMAN | HUMAN_REQUESTED | LangGraph returns handoff intent |
| AI_ACTIVE | VISITOR_REQUESTS_HUMAN | HUMAN_REQUESTED | Visitor sends "/human" or clicks button |
| AI_ACTIVE | END_CONVERSATION | CLOSED | Visitor closes chat or inactivity timeout |
| HUMAN_REQUESTED | AGENT_ACCEPTS | HUMAN_CONNECTED | Agent accepts via ACCEPT_CHAT |
| HUMAN_REQUESTED | NO_AGENT_TIMEOUT (5 min) | AI_ACTIVE | No agents available, fallback to AI |
| HUMAN_REQUESTED | END_CONVERSATION | CLOSED | Visitor closes chat |
| HUMAN_CONNECTED | AGENT_ENDS | CLOSED | Agent clicks "End Chat" |
| HUMAN_CONNECTED | VISITOR_ENDS | CLOSED | Visitor closes widget |
| HUMAN_CONNECTED | AGENT_DISCONNECT | HUMAN_REQUESTED | Agent WebSocket disconnects (network) |
| CLOSED | VISITOR_REOPENS | AI_ACTIVE | Visitor sends new message (new session) |

### 2.3 State-Specific Behavior

**AI_ACTIVE**

- Message Routing: All visitor messages → LangGraph → AI response
- Allowed Actions: Send message, request human, end chat
- Side Effects: Lead/issue capture if detected, auto-handoff if threshold met

**HUMAN_REQUESTED**

- Message Routing: Visitor messages stored but NOT sent to AI (queued for agent)
- Side Effects:
    - Broadcast to all available agents (org_id scoped)
    - 5-minute timeout starts
    - Auto-message to visitor: "An agent will be with you shortly"

**HUMAN_CONNECTED**

- Message Routing: Visitor ↔ Agent direct (no AI involvement)
- Side Effects:
    - Real-time delivery to both parties
    - Agent disconnect → automatic re-queue (HUMAN_REQUESTED)

**CLOSED**

- Message Routing: None (conversation archived)
- Side Effects:
    - Conversation moved to archive
    - Cleanup Redis entries
    - If visitor sends new message → creates NEW conversation

---

## 3. API & Real-Time Specification

### 3.1 WebSocket API: Visitor Connection

**Endpoint:** `wss://[api.platform.com/ws/visitor](http://api.platform.com/ws/visitor)`

**Authentication:**

- Query parameter: `?token=<jwt_token>`
- JWT contains: `{org_id, visitor_id, conversation_id (optional)}`

**Connection Response:**

```json
{
    "type": "SYSTEM_STATUS",
    "status": "connected",
    "conversation_id": "conv_a1b2c3d4e5",
    "state": "AI_ACTIVE",
    "timestamp": "2026-02-07T14:32:00Z"
}
```

#### USER_MESSAGE (Visitor → Server)

**Request Schema:**

```json
{
    "type": "USER_MESSAGE",
    "content": "What time is breakfast served?",
    "metadata": {
        "client_timestamp": "2026-02-07T14:32:15Z",
        "client_message_id": "msg_client_12345"
    }
}
```

**Field Validation:**

- `content`: Required, 1-2000 characters
- `metadata.client_message_id`: Optional, used for deduplication

**Success Response:**

```json
{
    "type": "MESSAGE_ACK",
    "message_id": "msg_a1b2c3d4",
    "timestamp": "2026-02-07T14:32:15.123Z"
}
```

**Backend Processing:**

1. Validate message length
2. Check rate limit (30 messages/minute)
3. Deduplication check (idempotency)
4. Persist message to PostgreSQL
5. ACK immediately
6. Route based on conversation state:
    - AI_ACTIVE → Send to LangGraph
    - HUMAN_REQUESTED → Queue for agent
    - HUMAN_CONNECTED → Forward to agent
    - CLOSED → Reopen conversation

**Error Responses:**

```json
// Rate limit exceeded
{
    "type": "ERROR",
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Maximum 30 messages per minute",
    "retry_after_seconds": 45
}

// Invalid content
{
    "type": "ERROR",
    "code": "INVALID_MESSAGE_LENGTH",
    "message": "Message must be 1-2000 characters"
}
```

#### AI_MESSAGE (Server → Visitor)

**Message Schema:**

```json
{
    "type": "AI_MESSAGE",
    "message_id": "msg_b2c3d4e5",
    "content": "Breakfast is served daily from 6:30 AM to 10:30 AM in the main dining room.",
    "metadata": {
        "confidence": 0.92,
        "sources": ["breakfast_policy.pdf", "faq.md"],
        "intent": "INFORMATION_RETRIEVAL",
        "response_time_ms": 1247
    },
    "timestamp": "2026-02-07T14:32:16.370Z"
}
```

**Backend Generation Flow:**

1. Fetch conversation context
2. Invoke LangGraph with message + history
3. Handle intent-based actions:
    - REQUEST_HUMAN → Initiate handoff
    - CAPTURE_LEAD → Store lead
    - ESCALATE_ISSUE → Store issue + auto-escalate if HIGH/CRITICAL
4. Persist AI response
5. Send to visitor via WebSocket
6. Stop typing indicator

#### SYSTEM_STATUS (Server → Visitor)

**Status Values:**

| Status | When Sent | Metadata |
| --- | --- | --- |
| `connected` | WebSocket established | `conversation_id`, `state` |
| `human_requested` | Handoff initiated | `estimated_wait_seconds` |
| `agent_connected` | Agent accepted chat | `agent_name`, `agent_avatar_url` |
| `agent_disconnected` | Agent lost connection | `reason` |
| `no_agents_available` | Timeout, fallback to AI | `wait_time_seconds` |
| `rate_limited` | Too many messages | `retry_after_seconds` |

**Example Messages:**

```json
// Agent connection
{
    "type": "SYSTEM_STATUS",
    "status": "agent_connected",
    "message": "Sarah from the front desk has joined the chat",
    "metadata": {
        "agent_name": "Sarah",
        "agent_avatar_url": "https://cdn.platform.com/avatars/agent_123.jpg"
    }
}

// No agents available
{
    "type": "SYSTEM_STATUS",
    "status": "no_agents_available",
    "message": "Our agents are currently assisting other guests. I'll continue helping you.",
    "metadata": {
        "wait_time_seconds": 300
    }
}
```

### 3.2 WebSocket API: Agent Connection

**Endpoint:** `wss://[api.platform.com/ws/agent](http://api.platform.com/ws/agent)`

**Authentication:**

- Header: `Authorization: Bearer <jwt_token>`
- JWT contains: `{agent_id, org_id, email, role}`

**Connection Response:**

```json
{
    "type": "AUTH_SUCCESS",
    "agent_id": "agent_a1b2c3",
    "org_id": "org_xyz789",
    "status": "AVAILABLE",
    "active_conversations": [...],
    "pending_requests": [...]
}
```

#### NEW_HUMAN_REQUEST (Server → Agent)

**Message Schema:**

```json
{
    "type": "NEW_HUMAN_REQUEST",
    "conversation_id": "conv_a1b2c3d4",
    "visitor_name": "Guest #4523",
    "preview": "I've been trying to cancel my reservation but...",
    "metadata": {
        "wait_time_seconds": 0,
        "conversation_history_count": 8,
        "detected_intent": "ISSUE_COMPLAINT",
        "handoff_reason": "Visitor frustration detected"
    }
}
```

**Backend Broadcast Logic:**

1. Get all available agents for org
2. Construct notification with conversation preview
3. Broadcast to all available agents
4. Play sound notification (client-side)
5. Log analytics event

#### ACCEPT_CHAT (Agent → Server)

**Request Schema:**

```json
{
    "type": "ACCEPT_CHAT",
    "conversation_id": "conv_a1b2c3d4"
}
```

**Backend Processing:**

1. Atomic assignment check (Redis SET NX - prevents double-assignment)
2. Verify conversation state is HUMAN_REQUESTED
3. Check agent capacity (max concurrent chats)
4. Update conversation state to HUMAN_CONNECTED
5. Fetch conversation history + queued messages
6. Send CHAT_ACCEPTED to agent with full context
7. Notify visitor that agent has joined
8. Withdraw request from other agents
9. Update agent status (BUSY if at capacity)

**Success Response:**

```json
{
    "type": "CHAT_ACCEPTED",
    "conversation_id": "conv_a1b2c3d4",
    "visitor_name": "Guest #4523",
    "history": [
        {
            "message_id": "msg_001",
            "sender_type": "VISITOR",
            "content": "Hi, I need help with my reservation",
            "timestamp": "2026-02-07T14:30:00Z"
        }
    ],
    "queued_messages": [...]
}
```

**Error Responses:**

```json
// Already assigned
{
    "type": "ACCEPTANCE_FAILED",
    "conversation_id": "conv_a1b2c3d4",
    "reason": "already_assigned",
    "assigned_to": "agent_xyz123"
}

// Capacity exceeded
{
    "type": "ACCEPTANCE_FAILED",
    "reason": "capacity_exceeded",
    "max_concurrent": 5,
    "current_active": 5
}
```

**Edge Cases:**

1. Race condition (two agents accept simultaneously): Redis atomic SET NX ensures only one succeeds
2. Visitor closes chat during acceptance: State validation catches this, returns ACCEPTANCE_FAILED
3. Agent disconnects after accepting: Disconnect handler re-queues conversation

#### AGENT_MESSAGE (Agent → Server → Visitor)

**Request Schema:**

```json
{
    "type": "AGENT_MESSAGE",
    "conversation_id": "conv_a1b2c3d4",
    "content": "I've located your reservation ABC123. I can process the cancellation for you right now.",
    "metadata": {
        "client_timestamp": "2026-02-07T14:42:00Z",
        "client_message_id": "msg_agent_001"
    }
}
```

**Backend Processing:**

1. Validate message length (1-5000 characters)
2. Verify conversation assignment (agent must be assigned to conversation)
3. Verify state is HUMAN_CONNECTED
4. Deduplication check
5. Persist message
6. ACK to agent
7. Forward to visitor
8. Update conversation timestamp

**Message to Visitor:**

```json
{
    "type": "AGENT_MESSAGE",
    "message_id": "msg_b2c3d4e5",
    "content": "I've located your reservation ABC123...",
    "agent_name": "Sarah",
    "agent_avatar_url": "https://cdn.platform.com/avatars/agent_123.jpg",
    "timestamp": "2026-02-07T14:42:00.456Z"
}
```

### 3.3 REST API Endpoints

#### POST /api/v1/leads

**Purpose:** Create a lead record from conversation

**Authentication:** Bearer token (requires `leads:write` permission)

**Request Schema:**

```json
{
    "conversation_id": "conv_a1b2c3d4",
    "contact_info": {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0123"
    },
    "intent_type": "BOOKING",
    "intent_details": {
        "check_in": "2026-03-15",
        "check_out": "2026-03-18",
        "room_type": "deluxe",
        "guest_count": 2
    },
    "source": "AI_DETECTED",
    "notes": "Interested in anniversary package"
}
```

**Field Validation:**

- `conversation_id`: Required, must exist and belong to org
- `contact_info`: Required, at least one of {name, email, phone}
- `intent_type`: Required, enum: `BOOKING`, `INQUIRY`, `EVENT`, `CALLBACK_REQUEST`
- `source`: Required, enum: `AI_DETECTED`, `AGENT_CREATED`, `MANUAL`

**Response (201 Created):**

```json
{
    "lead_id": "lead_x1y2z3",
    "status": "created",
    "message": "Lead created successfully",
    "timestamp": "2026-02-07T14:45:00Z"
}
```

**Side Effects:**

- Lead record created in PostgreSQL
- Webhook triggered (`lead.created` event)
- Email notification sent (if configured)
- Analytics event logged

**Edge Cases:**

1. Duplicate email within same org: Existing lead updated instead of creating duplicate
2. Conversation already has associated lead: Allows creation (multiple leads per conversation)

#### POST /api/v1/issues

**Purpose:** Create an issue/complaint record from conversation

**Request Schema:**

```json
{
    "conversation_id": "conv_a1b2c3d4",
    "category": "BILLING",
    "description": "Customer was charged twice for the same reservation",
    "severity": "HIGH",
    "metadata": {
        "reservation_id": "RES-12345",
        "charge_amount": 299.99
    },
    "source": "AI_DETECTED",
    "auto_escalate": true
}
```

**Field Validation:**

- `category`: Required, enum: `BILLING`, `SERVICE`, `FACILITY`, `RESERVATION`, `COMPLAINT`, `OTHER`
- `severity`: Required, enum: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `description`: Required, 10-2000 characters

**Response (201 Created):**

```json
{
    "issue_id": "issue_a1b2c3",
    "status": "created",
    "escalated": true,
    "external_ticket_id": "TICKET-98765",
    "timestamp": "2026-02-07T14:50:00Z"
}
```

**Side Effects:**

- Issue record created
- Conversation state changed to HUMAN_REQUESTED (if auto_escalate)
- Agents notified via WebSocket
- External ticket created (if integrated)
- Email/SMS notifications sent (if CRITICAL)

#### POST /api/v1/callbacks

**Purpose:** Schedule a callback request from visitor

**Request Schema:**

```json
{
    "conversation_id": "conv_a1b2c3d4",
    "contact_info": {
        "name": "Jane Doe",
        "phone": "+1-555-0199",
        "email": "jane.doe@email.com"
    },
    "preferred_time": "2026-02-08T10:00:00Z",
    "timezone": "America/New_York",
    "purpose": "Discuss group booking rates for corporate event",
    "source": "AI_DETECTED"
}
```

**Field Validation:**

- `contact_[info.phone](http://info.phone)`: Required, valid E.164 format
- `preferred_time`: Optional (defaults to next business hour)
- `source`: Required, enum: `AI_DETECTED`, `AGENT_CREATED`, `VISITOR_REQUESTED`

**Response (201 Created):**

```json
{
    "callback_id": "callback_x1y2z3",
    "status": "scheduled",
    "preferred_time": "2026-02-08T10:00:00Z",
    "confirmation_sent": true,
    "timestamp": "2026-02-07T15:00:00Z"
}
```

**Side Effects:**

- Callback record created
- Reminder task scheduled (15 min before)
- Agents notified via WebSocket
- Confirmation email sent to visitor
- Added to agent dashboard calendar

#### GET /api/v1/conversations/{conversation_id}

**Purpose:** Fetch complete conversation details

**Query Parameters:**

- `include_messages`: boolean (default: true)
- `message_limit`: integer (default: 100, max: 500)
- `include_metadata`: boolean (default: true)
- `include_related`: boolean (default: false) - Include leads/issues/callbacks

**Response (200 OK):**

```json
{
    "conversation_id": "conv_a1b2c3d4",
    "org_id": "org_xyz789",
    "visitor_id": "visitor_p1q2r3",
    "state": "HUMAN_CONNECTED",
    "agent_id": "agent_s4t5u6",
    "created_at": "2026-02-07T14:30:00Z",
    "updated_at": "2026-02-07T14:50:00Z",
    "messages": [
        {
            "message_id": "msg_001",
            "sender_type": "VISITOR",
            "content": "Hi, I need help with my reservation",
            "created_at": "2026-02-07T14:30:00Z"
        }
    ],
    "visitor_metadata": {
        "location": "New York, NY",
        "device": "mobile"
    },
    "leads": [...],
    "issues": [],
    "agent": {
        "agent_id": "agent_s4t5u6",
        "display_name": "Sarah",
        "email": "sarah@hotel.com"
    }
}
```

---

## 4. LangGraph Orchestration

### 4.1 Overview

LangGraph serves as the **decision-making pipeline** for AI-powered conversations.

**Key Principle:** LangGraph is a **stateless recommendation engine**. The backend owns all state, persistence, and side effects.

### 4.2 Graph Architecture

```
Input: conversation_id, message, history, org_id

┌──────────────────────────┐
│  1. Intent Router Node   │  ← Entry point
│  - Classify message      │
│  - Route to handler      │
└──────────┬───────────────┘
           │
    ┌──────┴────────┬─────────────┬──────────────┬────────────┐
    ▼               ▼             ▼              ▼            ▼
┌────────┐   ┌───────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
│  RAG   │   │   Lead    │  │  Issue  │  │  Handoff │  │ Chitchat │
│  Node  │   │ Detection │  │ Detect  │  │   Node   │  │   Node   │
└────┬───┘   └─────┬─────┘  └────┬────┘  └─────┬────┘  └─────┬────┘
     └─────────────┴─────────────┴─────────────┴─────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │  Output Schema   │
                       │  {               │
                       │    intent: str   │
                       │    response: str │
                       │    confidence: f │
                       │    actions: []   │
                       │  }               │
                       └──────────────────┘
```

### 4.3 Node Specifications

#### Intent Router Node

**Purpose:** Primary classifier that routes messages to appropriate handler nodes

**Processing Logic:**

1. Classify intent using LLM
2. Apply business rules (override LLM if needed)
3. Route to appropriate node based on intent

**Intents:**

- `RAG_QUERY` - Question answerable from knowledge base
- `LEAD_CAPTURE` - Booking interest, contact info sharing
- `ISSUE_COMPLAINT` - Problem, dissatisfaction, complaint
- `HANDOFF_REQUEST` - Explicit request for human
- `CHITCHAT` - Greeting, small talk

**Output:**

```python
{
    "next_node": "rag_node",
    "metadata": {
        "classified_intent": "RAG_QUERY",
        "confidence": 0.92
    }
}
```

#### RAG Node

**Purpose:** Retrieve relevant knowledge from vector store and generate response

**Processing:**

1. Generate embedding for query
2. Query vector store (org-scoped namespace)
3. Check retrieval confidence
4. Construct RAG prompt with context
5. Generate response
6. Hallucination check
7. Return decision

**Low Confidence Handling:**

If retrieval score < 0.7, recommend handoff:

```python
{
    "intent": "REQUEST_HUMAN",
    "response": None,
    "confidence": 0.6,
    "reasoning": "No high-confidence match in knowledge base"
}
```

**Success Output:**

```python
{
    "intent": "INFORMATION_RETRIEVAL",
    "response": "Breakfast is served daily from 6:30 AM to 10:30 AM...",
    "confidence": 0.92,
    "metadata": {
        "sources": ["breakfast_policy.pdf"],
        "retrieval_scores": [0.92, 0.87]
    }
}
```

**Hallucination Safeguards:**

1. Grounding check - verify all claims exist in context
2. Confidence threshold - require score >0.7
3. Citation requirement - track supporting chunks
4. Fallback to human - any uncertainty → handoff

#### Lead Detection Node

**Purpose:** Identify booking intent and extract contact information

**Processing:**

1. Extract structured information using LLM
2. Validate extracted data (email format, phone format)
3. Check if valid contact method exists
4. Generate confirmation message

**Output (Lead Detected):**

```python
{
    "intent": "CAPTURE_LEAD",
    "response": "Great! I've noted your interest in booking from 2026-03-15 to 2026-03-18...",
    "confidence": 0.89,
    "actions": [
        {
            "type": "CREATE_LEAD",
            "payload": {
                "contact_info": {"name": "John", "email": "john@example.com"},
                "intent_type": "BOOKING",
                "intent_details": {"check_in": "2026-03-15", "check_out": "2026-03-18"},
                "source": "AI_DETECTED"
            }
        }
    ]
}
```

**Backend Execution:**

```python
if langgraph_response["intent"] == "CAPTURE_LEAD":
    # Send AI response
    await send_ai_message(visitor_socket, response["response"])
    
    # Execute CREATE_LEAD action
    for action in response["actions"]:
        if action["type"] == "CREATE_LEAD":
            await create_lead_endpoint(**action["payload"])
```

#### Issue Detection Node

**Purpose:** Identify complaints, problems requiring escalation

**Processing:**

1. Classify issue type and severity
2. Determine response strategy based on severity
3. Generate empathetic response

**Severity Levels:**

- `CRITICAL` - Financial fraud, safety issues → Immediate handoff
- `HIGH` - Billing errors, major service failures → Immediate handoff
- `MEDIUM` - Minor service issues → AI attempts resolution, escalation ready
- `LOW` - Suggestions, minor inconveniences → Handle via AI

**Output (High Severity):**

```python
{
    "intent": "ESCALATE_ISSUE",
    "response": "I understand this is frustrating. Let me connect you with a manager...",
    "confidence": 0.94,
    "actions": [
        {
            "type": "CREATE_ISSUE",
            "payload": {
                "category": "BILLING",
                "description": "Customer reports duplicate charge",
                "severity": "HIGH",
                "auto_escalate": true
            }
        },
        {
            "type": "REQUEST_HUMAN",
            "payload": {"reason": "Issue escalation: BILLING (HIGH)", "priority": "HIGH"}
        }
    ]
}
```

#### Handoff Node

**Purpose:** Determine when and why to escalate to human agent

**Triggers:**

1. **Explicit:** "I want to speak to someone", "talk to a person"
2. **Implicit:** Failed RAG attempts (3+), high frustration score (>0.8)
3. **Complex query:** Complexity score >0.85

**Output:**

```python
{
    "intent": "REQUEST_HUMAN",
    "response": "Of course! I'm connecting you with one of our team members now.",
    "confidence": 1.0,
    "actions": [
        {
            "type": "INITIATE_HANDOFF",
            "payload": {"reason": "Explicit visitor request", "priority": "NORMAL"}
        }
    ]
}
```

### 4.4 LangGraph vs Backend Responsibilities

**LANGGRAPH DECIDES:**

- Intent classification
- Whether to request human handoff
- Which knowledge to retrieve
- Whether a lead/issue exists
- Natural language response content

**LANGGRAPH DOES NOT:**

- Write to PostgreSQL or Redis
- Send WebSocket messages
- Manage conversation state
- Create leads/issues directly
- Execute side effects

**BACKEND EXECUTES:**

- All database writes
- All WebSocket communications
- State transitions
- Lead/issue creation
- Agent notifications
- Webhooks, emails

---

## 5. RAG Architecture

### 5.1 Ingestion vs Runtime

**CRITICAL:** Vector store is populated **offline**. Runtime only **reads**.

```
OFFLINE INGESTION:
Hotel uploads docs → Processing → Chunking → Embedding → Vector Store

RUNTIME (READ-ONLY):
Visitor message → Query Embedding → Vector Store Query → Retrieved Context → LLM → Response
```

### 5.2 Multi-Tenant Isolation

**Namespace Strategy:**

- Each org gets isolated namespace: `org_{org_id}`
- Prevents cross-org data leakage

**Example:**

```python
# Runtime query
results = await vector_store.query(
    vector=query_embedding,
    namespace=f"org_{org_id}",  # Isolated per organization
    top_k=5
)
```

### 5.3 Document Chunking

**Strategy:** 512 tokens with 50-token overlap

**Rationale:**

- Balances context vs granularity
- Ensures no information lost at boundaries
- Fits within embedding model limits

### 5.4 Metadata Enrichment

**Fields:**

```python
{
    "text": "Breakfast is served daily from 6:30 AM...",
    "source": "breakfast_policy.pdf",
    "document_type": "POLICY",
    "section": "Dining Services",
    "last_updated": "2026-01-15T00:00:00Z",
    "org_id": "org_xyz789",
    "language": "en"
}
```

### 5.5 Hallucination Safeguards

1. **Grounding Verification:** Check if response claims exist in context
2. **Confidence Thresholding:** Require retrieval score >0.7
3. **Citation Requirements:** Track which chunks support each claim
4. **Fallback Strategies:** Low confidence → handoff or clarifying question

### 5.6 Why Vector Store is Not Authoritative

**Vector store contains:** Pre-ingested document embeddings

**Vector store does NOT contain:**

- Conversation history
- User messages
- Leads, issues, callbacks
- Real-time state

**Rationale:**

1. **Consistency:** PostgreSQL provides ACID guarantees
2. **Querying:** Complex relational queries not supported in vector stores
3. **Compliance:** GDPR deletion requires exact record removal
4. **Auditability:** Immutable logs require transactional storage

---

## 6. Storage Design

### 6.1 PostgreSQL Schema

**Organizations Table:**

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    config JSONB DEFAULT '{}',
    plan VARCHAR(50) DEFAULT 'FREE',
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Conversations Table:**

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id),
    visitor_id UUID NOT NULL,
    visitor_name VARCHAR(255),
    visitor_metadata JSONB DEFAULT '{}',
    state VARCHAR(50) NOT NULL DEFAULT 'AI_ACTIVE',
    agent_id UUID REFERENCES agents(id),
    handoff_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    connected_at TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE INDEX idx_conversations_org ON conversations(org_id);
CREATE INDEX idx_conversations_state ON conversations(state);
```

**Messages Table:**

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    sender_type VARCHAR(50) NOT NULL,  -- VISITOR, AI, AGENT, SYSTEM
    sender_id UUID,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    client_message_id VARCHAR(255),
    in_reply_to UUID REFERENCES messages(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
```

**Agents Table:**

```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id),
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'AGENT',
    max_concurrent_chats INT DEFAULT 5,
    status VARCHAR(50) DEFAULT 'OFFLINE',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_agents_email_org ON agents(org_id, email);
```

**Leads Table:**

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    contact_info JSONB NOT NULL,
    intent_type VARCHAR(50) NOT NULL,
    intent_details JSONB DEFAULT '{}',
    source VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'NEW',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_leads_org ON leads(org_id, created_at DESC);
```

**Issues Table:**

```sql
CREATE TABLE issues (
    id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    source VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'OPEN',
    external_ticket_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_issues_org ON issues(org_id, created_at DESC);
```

**Callbacks Table:**

```sql
CREATE TABLE callbacks (
    id UUID PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    contact_info JSONB NOT NULL,
    preferred_time TIMESTAMP NOT NULL,
    timezone VARCHAR(100),
    purpose TEXT,
    source VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'SCHEDULED',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_callbacks_org ON callbacks(org_id, preferred_time);
```

### 6.2 Redis Data Structures

**WebSocket Connections:**

```
visitor:{visitor_id}:socket → connection_id
agent:{agent_id}:socket → connection_id
connection:{connection_id}:metadata → {type, id, org_id}
```

**Agent Availability:**

```
org:{org_id}:agents:available → Set[agent_id]
org:{org_id}:agents:connected → Set[agent_id]
agent:{agent_id}:status → {status, active_chats, max_concurrent}
```

**Conversation Assignments:**

```
conversation:{conversation_id}:assigned_agent → agent_id (TTL 1 hour)
conversation:{conversation_id}:queued_messages → List[message_id]
```

**Rate Limiting:**

```
rate:visitor:{visitor_id}:messages → count (TTL 60s)
rate:org:{org_id}:leads → count (TTL 3600s)
```

---

## 7. Error Handling & Resilience

### 7.1 No Agent Available

**Scenario:** Visitor requests human, but all agents offline/busy

**Strategy 1: Fallback to AI (Timeout-Based)**

- Set 5-minute timeout
- Notify visitor of wait time
- If timeout expires, revert to AI_ACTIVE

**Strategy 2: Queue Position System**

- Add to queue, notify position
- When agent available, auto-assign from queue

**Strategy 3: Callback Scheduling**

- Offer callback instead of waiting
- Create callback record
- Close conversation

### 7.2 Agent Disconnects Mid-Chat

**Detection:** WebSocket disconnect event

**Handling:**

1. Find active conversations for disconnected agent
2. Transition to HUMAN_REQUESTED
3. Notify visitor of disconnect
4. Broadcast to available agents
5. Log incident for analytics

**Options:**

- Re-queue (default)
- Transfer to backup agent (if configured)
- Fallback to AI (if no agents available)

### 7.3 AI Failure (LangGraph Timeout)

**Detection:** LangGraph takes >10 seconds or raises exception

**Handling:**

1. Send fallback response: "I'm having trouble processing your request..."
2. Initiate handoff to human
3. Log error for monitoring
4. Alert if failure rate >5%

**Alternative:** Retry with simplified context (no history)

### 7.4 Vector Store Timeout

**Detection:** Vector store query >3 seconds or exception

**Handling:**

1. Return handoff recommendation
2. Use cached fallback responses (for common FAQs)
3. Monitor vector store health
4. Alert on consecutive failures (3+)

---

## 8. Security & Multi-Tenancy

### 8.1 org_id Isolation

**Enforcement Points:**

1. **WebSocket Connection:** Extract org_id from JWT
2. **Database Queries:** ALWAYS filter by org_id
3. **Vector Store:** Use org-scoped namespace
4. **Redis Keys:** Include org_id in all keys

**Example:**

```python
# ALWAYS scope queries
conversation = db.query(Conversation).filter(
    Conversation.id == conversation_id,
    Conversation.org_id == auth.org_id  # REQUIRED
).first()

# NEVER query without org_id check
# BAD: conversation = db.query(Conversation).get(conversation_id)
```

### 8.2 Agent Authorization

**Role-Based Access Control:**

**Roles:**

- `AGENT` - Basic conversation access
- `SUPERVISOR` - + Transfer, resolve issues
- `ADMIN` - Full access to all resources

**Permissions:**

```python
ROLE_PERMISSIONS = {
    "AGENT": [
        "conversations:read",
        "conversations:accept",
        "leads:read",
        "leads:write"
    ],
    "SUPERVISOR": [
        # All agent permissions +
        "conversations:transfer",
        "issues:resolve"
    ],
    "ADMIN": ["*"]  # All permissions
}
```

**Verification:**

```python
# Verify agent assignment
if conversation.agent_id != auth.agent_id:
    raise HTTPException(403, "Not assigned to this conversation")
```

### 8.3 Rate Limiting

**Per-Visitor:**

- 30 messages per minute

**Per-Org (Plan-Based):**

- FREE: 1,000 messages/month
- STARTER: 10,000 messages/month
- PROFESSIONAL: 100,000 messages/month
- ENTERPRISE: Unlimited

**API Endpoints:**

- `/api/v1/leads`: 100 per hour
- `/api/v1/issues`: 50 per hour
- `/api/v1/callbacks`: 30 per hour

### 8.4 Data Boundaries

**PII Protection:**

- Mask sensitive fields in logs
- Email: [`j***@example.com`](mailto:j***@example.com)
- Phone: `+1-***-**23`

**Cross-Org Access Prevention:**

- Always validate org ownership before returning data
- Don't reveal if resource exists in different org

**GDPR Compliance:**

- Soft deletion with `deleted_at` timestamp
- Hard deletion after 30 days (scheduled task)
- Right to be forgotten support

---

## 9. Versioning Strategy

### 9.1 API Versioning

**URL Path Versioning:**

```
/api/v1/leads
/api/v2/leads
```

**Breaking vs Non-Breaking:**

**Breaking (requires new version):**

- Removing fields
- Changing field types
- Removing endpoints
- Changing required fields

**Non-Breaking (same version):**

- Adding optional fields
- Adding new endpoints
- Deprecating (but not removing) fields

**Deprecation Timeline:**

1. T+0: Announce deprecation
2. T+3 months: Send deprecation warnings
3. T+6 months: Remove deprecated version

**Deprecation Headers:**

```python
response.headers["X-API-Deprecation"] = "Migrate to /api/v2/leads by 2026-08-01"
response.headers["X-API-Sunset"] = "2026-08-01"
```

### 9.2 WebSocket Protocol Evolution

**Message Type Versioning:**

```jsx
// v1
{"type": "AI_MESSAGE", "content": "..."}

// v2 (future)
{"type": "AI_MESSAGE", "version": 2, "content": "...", "metadata": {...}}
```

**Client Version Negotiation:**

- Client sends version in query param
- Server stores version in connection metadata
- Server formats messages based on client version
- Support at least 2 versions back

### 9.3 Database Schema Migrations

**Additive Changes (no downtime):**

- Add columns with defaults
- Add tables
- Add indexes

**Destructive Changes (coordination required):**

- Remove columns (deprecate first, wait 1 week)
- Change column types
- Remove tables

**Example (Alembic):**

```python
def upgrade():
    op.add_column('issues', sa.Column('priority', sa.String(50), server_default='NORMAL'))
    op.create_index('idx_issues_priority', 'issues', ['priority'])
```

---

## Appendix: Quick Reference

### State Transitions

| From | To | Trigger |
| --- | --- | --- |
| AI_ACTIVE | HUMAN_REQUESTED | REQUEST_HUMAN or visitor clicks "agent" |
| HUMAN_REQUESTED | HUMAN_CONNECTED | Agent accepts |
| HUMAN_REQUESTED | AI_ACTIVE | 5-min timeout |
| HUMAN_CONNECTED | CLOSED | Chat ended |
| HUMAN_CONNECTED | HUMAN_REQUESTED | Agent disconnects |

### WebSocket Message Types

**Visitor ↔ Server:**

- `USER_MESSAGE`, `AI_MESSAGE`, `AGENT_MESSAGE`, `SYSTEM_STATUS`, `MESSAGE_ACK`, `ERROR`

**Agent ↔ Server:**

- `AUTHENTICATE`, `ACCEPT_CHAT`, `AGENT_MESSAGE`, `NEW_HUMAN_REQUEST`, `CHAT_ACCEPTED`

### LangGraph Decisions

| Intent | Backend Action |
| --- | --- |
| INFORMATION_RETRIEVAL | Send AI response |
| CAPTURE_LEAD | Create lead + send response |
| ESCALATE_ISSUE | Create issue + handoff (if HIGH/CRITICAL) |
| REQUEST_HUMAN | Transition to HUMAN_REQUESTED |

### Redis Keys

```
visitor:{visitor_id}:socket
agent:{agent_id}:socket
org:{org_id}:agents:available
conversation:{conversation_id}:assigned_agent
rate:visitor:{visitor_id}:messages
```

---

**END OF DOCUMENT**

This ARC document represents a complete, production-ready specification for the multi-tenant SaaS AI chatbot platform with real-time human handoff, targeted at the hospitality industry.