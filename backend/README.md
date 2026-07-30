# Hotel Front Desk AI Chatbot

A production-grade, multi-tenant SaaS AI chatbot platform designed for the hospitality industry with intelligent intent routing, RAG-powered knowledge retrieval, and seamless human handoff capabilities.

## Overview

This chatbot system uses LangGraph orchestration to intelligently route conversations between AI and human agents, with persistent memory management via Redis and conversation storage in MongoDB. The system is optimized for hotel front desk operations, handling everything from guest inquiries to booking requests and issue escalation.

## Key Features

- **Intelligent Intent Classification**: Hybrid router using keyword matching + LLM classification
- **RAG-Powered Knowledge Base**: Vector store integration (ChromaDB) for accurate hotel policy/FAQ responses
- **Multi-Intent Handling**:
  - Information Retrieval (RAG)
  - Lead Capture (Booking Intent)
  - Issue/Complaint Detection
  - Human Handoff Requests
  - General Chat/Small Talk
- **Persistent Memory**: Redis-based conversation history with configurable TTL
- **Multi-Tenant Architecture**: Organization-scoped data isolation
- **Stateful Conversations**: Thread-based conversation tracking with checkpointing
- **Production-Ready**: Comprehensive error handling and fallback strategies

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONVERSATION FLOW                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Load Context  │ ← Redis Memory
                    │  from Redis   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │Intent Router  │ ← LLM Classification
                    │  Node         │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┬────────────┐
        ▼                   ▼                   ▼            ▼
  ┌──────────┐      ┌──────────┐      ┌──────────┐   ┌──────────┐
  │RAG Node  │      │Lead Node │      │Issue Node│   │Chat Node │
  │(KB Query)│      │(Booking) │      │(Escalate)│   │(Casual)  │
  └────┬─────┘      └────┬─────┘      └────┬─────┘   └────┬─────┘
       │                 │                  │              │
       └─────────────────┴──────────────────┴──────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │Save to Redis  │ → Persist Interaction
                    │   Memory      │
                    └───────────────┘
```

## Project Structure

```
front-desk/
├── db/
│   ├── connection.py          # MongoDB connection manager
│   ├── models.py              # Pydantic models (Message, Conversation)
│   └── __init__.py
├── model/
│   ├── llm.py                 # LLM configuration (Groq/Gemini)
│   └── __init__.py
├── node/
│   ├── chat_node.py           # General conversation handler
│   ├── handoff_node.py        # Human agent handoff
│   ├── issue_detection.py     # Complaint/issue escalation
│   ├── lead_detection.py      # Booking intent capture
│   ├── rag.py                 # RAG knowledge retrieval
│   ├── router.py              # Intent classification
│   └── __init__.py
├── schema/
│   ├── schemas.py             # State definitions (GraphState, IntentResult)
│   └── __init__.py
├── utils/
│   ├── docxProcessor.py       # DOCX document ingestion
│   ├── memory.py              # Legacy memory utility (deprecated)
│   ├── pdfProcessing.py       # PDF document ingestion
│   ├── redis_memory.py        # Redis-based conversation memory
│   ├── vec_store.py           # ChromaDB vector store service
│   └── __init__.py
├── graph.py                   # LangGraph workflow definition
├── main.py                    # CLI entry point
├── .env                       # Environment variables
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Redis (localhost:6379 or cloud instance)
- MongoDB (local or Atlas)
- ChromaDB Cloud account
- Groq API key (or Google Gemini)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/biswaisop/engage-prototype.git
cd front-desk
```

2. **Create virtual environment**:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install langgraph langchain-groq langchain-google-genai
pip install redis pymongo chromadb python-dotenv
pip install langchain-community pypdf python-docx
```

4. **Configure environment variables** (`.env`):
```env
# LLM Configuration
GROQ_LLM_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_key  # Alternative

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# MongoDB Configuration
MONGODB=mongodb://localhost:27017/
MONGODB-NAME=hotel-chatbot

# ChromaDB Configuration
CHROMADB_API_KEY=your_chromadb_key
CHROMADB_TENANT=your_tenant
VECTOR_DB=your_database
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Running the Chatbot

**CLI Mode**:
```bash
python main.py
```

**Example Interaction**:
```
Hotel Front Desk Bot (type 'quit' to exit)
Session: a1b2c3d4...
----------------------------------------

You: What time is breakfast served?
Bot: Breakfast is served daily from 6:30 AM to 10:30 AM in the main dining room.

You: I want to book a room for next weekend
Bot: I'd be happy to help you with that! Could you please provide...
```

## Intent Classification System

### Intent Types

| Intent | Description | Example Triggers |
|--------|-------------|------------------|
| `INFORMATION_RETRIEVAL` | Policy/FAQ questions | "What's the cancellation policy?", "Do you have a pool?" |
| `LEAD_CAPTURE` | Booking inquiries | "I want to book a room", "Check availability for March 15" |
| `ISSUE_COMPLAINT` | Problems/complaints | "My room is dirty", "I was charged twice" |
| `HANDOFF_REQUEST` | Human agent request | "Speak to a manager", "Talk to someone" |
| `CHAT` | Greetings/casual talk | "Hi", "Thank you", "My name is John" |

### Router Logic

The `intent_router_node` in `node/router.py` uses a **hybrid approach**:

1. **Fast Keyword Check** (emergency/handoff/greetings)
2. **LLM Classification** (complex/ambiguous messages)
3. **Context-Aware** (uses conversation history for follow-ups)

## Knowledge Base (RAG)

### Document Ingestion

**Supported Formats**: PDF, DOCX

**Processing Pipeline**:
```python
from utils import PDFprocessor, Vector_store_service

# Process documents
processor = PDFprocessor(chunk_size=600, chunk_overlap=80)
chunks = processor.processPDF("./data/hotel_policy.pdf")

# Store in vector database
vector_store = Vector_store_service(org_id="test-org-1")
result = vector_store.embed_documents(chunks)
```

**Chunking Strategy**:
- Chunk size: 600 characters
- Overlap: 80 characters
- Metadata enrichment (page, source, char count)

### Query Enhancement

The `rag_node` in `node/rag.py` enhances vague queries using conversation history:

```python
# User: "What's the policy?"
# User: "tell me more"  ← Enhanced with previous context
# Enhanced query: "What's the policy? tell me more"
```

## Memory Management

### Redis-Based Persistence

The `RedisMemoryService` in `utils/redis_memory.py` provides:

- **Sliding Window**: Stores last 30 messages per thread
- **TTL**: 3-day expiration (259200 seconds)
- **Thread Isolation**: Separate memory per `thread_id`

**Key Operations**:
```python
from utils import RedisMemoryService

redis_memory = RedisMemoryService(max_messages=20, ttl_seconds=259200)

# Add message
redis_memory.add_message(thread_id, "user", "Hello")

# Get formatted context for LLM
context = redis_memory.get_context_string(thread_id, limit=10)
# Output: "USER: Hello\nASSISTANT: Hi! How can I help you?"
```

### MongoDB Storage

Persistent conversation records in `db/models.py`:

```python
class Conversation(BaseModel):
    thread_id: str
    org_id: str
    user_id: Optional[str]
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
```

## Graph Workflow

The `graph.py` defines the LangGraph state machine:

```python
builder = StateGraph(GraphState)

# Nodes
builder.add_node("load_context", load_context)      # Load from Redis
builder.add_node("intent_router", router_with_llm)  # Classify intent
builder.add_node("rag_node", rag_handler)           # KB query
builder.add_node("lead_node", lead_handler)         # Booking capture
builder.add_node("issue_node", issue_handler)       # Escalation
builder.add_node("chat_node", chat_handler)         # Casual chat
builder.add_node("save_memory", save_to_redis)      # Persist to Redis

# Routing
builder.add_conditional_edges(
    "intent_router",
    lambda state: state.get("intent", "CHAT"),
    {
        "INFORMATION_RETRIEVAL": "rag_node",
        "LEAD_CAPTURE": "lead_node",
        "ISSUE_COMPLAINT": "issue_node",
        "CHAT": "chat_node",
    }
)
```

## Multi-Tenant Support

**Organization Isolation**:
- Vector store namespaces: `org_{org_id}`
- Redis keys: `chat:memory:{thread_id}`
- MongoDB queries: Always filtered by `org_id`

**Usage Example**:
```python
result = graph.invoke(
    {"message": "What's check-in time?", "org_id": "hotel-xyz"},
    config={"configurable": {"thread_id": "guest-123"}}
)
```

## Error Handling

### Fallback Strategies

| Scenario | Fallback Action |
|----------|----------------|
| Vector store timeout | Handoff to human agent |
| LLM failure | Cached generic response + escalation |
| No context found | "I don't have that information. Let me connect you to a human agent." |
| Redis unavailable | Continue without memory (stateless mode) |

### Hallucination Prevention

The RAG node includes multiple safeguards:
- Confidence threshold (>0.7 required)
- Grounding verification
- Citation tracking
- Explicit "I don't know" responses

## State Schema

```python
class GraphState(TypedDict):
    message: str                     # Current user input
    messages: List[Dict[str, str]]   # Full conversation history
    thread_id: str                   # Conversation session ID
    org_id: str                      # Organization identifier
    intent: Optional[str]            # Classified intent
    confidence: Optional[float]      # Classification confidence
    context: Optional[str]           # Retrieved knowledge context
    result: Optional[Dict]           # Node execution result
```

## Configuration

### LLM Selection

Switch between models in `model/llm.py`:

```python
# Groq (default)
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)

# Google Gemini (alternative)
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
```

### Memory Settings

Adjust in `graph.py`:

```python
redis_memory = RedisMemoryService(
    max_messages=20,        # Sliding window size
    ttl_seconds=259200      # 3-day expiration
)
```

## Roadmap

- [ ] WebSocket API for real-time chat
- [ ] Agent dashboard UI
- [ ] Webhook integrations
- [ ] Analytics and reporting
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Sentiment analysis

## Contributing

This is a private development repository. For questions or access requests, contact the repository owner.

## License

Proprietary - All rights reserved

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- LLM powered by [Groq](https://groq.com/)
- Vector storage via [ChromaDB](https://www.trychroma.com/)

---

**Architecture Reference**: See the `Architecture & API Reference (ARC)` document for complete system specification.
