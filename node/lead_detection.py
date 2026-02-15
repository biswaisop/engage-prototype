from utils.pg_memory import pg_memory
from db import get_db, Lead
import uuid

LEAD_SYSTEM_PROMPT = (
    "You are a hotel booking assistant. "
    "Help guests with reservations, pricing, and availability. "
    "Politely gather contact details and booking preferences. "
    "Be warm and professional."
)


def lead_node(state, llm):
    print("lead node executed")
    """Handle booking inquiries with PostgreSQL conversation memory."""
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
            system_prompt=LEAD_SYSTEM_PROMPT,
            history=formatted_history
        )
        
        response = llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        
        # Save exchange to PostgreSQL
        pg_memory.add_exchange(db, conversation.id, query, answer)
        
        # Create lead record in database
        lead = Lead(
            org_id=uuid.UUID(org_id) if isinstance(org_id, str) else org_id,
            conversation_id=conversation.id,
            contact_info={"message": query},
            intent_type="LEAD_CAPTURE",
            intent_details={"source_message": query},
            source="AI_DETECTED",
            status="NEW"
        )
        db.add(lead)
    
    return {
        **state,
        "result": {
            "intent": "LEAD_CAPTURE",
            "response": answer,
            "confidence": 0.95,
            "actions": [
                {
                    "type": "CREATE_LEAD",
                    "payload": {
                        "source": "CHAT"
                    }
                }
            ]
        }
    }