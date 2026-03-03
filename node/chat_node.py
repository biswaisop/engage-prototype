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
    context = state.get("context", "")
    prompt = f"""
        previous conversation: {context}
        user: {query}

    """
    
    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)
    
    return {
        **state,
        "result": {
            "intent": "CHAT",
            "response": answer,
            "actions": []
        }
    }
