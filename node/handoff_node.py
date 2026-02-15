# nodes/handoff_node.py
from utils.pg_memory import pg_memory
from db import get_db
import uuid


def handoff_node(state, llm):
    """Handle explicit handoff requests with PostgreSQL conversation memory."""
    query = state.get("message", "")
    org_id = state.get("org_id", str(uuid.uuid4()))
    thread_id = state.get("thread_id", str(uuid.uuid4()))
    response_text = "I'm connecting you with a human agent now. They'll be with you shortly."
    
    with get_db() as db:
        # Get or create conversation in PostgreSQL
        conversation = pg_memory.get_or_create_conversation(
            db, thread_id, org_id
        )
        
        # Update conversation state to request handoff
        conversation.state = "HUMAN_REQUESTED"
        conversation.handoff_reason = query
        
        # Save exchange to PostgreSQL
        pg_memory.add_exchange(db, conversation.id, query, response_text)
    
    return {
        **state,
        "result": {
            "intent": "HANDOFF_REQUEST",
            "response": response_text,
            "confidence": 1.0,
            "actions": [
                {
                    "type": "INITIATE_HANDOFF",
                    "payload": {"priority": "NORMAL"}
                }
            ]
        }
    }
