# node/issue_detection.py
from utils import memory

ISSUE_SYSTEM_PROMPT = (
    "You are a hotel support specialist handling guest complaints. "
    "Be empathetic, apologize sincerely, and assure prompt resolution. "
    "Let them know a human team member will assist immediately."
)


def issue_node(state: dict, llm):
    """Handle issues/complaints with conversation memory."""
    query = state.get("message", "")
    
    # Get history using shared memory utility
    history = memory.get_history(state, max_turns=4)
    formatted_history = memory.format_for_llm(history)
    
    # Build messages using shared utility
    messages = memory.build_messages(
        query=query,
        system_prompt=ISSUE_SYSTEM_PROMPT,
        history=formatted_history
    )
    
    response = llm.invoke(messages)
    answer = response.content if hasattr(response, "content") else str(response)

    return {
        **state,
        "result": {
            "intent": "ISSUE_COMPLAINT",
            "response": answer,
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
