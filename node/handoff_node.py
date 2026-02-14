# nodes/handoff_node.py
from utils import memory


def handoff_node(state, llm):
    """Handle explicit handoff requests with conversation memory."""
    query = state.get("message", "")
    response_text = "I'm connecting you with a human agent now. They'll be with you shortly."
    
    return {
        **state,
        "messages": memory.add_to_history(state, query, response_text),
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
