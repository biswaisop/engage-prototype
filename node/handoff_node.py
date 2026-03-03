# nodes/handoff_node.py
from utils import memory


def handoff_node(state, llm):
    """Handle explicit handoff requests with conversation memory."""
    query = state.get("message", "")
    response_text = "I'm connecting you with a human agent now. They'll be with you shortly."
    
    return {
        **state,
        "result": {
            "intent": "HANDOFF_REQUEST",
            "response": response_text,
            "actions": [
                {
                    "type": "INITIATE_HANDOFF",
                    "payload": {"priority": "NORMAL"}
                }
            ]
        }
    }
