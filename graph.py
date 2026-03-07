# graph.py
from langgraph.graph import StateGraph, END
from model.llm import llm
from schema.stateSchema import GraphState
from utils.redis_memory import RedisMemoryService
from node.router import intent_router_node
from node.rag import rag_node
from node.lead_detection import lead_node
from node.issue_detection import issue_node
from node.handoff_node import handoff_node
from node.chat_node import chat_node
# from langgraph.checkpoint.memory import InMemorySaver
from redis.exceptions import ConnectionError as RedisConnectionError
# checkpointer = InMemorySaver()

# Initialize Redis memory (module-level singleton)
redis_memory = RedisMemoryService(max_messages=20, ttl_seconds=259200)



def load_context(state: GraphState) -> GraphState:
    """Load conversation context from Redis"""
    thread_id = state.get("thread_id", "")
    print(f"[load_context] thread_id: {thread_id}")  # Debug
    try:
        if thread_id:
            context = redis_memory.get_context_string(thread_id, limit=6)
            
            # ✅ Hard cap context at 1000 chars to prevent bloat
            if context and len(context) > 1000:
                context = context[-1000:]
            print(f"[load_context] loaded context: {context[:100] if context else 'empty'}")  # Debug
            state["context"] = context or ""
    except RedisConnectionError as e:
        print(f"[load_context] Redis connection error: {e}")
        state["context"] = ""
    
    except Exception as e:
        print(f"[load_context] Redis error: {e}")
        state["context"] = ""
    
    return state

def save_to_redis(state: GraphState) -> GraphState:
    """Save interaction to Redis"""
    thread_id = state.get("thread_id", "")
    print(f"[save_to_redis] thread_id: {thread_id}")  # Debug
    try:
        if not thread_id:
            print("[save_to_redis] No thread_id, skipping save")  # Debug
            return state
        
        message = state.get("message", "").strip()
        response = state.get("result", {}).get("response", "").strip()
        intent = state.get("intent", "")
        
        print(f"[save_to_redis] message: {message[:50] if message else 'empty'}")  # Debug
        print(f"[save_to_redis] response: {response[:50] if response else 'empty'}")  # Debug
        
        # Save user message
        if message:
            redis_memory.add_message(thread_id, "user", message)
            print(f"[save_to_redis] Saved user message")  # Debug
        
        # Save assistant response
        if response:
            redis_memory.add_message(thread_id, "assistant", response, {"intent": intent})
            print(f"[save_to_redis] Saved assistant response")  # Debug
        state.pop("messages", None)
    except RedisConnectionError as e:
        print(f"[save_to_redis] Redis connection error: {e}")
    except Exception as e:
        print(f"[save_to_redis] Redis error: {e}")
    
    return state

def printState(s: GraphState):
    print(s)

builder = StateGraph(GraphState)

rag = rag_node()

# Add nodes
builder.add_node("load_context", load_context)
builder.add_node("intent_router", lambda s: intent_router_node(s, llm))
builder.add_node("rag_node", lambda s: rag.rag_node(s))
builder.add_node("lead_node", lambda s: lead_node(s, llm))
builder.add_node("issue_node", lambda s: issue_node(s, llm))
builder.add_node("handoff_node", lambda s: handoff_node(s, llm))
builder.add_node("chat_node", lambda s: chat_node(s, llm))
builder.add_node("save_memory", save_to_redis)
builder.add_node("print_state", printState)

# Entry point
builder.set_entry_point("load_context")
builder.add_edge("load_context", "intent_router")

# Conditional routing based on intent
builder.add_conditional_edges(
    "intent_router",
    lambda state: state.get("intent", "CHAT"),
    {
        "INFORMATION_RETRIEVAL": "rag_node",
        "LEAD_CAPTURE": "lead_node",
        "ISSUE_COMPLAINT": "issue_node",
        "HANDOFF_REQUEST": "handoff_node",
        "CHAT": "chat_node",
    }
)

# All nodes save to Redis before ending
builder.add_edge("rag_node", "save_memory")
builder.add_edge("lead_node", "save_memory")
builder.add_edge("issue_node", "save_memory")
builder.add_edge("handoff_node", "save_memory")
builder.add_edge("chat_node", "save_memory")
builder.add_edge("save_memory", "print_state")
builder.add_edge("print_state", END)

# Compile without checkpointer (Redis handles persistence)
graph = builder.compile()

if __name__ == "__main__":
    print(graph.invoke("Hello"))