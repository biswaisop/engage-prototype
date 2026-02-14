# nodes/chat_node.py
from utils import memory

CHAT_SYSTEM_PROMPT = (
    "You are a friendly hotel front-desk assistant. "
    "Keep responses warm, helpful, and concise. "
    "For any service requests, offer to help or connect to staff."
)


def chat_node(state, llm):
    print("chat node executed")
    """Handle general chat/small talk with conversation memory."""
    query = state.get("message", "")
    
    # Get history using shared memory utility
    history = memory.get_history(state, max_turns=4)
    formatted_history = memory.format_for_llm(history)
    
    # Build messages using shared utility
    messages = memory.build_messages(
        query=query,
        system_prompt=CHAT_SYSTEM_PROMPT,
        history=formatted_history
    )
    
    response = llm.invoke(messages)
    answer = response.content if hasattr(response, "content") else str(response)
    
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
