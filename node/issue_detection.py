# node/issue_detection.py
from utils.pg_memory import pg_memory
from db import get_db, Issue
import uuid

ISSUE_SYSTEM_PROMPT = (
    "You are a hotel support specialist handling guest complaints. "
    "Be empathetic, apologize sincerely, and assure prompt resolution. "
    "Let them know a human team member will assist immediately."
)


def issue_node(state: dict, llm):
    """Handle issues/complaints with PostgreSQL conversation memory."""
    query = state.get("message", "")
    org_id = state.get("org_id", str(uuid.uuid4()))
    thread_id = state.get("thread_id", str(uuid.uuid4()))
    
    with get_db() as db:
        # Get or create conversation in PostgreSQL
        conversation = pg_memory.get_or_create_conversation(
            db, thread_id, org_id
        )
        
        # Get history from PostgreSQL
        history = pg_memory.get_history(db, conversation.id, max_turns=4)
        formatted_history = pg_memory.format_for_llm(history)
        
        # Build messages using pg_memory utility
        messages = pg_memory.build_messages(
            query=query,
            system_prompt=ISSUE_SYSTEM_PROMPT,
            history=formatted_history
        )
        
        response = llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        
        # Save exchange to PostgreSQL
        pg_memory.add_exchange(db, conversation.id, query, answer)
        
        # Create issue record in database
        issue = Issue(
            org_id=uuid.UUID(org_id) if isinstance(org_id, str) else org_id,
            conversation_id=conversation.id,
            category="GENERAL",
            description=query,
            severity="HIGH",
            issue_metadata={"original_message": query},
            source="AI_DETECTED",
            status="OPEN"
        )
        db.add(issue)

    return {
        **state,
        "result": {
            "intent": "ISSUE_COMPLAINT",
            "response": answer,
            "confidence": 1.0,
            "actions": [
                {
                    "type": "CREATE_ISSUE",
                    "payload": {
                        "category": "GENERAL",
                        "severity": "HIGH",
                        "auto_escalate": True,
                    },
                },
                {
                    "type": "REQUEST_HUMAN",
                    "payload": {
                        "reason": "User reported an issue",
                        "priority": "HIGH",
                    },
                },
            ],
        },
    }
