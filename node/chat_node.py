# nodes/chat_node.py
from utils import memory
import uuid
from db import get_db
from utils import pg_memory
CHAT_SYSTEM_PROMPT = (
    "You are a friendly hotel front-desk assistant. "
    "Keep responses warm, helpful, and concise. "
    "For any service requests, offer to help or connect to staff."
)


def chat_node(state, llm):
    print("chat node executed")
    """Handle general chat/small talk with conversation memory."""
    query = state.get("message", "")
    thread_id = state.get("thread_id", str(uuid.uuid4()))
    org_id = state.get("org_id", str(uuid.uuid4()))
    
    with get_db() as db:
        conversation = pg_memory.get_or_create_conversation(db, thread_id = thread_id, org_id=org_id)

    history = pg_memory.get_history(db, conversation.id, max_turns=6)
    messages = pg_memory.build_messages(
        query=query,
        system_prompt=CHAT_SYSTEM_PROMPT,
        history=history
    )
    # Get history using shared memory utility
    # history = memory.get_history(state, max_turns=4)
    # formatted_history = memory.format_for_llm(history)
    
    #  Build messages using shared utility
    # messages = memory.build_messages(
    #     query=query,
    #     system_prompt=CHAT_SYSTEM_PROMPT,
    #     history=formatted_history
    # )
    
    response = llm.invoke(messages)
    answer = response.content if hasattr(response, "content") else str(response)

    pg_memory.add_exchange(
        db, 
        conversation_id=conversation.id,
        user_message=query,
        assistant_response=answer,
        assistant_type="AI"
    )
    
    return {
        **state,
        "messages": memory.add_to_history(state, query, answer),
        "result": {
            "intent": "CHAT",
            "response": answer,
            "confidence": 0.7,
            "actions": []
        }
    }
